package de.klaviertrainer.app;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.view.WindowManager;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;

import androidx.webkit.WebViewAssetLoader;

/**
 * Die App ist eine native Android-Hülle um die Web-Oberfläche in assets/www/index.html.
 * Die Seite wird über https://appassets.androidplatform.net geladen, damit Mikrofon
 * (getUserMedia) und YouTube-Einbettung funktionieren.
 */
public class MainActivity extends Activity {
    private static final String LOCAL_URL = "https://appassets.androidplatform.net/assets/www/index.html";
    /** Online-Version (GitHub Pages). Änderungen dort sind beim nächsten App-Start da – ohne Neuinstallation. */
    private static final String WEB_URL = BuildConfig.WEB_URL;
    private boolean usingFallback = false;
    private static final int REQ_MIC = 1;
    private static final int REQ_FILE = 2;

    private WebView web;
    private PermissionRequest pendingPermission;
    private ValueCallback<Uri[]> fileCallback;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // Bildschirm beim Üben nicht ausgehen lassen
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(Color.parseColor("#0F1115"));
        web = new WebView(this);
        web.setBackgroundColor(Color.parseColor("#0F1115"));
        root.addView(web, new FrameLayout.LayoutParams(-1, -1));
        setContentView(root);

        // Kamera-Notch / Systemleisten: Inhalt nicht darunter zeichnen
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
        // immer die neueste Online-Version holen; ohne Internet greift die eingebaute Version
        s.setCacheMode(WebSettings.LOAD_NO_CACHE);

        final WebViewAssetLoader loader = new WebViewAssetLoader.Builder()
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                .build();

        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                return loader.shouldInterceptRequest(request.getUrl());
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                // Keine Verbindung zur Online-Version → eingebaute Version laden
                if (request.isForMainFrame() && !usingFallback && !WEB_URL.isEmpty()) {
                    usingFallback = true;
                    view.loadUrl(LOCAL_URL);
                }
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri u = request.getUrl();
                if (isOwnHost(u)) return false;
                // externe Links (z. B. musescore.com) im normalen Browser öffnen
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
                    if (!wantsAudio || !isOwnHost(request.getOrigin())) { request.deny(); return; }
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
                    startActivityForResult(Intent.createChooser(i, "MIDI-Datei wählen"), REQ_FILE);
                } catch (Exception e) {
                    fileCallback = null;
                    return false;
                }
                return true;
            }
        });

        if (savedInstanceState != null) web.restoreState(savedInstanceState);
        else web.loadUrl(WEB_URL.isEmpty() ? LOCAL_URL : WEB_URL);
    }

    private boolean isOwnHost(Uri u) {
        if (u == null || u.getHost() == null) return false;
        if ("appassets.androidplatform.net".equals(u.getHost())) return true;
        return !WEB_URL.isEmpty() && u.getHost().equals(Uri.parse(WEB_URL).getHost());
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
        super.onActivityResult(requestCode, resultCode, data);
    }

    /** Zurück-Taste: erst die App-Ansicht schließen (Einstellungen, Song …), dann die App. */
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
    protected void onPause() { super.onPause(); web.onPause(); }

    @Override
    protected void onResume() { super.onResume(); web.onResume(); hideSystemBars(); }
}
