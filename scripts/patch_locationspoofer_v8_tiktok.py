import runpy
from pathlib import Path

# Start from proven V7: NO-API search + OSM map + spacing + Indonesia-only search.
runpy.run_path('scripts/patch_locationspoofer_v7_indonesia.py', run_name='__main__')

# Add TikTok Asia as an explicit hook target. The existing LocationHooker prefix logic
# also covers all subprocesses such as com.ss.android.ugc.trill:push / :sandboxed_process*.
hook = Path('locationspoofer/app/src/main/java/com/suseoaa/locationspoofer/xposed/LocationHooker.kt')
text = hook.read_text(encoding='utf-8')
anchor = '        val TARGET_PACKAGES = setOf(\n'
if anchor not in text:
    raise SystemExit('TARGET_PACKAGES anchor not found')
entry = '            "com.ss.android.ugc.trill",   // TikTok Asia (all subprocesses covered by prefix match)\n'
if '"com.ss.android.ugc.trill"' not in text:
    text = text.replace(anchor, anchor + entry, 1)

# Add a distinct log marker so the TikTok hook can be verified from logcat.
old_log = '        XposedBridge.log("[LocationSpoofer] Hooking package: $pkg")'
new_log = '        XposedBridge.log("[LocationSpoofer V8] Hooking package: $pkg")'
if old_log in text:
    text = text.replace(old_log, new_log, 1)

hook.write_text(text, encoding='utf-8')
