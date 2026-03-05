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

export default function ListView({ projects, onSelect }) {
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
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="overflow-x-auto project-list">
        <table className="min-w-full text-sm">
          <thead className="sticky top-0 bg-gray-50 border-b border-gray-200 z-10">
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
                Deltagare
              </th>
              <th className="px-4 py-3" />
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {sorted.length === 0 && (
              <tr>
                <td colSpan={9} className="px-4 py-10 text-center text-gray-400">
                  Inga projekt matchar filtret.
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
                </td>
                <td className="px-4 py-3">
                  <span className="text-blue-500 hover:text-blue-700 text-xs">→</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="px-4 py-2 text-xs text-gray-400 border-t border-gray-100">
        Visar {sorted.length} projekt — klicka på en rad för detaljer
      </div>
    </div>
  )
}
