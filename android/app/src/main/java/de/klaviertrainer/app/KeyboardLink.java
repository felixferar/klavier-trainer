package de.klaviertrainer.app;

import android.annotation.SuppressLint;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothManager;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanFilter;
import android.bluetooth.le.ScanResult;
import android.bluetooth.le.ScanSettings;
import android.content.Context;
import android.content.SharedPreferences;
import android.media.midi.MidiDevice;
import android.media.midi.MidiDeviceInfo;
import android.media.midi.MidiManager;
import android.media.midi.MidiOutputPort;
import android.media.midi.MidiReceiver;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.ParcelUuid;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

/**
 * Keyboard über Bluetooth-MIDI (oder USB-MIDI) verbinden und jeden Tastendruck an die Web-App melden.
 *
 * Nachrichten an die Web-App:
 *   kbState {state: off|scanning|connecting|on|lost|fail|btoff|noperm, name, addr, msg}
 *   kbFound {name, addr, usb}
 *   kbScanDone {}
 *   midi    {e: [[status, data1, data2], …]}
 */
@SuppressLint("MissingPermission") // Berechtigungen prüft MainActivity, bevor sie hier etwas aufruft
class KeyboardLink {
    interface Out { void send(JSONObject o); }

    /** Standard-Kennung für Bluetooth-MIDI-Geräte */
    private static final ParcelUuid MIDI_UUID = ParcelUuid.fromString("03B80E5A-EDE8-4B33-A751-6CE34EC4C700");
    private static final long SCAN_MS = 12000, RETRY_MS = 4000;

    private final Context ctx;
    private final Out out;
    private final SharedPreferences prefs;
    private final Handler h = new Handler(Looper.getMainLooper());
    private final MidiManager midi;
    private final BluetoothAdapter bt;

    private BluetoothLeScanner scanner;
    private ScanCallback scanCb;
    private final Set<String> seen = new HashSet<>();
    private MidiDevice device;
    private MidiOutputPort port;
    private String curAddr, curName;
    private boolean wanted = false; // soll verbunden sein (automatisch neu verbinden)
    private String state = "off";

    KeyboardLink(Context ctx, SharedPreferences prefs, Out out) {
        this.ctx = ctx;
        this.prefs = prefs;
        this.out = out;
        midi = (MidiManager) ctx.getSystemService(Context.MIDI_SERVICE);
        BluetoothManager bm = (BluetoothManager) ctx.getSystemService(Context.BLUETOOTH_SERVICE);
        bt = bm != null ? bm.getAdapter() : null;
        if (midi != null) {
            midi.registerDeviceCallback(new MidiManager.DeviceCallback() {
                @Override public void onDeviceRemoved(MidiDeviceInfo info) {
                    if (device != null && device.getInfo().getId() == info.getId()) lost();
                }
                @Override public void onDeviceAdded(MidiDeviceInfo info) {
                    // USB-Keyboard eingesteckt und noch nichts verbunden → direkt nehmen
                    if (info.getType() == MidiDeviceInfo.TYPE_USB && device == null && info.getOutputPortCount() > 0) openUsb(info);
                }
            }, h);
        }
    }

    boolean available() { return midi != null; }
    boolean bluetoothOn() { return bt != null && bt.isEnabled(); }
    String savedAddr() { return prefs.getString("kb_addr", ""); }

    // ------------------------------------------------------------ Suchen

    void scan() {
        if (midi == null) { setState("fail", "Dieses Handy unterstützt kein MIDI."); return; }
        seen.clear();
        // USB-Geräte gleich mit anbieten
        for (MidiDeviceInfo info : midi.getDevices()) {
            if (info.getType() == MidiDeviceInfo.TYPE_USB && info.getOutputPortCount() > 0) found(nameOf(info), "usb:" + info.getId(), true);
        }
        if (!bluetoothOn()) { setState("btoff", "Bluetooth ist aus."); return; }
        scanner = bt.getBluetoothLeScanner();
        if (scanner == null) { setState("btoff", "Bluetooth ist aus."); return; }
        stopScan();
        scanCb = new ScanCallback() {
            @Override public void onScanResult(int type, ScanResult r) { onResult(r); }
            @Override public void onBatchScanResults(java.util.List<ScanResult> rs) { for (ScanResult r : rs) onResult(r); }
            @Override public void onScanFailed(int code) { setState("fail", "Suche fehlgeschlagen (" + code + ")."); }
        };
        ScanFilter f = new ScanFilter.Builder().setServiceUuid(MIDI_UUID).build();
        ScanSettings s = new ScanSettings.Builder().setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY).build();
        try {
            scanner.startScan(Collections.singletonList(f), s, scanCb);
        } catch (Exception e) {
            setState("fail", "Suche nicht möglich: " + e.getMessage());
            return;
        }
        setState("scanning", null);
        h.postDelayed(scanEnd, SCAN_MS);
    }

    private final Runnable scanEnd = () -> {
        stopScan();
        try { out.send(new JSONObject().put("cmd", "kbScanDone")); } catch (Exception ignored) {}
        if ("scanning".equals(state)) setState(device != null ? "on" : "off", null);
    };

    private void onResult(ScanResult r) {
        BluetoothDevice d = r.getDevice();
        if (d == null) return;
        String name = d.getName();
        if ((name == null || name.isEmpty()) && r.getScanRecord() != null) name = r.getScanRecord().getDeviceName();
        found(name == null || name.isEmpty() ? "Bluetooth-Keyboard" : name, d.getAddress(), false);
    }

    private void found(String name, String addr, boolean usb) {
        if (!seen.add(addr)) return;
        try { out.send(new JSONObject().put("cmd", "kbFound").put("name", name).put("addr", addr).put("usb", usb)); } catch (Exception ignored) {}
    }

    void stopScan() {
        h.removeCallbacks(scanEnd);
        if (scanner != null && scanCb != null) { try { scanner.stopScan(scanCb); } catch (Exception ignored) {} }
        scanCb = null;
    }

    // ------------------------------------------------------------ Verbinden

    void connect(String addr, String name) {
        stopScan();
        closeDevice();
        wanted = true;
        curAddr = addr;
        curName = name;
        if (addr.startsWith("usb:")) {
            int id = Integer.parseInt(addr.substring(4));
            for (MidiDeviceInfo info : midi.getDevices()) if (info.getId() == id) { openUsb(info); return; }
            setState("fail", "Das USB-Keyboard ist nicht mehr eingesteckt.");
            return;
        }
        if (!bluetoothOn()) { setState("btoff", "Bluetooth ist aus."); return; }
        BluetoothDevice d;
        try { d = bt.getRemoteDevice(addr); } catch (Exception e) { setState("fail", "Ungültiges Gerät."); return; }
        setState("connecting", null);
        midi.openBluetoothDevice(d, dev -> {
            if (dev == null) { failOrRetry("Verbindung fehlgeschlagen. Ist das Keyboard eingeschaltet und in der Nähe?"); return; }
            attach(dev);
        }, h);
        h.postDelayed(connectTimeout, 15000);
    }

    private final Runnable connectTimeout = () -> {
        if ("connecting".equals(state)) failOrRetry("Keine Antwort vom Keyboard. Ist es eingeschaltet und Bluetooth am Keyboard an?");
    };

    private void openUsb(MidiDeviceInfo info) {
        wanted = true;
        curAddr = "usb:" + info.getId();
        curName = nameOf(info);
        setState("connecting", null);
        midi.openDevice(info, dev -> { if (dev == null) setState("fail", "USB-Keyboard ließ sich nicht öffnen."); else attach(dev); }, h);
    }

    private void attach(MidiDevice dev) {
        h.removeCallbacks(connectTimeout);
        device = dev;
        int n = dev.getInfo().getOutputPortCount();
        if (n < 1) { setState("fail", "Das Gerät sendet keine Tasten."); closeDevice(); return; }
        port = dev.openOutputPort(0);
        if (port == null) { setState("fail", "Das Keyboard ist schon mit einer anderen App verbunden."); closeDevice(); return; }
        port.connect(receiver);
        String nm = nameOf(dev.getInfo());
        if (nm != null && !nm.isEmpty() && !nm.startsWith("MIDI")) curName = nm;
        if (curAddr != null && !curAddr.startsWith("usb:")) prefs.edit().putString("kb_addr", curAddr).putString("kb_name", curName).apply();
        setState("on", null);
    }

    private void failOrRetry(String msg) {
        closeDevice();
        if (wanted && curAddr != null && !curAddr.startsWith("usb:") && "lost".equals(state)) { h.postDelayed(retry, RETRY_MS); return; }
        setState("fail", msg);
    }

    private void lost() {
        closeDevice();
        setState("lost", "Verbindung zum Keyboard verloren – verbinde neu …");
        if (wanted && curAddr != null && !curAddr.startsWith("usb:")) h.postDelayed(retry, RETRY_MS);
    }

    private final Runnable retry = () -> {
        if (!wanted || device != null || curAddr == null || !bluetoothOn()) return;
        BluetoothDevice d;
        try { d = bt.getRemoteDevice(curAddr); } catch (Exception e) { return; }
        midi.openBluetoothDevice(d, dev -> {
            if (dev == null) { h.postDelayed(KeyboardLink.this.retry, RETRY_MS); return; }
            attach(dev);
        }, h);
    };

    /** Beim App-Start: zuletzt verbundenes Keyboard still wieder verbinden */
    void autoConnect() {
        String a = savedAddr();
        if (a.isEmpty() || device != null || !bluetoothOn()) { report(); return; }
        curAddr = a;
        curName = prefs.getString("kb_name", "Keyboard");
        wanted = true;
        state = "lost"; // so wird bei Misserfolg leise weiter probiert
        setState("connecting", null);
        retry.run();
    }

    void disconnect(boolean forget) {
        wanted = false;
        h.removeCallbacks(retry);
        stopScan();
        closeDevice();
        if (forget) prefs.edit().remove("kb_addr").remove("kb_name").apply();
        setState("off", null);
    }

    private void closeDevice() {
        try { if (port != null) { port.disconnect(receiver); port.close(); } } catch (Exception ignored) {}
        try { if (device != null) device.close(); } catch (Exception ignored) {}
        port = null;
        device = null;
    }

    void report() { setState(device != null ? "on" : state, null); }

    private void setState(String s, String msg) {
        state = s;
        try {
            JSONObject o = new JSONObject().put("cmd", "kbState").put("state", s).put("name", curName == null ? "" : curName)
                    .put("addr", curAddr == null ? "" : curAddr).put("saved", savedAddr());
            if (msg != null) o.put("msg", msg);
            out.send(o);
        } catch (Exception ignored) {}
    }

    private static String nameOf(MidiDeviceInfo info) {
        Bundle p = info.getProperties();
        String n = p.getString(MidiDeviceInfo.PROPERTY_NAME);
        if (n == null) n = p.getString(MidiDeviceInfo.PROPERTY_PRODUCT);
        return n == null ? "Keyboard" : n;
    }

    // ------------------------------------------------------------ MIDI-Daten lesen

    private int running = 0, need = 0, have = 0;
    private final int[] buf = new int[2];

    private final MidiReceiver receiver = new MidiReceiver() {
        @Override
        public void onSend(byte[] msg, int offset, int count, long timestamp) {
            JSONArray ev = new JSONArray();
            for (int i = offset; i < offset + count; i++) {
                int b = msg[i] & 0xFF;
                if (b >= 0xF8) continue;                 // Echtzeit-Bytes (Clock, Active Sensing) ignorieren
                if (b >= 0x80) {
                    if (b >= 0xF0) { running = 0; need = 0; continue; } // System-Nachrichten: nicht gebraucht
                    running = b;
                    int hi = b & 0xF0;
                    need = (hi == 0xC0 || hi == 0xD0) ? 1 : 2;
                    have = 0;
                    continue;
                }
                if (running == 0) continue;
                buf[have++] = b;
                if (have >= need) {
                    int hi = running & 0xF0;
                    if (hi == 0x90 || hi == 0x80 || hi == 0xB0) {
                        JSONArray e = new JSONArray();
                        e.put(running).put(buf[0]).put(need > 1 ? buf[1] : 0);
                        ev.put(e);
                    }
                    have = 0; // Running Status: nächste Datenbytes gehören zur selben Nachricht
                }
            }
            if (ev.length() > 0) {
                try { out.send(new JSONObject().put("cmd", "midi").put("e", ev)); } catch (Exception ignored) {}
            }
        }
    };
}
