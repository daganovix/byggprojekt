import { useEffect } from 'react'

const STATUS_BADGE = {
  'Planerat': 'bg-yellow-100 text-yellow-800',
  'Pågående': 'bg-blue-100 text-blue-800',
  'Klart': 'bg-green-100 text-green-800',
}

const TYPE_PILL = {
  'Bostäder': 'bg-orange-100 text-orange-700',
  'Infrastruktur': 'bg-purple-100 text-purple-700',
  'Kommersiellt': 'bg-cyan-100 text-cyan-700',
  'Offentligt': 'bg-teal-100 text-teal-700',
  'Industri': 'bg-gray-100 text-gray-700',
  'Övrigt': 'bg-slate-100 text-slate-700',
}

function Field({ label, value }) {
  if (!value) return null
  return (
    <div>
      <dt className="text-xs font-semibold text-gray-400 uppercase tracking-wide">{label}</dt>
      <dd className="mt-0.5 text-gray-800">{value}</dd>
    </div>
  )
}

export default function ProjectModal({ project: p, onClose }) {
  // Close on Escape
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  const timeline =
    p.timeline_start
      ? `${p.timeline_start}${p.timeline_end && p.timeline_end !== p.timeline_start ? ` – ${p.timeline_end}` : ''}`
      : null

  return (
    <div
      className="fixed inset-0 z-[2000] flex items-center justify-center p-4 bg-black/50"
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-100 px-6 py-4 flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <h2 className="text-lg font-bold text-gray-900 leading-snug">{p.name}</h2>
            <div className="flex gap-2 mt-1.5 flex-wrap">
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${TYPE_PILL[p.type] || 'bg-gray-100'}`}>
                {p.type}
              </span>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_BADGE[p.status] || 'bg-gray-100'}`}>
                {p.status}
              </span>
              {p.region && (
                <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                  {p.region}
                </span>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-700 text-2xl leading-none shrink-0"
            aria-label="Stäng"
          >
            ×
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-5 space-y-6">
          {/* Description */}
          {p.description && (
            <p className="text-gray-700 leading-relaxed">{p.description}</p>
          )}

          {/* Key facts */}
          <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Field label="Plats" value={p.location !== p.region ? p.location : ''} />
            <Field label="Region" value={p.region} />
            <Field label="Beräknad kostnad" value={p.estimated_cost} />
            <Field label="Tidplan" value={timeline} />
            <Field label="Publicerad" value={new Date(p.published_at).toLocaleDateString('sv-SE')} />
            <Field label="Källa" value={p.source_name} />
          </dl>

          {/* Participants */}
          {p.participants && p.participants.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
                Deltagare
              </h3>
              <div className="space-y-2">
                {p.participants.map((pt, i) => (
                  <div key={i} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold text-sm shrink-0">
                      {pt.name.charAt(0)}
                    </div>
                    <div className="min-w-0">
                      <div className="font-medium text-gray-900">{pt.name}</div>
                      {pt.role && <div className="text-sm text-gray-500">{pt.role}</div>}
                      {pt.contact && (
                        <a
                          href={pt.contact.includes('@') ? `mailto:${pt.contact}` : pt.contact}
                          className="text-sm text-blue-600 hover:underline break-all"
                        >
                          {pt.contact}
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Source link */}
          {p.source_url && (
            <div className="pt-2 border-t border-gray-100">
              <a
                href={p.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-sm text-blue-600 hover:underline"
              >
                Läs original artikel →
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
