from pathlib import Path

root = Path('locationspoofer')

# 1) Search -> OpenStreetMap Nominatim, plus move map 12dp below search.
src = root / 'app/src/main/java/com/suseoaa/locationspoofer/ui/screen/SpoofingScreen.kt'
text = src.read_text(encoding='utf-8')

old_map = '''        // 地图缩略图\n        Box(modifier = Modifier.fillMaxWidth().height(280.dp)) {'''
new_map = '''        // 地图缩略图\n        Spacer(Modifier.height(12.dp))\n        Box(modifier = Modifier.fillMaxWidth().height(268.dp)) {'''
if old_map not in text:
    raise SystemExit('map preview block not found')
text = text.replace(old_map, new_map, 1)

marker = 'private var cachedPlacesClient:'
if marker not in text:
    raise SystemExit('performPoiSearch marker not found')
start = text.index(marker)
replacement = r'''fun performPoiSearch(
    context: android.content.Context,
    keyword: String,
    isDomestic: Boolean,
    onResult: (List<AppPoiItem>) -> Unit
) {
    if (keyword.isBlank()) { onResult(emptyList()); return }
    kotlinx.coroutines.GlobalScope.launch(kotlinx.coroutines.Dispatchers.IO) {
        try {
            val encoded = java.net.URLEncoder.encode(keyword.trim(), "UTF-8")
            val url = "https://nominatim.openstreetmap.org/search?format=jsonv2&limit=10&addressdetails=1&accept-language=id,en&q=$encoded"
            val client = okhttp3.OkHttpClient.Builder()
                .connectTimeout(10, java.util.concurrent.TimeUnit.SECONDS)
                .readTimeout(15, java.util.concurrent.TimeUnit.SECONDS)
                .callTimeout(20, java.util.concurrent.TimeUnit.SECONDS)
                .build()
            val request = okhttp3.Request.Builder()
                .url(url)
                .header("User-Agent", "LocationSpoofer/1.11.7 (Android; OSM-MAP-NO-API-V6)")
                .header("Accept", "application/json")
                .build()
            val results = mutableListOf<AppPoiItem>()
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) throw java.io.IOException("HTTP ${response.code}")
                val array = org.json.JSONArray(response.body?.string().orEmpty())
                for (i in 0 until array.length()) {
                    val obj = array.optJSONObject(i) ?: continue
                    val lat = obj.optString("lat").toDoubleOrNull() ?: continue
                    val lng = obj.optString("lon").toDoubleOrNull() ?: continue
                    val displayName = obj.optString("display_name", "")
                    val osmName = obj.optString("name", "")
                    val title = if (osmName.isNotBlank()) osmName else displayName.substringBefore(',').ifBlank { keyword }
                    results.add(AppPoiItem(title, displayName, lat, lng))
                }
            }
            kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.Main) {
                if (results.isEmpty()) android.widget.Toast.makeText(context, "No search results for: $keyword", android.widget.Toast.LENGTH_SHORT).show()
                onResult(results)
            }
        } catch (e: Exception) {
            kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.Main) {
                android.widget.Toast.makeText(context, "Search Error: ${e.message}", android.widget.Toast.LENGTH_LONG).show()
                onResult(emptyList())
            }
        }
    }
}
'''
src.write_text(text[:start] + replacement + '\n', encoding='utf-8')

# 2) Do not initialize Google Places at startup.
app = root / 'app/src/main/java/com/suseoaa/locationspoofer/LocationApp.kt'
a = app.read_text(encoding='utf-8')
old = '''        if (!Places.isInitialized()) {\n            Places.initialize(this, BuildConfig.GOOGLE_MAPS_API_KEY)\n        }\n'''
if old not in a:
    raise SystemExit('Places startup block not found')
a = a.replace(old, '''        // NO-API build: Google Places is intentionally not initialized.\n''', 1)
app.write_text(a, encoding='utf-8')

# 3) Replace Google/AMap map renderer with OpenStreetMap/osmdroid.
mapfile = root / 'app/src/main/java/com/suseoaa/locationspoofer/ui/components/AppMapView.kt'
mapfile.write_text(r'''package com.suseoaa.locationspoofer.ui.components

import android.os.Handler
import android.os.Looper
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import org.osmdroid.config.Configuration
import org.osmdroid.events.MapListener
import org.osmdroid.events.ScrollEvent
import org.osmdroid.events.ZoomEvent
import org.osmdroid.tileprovider.tilesource.TileSourceFactory
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.CustomZoomButtonsController
import org.osmdroid.views.MapView
import org.osmdroid.views.overlay.Marker
import org.osmdroid.views.overlay.Polyline

interface AppMapMarker {
    fun setPosition(lat: Double, lng: Double)
}

enum class MarkerType { GREEN, RED, ORANGE, DEFAULT }

interface AppMapController {
    fun clear()
    fun addPolyline(points: List<Pair<Double, Double>>, colorInt: Int, width: Float)
    fun addMarker(lat: Double, lng: Double, title: String, type: MarkerType): AppMapMarker
    fun animateCamera(lat: Double, lng: Double, zoom: Float? = null)
    fun moveCamera(lat: Double, lng: Double, zoom: Float? = null)
    val cameraTargetLat: Double?
    val cameraTargetLng: Double?
    fun setOnCameraChangeListener(onFinish: (lat: Double, lng: Double) -> Unit)
    fun disableUiControls()
}

class OSMMapControllerImpl(private val map: MapView) : AppMapController {
    override fun clear() {
        map.overlays.clear()
        map.invalidate()
    }

    override fun addPolyline(points: List<Pair<Double, Double>>, colorInt: Int, width: Float) {
        val line = Polyline().apply {
            setPoints(points.map { GeoPoint(it.first, it.second) })
            outlinePaint.color = colorInt
            outlinePaint.strokeWidth = width
        }
        map.overlays.add(line)
        map.invalidate()
    }

    override fun addMarker(lat: Double, lng: Double, title: String, type: MarkerType): AppMapMarker {
        val marker = Marker(map).apply {
            position = GeoPoint(lat, lng)
            this.title = title
            setAnchor(Marker.ANCHOR_CENTER, Marker.ANCHOR_BOTTOM)
        }
        map.overlays.add(marker)
        map.invalidate()
        return object : AppMapMarker {
            override fun setPosition(lat: Double, lng: Double) {
                marker.position = GeoPoint(lat, lng)
                map.invalidate()
            }
        }
    }

    override fun animateCamera(lat: Double, lng: Double, zoom: Float?) {
        if (zoom != null) map.controller.setZoom(zoom.toDouble())
        map.controller.animateTo(GeoPoint(lat, lng))
    }

    override fun moveCamera(lat: Double, lng: Double, zoom: Float?) {
        if (zoom != null) map.controller.setZoom(zoom.toDouble())
        map.controller.setCenter(GeoPoint(lat, lng))
    }

    override val cameraTargetLat: Double? get() = map.mapCenter?.latitude
    override val cameraTargetLng: Double? get() = map.mapCenter?.longitude

    override fun setOnCameraChangeListener(onFinish: (lat: Double, lng: Double) -> Unit) {
        val handler = Handler(Looper.getMainLooper())
        var pending: Runnable? = null
        fun schedule() {
            pending?.let { handler.removeCallbacks(it) }
            val task = Runnable {
                val p = map.mapCenter
                onFinish(p.latitude, p.longitude)
            }
            pending = task
            handler.postDelayed(task, 220L)
        }
        map.addMapListener(object : MapListener {
            override fun onScroll(event: ScrollEvent?): Boolean { schedule(); return true }
            override fun onZoom(event: ZoomEvent?): Boolean { schedule(); return true }
        })
    }

    override fun disableUiControls() {
        map.zoomController.setVisibility(CustomZoomButtonsController.Visibility.NEVER)
        map.setMultiTouchControls(true)
        map.setBuiltInZoomControls(false)
    }
}

@Composable
fun AppMapView(
    isDomestic: Boolean,
    modifier: Modifier = Modifier,
    onMapReady: (AppMapController) -> Unit
) {
    val context = LocalContext.current
    val lifecycle = LocalLifecycleOwner.current.lifecycle

    val mapView = remember {
        Configuration.getInstance().userAgentValue = context.packageName
        MapView(context).apply {
            setTileSource(TileSourceFactory.MAPNIK)
            setMultiTouchControls(true)
            setTilesScaledToDpi(true)
            minZoomLevel = 3.0
            maxZoomLevel = 20.0
            zoomController.setVisibility(CustomZoomButtonsController.Visibility.NEVER)
        }
    }

    DisposableEffect(lifecycle, mapView) {
        val observer = LifecycleEventObserver { _, event ->
            when (event) {
                Lifecycle.Event.ON_RESUME -> mapView.onResume()
                Lifecycle.Event.ON_PAUSE -> mapView.onPause()
                Lifecycle.Event.ON_DESTROY -> mapView.onDetach()
                else -> Unit
            }
        }
        lifecycle.addObserver(observer)
        if (lifecycle.currentState.isAtLeast(Lifecycle.State.RESUMED)) mapView.onResume()
        onDispose {
            lifecycle.removeObserver(observer)
            mapView.onPause()
            mapView.onDetach()
        }
    }

    AndroidView(
        factory = {
            mapView.apply {
                setOnTouchListener { v, _ ->
                    v.parent?.requestDisallowInterceptTouchEvent(true)
                    false
                }
                post { onMapReady(OSMMapControllerImpl(this)) }
            }
        },
        modifier = modifier
    )
}
''', encoding='utf-8')

# 4) Add osmdroid dependency and use CI debug signing.
gradle = root / 'app/build.gradle.kts'
g = gradle.read_text(encoding='utf-8')
dep_anchor = '    implementation(libs.okhttp)\n'
if 'org.osmdroid:osmdroid-android' not in g:
    if dep_anchor not in g:
        raise SystemExit('dependency anchor not found')
    g = g.replace(dep_anchor, dep_anchor + '    implementation("org.osmdroid:osmdroid-android:6.1.20")\n', 1)
oldg = 'debug {\n            signingConfig = signingConfigs.getByName("release")'
newg = 'debug {\n            signingConfig = signingConfigs.getByName("debug")'
if oldg in g:
    g = g.replace(oldg, newg, 1)
gradle.write_text(g, encoding='utf-8')
