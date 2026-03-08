import { useEffect, useRef, useState } from 'react'
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

function IconBell() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
      <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/>
      <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>
    </svg>
  )
}

function IconBuilding() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
      <rect width="16" height="20" x="4" y="2" rx="2"/>
      <path d="M9 22v-4h6v4M8 6h.01M16 6h.01M12 6h.01M12 10h.01M8 10h.01M16 10h.01M8 14h.01M16 14h.01M12 14h.01"/>
    </svg>
  )
}

function IconLayers() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
      <path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/>
      <path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/>
      <path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>
    </svg>
  )
}

function IconSparkles() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5">
      <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/>
      <path d="M20 3v4M22 5h-4M4 17v2M5 18H3"/>
    </svg>
  )
}

function IconSend() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
      <path d="m22 2-7 20-4-9-9-4Z"/>
      <path d="M22 2 11 13"/>
    </svg>
  )
}

function IconFileText() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
      <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/>
      <path d="M14 2v4a2 2 0 0 0 2 2h4M10 9H8M16 13H8M16 17H8"/>
    </svg>
  )
}

function IconClock() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
      <circle cx="12" cy="12" r="10"/>
      <polyline points="12 6 12 12 16 14"/>
    </svg>
  )
}

function IconFlame() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className="w-3.5 h-3.5">
      <path d="M12 2c0 0-5 5.5-5 10a5 5 0 0 0 10 0c0-4.5-5-10-5-10zm0 14a3 3 0 0 1-3-3c0-2 1.5-4 3-6 1.5 2 3 4 3 6a3 3 0 0 1-3 3z"/>
    </svg>
  )
}

function IconPaperclip() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
      <path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
    </svg>
  )
}

function IconImage() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
      <rect width="18" height="18" x="3" y="3" rx="2"/>
      <circle cx="9" cy="9" r="2"/>
      <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>
    </svg>
  )
}

function IconTrash() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-3.5 h-3.5">
      <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
    </svg>
  )
}

function IconChevronDown() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-3.5 h-3.5">
      <path d="m6 9 6 6 6-6"/>
    </svg>
  )
}

function IconChevronUp() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-3.5 h-3.5">
      <path d="m18 15-6-6-6 6"/>
    </svg>
  )
}

function IconExternalLink() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-3.5 h-3.5">
      <path d="M15 3h6v6M10 14 21 3M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
    </svg>
  )
}

// ── AI Sales Coach ────────────────────────────────────────────────────────────

const SUGGESTED_PROMPTS = [
  'Vem kontaktar jag först och varför?',
  'Skriv ett prospekteringsmail',
  'Vilken vinkel har vi störst chans med?',
  'Vilka invändningar kan jag möta?',
  'Hur lägger jag upp ett första samtal?',
]

function SalesCoach({ project }) {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    if (open && messages.length === 0) {
      sendMessage('Ge mig en snabb situationsanalys av projektet och föreslå de tre viktigaste åtgärderna.')
    }
  }, [open])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function sendMessage(text) {
    if (streaming) return
    const userMsg = text || input.trim()
    if (!userMsg) return
    setInput('')

    const history = messages.map(m => ({ role: m.role, content: m.content }))
    setMessages(prev => [
      ...prev,
      { role: 'user', content: userMsg },
      { role: 'assistant', content: '' },
    ])
    setStreaming(true)

    try {
      const res = await fetch(`/api/projects/${project.id}/coach`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, history }),
      })

      if (!res.ok) {
        throw new Error(`Serverfel: ${res.status}`)
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let assistantText = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const data = line.slice(6)
          if (data === '[DONE]') break
          try {
            const parsed = JSON.parse(data)
            if (parsed.error) {
              assistantText = `Fel: ${parsed.error}`
            } else {
              assistantText += parsed.text || ''
            }
            setMessages(prev => {
              const updated = [...prev]
              updated[updated.length - 1] = { role: 'assistant', content: assistantText }
              return updated
            })
          } catch {}
        }
      }
    } catch (err) {
      setMessages(prev => {
        const updated = [...prev]
        updated[updated.length - 1] = {
          role: 'assistant',
          content: `Ett fel uppstod: ${err.message}. Kontrollera att ANTHROPIC_API_KEY är konfigurerad.`,
        }
        return updated
      })
    } finally {
      setStreaming(false)
    }
  }

  return (
    <div className="border-t border-gray-100 pt-4">
      {!open ? (
        <button
          onClick={() => setOpen(true)}
          className="w-full flex items-center justify-center gap-2.5 px-4 py-3.5 rounded-xl font-semibold text-white text-sm shadow-lg shadow-indigo-200 transition-all hover:shadow-indigo-300 hover:scale-[1.01] active:scale-[0.99]"
          style={{ background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%)' }}
        >
          <IconSparkles />
          AI Säljcoach – få coachning baserat på detta projekt
        </button>
      ) : (
        <div className="rounded-xl border border-indigo-100 overflow-hidden shadow-sm">
          {/* Coach header */}
          <div
            className="flex items-center justify-between px-4 py-3"
            style={{ background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%)' }}
          >
            <div className="flex items-center gap-2 text-white font-semibold text-sm">
              <IconSparkles />
              AI Säljcoach
            </div>
            <button
              onClick={() => setOpen(false)}
              className="text-white/70 hover:text-white text-xl leading-none"
              aria-label="Stäng"
            >
              ×
            </button>
          </div>

          {/* Messages */}
          <div className="bg-gray-50 px-4 py-3 space-y-3 max-h-80 overflow-y-auto">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[85%] rounded-lg px-3 py-2 text-sm leading-relaxed whitespace-pre-wrap ${
                    m.role === 'user'
                      ? 'bg-indigo-600 text-white'
                      : 'bg-white border border-gray-200 text-gray-800'
                  }`}
                >
                  {m.content || (
                    <span className="inline-flex gap-1 opacity-60">
                      <span className="animate-bounce" style={{ animationDelay: '0ms' }}>·</span>
                      <span className="animate-bounce" style={{ animationDelay: '150ms' }}>·</span>
                      <span className="animate-bounce" style={{ animationDelay: '300ms' }}>·</span>
                    </span>
                  )}
                </div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>

          {/* Suggested prompts */}
          {messages.length <= 2 && !streaming && (
            <div className="bg-gray-50 px-4 pb-2 flex flex-wrap gap-1.5">
              {SUGGESTED_PROMPTS.map(p => (
                <button
                  key={p}
                  onClick={() => sendMessage(p)}
                  className="text-xs px-2.5 py-1 rounded-full border border-indigo-200 bg-white text-indigo-700 hover:bg-indigo-50 transition-colors"
                >
                  {p}
                </button>
              ))}
            </div>
          )}

          {/* Input */}
          <div className="border-t border-gray-100 bg-white flex items-center gap-2 px-3 py-2">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() } }}
              placeholder="Ställ en fråga om projektet…"
              disabled={streaming}
              className="flex-1 text-sm outline-none bg-transparent placeholder-gray-400 disabled:opacity-50"
            />
            <button
              onClick={() => sendMessage()}
              disabled={streaming || !input.trim()}
              className="shrink-0 p-1.5 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-40 transition-colors"
            >
              <IconSend />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Quote Modal ───────────────────────────────────────────────────────────────

function QuoteModal({ name, projectName, projectLocation, onClose }) {
  const [description, setDescription] = useState('')
  const [price, setPrice] = useState('')
  const [files, setFiles] = useState([])

  function handleSubmit(e) {
    e.preventDefault()
    const lines = ['Hej,', '']
    if (description) lines.push('OFFERTBESKRIVNING:', description, '')
    if (price) lines.push(`OFFERTPRIS: ${price}`, '')
    lines.push('Med vänlig hälsning,\n[DITT NAMN]\n[FÖRETAG]\n[TELEFON]')
    const body = lines.join('\n')
    const subject = `Offert – ${projectName}${projectLocation ? ` (${projectLocation})` : ''}`
    window.location.href = `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
    onClose()
  }

  return (
    <div
      className="fixed inset-0 z-[3500] flex items-center justify-center p-4 bg-black/60"
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md">
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <div>
            <h3 className="font-semibold text-gray-900">Lämna offert</h3>
            <p className="text-xs text-gray-400 mt-0.5">till {name} · {projectName}</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700 text-2xl leading-none" aria-label="Stäng">×</button>
        </div>
        <form onSubmit={handleSubmit} className="px-5 py-4 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1">Beskrivning</label>
            <textarea
              value={description}
              onChange={e => setDescription(e.target.value)}
              rows={4}
              placeholder="Beskriv er tjänst, produkt eller lösning…"
              className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 outline-none focus:border-orange-400 resize-none"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1">Offertpris</label>
            <input
              type="text"
              value={price}
              onChange={e => setPrice(e.target.value)}
              placeholder="t.ex. 150 000 kr exkl. moms"
              className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 outline-none focus:border-orange-400"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1">Bifoga filer</label>
            <input
              type="file"
              multiple
              onChange={e => setFiles([...e.target.files])}
              className="w-full text-sm text-gray-600 file:mr-3 file:py-1 file:px-3 file:rounded file:border-0 file:text-xs file:font-medium file:bg-orange-50 file:text-orange-700 hover:file:bg-orange-100"
            />
            {files.length > 0 && (
              <p className="text-xs text-gray-400 mt-1">{files.length} fil(er) vald(a) – bifogas i e-postprogrammet</p>
            )}
          </div>
          <div className="flex justify-end gap-2 pt-1">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm text-gray-500 hover:text-gray-700 transition-colors">Avbryt</button>
            <button type="submit" className="px-4 py-2 text-sm font-medium text-white bg-orange-600 hover:bg-orange-700 rounded-lg transition-colors">Skapa offertmail</button>
          </div>
        </form>
      </div>
    </div>
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

function ParticipantActions({ name, role, projectName, projectLocation, compact = false }) {
  const [quoteOpen, setQuoteOpen] = useState(false)
  const { linkedinHref, emailHref } = buildParticipantActions(name, role, projectName, projectLocation)

  const alertsHref = `https://www.google.com/alerts?q=${encodeURIComponent(name)}&hl=sv`
  const moreProjectsHref = `https://www.google.com/search?q=${encodeURIComponent(`"${name}" byggprojekt upphandling`)}`

  if (compact) {
    return (
      <>
        <div className="flex gap-1">
          <a href={linkedinHref} target="_blank" rel="noopener noreferrer" title={`Hitta beslutsfattare på ${name}`}
            className="w-6 h-6 rounded-full flex items-center justify-center text-[#0a66c2] bg-blue-50 hover:bg-blue-100 border border-blue-100 transition-colors">
            <IconLinkedIn />
          </a>
          <a href={emailHref} title={`E-postmall till ${name}`}
            className="w-6 h-6 rounded-full flex items-center justify-center text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-100 transition-colors">
            <IconMail />
          </a>
          <a href={alertsHref} target="_blank" rel="noopener noreferrer" title={`Bevaka nyheter om ${name}`}
            className="w-6 h-6 rounded-full flex items-center justify-center text-amber-700 bg-amber-50 hover:bg-amber-100 border border-amber-100 transition-colors">
            <IconBell />
          </a>
          <a href={moreProjectsHref} target="_blank" rel="noopener noreferrer" title={`Fler projekt med ${name}`}
            className="w-6 h-6 rounded-full flex items-center justify-center text-violet-700 bg-violet-50 hover:bg-violet-100 border border-violet-100 transition-colors">
            <IconBuilding />
          </a>
        </div>
        {quoteOpen && <QuoteModal name={name} projectName={projectName} projectLocation={projectLocation} onClose={() => setQuoteOpen(false)} />}
      </>
    )
  }

  return (
    <>
      <div className="flex flex-wrap gap-1.5 mt-2">
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
        <a
          href={alertsHref}
          target="_blank"
          rel="noopener noreferrer"
          title={`Bevaka nyheter om ${name}`}
          className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium text-amber-700 bg-amber-50 hover:bg-amber-100 border border-amber-100 transition-colors"
        >
          <IconBell /><span>Bevaka bolaget</span>
        </a>
        <a
          href={moreProjectsHref}
          target="_blank"
          rel="noopener noreferrer"
          title={`Fler projekt med ${name}`}
          className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium text-violet-700 bg-violet-50 hover:bg-violet-100 border border-violet-100 transition-colors"
        >
          <IconBuilding /><span>Fler projekt</span>
        </a>
        <button
          onClick={() => setQuoteOpen(true)}
          title={`Lämna offert till ${name}`}
          className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium text-orange-700 bg-orange-50 hover:bg-orange-100 border border-orange-100 transition-colors"
        >
          <IconFileText /><span>Lämna offert</span>
        </button>
      </div>
      {quoteOpen && <QuoteModal name={name} projectName={projectName} projectLocation={projectLocation} onClose={() => setQuoteOpen(false)} />}
    </>
  )
}

// ── Recommended actions (project-level) ──────────────────────────────────────

function RecommendedActions({ p }) {
  const procurementQuery = [p.name, p.location, 'upphandling förfrågningsunderlag'].filter(Boolean).join(' ')
  const newsQuery = [p.name, p.location].filter(Boolean).join(' ')
  const alertsQuery = [p.name, p.location].filter(Boolean).join(' ')
  const similarQuery = [p.type, p.region, 'byggprojekt upphandling'].filter(Boolean).join(' ')

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
    {
      icon: <IconBell />,
      label: 'Bevaka projektet',
      sub: 'Få notis vid nyheter & statusändringar',
      href: `https://www.google.com/alerts?q=${encodeURIComponent(alertsQuery)}&hl=sv`,
      style: 'text-amber-700 bg-amber-50 hover:bg-amber-100 border-amber-100',
    },
    {
      icon: <IconLayers />,
      label: 'Liknande projekt',
      sub: `Fler ${p.type || 'bygg'}projekt i ${p.region || 'regionen'}`,
      href: `https://www.google.com/search?q=${encodeURIComponent(similarQuery)}`,
      style: 'text-violet-700 bg-violet-50 hover:bg-violet-100 border-violet-100',
    },
  ]

  return (
    <div>
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2.5">
        Rekommenderade åtgärder
      </h3>
      <div className="flex gap-3">
        {actions.map(a => (
          <a
            key={a.label}
            href={a.href}
            target="_blank"
            rel="noopener noreferrer"
            title={a.sub}
            className={`flex flex-col items-center gap-1.5 w-14 transition-colors group`}
          >
            <span className={`w-10 h-10 rounded-full flex items-center justify-center border transition-colors ${a.style}`}>
              {a.icon}
            </span>
            <span className="text-[10px] text-center text-gray-500 leading-tight group-hover:text-gray-700 transition-colors">{a.label}</span>
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
      <div className="space-y-1.5">
        {data.predictions.map((pred, i) => {
          const conf = CONFIDENCE_STYLE[pred.confidence] || CONFIDENCE_STYLE.låg
          return (
            <div key={i} className={`px-3 py-2 rounded-lg border border-dashed ${conf.bg}`}>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-medium text-sm text-gray-700">{pred.name}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${conf.text} bg-white border`}>
                  {conf.label}
                </span>
                {pred.confidence === 'hög' && (
                  <ParticipantActions
                    name={pred.name}
                    role={pred.likely_role || ''}
                    projectName={projectName}
                    projectLocation={projectLocation}
                    compact
                  />
                )}
              </div>
              {(pred.likely_role || pred.basis) && (
                <div className="text-xs text-gray-400 mt-0.5">
                  {[pred.likely_role, pred.basis].filter(Boolean).join(' · ')}
                </div>
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

// ── Updates Panel ─────────────────────────────────────────────────────────────

const PERIODS = [
  { key: 'day',   label: '1 dag' },
  { key: 'week',  label: '1 vecka' },
  { key: 'month', label: '1 månad' },
]

function UpdateItem({ update, projectId }) {
  const [open, setOpen] = useState(false)
  const [analysis, setAnalysis] = useState('')
  const [loading, setLoading] = useState(false)

  async function loadAnalysis() {
    if (analysis) { setOpen(o => !o); return }
    setOpen(true)
    setLoading(true)
    setAnalysis('')
    try {
      const res = await fetch(`/api/projects/${projectId}/analyze-update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: update.title, description: update.description }),
      })
      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buf = ''
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buf += decoder.decode(value, { stream: true })
        const lines = buf.split('\n')
        buf = lines.pop()
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const data = line.slice(6)
          if (data === '[DONE]') break
          try {
            const { text } = JSON.parse(data)
            if (text) setAnalysis(a => a + text)
          } catch {}
        }
      }
    } catch (e) {
      setAnalysis('Kunde inte hämta analys.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="border border-gray-100 rounded-lg overflow-hidden">
      <button
        onClick={loadAnalysis}
        className="w-full text-left px-3 py-2.5 hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-800 leading-snug line-clamp-2">{update.title}</p>
            <p className="text-xs text-gray-400 mt-0.5">{update.published}</p>
          </div>
          <div className="flex items-center gap-1.5 shrink-0 mt-0.5">
            <a
              href={update.url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={e => e.stopPropagation()}
              className="text-gray-400 hover:text-blue-600 transition-colors"
              title="Öppna artikel"
            >
              <IconExternalLink />
            </a>
            <span className="text-gray-300">{open ? <IconChevronUp /> : <IconChevronDown />}</span>
          </div>
        </div>
      </button>
      {open && (
        <div className="px-3 pb-3 pt-1 bg-indigo-50 border-t border-indigo-100">
          <p className="text-xs font-semibold text-indigo-500 uppercase tracking-wide mb-1.5">AI-analys</p>
          {loading && !analysis && (
            <p className="text-xs text-gray-400 italic">Analyserar…</p>
          )}
          {analysis && (
            <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{analysis}</p>
          )}
        </div>
      )}
    </div>
  )
}

function UpdatesPanel({ project, onClose }) {
  const [period, setPeriod] = useState('week')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    setData(null)
    axios.get(`/api/projects/${project.id}/updates?period=${period}`)
      .then(r => setData(r.data))
      .catch(() => setData({ updates: [], error: 'Kunde inte hämta uppdateringar.' }))
      .finally(() => setLoading(false))
  }, [period, project.id])

  return (
    <div
      className="fixed inset-0 z-[3000] flex items-center justify-center p-4 bg-black/60"
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-lg max-h-[85vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <div>
            <h3 className="font-semibold text-gray-900">Senaste uppdateringar</h3>
            <p className="text-xs text-gray-400 mt-0.5 truncate max-w-xs">{project.name}</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700 text-2xl leading-none" aria-label="Stäng">×</button>
        </div>

        {/* Period tabs */}
        <div className="flex gap-1 px-5 pt-3 pb-2">
          {PERIODS.map(p => (
            <button
              key={p.key}
              onClick={() => setPeriod(p.key)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                period === p.key
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto px-5 pb-5">
          {loading && (
            <p className="text-sm text-gray-400 text-center py-8">Hämtar nyheter…</p>
          )}
          {!loading && data && data.updates.length === 0 && (
            <p className="text-sm text-gray-400 text-center py-8">
              {data.error || 'Inga nyheter hittades för den valda perioden.'}
            </p>
          )}
          {!loading && data && data.updates.length > 0 && (
            <div className="space-y-2">
              {data.updates.map((u, i) => (
                <UpdateItem key={i} update={u} projectId={project.id} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}


// ── Heat Meter ────────────────────────────────────────────────────────────────

const HEAT_LEVELS = [
  { min: 0,  max: 1,  label: 'Okänd',  color: 'text-gray-400', bg: 'bg-gray-100', bars: 0 },
  { min: 1,  max: 3,  label: 'Kall',   color: 'text-blue-500', bg: 'bg-blue-50',  bars: 1 },
  { min: 3,  max: 7,  label: 'Ljummen',color: 'text-yellow-600',bg: 'bg-yellow-50',bars: 2 },
  { min: 7,  max: 15, label: 'Varm',   color: 'text-orange-500',bg: 'bg-orange-50',bars: 3 },
  { min: 15, max: Infinity, label: 'Het', color: 'text-red-600', bg: 'bg-red-50', bars: 4 },
]

function HeatMeter({ projectId }) {
  const [count, setCount] = useState(null)

  useEffect(() => {
    axios.post(`/api/projects/${projectId}/view`)
      .then(r => setCount(r.data.count))
      .catch(() => setCount(null))
  }, [projectId])

  if (count === null) return null
  const level = HEAT_LEVELS.findLast(l => count >= l.min) || HEAT_LEVELS[0]

  return (
    <div className={`inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium border ${level.color} ${level.bg} border-current/20`}
      title={`Öppnat ${count} gång${count !== 1 ? 'er' : ''}`}>
      <span className="flex gap-0.5">
        {[1,2,3,4].map(i => (
          <span key={i} className={i <= level.bars ? '' : 'opacity-20'}>
            <IconFlame />
          </span>
        ))}
      </span>
      <span>{level.label}</span>
      <span className="opacity-60">·{count}</span>
    </div>
  )
}

// ── Notes Panel ───────────────────────────────────────────────────────────────

const LS_FILES_KEY = (id) => `project_attachments_${id}`

function NotesPanel({ projectId }) {
  const [text, setText] = useState('')
  const [saved, setSaved] = useState(true)
  const [attachments, setAttachments] = useState([])
  const [lightbox, setLightbox] = useState(null)
  const fileRef = useRef(null)
  const photoRef = useRef(null)
  const timerRef = useRef(null)

  // Load notes text from backend + attachments from localStorage
  useEffect(() => {
    axios.get(`/api/projects/${projectId}/notes`)
      .then(r => { setText(r.data.content); setSaved(true) })
      .catch(() => {})
    const stored = localStorage.getItem(LS_FILES_KEY(projectId))
    if (stored) {
      try { setAttachments(JSON.parse(stored)) } catch {}
    }
  }, [projectId])

  // Auto-save text 1.5 s after last keystroke
  function handleChange(e) {
    setText(e.target.value)
    setSaved(false)
    clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => {
      axios.put(`/api/projects/${projectId}/notes`, { content: e.target.value })
        .then(() => setSaved(true))
        .catch(() => {})
    }, 1500)
  }

  function addFiles(files, isImage) {
    const readers = [...files].map(file => new Promise(resolve => {
      const fr = new FileReader()
      fr.onload = e => resolve({ name: file.name, type: file.type, data: e.target.result, isImage })
      fr.readAsDataURL(file)
    }))
    Promise.all(readers).then(newFiles => {
      setAttachments(prev => {
        const updated = [...prev, ...newFiles]
        localStorage.setItem(LS_FILES_KEY(projectId), JSON.stringify(updated))
        return updated
      })
    })
  }

  function removeAttachment(idx) {
    setAttachments(prev => {
      const updated = prev.filter((_, i) => i !== idx)
      localStorage.setItem(LS_FILES_KEY(projectId), JSON.stringify(updated))
      return updated
    })
  }

  return (
    <div className="border-t border-gray-100 pt-4">
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Mina anteckningar</h3>
      <textarea
        value={text}
        onChange={handleChange}
        rows={4}
        placeholder="Skriv anteckningar om projektet…"
        className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 outline-none focus:border-indigo-400 resize-none transition-colors"
      />
      <div className="flex items-center justify-between mt-1 mb-3">
        <div className="flex gap-2">
          <button
            onClick={() => fileRef.current.click()}
            className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded border border-gray-200 text-gray-600 hover:bg-gray-50 transition-colors"
          >
            <IconPaperclip /><span>Bifoga fil</span>
          </button>
          <button
            onClick={() => photoRef.current.click()}
            className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded border border-gray-200 text-gray-600 hover:bg-gray-50 transition-colors"
          >
            <IconImage /><span>Lägg till foto</span>
          </button>
          <input ref={fileRef} type="file" multiple className="hidden"
            onChange={e => { addFiles(e.target.files, false); e.target.value = '' }} />
          <input ref={photoRef} type="file" accept="image/*" multiple className="hidden"
            onChange={e => { addFiles(e.target.files, true); e.target.value = '' }} />
        </div>
        <span className={`text-xs transition-colors ${saved ? 'text-gray-300' : 'text-amber-500'}`}>
          {saved ? 'Sparat' : 'Sparar…'}
        </span>
      </div>

      {attachments.length > 0 && (
        <div className="space-y-1.5">
          {/* Images grid */}
          {attachments.some(a => a.isImage) && (
            <div className="flex flex-wrap gap-2 mb-2">
              {attachments.filter(a => a.isImage).map((a, idx) => {
                const realIdx = attachments.indexOf(a)
                return (
                  <div key={idx} className="relative group w-20 h-20">
                    <img
                      src={a.data}
                      alt={a.name}
                      className="w-full h-full object-cover rounded-lg border border-gray-200 cursor-pointer hover:opacity-90 transition-opacity"
                      onClick={() => setLightbox(a.data)}
                    />
                    <button
                      onClick={() => removeAttachment(realIdx)}
                      className="absolute top-0.5 right-0.5 w-5 h-5 rounded-full bg-white/90 text-red-500 hidden group-hover:flex items-center justify-center border border-gray-200 hover:bg-red-50 transition-colors"
                    >
                      <IconTrash />
                    </button>
                  </div>
                )
              })}
            </div>
          )}
          {/* File list */}
          {attachments.filter(a => !a.isImage).map((a, idx) => {
            const realIdx = attachments.indexOf(a)
            return (
              <div key={idx} className="flex items-center justify-between gap-2 px-2.5 py-1.5 bg-gray-50 rounded-lg border border-gray-100">
                <div className="flex items-center gap-1.5 min-w-0">
                  <IconPaperclip />
                  <a href={a.data} download={a.name} className="text-xs text-blue-600 hover:underline truncate">{a.name}</a>
                </div>
                <button onClick={() => removeAttachment(realIdx)} className="text-gray-400 hover:text-red-500 shrink-0 transition-colors">
                  <IconTrash />
                </button>
              </div>
            )
          })}
        </div>
      )}

      {/* Lightbox */}
      {lightbox && (
        <div
          className="fixed inset-0 z-[4000] flex items-center justify-center bg-black/80"
          onClick={() => setLightbox(null)}
        >
          <img src={lightbox} alt="" className="max-w-[90vw] max-h-[90vh] rounded-lg shadow-2xl" />
        </div>
      )}
    </div>
  )
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
  const [updatesOpen, setUpdatesOpen] = useState(false)

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
    <>
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
          <div className="flex flex-col items-end gap-1.5 shrink-0">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setUpdatesOpen(true)}
                className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-100 transition-colors"
                title="Senaste nyheter om projektet"
              >
                <IconClock /><span>Senaste uppdateringar</span>
              </button>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-700 text-2xl leading-none"
                aria-label="Stäng"
              >
                ×
              </button>
            </div>
            <HeatMeter projectId={p.id} />
          </div>
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

          {/* AI Sales Coach */}
          <SalesCoach project={p} />

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

          {/* Notes */}
          <NotesPanel projectId={p.id} />
        </div>
      </div>
    </div>
    {updatesOpen && <UpdatesPanel project={p} onClose={() => setUpdatesOpen(false)} />}
    </>
  )
}
