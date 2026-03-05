export default function StatsBar({ stats }) {
  const typeColors = {
    'Bostäder': 'bg-orange-500',
    'Infrastruktur': 'bg-purple-500',
    'Kommersiellt': 'bg-cyan-500',
    'Offentligt': 'bg-teal-500',
    'Industri': 'bg-gray-500',
    'Övrigt': 'bg-slate-400',
  }

  return (
    <div className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-screen-2xl mx-auto px-4 py-2 flex flex-wrap gap-4 items-center text-sm">
        <span className="font-semibold text-gray-700">Totalt: {stats.total}</span>
        <span className="text-gray-300">|</span>
        {Object.entries(stats.by_status || {}).map(([s, n]) => (
          <span key={s} className="text-gray-600">
            <span className="font-medium">{n}</span> {s}
          </span>
        ))}
        <span className="text-gray-300">|</span>
        {Object.entries(stats.by_type || {}).map(([t, n]) => (
          <span key={t} className="flex items-center gap-1">
            <span className={`w-2 h-2 rounded-full ${typeColors[t] || 'bg-gray-400'}`} />
            <span className="text-gray-600"><span className="font-medium">{n}</span> {t}</span>
          </span>
        ))}
      </div>
    </div>
  )
}
