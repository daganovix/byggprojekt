import { useState } from 'react'

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

const SORT_FIELDS = [
  { key: 'name', label: 'Namn' },
  { key: 'type', label: 'Typ' },
  { key: 'region', label: 'Region' },
  { key: 'cost_value_msek', label: 'Kostnad' },
  { key: 'timeline_start', label: 'Start' },
  { key: 'status', label: 'Status' },
  { key: 'published_at', label: 'Datum' },
]

function ProjectTable({ projects, onSelect, showParticipants, emptyText }) {
  const [sortKey, setSortKey] = useState('published_at')
  const [sortDir, setSortDir] = useState('desc')

  const toggleSort = (key) => {
    if (sortKey === key) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSortKey(key); setSortDir('asc') }
  }

  const sorted = [...projects].sort((a, b) => {
    let av = a[sortKey] ?? ''
    let bv = b[sortKey] ?? ''
    if (typeof av === 'string') av = av.toLowerCase()
    if (typeof bv === 'string') bv = bv.toLowerCase()
    if (av < bv) return sortDir === 'asc' ? -1 : 1
    if (av > bv) return sortDir === 'asc' ? 1 : -1
    return 0
  })

  const arrow = (key) => sortKey === key ? (sortDir === 'asc' ? ' ↑' : ' ↓') : ''

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            {SORT_FIELDS.map(f => (
              <th
                key={f.key}
                onClick={() => toggleSort(f.key)}
                className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide cursor-pointer hover:text-gray-800 select-none whitespace-nowrap"
              >
                {f.label}{arrow(f.key)}
              </th>
            ))}
            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide whitespace-nowrap">
              {showParticipants ? 'Deltagare' : 'Källa'}
            </th>
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {sorted.length === 0 && (
            <tr>
              <td colSpan={9} className="px-4 py-8 text-center text-gray-400">
                {emptyText}
              </td>
            </tr>
          )}
          {sorted.map(p => (
            <tr
              key={p.id}
              className="hover:bg-blue-50 cursor-pointer transition"
              onClick={() => onSelect(p)}
            >
              <td className="px-4 py-3 font-medium text-gray-900 max-w-xs">
                <div className="truncate" title={p.name}>{p.name}</div>
                <div className="text-xs text-gray-400 truncate">{p.source_name}</div>
              </td>
              <td className="px-4 py-3 whitespace-nowrap">
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${TYPE_PILL[p.type] || 'bg-gray-100 text-gray-600'}`}>
                  {p.type}
                </span>
              </td>
              <td className="px-4 py-3 text-gray-600 whitespace-nowrap">{p.region || '—'}</td>
              <td className="px-4 py-3 text-gray-600 whitespace-nowrap">
                {p.estimated_cost || '—'}
              </td>
              <td className="px-4 py-3 text-gray-600 whitespace-nowrap">
                {p.timeline_start
                  ? `${p.timeline_start}${p.timeline_end && p.timeline_end !== p.timeline_start ? `–${p.timeline_end}` : ''}`
                  : '—'}
              </td>
              <td className="px-4 py-3 whitespace-nowrap">
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_BADGE[p.status] || 'bg-gray-100 text-gray-600'}`}>
                  {p.status}
                </span>
              </td>
              <td className="px-4 py-3 text-gray-500 whitespace-nowrap">
                {new Date(p.published_at).toLocaleDateString('sv-SE')}
              </td>
              <td className="px-4 py-3 text-gray-600 max-w-xs">
                {showParticipants ? (
                  <div className="text-xs space-y-0.5">
                    {(p.participants || []).slice(0, 2).map((pt, i) => (
                      <div key={i} className="truncate">
                        <span className="font-medium">{pt.name}</span>
                        {pt.role && <span className="text-gray-400"> · {pt.role}</span>}
                      </div>
                    ))}
                    {p.participants.length > 2 && (
                      <div className="text-gray-400">+{p.participants.length - 2} till</div>
                    )}
                  </div>
                ) : (
                  <span className="text-xs text-gray-400">{p.source_name}</span>
                )}
              </td>
              <td className="px-4 py-3">
                <span className="text-blue-500 hover:text-blue-700 text-xs">→</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function ListView({ projects, onSelect }) {
  const confirmed = projects.filter(p => p.participants && p.participants.length > 0)
  const rumors    = projects.filter(p => !p.participants || p.participants.length === 0)

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="flex items-center gap-4 text-sm text-gray-600">
        <span className="font-medium text-gray-800">{projects.length} projekt totalt</span>
        <span className="text-gray-300">|</span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
          {confirmed.length} bekräftade
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-amber-400 inline-block" />
          {rumors.length} rykten
        </span>
      </div>
      {/* Bekräftade projekt */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-200 bg-gray-50">
          <span className="w-2 h-2 rounded-full bg-emerald-500 shrink-0" />
          <h2 className="font-semibold text-gray-800 text-sm">Bekräftade projekt</h2>
          <span className="ml-auto text-xs text-gray-400 font-medium">{confirmed.length} projekt</span>
        </div>
        <ProjectTable
          projects={confirmed}
          onSelect={onSelect}
          showParticipants={true}
          emptyText="Inga projekt med bekräftade deltagare matchar filtret."
        />
        {confirmed.length > 0 && (
          <div className="px-4 py-2 text-xs text-gray-400 border-t border-gray-100">
            Klicka på en rad för detaljer
          </div>
        )}
      </div>

      {/* Projektrykten */}
      <div className="bg-white rounded-lg shadow-sm border border-amber-200 overflow-hidden">
        <div className="flex items-center gap-3 px-4 py-3 border-b border-amber-200 bg-amber-50">
          <span className="w-2 h-2 rounded-full bg-amber-400 shrink-0" />
          <h2 className="font-semibold text-amber-900 text-sm">Projektrykten</h2>
          <span className="text-xs text-amber-600">Inga bekräftade deltagare ännu</span>
          <span className="ml-auto text-xs text-amber-600 font-medium">{rumors.length} projekt</span>
        </div>
        <ProjectTable
          projects={rumors}
          onSelect={onSelect}
          showParticipants={false}
          emptyText="Inga projektrykten matchar filtret."
        />
        {rumors.length > 0 && (
          <div className="px-4 py-2 text-xs text-amber-600/70 border-t border-amber-100 bg-amber-50/30">
            Klicka på ett projekt för att se AI-prediktion om troliga aktörer
          </div>
        )}
      </div>
    </div>
  )
}
