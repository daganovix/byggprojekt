import { useState } from 'react'

export default function FilterPanel({ filters, options, onChange }) {
  const [localSearch, setLocalSearch] = useState(filters.search || '')

  const set = (key, value) => onChange(prev => ({ ...prev, [key]: value }))

  const handleSearchKey = (e) => {
    if (e.key === 'Enter') set('search', localSearch)
  }

  const clearAll = () => {
    setLocalSearch('')
    onChange({ type: '', region: '', status: '', country: '', search: '' })
  }

  const hasFilters = filters.type || filters.region || filters.status || filters.country || filters.search

  return (
    <div className="flex flex-wrap gap-2 items-end">
      {/* Search */}
      <div className="flex gap-1">
        <input
          type="text"
          placeholder="Sök projekt, ort…"
          value={localSearch}
          onChange={e => setLocalSearch(e.target.value)}
          onKeyDown={handleSearchKey}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm w-48 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={() => set('search', localSearch)}
          className="px-3 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition"
        >
          Sök
        </button>
      </div>

      {/* Type */}
      <select
        value={filters.type}
        onChange={e => set('type', e.target.value)}
        className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">Alla typer</option>
        {options.types.map(t => <option key={t} value={t}>{t}</option>)}
      </select>

      {/* Region */}
      <select
        value={filters.region}
        onChange={e => set('region', e.target.value)}
        className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">Alla regioner</option>
        {options.regions.map(r => <option key={r} value={r}>{r}</option>)}
      </select>

      {/* Country */}
      <select
        value={filters.country}
        onChange={e => set('country', e.target.value)}
        className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">Alla länder</option>
        <option value="Sverige">🇸🇪 Sverige</option>
        <option value="Norge">🇳🇴 Norge</option>
        <option value="Danmark">🇩🇰 Danmark</option>
      </select>

      {/* Status */}
      <select
        value={filters.status}
        onChange={e => set('status', e.target.value)}
        className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="">Alla statusar</option>
        {options.statuses.map(s => <option key={s} value={s}>{s}</option>)}
      </select>

      {hasFilters && (
        <button
          onClick={clearAll}
          className="px-3 py-2 text-sm text-gray-600 hover:text-red-600 underline transition"
        >
          Rensa filter
        </button>
      )}
    </div>
  )
}
