package com.cahazu.email;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.webkit.CookieManager;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.Toast;

import java.security.SecureRandom;

public class MainActivity extends Activity {
    private static final String HOME = "https://emailfake.com/";
    private static final int BLACK = Color.rgb(0, 0, 0);
    private static final int DARK = Color.rgb(18, 18, 18);
    private static final int GOLD = Color.rgb(255, 215, 0);

    private static final String[] FIRST_NAMES = {
            "adia", "aldi", "alif", "amel", "anisa", "arya", "ayu", "bella", "bima", "citra",
            "dani", "dimas", "eka", "fajar", "farhan", "fitri", "gina", "hafiz", "ilham", "indah",
            "intan", "irfan", "jihan", "kevin", "lina", "maya", "nabila", "nadia", "nanda", "putri",
            "rafi", "rahma", "rani", "reza", "rizki", "salsa", "sinta", "tiara", "vina", "yoga"
    };

    private static final String[] LAST_NAMES = {
            "aditya", "akbar", "ananda", "angga", "arif", "fahmi", "fauzan", "hadi", "hakim", "hamzah",
            "jaya", "kurnia", "maulana", "nugraha", "pratama", "putra", "ramadhan", "saputra", "setiawan", "utama",
            "wijaya", "yudha", "fajar", "ilham", "darma", "reza", "rizal", "firman", "bagas", "surya"
    };

    private final SecureRandom random = new SecureRandom();
    private WebView webView;
    private String lastPrefix = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        applyWindowDarkTheme();

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(BLACK);
        root.setLayoutParams(new ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));

        Button randomButton = new Button(this);
        randomButton.setText("ACAK NAMA");
        randomButton.setAllCaps(true);
        randomButton.setTextColor(GOLD);
        randomButton.setTextSize(15f);
        randomButton.setMinHeight(dp(48));
        randomButton.setPadding(dp(14), dp(8), dp(14), dp(8));

        GradientDrawable buttonBg = new GradientDrawable();
        buttonBg.setColor(DARK);
        buttonBg.setCornerRadius(dp(12));
        buttonBg.setStroke(dp(1), Color.rgb(120, 100, 0));
        randomButton.setBackground(buttonBg);

        LinearLayout.LayoutParams buttonParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT);
        buttonParams.setMargins(dp(10), dp(8), dp(10), dp(8));
        root.addView(randomButton, buttonParams);

        webView = new WebView(this);
        webView.setBackgroundColor(BLACK);
        LinearLayout.LayoutParams webParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                0,
                1f);
        root.addView(webView, webParams);
        setContentView(root);

        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setLoadsImagesAutomatically(true);
        s.setLoadWithOverviewMode(false);
        s.setUseWideViewPort(true);
        s.setBuiltInZoomControls(true);
        s.setDisplayZoomControls(false);
        s.setSupportZoom(true);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        s.setAllowContentAccess(true);
        s.setAllowFileAccess(false);
        s.setMediaPlaybackRequiresUserGesture(false);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            s.setForceDark(WebSettings.FORCE_DARK_ON);
        }

        CookieManager cookies = CookieManager.getInstance();
        cookies.setAcceptCookie(true);
        cookies.setAcceptThirdPartyCookies(webView, true);

        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                return handleUrl(url);
            }

            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                super.onPageStarted(view, url, favicon);
                view.setBackgroundColor(BLACK);
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                applyDarkPageCss(view);
                CookieManager.getInstance().flush();
            }
        });

        webView.setOnLongClickListener(v -> false);
        webView.setScrollBarStyle(View.SCROLLBARS_INSIDE_OVERLAY);

        randomButton.setOnClickListener(v -> randomizeEmailPrefix());

        if (savedInstanceState == null) {
            webView.loadUrl(HOME);
        } else {
            webView.restoreState(savedInstanceState);
        }
    }

    private void applyWindowDarkTheme() {
        Window window = getWindow();
        window.setStatusBarColor(BLACK);
        window.setNavigationBarColor(BLACK);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            window.getDecorView().setSystemUiVisibility(0);
        }
    }

    private void applyDarkPageCss(WebView view) {
        if (view == null) return;
        String js = "(function(){" +
                "var id='cahazu-dark-style';" +
                "var old=document.getElementById(id);if(old)old.remove();" +
                "var s=document.createElement('style');s.id=id;" +
                "s.innerHTML='" +
                "html,body{background:#000!important;color:#e8e8e8!important;}" +
                "main,section,article,.container,.content,.wrapper,.card,.panel,.box,.well{background-color:#000!important;color:#e8e8e8!important;}" +
                "input,select,textarea{background:#111!important;color:#fff!important;border-color:#444!important;}" +
                "button,.btn,input[type=button],input[type=submit]{background:#151515!important;color:#ffd700!important;border-color:#665500!important;}" +
                "a{color:#ffd84d!important;}hr{border-color:#333!important;}" +
                "';" +
                "(document.head||document.documentElement).appendChild(s);" +
                "document.documentElement.style.backgroundColor='#000';" +
                "if(document.body){document.body.style.backgroundColor='#000';document.body.style.color='#e8e8e8';}" +
                "})()";
        view.evaluateJavascript(js, null);
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    private String generateRandomPrefix() {
        String prefix;
        do {
            String first = FIRST_NAMES[random.nextInt(FIRST_NAMES.length)];
            String last = LAST_NAMES[random.nextInt(LAST_NAMES.length)];
            int number = 10 + random.nextInt(90);
            prefix = first + last + number;
        } while (prefix.equals(lastPrefix));
        lastPrefix = prefix;
        return prefix;
    }

    private void randomizeEmailPrefix() {
        if (webView == null) return;

        final String prefix = generateRandomPrefix();
        String js = "(function(){" +
                "var inputs=Array.prototype.slice.call(document.querySelectorAll('input'));" +
                "var target=null;" +
                "for(var i=0;i<inputs.length;i++){" +
                "var e=inputs[i];" +
                "if(e.disabled||e.readOnly)continue;" +
                "var t=(e.type||'text').toLowerCase();" +
                "if(t!=='text'&&t!=='search'&&t!=='email')continue;" +
                "var r=e.getBoundingClientRect();" +
                "if(r.width<30||r.height<15||r.bottom<0)continue;" +
                "var val=(e.value||'').trim();" +
                "if(val.indexOf('@')>=0)continue;" +
                "if(val.indexOf('.')>=0&&val.length>3)continue;" +
                "target=e;break;" +
                "}" +
                "if(!target)return 'NO_INPUT';" +
                "var setter=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;" +
                "setter.call(target,'" + prefix + "');" +
                "target.focus();" +
                "target.dispatchEvent(new Event('input',{bubbles:true}));" +
                "target.dispatchEvent(new Event('change',{bubbles:true}));" +
                "target.dispatchEvent(new KeyboardEvent('keyup',{bubbles:true,key:'a'}));" +
                "target.blur();" +
                "return 'OK';" +
                "})()";

        webView.evaluateJavascript(js, result -> {
            if (result != null && result.contains("NO_INPUT")) {
                Toast.makeText(this, "Kolom nama email belum ditemukan", Toast.LENGTH_SHORT).show();
            } else {
                Toast.makeText(this, "Nama baru: " + prefix, Toast.LENGTH_SHORT).show();
            }
        });
    }

    private boolean handleUrl(String url) {
        if (url == null) return false;
        Uri uri = Uri.parse(url);
        String scheme = uri.getScheme();
        if (scheme == null || scheme.equalsIgnoreCase("http") || scheme.equalsIgnoreCase("https")) {
            return false;
        }
        try {
            startActivity(new Intent(Intent.ACTION_VIEW, uri));
        } catch (Exception ignored) {
        }
        return true;
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        webView.saveState(outState);
        super.onSaveInstanceState(outState);
    }

    @Override
    protected void onPause() {
        CookieManager.getInstance().flush();
        webView.onPause();
        super.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        webView.onResume();
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.stopLoading();
            webView.loadUrl("about:blank");
            webView.clearHistory();
            webView.removeAllViews();
            webView.destroy();
            webView = null;
        }
        super.onDestroy();
    }
}
