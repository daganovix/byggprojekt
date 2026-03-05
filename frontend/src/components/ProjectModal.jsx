import { useEffect, useState } from 'react'
import axios from 'axios'

// ── Icons ────────────────────────────────────────────────────────────────────

function IconLinkedIn() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
      <path d="M20.45 20.45h-3.56v-5.57c0-1.33-.03-3.04-1.85-3.04-1.85 0-2.14 1.44-2.14 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.45v6.29zM5.34 7.43a2.07 2.07 0 1 1 0-4.14 2.07 2.07 0 0 1 0 4.14zM7.12 20.45H3.55V9h3.57v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.72v20.56C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.72V1.72C24 .77 23.2 0 22.22 0z"/>
    </svg>
  )
}

function IconSearch() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
      <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
    </svg>
  )
}

function IconNewspaper() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
      <path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/>
      <path d="M18 14h-8M15 18h-5M10 6h8v4h-8z"/>
    </svg>
  )
}

function IconMail() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
      <rect width="20" height="16" x="2" y="4" rx="2"/>
      <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
    </svg>
  )
}

// ── Per-participant contact actions ──────────────────────────────────────────

// Role-specific LinkedIn search keywords
const ROLE_LINKEDIN = {
  'Beställare':        'inköpschef upphandlingsansvarig beslutsfattare',
  'Byggherre':         'projektchef fastighetschef beslutsfattare',
  'Totalentreprenör':  'inköpschef projektledare underentreprenad',
  'Generalentreprenör':'inköpschef projektledare underentreprenad',
  'Fastighetsägare':   'fastighetsförvaltare driftsansvarig',
  'Arkitekt':          'arkitekt projektledare',
  'Konstruktör':       'konstruktör projektledare',
  'Projektledare':     'projektledare uppdragsansvarig',
  'Förvaltare':        'förvaltningschef driftsansvarig',
}

// Role-specific email body (what value do we offer this role?)
const ROLE_EMAIL_BODY = {
  'Beställare': (c, p, l) => [
    'Hej,',
    '',
    `Jag noterade att ${c} är beställare för "${p}"${l ? ` i ${l}` : ''}. Vi vill gärna presentera oss som potentiell leverantör eller utförare i projektet.`,
    '',
    'Har ni möjlighet till ett kort samtal om hur vi kan bidra till projektets genomförande?',
    '',
    'Med vänliga hälsningar,',
  ].join('\n'),
  'Byggherre': (c, p, l) => [
    'Hej,',
    '',
    `Jag noterade att ${c} är byggherre för "${p}"${l ? ` i ${l}` : ''}. Vi vill gärna presentera oss som potentiell leverantör, konsult eller utförare.`,
    '',
    'Har ni möjlighet till ett kort samtal om hur vi kan bidra?',
    '',
    'Med vänliga hälsningar,',
  ].join('\n'),
  'Totalentreprenör': (c, p, l) => [
    'Hej,',
    '',
    `Jag noterade att ${c} är totalentreprenör för "${p}"${l ? ` i ${l}` : ''}. Vi vill presentera oss som potentiell underentreprenör eller materialleverantör i projektet.`,
    '',
    'Har ni möjlighet till ett kort samtal om era behov av underleverantörer?',
    '',
    'Med vänliga hälsningar,',
  ].join('\n'),
  'Generalentreprenör': (c, p, l) => [
    'Hej,',
    '',
    `Jag noterade att ${c} är generalentreprenör för "${p}"${l ? ` i ${l}` : ''}. Vi vill presentera oss som potentiell underentreprenör eller leverantör.`,
    '',
    'Har ni möjlighet till ett kort samtal om era upphandlingsbehov?',
    '',
    'Med vänliga hälsningar,',
  ].join('\n'),
  'Fastighetsägare': (c, p, l) => [
    'Hej,',
    '',
    `Jag noterade att ${c} äger fastigheten kopplad till "${p}"${l ? ` i ${l}` : ''}. Vi vill presentera relevanta tjänster för projektet och framtida förvaltning.`,
    '',
    'Har ni möjlighet till ett kort samtal?',
    '',
    'Med vänliga hälsningar,',
  ].join('\n'),
  'Arkitekt': (c, p, l) => [
    'Hej,',
    '',
    `Jag noterade att ${c} är arkitekt för "${p}"${l ? ` i ${l}` : ''}. Vi vill presentera möjligheten till samarbete som konstruktör, teknisk konsult eller specialistleverantör.`,
    '',
    'Har ni möjlighet till ett kort samtal om eventuellt samarbete?',
    '',
    'Med vänliga hälsningar,',
  ].join('\n'),
}

function buildParticipantActions(name, role, projectName, projectLocation) {
  const liKeywords = ROLE_LINKEDIN[role] || 'projektledare inköpschef beslutsfattare'
  const linkedinHref = `https://www.linkedin.com/search/results/people/?keywords=${encodeURIComponent(`${name} ${liKeywords}`)}`

  const bodyFn = ROLE_EMAIL_BODY[role]
  const emailBody = bodyFn
    ? bodyFn(name, projectName, projectLocation)
    : [
        'Hej,',
        '',
        `Jag noterade att ${name} är involverade i projektet "${projectName}"${projectLocation ? ` i ${projectLocation}` : ''} och vill gärna presentera hur vi kan bidra.`,
        '',
        'Har ni möjlighet till ett kort samtal för att utforska ett eventuellt samarbete?',
        '',
        'Med vänliga hälsningar,',
      ].join('\n')

  const emailSubject = `Intresseanmälan – ${projectName} – ${name}`
  const emailHref = `mailto:?subject=${encodeURIComponent(emailSubject)}&body=${encodeURIComponent(emailBody)}`

  return { linkedinHref, emailHref }
}

function ParticipantActions({ name, role, projectName, projectLocation }) {
  const { linkedinHref, emailHref } = buildParticipantActions(name, role, projectName, projectLocation)
  return (
    <div className="flex gap-1.5 mt-2">
      <a
        href={linkedinHref}
        target="_blank"
        rel="noopener noreferrer"
        title={`Hitta beslutsfattare på ${name}`}
        className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium text-[#0a66c2] bg-blue-50 hover:bg-blue-100 border border-blue-100 transition-colors"
      >
        <IconLinkedIn /><span>Beslutsfattare</span>
      </a>
      <a
        href={emailHref}
        title={`E-postmall till ${name}`}
        className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-100 transition-colors"
      >
        <IconMail /><span>E-postmall</span>
      </a>
    </div>
  )
}

// ── Recommended actions (project-level) ──────────────────────────────────────

function RecommendedActions({ p }) {
  const procurementQuery = [p.name, p.location, 'upphandling förfrågningsunderlag'].filter(Boolean).join(' ')
  const newsQuery = [p.name, p.location].filter(Boolean).join(' ')

  const actions = [
    {
      icon: <IconSearch />,
      label: 'Sök upphandling',
      sub: 'Hitta anbudsförfrågningar',
      href: `https://www.google.com/search?q=${encodeURIComponent(procurementQuery)}`,
      style: 'text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border-indigo-100',
    },
    {
      icon: <IconNewspaper />,
      label: 'Nyheter om projektet',
      sub: 'Senaste nytt & bakgrund',
      href: `https://www.google.com/search?q=${encodeURIComponent(newsQuery)}&tbm=nws`,
      style: 'text-gray-700 bg-gray-50 hover:bg-gray-100 border-gray-100',
    },
  ]

  return (
    <div>
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2.5">
        Rekommenderade åtgärder
      </h3>
      <div className="grid grid-cols-2 gap-2">
        {actions.map(a => (
          <a
            key={a.label}
            href={a.href}
            target="_blank"
            rel="noopener noreferrer"
            className={`flex items-start gap-2.5 p-3 rounded-lg border transition-colors ${a.style}`}
          >
            <span className="shrink-0 mt-0.5">{a.icon}</span>
            <div className="min-w-0">
              <div className="font-medium text-sm leading-tight">{a.label}</div>
              <div className="text-xs opacity-60 mt-0.5 leading-tight truncate">{a.sub}</div>
            </div>
          </a>
        ))}
      </div>
    </div>
  )
}

const CONFIDENCE_STYLE = {
  hög:   { bar: 'bg-emerald-500', label: 'Hög', text: 'text-emerald-700', bg: 'bg-emerald-50 border-emerald-200' },
  medel: { bar: 'bg-amber-400',   label: 'Medel', text: 'text-amber-700', bg: 'bg-amber-50 border-amber-200' },
  låg:   { bar: 'bg-gray-300',    label: 'Låg', text: 'text-gray-500',   bg: 'bg-gray-50 border-gray-200' },
}

function PredictedParticipants({ projectId, projectName, projectLocation }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    axios.get(`/api/projects/${projectId}/predictions`)
      .then(r => setData(r.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false))
  }, [projectId])

  if (loading) return (
    <div className="text-xs text-gray-400 py-2">Analyserar historiska samarbeten…</div>
  )
  if (!data || data.predictions.length === 0) return null

  return (
    <div>
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">
        Troliga obekräftade deltagare
      </h3>
      {data.missing_roles.length > 0 && (
        <p className="text-xs text-gray-400 mb-2.5">
          Roller som saknas: <span className="font-medium text-gray-500">{data.missing_roles.join(', ')}</span>
        </p>
      )}
      <div className="space-y-2">
        {data.predictions.map((pred, i) => {
          const conf = CONFIDENCE_STYLE[pred.confidence] || CONFIDENCE_STYLE.låg
          return (
            <div key={i} className={`p-3 rounded-lg border border-dashed ${conf.bg}`}>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-white border-2 border-dashed border-gray-300 flex items-center justify-center text-gray-400 font-bold text-sm shrink-0">
                  {pred.name.charAt(0)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-medium text-gray-700">{pred.name}</span>
                    <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${conf.text} bg-white border`}>
                      {conf.label} sannolikhet
                    </span>
                  </div>
                  {pred.likely_role && (
                    <div className="text-sm text-gray-500 mt-0.5">{pred.likely_role}</div>
                  )}
                  <div className="text-xs text-gray-400 mt-0.5 italic">{pred.basis}</div>
                </div>
              </div>
              {pred.confidence === 'hög' && (
                <ParticipantActions
                  name={pred.name}
                  role={pred.likely_role || ''}
                  projectName={projectName}
                  projectLocation={projectLocation}
                />
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

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
                  <div key={i} className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-start gap-3">
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
                    <ParticipantActions
                      name={pt.name}
                      role={pt.role || ''}
                      projectName={p.name}
                      projectLocation={p.location || p.region || ''}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Predicted participants */}
          <div className="border-t border-gray-100 pt-4">
            <PredictedParticipants
              projectId={p.id}
              projectName={p.name}
              projectLocation={p.location || p.region || ''}
            />
          </div>

          {/* Recommended actions */}
          <div className="border-t border-gray-100 pt-4">
            <RecommendedActions p={p} />
          </div>

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
