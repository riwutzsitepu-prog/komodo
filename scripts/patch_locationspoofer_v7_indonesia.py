import runpy
from pathlib import Path

# Start from the proven V6 patch (NO-API search + OSM map + 12dp spacing).
runpy.run_path('scripts/patch_locationspoofer_v6.py', run_name='__main__')

# Restrict Nominatim search results to Indonesia only.
src = Path('locationspoofer/app/src/main/java/com/suseoaa/locationspoofer/ui/screen/SpoofingScreen.kt')
text = src.read_text(encoding='utf-8')
old = 'https://nominatim.openstreetmap.org/search?format=jsonv2&limit=10&addressdetails=1&accept-language=id,en&q=$encoded'
new = 'https://nominatim.openstreetmap.org/search?format=jsonv2&limit=10&addressdetails=1&accept-language=id,en&countrycodes=id&q=$encoded'
if old not in text:
    raise SystemExit('Nominatim URL anchor not found')
text = text.replace(old, new, 1)
text = text.replace('OSM-MAP-NO-API-V6', 'OSM-MAP-NO-API-V7-ID', 1)
src.write_text(text, encoding='utf-8')
