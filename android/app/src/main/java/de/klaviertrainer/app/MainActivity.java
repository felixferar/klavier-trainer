package de.klaviertrainer.app;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.ActivityInfo;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.graphics.Rect;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.Looper;
import android.os.SystemClock;
import android.util.Base64;
import android.view.PixelCopy;
import android.view.View;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.view.WindowManager;
import android.webkit.PermissionRequest;
import android.webkit.RenderProcessGoneDetail;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;

import androidx.webkit.JavaScriptReplyProxy;
import androidx.webkit.WebViewAssetLoader;
import androidx.webkit.WebViewCompat;
import androidx.webkit.WebViewFeature;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

/**
 * Native Android-Hülle um die Web-Oberfläche.
 *
 * Die Oberfläche läuft IMMER unter https://appassets.androidplatform.net/www/ – egal ob sie
 * frisch von GitHub Pages kommt, aus dem Zwischenspeicher oder aus der eingebauten Kopie.
 * Dadurch gibt es nur einen localStorage (vorher: online und offline getrennt → Datenverlust).
 *
 * Reihenfolge beim Laden: GitHub Pages (kurzer Timeout) → zuletzt geladene Version → eingebaute Version.
 */
public class MainActivity extends Activity {
    private static final String APP_HOST = "appassets.androidplatform.net";
    private static final String APP_ORIGIN = "https://" + APP_HOST;
    private static final String APP_URL = APP_ORIGIN + "/www/index.html";
    private static final String MIGRATE_URL = APP_ORIGIN + "/migrate.html";
    /** Online-Version (GitHub Pages), beim Bauen gesetzt. Leer = nur eingebaute Version. */
    private static final String WEB_URL = BuildConfig.WEB_URL;

    private static final int REQ_MIC = 1, REQ_FILE = 2, REQ_SAVE = 3, REQ_BT = 4;
    private static final int CONNECT_TIMEOUT_MS = 3000, READ_TIMEOUT_MS = 5000;

    private WebView web;
    private PermissionRequest pendingPermission;
    private ValueCallback<Uri[]> fileCallback;
    private JavaScriptReplyProxy reply;
    private byte[] pendingSave;
    private SharedPreferences prefs;
    private KeyboardLink kb;
    private Runnable afterBtPerm;

    /** Woher die aktuell angezeigte Oberfläche stammt: online | cache | offline */
    private volatile String source = "offline";

    // Einmalige Übernahme der Daten aus dem alten Speicher (github.io-Origin)
    private enum Mig { NONE, LOAD_OLD, LOAD_NEW }
    private Mig mig = Mig.NONE;
    private String migDump;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        prefs = getSharedPreferences("kt", MODE_PRIVATE);
        // Absturzprotokoll: wird beim nächsten Start an die Web-App gemeldet (Einstellungen → Fehlersuche)
        final Thread.UncaughtExceptionHandler prevHandler = Thread.getDefaultUncaughtExceptionHandler();
        Thread.setDefaultUncaughtExceptionHandler((th, ex) -> {
            try {
                StringWriter sw = new StringWriter();
                ex.printStackTrace(new PrintWriter(sw));
                String st = sw.toString();
                prefs.edit().putString("lastCrash", new java.util.Date() + " · Thread " + th.getName() + "\n" + (st.length() > 6000 ? st.substring(0, 6000) : st)).commit();
            } catch (Throwable ignored) {}
            if (prevHandler != null) prevHandler.uncaughtException(th, ex);
        });
        kb = new KeyboardLink(this, prefs, this::send);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(Color.parseColor("#171512"));
        web = new WebView(this);
        web.setBackgroundColor(Color.parseColor("#171512"));
        root.addView(web, new FrameLayout.LayoutParams(-1, -1));
        setContentView(root);

        root.setOnApplyWindowInsetsListener((v, insets) -> {
            if (Build.VERSION.SDK_INT >= 30) {
                android.graphics.Insets i = insets.getInsets(WindowInsets.Type.displayCutout() | WindowInsets.Type.systemBars());
                v.setPadding(i.left, i.top, i.right, i.bottom);
            }
            return insets;
        });
        hideSystemBars();

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setAllowFileAccess(false);
        s.setUserAgentString(s.getUserAgentString() + " KlavierTrainerApp/" + BuildConfig.VERSION_NAME);

        final WebViewAssetLoader loader = new WebViewAssetLoader.Builder()
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                .build();

        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                Uri u = request.getUrl();
                if (APP_HOST.equals(u.getHost()) && u.getPath() != null) {
                    String p = u.getPath();
                    if (p.equals("/migrate.html")) return text("text/html", "<!doctype html><meta charset=utf-8><title>.</title>");
                    if (p.startsWith("/www/")) return serveWeb(p.substring(5));
                }
                return loader.shouldInterceptRequest(u);
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                onMigrationPage(url);
            }

            // Der Teil, der die Webseite darstellt, ist abgestürzt (z. B. Speicher beim Drehen mit großem Video).
            // Ohne diese Methode beendet Android die ganze App. So: protokollieren und neu starten.
            @Override
            public boolean onRenderProcessGone(WebView view, RenderProcessGoneDetail detail) {
                try {
                    prefs.edit().putString("lastCrash", new java.util.Date() + " · Darstellung abgestürzt (" + (detail.didCrash() ? "Absturz" : "vom System beendet, wohl Speicher") + ")").commit();
                } catch (Throwable ignored) {}
                scanning = false;
                try { ((FrameLayout) view.getParent()).removeView(view); view.destroy(); } catch (Throwable ignored) {}
                setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_UNSPECIFIED);
                Intent i = getIntent();
                finish();
                startActivity(i);
                return true;
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                // Alte Seite für die Datenübernahme nicht erreichbar (offline) → beim nächsten Start erneut
                if (request.isForMainFrame() && mig == Mig.LOAD_OLD) {
                    mig = Mig.NONE;
                    view.loadUrl(APP_URL);
                }
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri u = request.getUrl();
                if (isOwnHost(u)) return false;
                try { startActivity(new Intent(Intent.ACTION_VIEW, u)); } catch (Exception ignored) {}
                return true;
            }
        });

        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onPermissionRequest(final PermissionRequest request) {
                runOnUiThread(() -> {
                    boolean wantsAudio = false;
                    for (String r : request.getResources())
                        if (PermissionRequest.RESOURCE_AUDIO_CAPTURE.equals(r)) wantsAudio = true;
                    if (!wantsAudio || !APP_HOST.equals(request.getOrigin().getHost())) { request.deny(); return; }
                    if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                        request.grant(new String[]{PermissionRequest.RESOURCE_AUDIO_CAPTURE});
                    } else {
                        pendingPermission = request;
                        requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, REQ_MIC);
                    }
                });
            }

            @Override
            public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
                if (fileCallback != null) fileCallback.onReceiveValue(null);
                fileCallback = callback;
                Intent i = new Intent(Intent.ACTION_GET_CONTENT);
                i.addCategory(Intent.CATEGORY_OPENABLE);
                i.setType("*/*");
                try {
                    startActivityForResult(Intent.createChooser(i, "Datei wählen"), REQ_FILE);
                } catch (Exception e) {
                    fileCallback = null;
                    return false;
                }
                return true;
            }
        });

        // Brücke Web ↔ App: nur für die eigene Seite im Hauptframe (nicht für das YouTube-iframe)
        if (WebViewFeature.isFeatureSupported(WebViewFeature.WEB_MESSAGE_LISTENER)) {
            WebViewCompat.addWebMessageListener(web, "KTNative", Collections.singleton(APP_ORIGIN),
                    (view, message, origin, isMainFrame, proxy) -> {
                        if (!isMainFrame || message.getData() == null) return;
                        reply = proxy;
                        handleMessage(message.getData());
                    });
        }

        boolean migrated = prefs.getBoolean("migrated_v1", false);
        if (!migrated && !WEB_URL.isEmpty()) {
            mig = Mig.LOAD_OLD;
            web.loadUrl(WEB_URL);
        } else if (savedInstanceState != null) {
            web.restoreState(savedInstanceState);
        } else {
            web.loadUrl(APP_URL);
        }
    }

    // ---------------------------------------------------------------- Laden der Oberfläche

    private WebResourceResponse serveWeb(String rel) {
        if (rel.isEmpty()) rel = "index.html";
        if (rel.contains("..")) return null;
        File cached = new File(new File(getFilesDir(), "www"), rel);
        boolean isIndex = rel.equals("index.html");

        if (!WEB_URL.isEmpty()) {
            HttpURLConnection c = null;
            try {
                c = (HttpURLConnection) new URL(WEB_URL + rel + "?t=" + System.currentTimeMillis()).openConnection();
                c.setConnectTimeout(CONNECT_TIMEOUT_MS);
                c.setReadTimeout(READ_TIMEOUT_MS);
                c.setUseCaches(false);
                c.setRequestProperty("Cache-Control", "no-cache");
                if (c.getResponseCode() == 200) {
                    byte[] body = readAll(c.getInputStream());
                    if (body.length > 0) {
                        String mime = mimeOf(c.getContentType(), rel);
                        if (isIndex) {
                            source = "online";
                            writeAtomic(cached, body); // für offline: zuletzt geladene Version
                        }
                        return response(mime, body);
                    }
                }
            } catch (Exception ignored) {
                // offline / Timeout → Fallback
            } finally {
                if (c != null) c.disconnect();
            }
        }
        try {
            if (cached.isFile()) {
                if (isIndex) source = "cache";
                return response(mimeOf(null, rel), readAll(new FileInputStream(cached)));
            }
        } catch (Exception ignored) {}
        try {
            byte[] body = readAll(getAssets().open("www/" + rel));
            if (isIndex) source = "offline";
            return response(mimeOf(null, rel), body);
        } catch (Exception e) {
            WebResourceResponse r = text("text/plain", "Nicht gefunden");
            r.setStatusCodeAndReasonPhrase(404, "Not Found");
            return r;
        }
    }

    private static WebResourceResponse response(String mime, byte[] body) {
        Map<String, String> h = new HashMap<>();
        h.put("Cache-Control", "no-store");
        return new WebResourceResponse(mime, "utf-8", 200, "OK", h, new ByteArrayInputStream(body));
    }

    private static WebResourceResponse text(String mime, String s) {
        return response(mime, s.getBytes(StandardCharsets.UTF_8));
    }

    private static String mimeOf(String contentType, String rel) {
        if (contentType != null && !contentType.isEmpty()) return contentType.split(";")[0].trim();
        if (rel.endsWith(".html")) return "text/html";
        if (rel.endsWith(".js")) return "application/javascript";
        if (rel.endsWith(".css")) return "text/css";
        if (rel.endsWith(".json")) return "application/json";
        if (rel.endsWith(".svg")) return "image/svg+xml";
        if (rel.endsWith(".png")) return "image/png";
        return "application/octet-stream";
    }

    private static byte[] readAll(InputStream in) throws Exception {
        try (InputStream i = in) {
            ByteArrayOutputStream o = new ByteArrayOutputStream();
            byte[] b = new byte[16384];
            int n;
            while ((n = i.read(b)) > 0) o.write(b, 0, n);
            return o.toByteArray();
        }
    }

    private static void writeAtomic(File f, byte[] data) {
        try {
            File dir = f.getParentFile();
            if (dir != null && !dir.isDirectory() && !dir.mkdirs()) return;
            File tmp = new File(f.getPath() + ".tmp");
            try (FileOutputStream o = new FileOutputStream(tmp)) { o.write(data); }
            if (!tmp.renameTo(f)) tmp.delete();
        } catch (Exception ignored) {}
    }

    // ---------------------------------------------------------------- Datenübernahme (einmalig)

    private void onMigrationPage(String url) {
        if (url == null) return;
        Uri u = Uri.parse(url);
        if (mig == Mig.LOAD_OLD && !WEB_URL.isEmpty() && Uri.parse(WEB_URL).getHost().equals(u.getHost())) {
            web.evaluateJavascript(
                    "(function(){var o={};for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);" +
                            "if(k.indexOf('kt_')===0)o[k]=localStorage.getItem(k)}return JSON.stringify(o)})()",
                    v -> {
                        migDump = v; // ist bereits ein JS-String-Literal
                        mig = Mig.LOAD_NEW;
                        web.loadUrl(MIGRATE_URL);
                    });
        } else if (mig == Mig.LOAD_NEW && url.startsWith(MIGRATE_URL)) {
            String dump = (migDump == null || migDump.equals("null")) ? "'{}'" : migDump;
            web.evaluateJavascript(
                    "(function(d){d=JSON.parse(d);if(localStorage.getItem('kt_migrated'))return 'skip';" +
                            "for(var k in d)localStorage.setItem(k,d[k]);localStorage.setItem('kt_migrated','1');return 'ok'})(" + dump + ")",
                    r -> {
                        if (r != null && (r.contains("ok") || r.contains("skip")))
                            prefs.edit().putBoolean("migrated_v1", true).apply();
                        mig = Mig.NONE;
                        migDump = null;
                        web.loadUrl(APP_URL);
                    });
        }
    }

    // ---------------------------------------------------------------- Brücke

    private void handleMessage(String data) {
        try {
            JSONObject m = new JSONObject(data);
            switch (m.optString("cmd")) {
                case "info": {
                    JSONObject o = new JSONObject();
                    o.put("cmd", "info");
                    o.put("source", source);
                    o.put("version", BuildConfig.VERSION_NAME);
                    o.put("build", BuildConfig.VERSION_CODE);
                    o.put("caps", new JSONArray().put("b64save").put("orient").put("scanWide").put("crashlog"));
                    o.put("crash", prefs.getString("lastCrash", ""));
                    send(o);
                    break;
                }
                case "save": {
                    String d = m.optString("data", "");
                    // b64:true → Binärdatei (z. B. .mid); sonst Text (UTF-8)
                    pendingSave = m.optBoolean("b64", false) ? Base64.decode(d, Base64.DEFAULT) : d.getBytes(StandardCharsets.UTF_8);
                    Intent i = new Intent(Intent.ACTION_CREATE_DOCUMENT);
                    i.addCategory(Intent.CATEGORY_OPENABLE);
                    i.setType(m.optString("mime", "application/json"));
                    i.putExtra(Intent.EXTRA_TITLE, m.optString("name", "klavier-trainer-backup.json"));
                    startActivityForResult(i, REQ_SAVE);
                    break;
                }
                case "capture":
                    capture();
                    break;
                case "crashClear":
                    prefs.edit().remove("lastCrash").apply();
                    break;
                case "orient": {
                    // Umwandlung: quer und fest; danach wieder frei drehbar
                    setRequestedOrientation(m.optBoolean("landscape", false)
                            ? ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE : ActivityInfo.SCREEN_ORIENTATION_UNSPECIFIED);
                    JSONObject o = new JSONObject();
                    o.put("cmd", "orient");
                    o.put("ok", true);
                    send(o);
                    break;
                }
                case "scanStart":
                    startScan(m);
                    break;
                case "scanStop":
                    scanning = false;
                    break;
                // ---- Keyboard über Bluetooth-MIDI / USB-MIDI
                case "kbScan":
                    withBtPerm(() -> kb.scan());
                    break;
                case "kbConnect": {
                    final String addr = m.optString("addr"), name = m.optString("name", "Keyboard");
                    withBtPerm(() -> kb.connect(addr, name));
                    break;
                }
                case "kbDisconnect":
                    kb.disconnect(m.optBoolean("forget", true));
                    break;
                case "kbAuto":
                    if (hasBtPerm()) kb.autoConnect(); else kb.report();
                    break;
                case "kbStatus":
                    kb.report();
                    break;
                case "kbEnableBt":
                    withBtPerm(() -> {
                        try { startActivity(new Intent(android.bluetooth.BluetoothAdapter.ACTION_REQUEST_ENABLE)); } catch (Exception ignored) {}
                    });
                    break;
            }
        } catch (Exception e) {
            sendError("unknown", e);
        }
    }

    private void send(JSONObject o) {
        final String s = o.toString();
        runOnUiThread(() -> { if (reply != null) reply.postMessage(s); });
    }

    private void sendError(String cmd, Exception e) {
        try {
            JSONObject o = new JSONObject();
            o.put("cmd", cmd);
            o.put("ok", false);
            o.put("error", String.valueOf(e != null ? e.getMessage() : "Fehler"));
            send(o);
        } catch (Exception ignored) {}
    }

    /** Test: Kann die App ihr eigenes Fenster inkl. YouTube-Video abfotografieren? (Grundlage für „Video → Noten“) */
    private void capture() {
        int w = web.getWidth(), h = web.getHeight();
        if (w <= 0 || h <= 0) { sendError("capture", null); return; }
        final Bitmap bmp = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888);
        int[] loc = new int[2];
        web.getLocationInWindow(loc);
        Rect r = new Rect(loc[0], loc[1], loc[0] + w, loc[1] + h);
        PixelCopy.request(getWindow(), r, bmp, result -> {
            if (result != PixelCopy.SUCCESS) {
                sendError("capture", new Exception("PixelCopy-Fehler " + result));
                return;
            }
            new Thread(() -> {
                try {
                    float scale = Math.min(1f, 1280f / Math.max(w, h));
                    Bitmap out = scale < 1f ? Bitmap.createScaledBitmap(bmp, Math.round(w * scale), Math.round(h * scale), true) : bmp;
                    ByteArrayOutputStream o = new ByteArrayOutputStream();
                    out.compress(Bitmap.CompressFormat.JPEG, 80, o);
                    JSONObject j = new JSONObject();
                    j.put("cmd", "capture");
                    j.put("ok", true);
                    j.put("img", "data:image/jpeg;base64," + Base64.encodeToString(o.toByteArray(), Base64.NO_WRAP));
                    send(j);
                } catch (Exception e) {
                    sendError("capture", e);
                }
            }).start();
        }, new Handler(Looper.getMainLooper()));
    }

    // ---------------------------------------------------------------- Video → Noten: Bildzeilen-Scanner
    // Fotografiert ~25× pro Sekunde den Videobereich (verkleinert) und schickt nur einzelne Pixelzeilen
    // (durch die schwarzen und die weißen Tasten der Video-Tastatur) an die Web-App.
    // Läuft auf einem eigenen Hintergrund-Thread: Fotografieren, Pixel auslesen und Verpacken bremsen
    // weder das Video noch die Oberfläche (vorher alles auf dem Haupt-Thread).
    private volatile boolean scanning = false;
    private boolean scanBusy = false;   // nur auf dem Scan-Thread benutzt
    private Bitmap scanBmp;
    private Rect scanRect;
    private int[] scanRows;
    private int scanInterval = 40;
    private Handler scanHandler;

    private Handler scanHandler() {
        if (scanHandler == null) {
            HandlerThread t = new HandlerThread("kt-scan");
            t.start();
            scanHandler = new Handler(t.getLooper());
        }
        return scanHandler;
    }

    private void startScan(JSONObject m) throws Exception {
        float d = getResources().getDisplayMetrics().density;
        int[] loc = new int[2];
        web.getLocationInWindow(loc);
        int x = loc[0] + Math.round((float) m.getDouble("x") * d), y = loc[1] + Math.round((float) m.getDouble("y") * d);
        int w = Math.max(1, Math.round((float) m.getDouble("w") * d)), h = Math.max(1, Math.round((float) m.getDouble("h") * d));
        final Rect rect = new Rect(x, y, x + w, y + h);
        // Zeilenbreite: so viel wie gewünscht, höchstens die echte Pixelbreite des Videobereichs und 1280
        final int ow = Math.max(64, Math.min(Math.min(1280, w), m.optInt("ow", 480)));
        final int oh = Math.max(8, Math.round(ow * (float) h / w));
        JSONArray rows = m.getJSONArray("rows");
        final int[] rr = new int[rows.length()];
        for (int i = 0; i < rows.length(); i++)
            rr[i] = Math.max(0, Math.min(oh - 1, (int) Math.round(rows.getDouble(i) * (oh - 1))));
        final int interval = Math.max(20, m.optInt("interval", 40));
        scanHandler().post(() -> {
            scanRect = rect;
            scanBmp = Bitmap.createBitmap(ow, oh, Bitmap.Config.ARGB_8888);
            scanRows = rr;
            scanInterval = interval;
            scanBusy = false;
            scanning = true;
            scanHandler.removeCallbacks(scanTick); // nie zwei Schleifen gleichzeitig (Neustart nach Markieren)
            scanHandler.post(scanTick);
            try {
                JSONObject o = new JSONObject();
                o.put("cmd", "scanStarted");
                o.put("ok", true);
                o.put("w", ow);
                send(o);
            } catch (Exception ignored) {}
        });
    }

    private final Runnable scanTick = new Runnable() {
        @Override
        public void run() {
            if (!scanning) return;
            if (!scanBusy && scanBmp != null) {
                scanBusy = true;
                final long t = SystemClock.uptimeMillis();
                try {
                    PixelCopy.request(getWindow(), scanRect, scanBmp, res -> {
                        scanBusy = false;
                        if (res == PixelCopy.SUCCESS && scanning) sendRows(t);
                    }, scanHandler);
                } catch (Exception e) {
                    scanBusy = false;
                }
            }
            scanHandler.postDelayed(this, scanInterval);
        }
    };

    private void sendRows(long t) {
        try {
            int ow = scanBmp.getWidth();
            int[] px = new int[ow];
            byte[] out = new byte[ow * 3 * scanRows.length];
            int k = 0;
            for (int r : scanRows) {
                scanBmp.getPixels(px, 0, ow, 0, r, ow, 1);
                for (int p : px) {
                    out[k++] = (byte) ((p >> 16) & 255);
                    out[k++] = (byte) ((p >> 8) & 255);
                    out[k++] = (byte) (p & 255);
                }
            }
            JSONObject j = new JSONObject();
            j.put("cmd", "rows");
            j.put("t", t);
            j.put("w", ow);
            j.put("n", scanRows.length);
            j.put("d", Base64.encodeToString(out, Base64.NO_WRAP));
            send(j);
        } catch (Exception ignored) {}
    }

    // ---------------------------------------------------------------- Bluetooth-Berechtigungen

    private String[] btPerms() {
        if (Build.VERSION.SDK_INT >= 31)
            return new String[]{Manifest.permission.BLUETOOTH_SCAN, Manifest.permission.BLUETOOTH_CONNECT};
        return new String[]{Manifest.permission.ACCESS_FINE_LOCATION};
    }

    private boolean hasBtPerm() {
        for (String p : btPerms()) if (checkSelfPermission(p) != PackageManager.PERMISSION_GRANTED) return false;
        return true;
    }

    private void withBtPerm(Runnable r) {
        if (hasBtPerm()) { r.run(); return; }
        afterBtPerm = r;
        requestPermissions(btPerms(), REQ_BT);
    }

    // ---------------------------------------------------------------- System

    private boolean isOwnHost(Uri u) {
        if (u == null || u.getHost() == null) return false;
        if (APP_HOST.equals(u.getHost())) return true;
        // github.io nur während der einmaligen Datenübernahme
        return mig != Mig.NONE && !WEB_URL.isEmpty() && u.getHost().equals(Uri.parse(WEB_URL).getHost());
    }

    private void hideSystemBars() {
        if (Build.VERSION.SDK_INT >= 30) {
            WindowInsetsController c = getWindow().getInsetsController();
            if (c != null) {
                c.hide(WindowInsets.Type.statusBars() | WindowInsets.Type.navigationBars());
                c.setSystemBarsBehavior(WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
            }
        } else {
            getWindow().getDecorView().setSystemUiVisibility(
                    View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY | View.SYSTEM_UI_FLAG_FULLSCREEN
                            | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
        }
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) hideSystemBars();
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] results) {
        if (requestCode == REQ_BT) {
            boolean ok = results.length > 0;
            for (int r : results) if (r != PackageManager.PERMISSION_GRANTED) ok = false;
            Runnable r = afterBtPerm;
            afterBtPerm = null;
            if (ok && r != null) r.run();
            else try { send(new JSONObject().put("cmd", "kbState").put("state", "noperm").put("msg", "Ohne die Erlaubnis für „Geräte in der Nähe“ kann die App das Keyboard nicht finden.")); } catch (Exception ignored) {}
            return;
        }
        if (requestCode == REQ_MIC && pendingPermission != null) {
            if (results.length > 0 && results[0] == PackageManager.PERMISSION_GRANTED)
                pendingPermission.grant(new String[]{PermissionRequest.RESOURCE_AUDIO_CAPTURE});
            else pendingPermission.deny();
            pendingPermission = null;
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == REQ_FILE && fileCallback != null) {
            Uri[] result = null;
            if (resultCode == RESULT_OK && data != null && data.getData() != null)
                result = new Uri[]{data.getData()};
            fileCallback.onReceiveValue(result);
            fileCallback = null;
            return;
        }
        if (requestCode == REQ_SAVE) {
            boolean ok = false;
            if (resultCode == RESULT_OK && data != null && data.getData() != null && pendingSave != null) {
                try (OutputStream o = getContentResolver().openOutputStream(data.getData(), "wt")) {
                    if (o != null) { o.write(pendingSave); ok = true; }
                } catch (Exception ignored) {}
            }
            pendingSave = null;
            try {
                JSONObject j = new JSONObject();
                j.put("cmd", "saved");
                j.put("ok", ok);
                send(j);
            } catch (Exception ignored) {}
            return;
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    @Override
    @SuppressWarnings("deprecation")
    public void onBackPressed() {
        web.evaluateJavascript("(window.appBack && window.appBack()) ? 'y' : 'n'", value -> {
            if (value == null || !value.contains("y")) MainActivity.super.onBackPressed();
        });
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        web.saveState(outState);
    }

    @Override
    protected void onDestroy() { if (kb != null) kb.disconnect(false); super.onDestroy(); }

    @Override
    protected void onPause() { super.onPause(); scanning = false; web.onPause(); }

    @Override
    protected void onResume() { super.onResume(); web.onResume(); hideSystemBars(); }
}
