package pt.viarchive.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Insets;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.WindowInsets;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.Toast;
import androidx.webkit.WebViewAssetLoader;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/** Local assets only: no server, INTERNET permission, cross-origin bridge, or file:// access. */
public final class MainActivity extends Activity {
    private static final int EXPORT_REQUEST = 42;
    private WebView web;
    private String assetHost;
    private Uri entry;
    private File pendingExport;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        assetHost = getString(R.string.asset_host);
        entry = new Uri.Builder().scheme("https").authority(assetHost).path("/").build();
        if (Build.VERSION.SDK_INT >= 30) getWindow().setDecorFitsSystemWindows(false);
        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(Color.rgb(16, 17, 23));
        web = new WebView(this);
        web.setBackgroundColor(Color.rgb(16, 17, 23));
        root.addView(web, new FrameLayout.LayoutParams(-1, -1));
        setContentView(root);
        root.setOnApplyWindowInsetsListener((view, insets) -> {
            if (Build.VERSION.SDK_INT >= 30) {
                Insets bars = insets.getInsets(WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout() | WindowInsets.Type.ime());
                view.setPadding(bars.left, bars.top, bars.right, bars.bottom);
                return WindowInsets.CONSUMED;
            }
            // Before Android 11 the decor already fits system bars and adjustResize handles the keyboard.
            return insets.consumeSystemWindowInsets();
        });
        root.requestApplyInsets();
        WebView.setWebContentsDebuggingEnabled(false);
        WebSettings settings = web.getSettings();
        settings.setJavaScriptEnabled(true); // React runs from our packaged, CSP-protected assets only.
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(false);
        settings.setAllowContentAccess(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setSupportMultipleWindows(false);
        settings.setJavaScriptCanOpenWindowsAutomatically(false);
        settings.setMediaPlaybackRequiresUserGesture(true);
        WebViewAssetLoader loader = new WebViewAssetLoader.Builder()
            .setDomain(assetHost).addPathHandler("/", this::assetResponse).build();
        web.setWebViewClient(new WebViewClient() {
            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                if (!isLocal(request.getUrl()) || !"GET".equals(request.getMethod())) return failure(403, "Blocked");
                WebResourceResponse response = loader.shouldInterceptRequest(request.getUrl());
                return response == null ? failure(404, "Not Found") : response;
            }
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                if (isLocal(request.getUrl())) return false;
                if (request.isForMainFrame()) openExternal(request.getUrl());
                return true;
            }
            @Override public void onPageFinished(WebView view, String url) {
                if (!isLocal(Uri.parse(url))) return;
                // React renders source links with target=_blank; route their clicks through our allowlist.
                view.evaluateJavascript("if(!window.__offlineLinks){window.__offlineLinks=true;document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[target]');if(a)a.removeAttribute('target');},true);}", null);
            }
        });
        web.setWebChromeClient(new WebChromeClient());
        web.addJavascriptInterface(new ArchiveBridge(), "Android");
        if (state != null) {
            String pending = state.getString("pendingExport");
            if (pending != null && pending.matches("archive-export-[a-zA-Z0-9-]+\\.json")) {
                File file = new File(getCacheDir(), pending);
                if (file.isFile()) pendingExport = file;
            }
        }
        if (state == null || web.restoreState(state) == null || web.getUrl() == null || !isLocal(Uri.parse(web.getUrl()))) web.loadUrl(entry.toString());
        if (Build.VERSION.SDK_INT >= 33) getOnBackInvokedDispatcher().registerOnBackInvokedCallback(
            android.window.OnBackInvokedDispatcher.PRIORITY_DEFAULT, this::navigateBack);
    }

    private boolean isLocal(Uri uri) {
        return "https".equals(uri.getScheme()) && assetHost.equals(uri.getHost())
            && (uri.getPort() == -1 || uri.getPort() == 443) && uri.getUserInfo() == null;
    }

    private WebResourceResponse assetResponse(String path) {
        if (path.contains("..") || path.contains("\\") || path.indexOf('\0') >= 0) return failure(403, "Blocked");
        String asset = path.isEmpty() ? "index.html" : path;
        InputStream stream;
        try {
            stream = getAssets().open("www/" + asset);
        } catch (IOException absent) {
            if (path.contains(".")) return failure(404, "Not Found");
            // BrowserRouter deep links and history all resolve locally, without a server.
            asset = "index.html";
            try { stream = getAssets().open("www/index.html"); }
            catch (IOException missingBundle) { return failure(404, "Not Found"); }
        }
        Map<String, String> headers = new HashMap<>();
        headers.put("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self'; frame-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'");
        headers.put("X-Content-Type-Options", "nosniff");
        return new WebResourceResponse(mime(asset), "UTF-8", 200, "OK", headers, stream);
    }

    private static String mime(String path) {
        String lower = path.toLowerCase(Locale.ROOT);
        if (lower.endsWith(".html")) return "text/html";
        if (lower.endsWith(".js")) return "application/javascript";
        if (lower.endsWith(".css")) return "text/css";
        if (lower.endsWith(".json")) return "application/json";
        if (lower.endsWith(".svg")) return "image/svg+xml";
        if (lower.endsWith(".webp")) return "image/webp";
        if (lower.endsWith(".png")) return "image/png";
        if (lower.endsWith(".woff2")) return "font/woff2";
        if (lower.endsWith(".woff")) return "font/woff";
        if (lower.endsWith(".txt")) return "text/plain";
        return "application/octet-stream";
    }

    private static WebResourceResponse failure(int code, String reason) {
        return new WebResourceResponse("text/plain", "UTF-8", code, reason, new HashMap<>(), new ByteArrayInputStream(new byte[0]));
    }

    private void openExternal(Uri uri) {
        if (!("https".equals(uri.getScheme()) || "http".equals(uri.getScheme())) || uri.getHost() == null) return;
        new AlertDialog.Builder(this).setTitle("Ligação externa")
            .setMessage("Esta fonte abre no navegador e precisa de Internet. O arquivo continua disponível offline.\n\n" + uri.getHost())
            .setNegativeButton("Ficar no arquivo", null)
            .setPositiveButton("Abrir navegador", (dialog, which) -> {
                try { startActivity(new Intent(Intent.ACTION_VIEW, uri).addCategory(Intent.CATEGORY_BROWSABLE)); }
                catch (ActivityNotFoundException e) { message("Não foi encontrado um navegador."); }
            }).show();
    }

    private void navigateBack() { if (web.canGoBack()) web.goBack(); else finish(); }
    @Override public void onBackPressed() { navigateBack(); }
    @Override protected void onSaveInstanceState(Bundle state) {
        web.saveState(state);
        if (pendingExport != null) state.putString("pendingExport", pendingExport.getName());
        super.onSaveInstanceState(state);
    }
    @Override protected void onPause() { web.onPause(); super.onPause(); }
    @Override protected void onResume() { super.onResume(); if (web != null) web.onResume(); }
    @Override protected void onDestroy() {
        if (web != null) { web.removeJavascriptInterface("Android"); web.destroy(); }
        if (isFinishing()) clearExport();
        super.onDestroy();
    }
    private void message(String text) { Toast.makeText(this, text, Toast.LENGTH_LONG).show(); }
    private void clearExport() { if (pendingExport != null) { pendingExport.delete(); pendingExport = null; } }

    public final class ArchiveBridge {
        @JavascriptInterface public void saveFavorites(String json) {
            if (json == null || json.length() > 1_000_000) {
                runOnUiThread(() -> message("A exportação é demasiado grande.")); return;
            }
            try {
                JSONObject data = new JSONObject(json);
                if (!"VI Archive".equals(data.getString("archive")) || data.getString("exported_at").isEmpty()) throw new JSONException("Invalid archive");
                JSONArray entities = data.getJSONArray("entities");
                Set<String> ids = new HashSet<>();
                for (int i = 0; i < entities.length(); i++) {
                    JSONObject item = entities.getJSONObject(i);
                    String id = item.getString("id");
                    if (id.isEmpty() || !ids.add(id) || item.getString("slug").isEmpty() || item.getString("name").isEmpty()) throw new JSONException("Invalid entity");
                }
            } catch (JSONException e) { runOnUiThread(() -> message("Não foi possível validar os guardados.")); return; }
            runOnUiThread(() -> {
                if (isFinishing() || web.getUrl() == null || !isLocal(Uri.parse(web.getUrl()))) return;
                if (pendingExport != null) { message("Conclua ou cancele a exportação anterior."); return; }
                try {
                    pendingExport = File.createTempFile("archive-export-", ".json", getCacheDir());
                    try (OutputStream out = new FileOutputStream(pendingExport)) { out.write(json.getBytes(StandardCharsets.UTF_8)); }
                    Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT).addCategory(Intent.CATEGORY_OPENABLE)
                        .setType("application/json").putExtra(Intent.EXTRA_TITLE, "vi-archive-guardados.json");
                    startActivityForResult(intent, EXPORT_REQUEST);
                } catch (IOException | ActivityNotFoundException e) { clearExport(); message("Não foi possível iniciar a exportação."); }
            });
        }
    }

    @Override protected void onActivityResult(int request, int result, Intent data) {
        super.onActivityResult(request, result, data);
        if (request != EXPORT_REQUEST) return;
        if (result != RESULT_OK || data == null || data.getData() == null || pendingExport == null) { clearExport(); return; }
        final File source = pendingExport;
        final Uri destination = data.getData();
        pendingExport = null;
        new Thread(() -> {
            try (InputStream in = new FileInputStream(source); OutputStream out = getContentResolver().openOutputStream(destination, "wt")) {
                if (out == null) throw new IOException("No document stream");
                byte[] buffer = new byte[8192];
                int count;
                while ((count = in.read(buffer)) != -1) out.write(buffer, 0, count);
                out.flush();
                runOnUiThread(() -> message("Guardados exportados."));
            } catch (IOException | SecurityException e) {
                try { android.provider.DocumentsContract.deleteDocument(getContentResolver(), destination); } catch (Exception ignored) { /* Provider may not support deletion. */ }
                runOnUiThread(() -> message("Não foi possível guardar o ficheiro. Tente novamente."));
            } finally { source.delete(); }
        }, "archive-export").start();
    }
}
