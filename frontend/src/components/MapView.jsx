import { useEffect, useRef } from 'react'
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

function FitBounds({ projects }) {
  const map = useMap()
  useEffect(() => {
    if (projects.length === 0) return
    const bounds = L.latLngBounds(projects.map(p => [p.lat, p.lng]))
    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 12 })
    }
  }, [projects, map])
  return null
}

export default function MapView({ projects, allProjects, onSelect }) {
  const noCoords = allProjects.length - projects.length

  return (
    <div className="flex flex-col gap-2">
      {noCoords > 0 && (
        <p className="text-xs text-amber-600">
          ⚠ {noCoords} projekt saknar koordinater och visas inte på kartan — se listvy.
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
        {projects.length > 0 && <FitBounds projects={projects} />}
        {projects.map(p => (
          <Marker key={p.id} position={[p.lat, p.lng]} icon={makeIcon(p.type)}>
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
                </div>
                <div className="text-gray-600">{p.location}{p.region && p.location !== p.region ? `, ${p.region}` : ''}</div>
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
      </div>
    </div>
  )
}
