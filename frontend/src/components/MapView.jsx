import { useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'

// Fix default marker icons for Vite
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const TYPE_COLORS = {
  'Bostäder': '#f97316',
  'Infrastruktur': '#8b5cf6',
  'Kommersiellt': '#06b6d4',
  'Offentligt': '#14b8a6',
  'Industri': '#6b7280',
  'Övrigt': '#94a3b8',
}

const STATUS_EMOJI = {
  'Planerat': '📋',
  'Pågående': '🏗️',
  'Klart': '✅',
}

// Approximate centre-points for Swedish cities and regions used as fallback
// when a project has no geocoded coordinates.
const CITY_COORDS = {
  // Cities
  'Stockholm':    [59.3326, 18.0649],
  'Göteborg':     [57.7089, 11.9746],
  'Malmö':        [55.6050, 13.0038],
  'Uppsala':      [59.8586, 17.6389],
  'Linköping':    [58.4108, 15.6214],
  'Örebro':       [59.2741, 15.2066],
  'Västerås':     [59.6099, 16.5448],
  'Helsingborg':  [56.0465, 12.6945],
  'Norrköping':   [58.5942, 16.1826],
  'Jönköping':    [57.7826, 14.1618],
  'Umeå':         [63.8258, 20.2630],
  'Lund':         [55.7047, 13.1910],
  'Borås':        [57.7210, 12.9401],
  'Eskilstuna':   [59.3666, 16.5077],
  'Gävle':        [60.6749, 17.1413],
  'Sundsvall':    [62.3908, 17.3069],
  'Halmstad':     [56.6745, 12.8578],
  'Växjö':        [56.8777, 14.8091],
  'Karlstad':     [59.3793, 13.5036],
  'Kristianstad': [56.0294, 14.1567],
  'Kalmar':       [56.6634, 16.3568],
  'Falun':        [60.6065, 15.6355],
  'Skellefteå':   [64.7507, 20.9528],
  'Luleå':        [65.5848, 22.1547],
  'Östersund':    [63.1792, 14.6357],
  'Södertälje':   [59.1955, 17.6253],
  'Nacka':        [59.3085, 18.1631],
  'Täby':         [59.4440, 18.0689],
  'Huddinge':     [59.2367, 17.9808],
  'Botkyrka':     [59.2000, 17.8310],
  'Sollentuna':   [59.4279, 17.9503],
  'Järfälla':     [59.4327, 17.8322],
  'Upplands Väsby':[59.5197, 17.9130],
  'Haninge':      [59.1652, 18.1560],
  'Tyresö':       [59.2442, 18.2286],
  'Lidingö':      [59.3639, 18.1539],
  'Solna':        [59.3598, 17.9979],
  'Sundbyberg':   [59.3620, 17.9713],
  'Danderyd':     [59.4000, 18.0328],
  'Vallentuna':   [59.5344, 18.0779],
  'Nykvarn':      [59.1833, 17.4500],
  // Regions (used when city doesn't match)
  'Västra Götaland':  [57.7089, 11.9746],
  'Skåne':            [55.9897, 13.5958],
  'Östergötland':     [58.4108, 15.6214],
  'Södermanland':     [59.1833, 17.4000],
  'Västmanland':      [59.6099, 16.5448],
  'Dalarna':          [60.6065, 15.6355],
  'Halland':          [56.6745, 12.8578],
  'Jämtland':         [63.1792, 14.6357],
  'Norrbotten':       [65.5848, 22.1547],
  'Västerbotten':     [63.8258, 20.2630],
  'Gävleborg':        [60.6749, 17.1413],
  'Västernorrland':   [62.3908, 17.3069],
  'Värmland':         [59.3793, 13.5036],
  'Örebro':           [59.2741, 15.2066],
  'Kronoberg':        [56.8777, 14.8091],
  'Blekinge':         [56.1667, 15.5833],
  'Kalmar':           [56.6634, 16.3568],
  'Gotland':          [57.4684, 18.4867],
  'Jönköping':        [57.7826, 14.1618],
  'Uppsala':          [59.8586, 17.6389],
  'Uppland':          [59.8586, 17.6389],
}

/**
 * Returns { lat, lng, approx } for a project.
 * approx=true means we used a city/region centre as fallback.
 * Returns null if no position can be determined.
 */
function resolveCoords(p) {
  if (p.lat && p.lng) return { lat: p.lat, lng: p.lng, approx: false }

  // Try location string first, then region
  for (const key of [p.location, p.region]) {
    if (!key) continue
    // Direct lookup
    if (CITY_COORDS[key]) {
      const [lat, lng] = CITY_COORDS[key]
      return { lat, lng, approx: true }
    }
    // Partial match — find the first city whose name appears in the key
    const hit = Object.keys(CITY_COORDS).find(city =>
      key.toLowerCase().includes(city.toLowerCase())
    )
    if (hit) {
      const [lat, lng] = CITY_COORDS[hit]
      return { lat, lng, approx: true }
    }
  }
  return null
}

function makeIcon(type) {
  const color = TYPE_COLORS[type] || '#374151'
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="28" height="36" viewBox="0 0 28 36">
      <path d="M14 0C6.3 0 0 6.3 0 14c0 10.5 14 22 14 22s14-11.5 14-22C28 6.3 21.7 0 14 0z"
        fill="${color}" stroke="white" stroke-width="2"/>
      <circle cx="14" cy="14" r="6" fill="white" opacity="0.9"/>
    </svg>`
  return L.divIcon({
    html: svg,
    className: '',
    iconSize: [28, 36],
    iconAnchor: [14, 36],
    popupAnchor: [0, -36],
  })
}

function makeApproxIcon(type) {
  const color = TYPE_COLORS[type] || '#374151'
  // Smaller, semi-transparent, dashed stroke to signal "approximate position"
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="22" height="28" viewBox="0 0 28 36">
      <path d="M14 0C6.3 0 0 6.3 0 14c0 10.5 14 22 14 22s14-11.5 14-22C28 6.3 21.7 0 14 0z"
        fill="${color}" fill-opacity="0.45" stroke="${color}" stroke-width="2.5"
        stroke-dasharray="4 2.5"/>
      <circle cx="14" cy="14" r="6" fill="white" opacity="0.7"/>
      <text x="14" y="18.5" text-anchor="middle" font-size="9" font-weight="bold"
        font-family="sans-serif" fill="${color}" opacity="0.9">~</text>
    </svg>`
  return L.divIcon({
    html: svg,
    className: '',
    iconSize: [22, 28],
    iconAnchor: [11, 28],
    popupAnchor: [0, -28],
  })
}

function FitBounds({ coords }) {
  const map = useMap()
  useEffect(() => {
    if (coords.length === 0) return
    const bounds = L.latLngBounds(coords.map(c => [c.lat, c.lng]))
    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 12 })
    }
  }, [coords, map])
  return null
}

export default function MapView({ projects, onSelect }) {
  // Resolve coordinates for every project (exact or city-centre fallback)
  const resolved = projects
    .map(p => ({ ...p, _coords: resolveCoords(p) }))
    .filter(p => p._coords !== null)

  const approxCount = resolved.filter(p => p._coords.approx).length
  const hiddenCount = projects.length - resolved.length

  return (
    <div className="flex flex-col gap-2">
      {approxCount > 0 && (
        <p className="text-xs text-amber-600">
          ~ {approxCount} projekt saknar exakta koordinater och visas vid stadens centrum (markerade med ~).
          {hiddenCount > 0 && ` ${hiddenCount} projekt kunde inte placeras alls.`}
        </p>
      )}
      <MapContainer
        center={[62.5, 16.0]}
        zoom={5}
        className="map-container shadow-md"
        scrollWheelZoom
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {resolved.length > 0 && <FitBounds coords={resolved.map(p => p._coords)} />}
        {resolved.map(p => (
          <Marker
            key={p.id}
            position={[p._coords.lat, p._coords.lng]}
            icon={p._coords.approx ? makeApproxIcon(p.type) : makeIcon(p.type)}
          >
            <Popup maxWidth={300}>
              <div className="space-y-1 text-sm">
                <div className="font-semibold text-base leading-tight">{p.name}</div>
                <div className="flex gap-1 flex-wrap">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium type-${p.type}`}>
                    {p.type}
                  </span>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium badge-${p.status}`}>
                    {STATUS_EMOJI[p.status]} {p.status}
                  </span>
                  {p._coords.approx && (
                    <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-700">
                      ~ ungefärlig position
                    </span>
                  )}
                </div>
                <div className="text-gray-600">
                  {p.location}{p.region && p.location !== p.region ? `, ${p.region}` : ''}
                </div>
                {p.estimated_cost && (
                  <div><span className="text-gray-500">Kostnad:</span> {p.estimated_cost}</div>
                )}
                {(p.timeline_start || p.timeline_end) && (
                  <div>
                    <span className="text-gray-500">Tidplan:</span>{' '}
                    {p.timeline_start}
                    {p.timeline_end && p.timeline_end !== p.timeline_start ? `–${p.timeline_end}` : ''}
                  </div>
                )}
                <button
                  onClick={() => onSelect(p)}
                  className="mt-2 w-full text-center text-blue-600 hover:underline text-xs"
                >
                  Visa detaljer →
                </button>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 text-xs text-gray-600">
        {Object.entries(TYPE_COLORS).map(([type, color]) => (
          <span key={type} className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-full inline-block" style={{ backgroundColor: color }} />
            {type}
          </span>
        ))}
        <span className="flex items-center gap-1 text-amber-600">
          <span className="w-3 h-3 rounded-full inline-block border border-dashed border-amber-500 bg-amber-100" />
          ~ ungefärlig position
        </span>
      </div>
    </div>
  )
}
