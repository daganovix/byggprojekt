import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import MapView from './components/MapView'
import ListView from './components/ListView'
import FilterPanel from './components/FilterPanel'
import ProjectModal from './components/ProjectModal'
import StatsBar from './components/StatsBar'

const API = '/api'

export default function App() {
  const [projects, setProjects] = useState([])
  const [stats, setStats] = useState(null)
  const [filterOptions, setFilterOptions] = useState({ types: [], regions: [], statuses: [], countries: [] })
  const [filters, setFilters] = useState({ type: '', region: '', status: '', country: '', search: '' })
  const [loading, setLoading] = useState(true)
  const [view, setView] = useState('map') // 'map' | 'list'
  const [selectedProject, setSelectedProject] = useState(null)
  const [refreshing, setRefreshing] = useState(false)

  const fetchProjects = useCallback(async () => {
    setLoading(true)
    try {
      const params = {}
      if (filters.type)    params.type    = filters.type
      if (filters.region)  params.region  = filters.region
      if (filters.status)  params.status  = filters.status
      if (filters.country) params.country = filters.country
      if (filters.search)  params.search  = filters.search

      const [projRes, statsRes] = await Promise.all([
        axios.get(`${API}/projects`, { params }),
        axios.get(`${API}/stats`),
      ])
      setProjects(projRes.data.projects)
      setStats(statsRes.data)
    } catch (err) {
      console.error('Failed to fetch projects', err)
    } finally {
      setLoading(false)
    }
  }, [filters])

  useEffect(() => {
    axios.get(`${API}/filters`).then(r => setFilterOptions(r.data)).catch(() => {})
  }, [])

  useEffect(() => {
    fetchProjects()
  }, [fetchProjects])

  const triggerRefresh = async () => {
    setRefreshing(true)
    try {
      const before = projects.length
      await axios.post(`${API}/refresh`)
      // Poll until project count increases or 3 minutes pass
      const deadline = Date.now() + 3 * 60 * 1000
      const poll = async () => {
        if (Date.now() > deadline) { fetchProjects(); setRefreshing(false); return }
        try {
          const res = await axios.get(`${API}/stats`)
          if (res.data.total > before) { fetchProjects(); setRefreshing(false); return }
        } catch { /* ignore */ }
        setTimeout(poll, 5000)
      }
      setTimeout(poll, 5000)
    } catch {
      setRefreshing(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-blue-700 text-white shadow-md">
        <div className="max-w-screen-2xl mx-auto px-4 py-3 flex items-center justify-between flex-wrap gap-2">
          <div>
            <h1 className="text-xl font-bold tracking-tight">Byggprojekt Norden</h1>
            <p className="text-blue-200 text-xs">Nyheter och karta över nya byggprojekt i Sverige, Norge och Danmark</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-blue-200">
              {projects.length} projekt {filters.type || filters.region || filters.country || filters.search ? '(filtrerade)' : 'totalt'}
            </span>
            <button
              onClick={triggerRefresh}
              disabled={refreshing}
              className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 rounded text-sm font-medium disabled:opacity-60 transition"
            >
              {refreshing ? 'Hämtar…' : '↻ Uppdatera'}
            </button>
          </div>
        </div>
      </header>

      {stats && <StatsBar stats={stats} />}

      <div className="max-w-screen-2xl mx-auto w-full px-4 py-4 flex flex-col gap-4 flex-1">
        {/* Filter + view toggle row */}
        <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-end justify-between">
          <FilterPanel
            filters={filters}
            options={filterOptions}
            onChange={setFilters}
          />
          <div className="flex rounded-lg overflow-hidden border border-gray-300 shrink-0">
            <button
              onClick={() => setView('map')}
              className={`px-4 py-2 text-sm font-medium transition ${
                view === 'map' ? 'bg-blue-700 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              🗺 Karta
            </button>
            <button
              onClick={() => setView('list')}
              className={`px-4 py-2 text-sm font-medium transition ${
                view === 'list' ? 'bg-blue-700 text-white' : 'bg-white text-gray-700 hover:bg-gray-100'
              }`}
            >
              ☰ Lista
            </button>
          </div>
        </div>

        {/* Main content */}
        {loading ? (
          <div className="flex items-center justify-center h-96 text-gray-500 text-lg">
            Laddar projekt…
          </div>
        ) : view === 'map' ? (
          <MapView
            projects={projects}
            onSelect={setSelectedProject}
          />
        ) : (
          <ListView
            projects={projects}
            onSelect={setSelectedProject}
          />
        )}
      </div>

      {/* Project detail modal */}
      {selectedProject && (
        <ProjectModal
          project={selectedProject}
          onClose={() => setSelectedProject(null)}
        />
      )}
    </div>
  )
}
