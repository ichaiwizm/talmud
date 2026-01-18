import { useState, useEffect, useRef } from 'react'
import { ArrowLeft, MessageCircle, Users, Network, Mic2, Crown } from 'lucide-react'

const BOOKS = ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy']

const SPEECH_TYPE_COLORS: Record<string, string> = {
  command: '#ef4444',
  blessing: '#22c55e',
  curse: '#7c3aed',
  prophecy: '#3b82f6',
  prayer: '#14b8a6',
  promise: '#f59e0b',
  warning: '#f97316',
  question: '#ec4899',
  dialogue: '#6366f1',
  narrative: '#64748b',
}

interface Speech {
  id: number
  verse_id: number
  verse_ref: string
  speaker: string
  addressee: string | null
  speech_type: string | null
  text: string
  text_hebrew: string
  is_divine: boolean
  is_quoted: boolean
}

interface Speaker {
  id: number | null
  name: string
  speech_count: number
  divine_count: number
}

interface SpeechType {
  type: string
  count: number
  divine_count: number
}

interface NetworkNode {
  id: string | number
  name: string
  is_divine: boolean
}

interface NetworkLink {
  source: string | number
  target: number
  count: number
  is_divine: boolean
}

interface Props {
  onBack: () => void
}

type ViewMode = 'speeches' | 'speakers' | 'network'

export default function VoiceChamber({ onBack }: Props) {
  const [view, setView] = useState<ViewMode>('speeches')
  const [book, setBook] = useState<string | null>(null)
  const [speeches, setSpeeches] = useState<Speech[]>([])
  const [speakers, setSpeakers] = useState<Speaker[]>([])
  const [speechTypes, setSpeechTypes] = useState<SpeechType[]>([])
  const [network, setNetwork] = useState<{ nodes: NetworkNode[]; links: NetworkLink[] }>({ nodes: [], links: [] })
  const [loading, setLoading] = useState(true)
  const [selectedSpeaker, setSelectedSpeaker] = useState<string | null>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  // Load data
  useEffect(() => {
    setLoading(true)
    const params = new URLSearchParams()
    if (book) params.set('book', book)

    Promise.all([
      fetch(`/api/voice-chamber/speeches?${params}&limit=150`).then(r => r.json()),
      fetch('/api/voice-chamber/speakers').then(r => r.json()),
      fetch('/api/voice-chamber/speech-types').then(r => r.json()),
      fetch(`/api/voice-chamber/network?${params}`).then(r => r.json()),
    ]).then(([speechData, speakerData, typeData, networkData]) => {
      setSpeeches(speechData)
      setSpeakers(speakerData)
      setSpeechTypes(typeData)
      setNetwork(networkData)
      setLoading(false)
    }).catch(console.error)
  }, [book])

  // Draw network on canvas
  useEffect(() => {
    if (view !== 'network' || !canvasRef.current || network.nodes.length === 0) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const width = canvas.width
    const height = canvas.height
    const centerX = width / 2
    const centerY = height / 2

    // Clear
    ctx.fillStyle = '#1a1410'
    ctx.fillRect(0, 0, width, height)

    // Calculate positions in a circle
    const positions = new Map<string | number, { x: number; y: number }>()
    const radius = Math.min(width, height) * 0.35

    network.nodes.forEach((node, i) => {
      const angle = (i / network.nodes.length) * Math.PI * 2 - Math.PI / 2
      const r = node.is_divine ? radius * 0.3 : radius
      positions.set(node.id, {
        x: centerX + Math.cos(angle) * r,
        y: centerY + Math.sin(angle) * r,
      })
    })

    // Draw links
    network.links.forEach(link => {
      const source = positions.get(link.source)
      const target = positions.get(link.target)
      if (!source || !target) return

      ctx.beginPath()
      ctx.moveTo(source.x, source.y)
      ctx.lineTo(target.x, target.y)
      ctx.strokeStyle = link.is_divine ? 'rgba(251, 191, 36, 0.4)' : 'rgba(255, 255, 255, 0.15)'
      ctx.lineWidth = Math.min(link.count * 0.5, 4)
      ctx.stroke()
    })

    // Draw nodes
    network.nodes.forEach(node => {
      const pos = positions.get(node.id)
      if (!pos) return

      const nodeSize = node.is_divine ? 20 : 12

      // Glow for divine
      if (node.is_divine) {
        const gradient = ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, nodeSize * 2)
        gradient.addColorStop(0, 'rgba(251, 191, 36, 0.5)')
        gradient.addColorStop(1, 'transparent')
        ctx.beginPath()
        ctx.arc(pos.x, pos.y, nodeSize * 2, 0, Math.PI * 2)
        ctx.fillStyle = gradient
        ctx.fill()
      }

      // Node
      ctx.beginPath()
      ctx.arc(pos.x, pos.y, nodeSize, 0, Math.PI * 2)
      ctx.fillStyle = node.is_divine ? '#fbbf24' : '#f59e0b'
      ctx.fill()

      // Label
      ctx.font = node.is_divine ? 'bold 12px sans-serif' : '10px sans-serif'
      ctx.fillStyle = '#fff'
      ctx.textAlign = 'center'
      ctx.fillText(node.name, pos.x, pos.y + nodeSize + 14)
    })
  }, [view, network])

  const filteredSpeeches = selectedSpeaker
    ? speeches.filter(s => s.speaker === selectedSpeaker)
    : speeches

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#1a1410] via-[#231a14] to-[#1a1410]">
      {/* Theatrical curtain effect at top */}
      <div
        className="absolute top-0 left-0 right-0 h-32 pointer-events-none"
        style={{
          background: 'linear-gradient(180deg, #8B0000 0%, transparent 100%)',
          opacity: 0.15,
        }}
      />

      {/* Header */}
      <header className="sticky top-0 z-30 backdrop-blur-md bg-[#1a1410]/80 border-b border-amber-900/30">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={onBack}
              className="p-2.5 rounded-xl bg-amber-900/30 hover:bg-amber-900/50 border border-amber-700/30 transition-all"
            >
              <ArrowLeft className="w-5 h-5 text-amber-200/70" />
            </button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg shadow-amber-900/50">
                <MessageCircle className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-amber-100">Voice Chamber</h1>
                <p className="text-sm text-amber-500/70">Le théâtre des dialogues</p>
              </div>
            </div>
          </div>

          {/* View switcher */}
          <div className="flex items-center gap-3">
            <div className="flex gap-1 p-1 rounded-lg bg-amber-900/30 border border-amber-700/30">
              <button
                onClick={() => setView('speeches')}
                className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-medium transition-all ${view === 'speeches' ? 'bg-amber-600 text-white' : 'text-amber-300/60 hover:text-amber-200'}`}
              >
                <Mic2 className="w-3.5 h-3.5" />
                Discours
              </button>
              <button
                onClick={() => setView('speakers')}
                className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-medium transition-all ${view === 'speakers' ? 'bg-amber-600 text-white' : 'text-amber-300/60 hover:text-amber-200'}`}
              >
                <Users className="w-3.5 h-3.5" />
                Orateurs
              </button>
              <button
                onClick={() => setView('network')}
                className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-medium transition-all ${view === 'network' ? 'bg-amber-600 text-white' : 'text-amber-300/60 hover:text-amber-200'}`}
              >
                <Network className="w-3.5 h-3.5" />
                Réseau
              </button>
            </div>

            {/* Book filter */}
            <select
              value={book || ''}
              onChange={e => setBook(e.target.value || null)}
              className="px-3 py-2 rounded-lg bg-amber-900/30 border border-amber-700/30 text-amber-200 text-sm focus:outline-none focus:ring-2 focus:ring-amber-500"
            >
              <option value="">Tous les livres</option>
              {BOOKS.map(b => (
                <option key={b} value={b}>{b}</option>
              ))}
            </select>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="flex flex-col items-center gap-4">
              <div className="w-12 h-12 rounded-full border-2 border-amber-700/30 border-t-amber-500 animate-spin" />
              <span className="text-amber-500/70 text-sm">Ouverture du rideau...</span>
            </div>
          </div>
        ) : (
          <>
            {/* Speeches view */}
            {view === 'speeches' && (
              <div className="space-y-6">
                {/* Speech type legend */}
                <div className="flex flex-wrap gap-3 p-4 rounded-xl bg-amber-900/20 border border-amber-800/30">
                  {speechTypes.slice(0, 8).map(st => (
                    <div key={st.type} className="flex items-center gap-2">
                      <span
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: SPEECH_TYPE_COLORS[st.type] || '#64748b' }}
                      />
                      <span className="text-xs text-amber-300/70 capitalize">{st.type}</span>
                      <span className="text-xs text-amber-500/50">({st.count})</span>
                    </div>
                  ))}
                </div>

                {/* Speaker filter */}
                {selectedSpeaker && (
                  <div className="flex items-center gap-2 p-3 rounded-lg bg-amber-600/20 border border-amber-600/30">
                    <span className="text-sm text-amber-200">Filtré par: {selectedSpeaker}</span>
                    <button
                      onClick={() => setSelectedSpeaker(null)}
                      className="ml-auto text-xs text-amber-400 hover:text-amber-200"
                    >
                      Effacer
                    </button>
                  </div>
                )}

                {/* Speeches list */}
                <div className="space-y-3">
                  {filteredSpeeches.map((speech, idx) => (
                    <div
                      key={speech.id}
                      className={`
                        relative p-5 rounded-xl transition-all
                        ${speech.is_divine
                          ? 'bg-gradient-to-r from-amber-900/40 to-amber-800/20 border-l-4 border-amber-500'
                          : 'bg-amber-950/30 border border-amber-800/20 hover:border-amber-700/40'}
                      `}
                      style={{ animationDelay: `${idx * 30}ms` }}
                    >
                      {/* Divine crown icon */}
                      {speech.is_divine && (
                        <Crown className="absolute top-3 right-3 w-5 h-5 text-amber-500" />
                      )}

                      {/* Speaker info */}
                      <div className="flex items-center gap-3 mb-3">
                        <button
                          onClick={() => setSelectedSpeaker(speech.speaker)}
                          className={`
                            px-3 py-1 rounded-full text-sm font-medium transition-all
                            ${speech.is_divine
                              ? 'bg-amber-500 text-amber-950 hover:bg-amber-400'
                              : 'bg-amber-800/50 text-amber-200 hover:bg-amber-700/50'}
                          `}
                        >
                          {speech.speaker}
                        </button>
                        {speech.addressee && (
                          <>
                            <span className="text-amber-600">→</span>
                            <span className="text-sm text-amber-400/80">{speech.addressee}</span>
                          </>
                        )}
                        {speech.speech_type && (
                          <span
                            className="ml-auto px-2 py-0.5 rounded text-xs font-medium text-white/90"
                            style={{ backgroundColor: SPEECH_TYPE_COLORS[speech.speech_type] || '#64748b' }}
                          >
                            {speech.speech_type}
                          </span>
                        )}
                      </div>

                      {/* Speech text */}
                      {speech.text && (
                        <p className="text-amber-100/90 leading-relaxed mb-2 italic">
                          "{speech.text}"
                        </p>
                      )}

                      {/* Reference */}
                      <span className="text-xs text-amber-500/60">{speech.verse_ref}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Speakers view */}
            {view === 'speakers' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {speakers.map((speaker, idx) => {
                  const isDivine = speaker.name === 'God' || speaker.divine_count > 0
                  const divineRatio = speaker.speech_count > 0 ? speaker.divine_count / speaker.speech_count : 0

                  return (
                    <div
                      key={speaker.id || 'god'}
                      className={`
                        p-5 rounded-xl transition-all cursor-pointer
                        ${isDivine && speaker.name === 'God'
                          ? 'bg-gradient-to-br from-amber-600/30 to-amber-800/20 border border-amber-500/50'
                          : 'bg-amber-950/40 border border-amber-800/30 hover:border-amber-600/50'}
                      `}
                      style={{ animationDelay: `${idx * 50}ms` }}
                      onClick={() => {
                        setSelectedSpeaker(speaker.name)
                        setView('speeches')
                      }}
                    >
                      <div className="flex items-center gap-3 mb-3">
                        {speaker.name === 'God' && (
                          <Crown className="w-5 h-5 text-amber-500" />
                        )}
                        <h3 className="text-lg font-medium text-amber-100">{speaker.name}</h3>
                      </div>

                      <div className="flex items-end justify-between">
                        <div>
                          <span className="text-3xl font-bold text-amber-400">{speaker.speech_count}</span>
                          <span className="text-sm text-amber-500/70 ml-2">discours</span>
                        </div>

                        {speaker.divine_count > 0 && speaker.name !== 'God' && (
                          <div className="text-right">
                            <span className="text-sm text-amber-500">{speaker.divine_count}</span>
                            <span className="text-xs text-amber-600/70 block">divins</span>
                          </div>
                        )}
                      </div>

                      {/* Divine ratio bar */}
                      {divineRatio > 0 && speaker.name !== 'God' && (
                        <div className="mt-3 h-1 bg-amber-900/50 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-amber-500 rounded-full"
                            style={{ width: `${divineRatio * 100}%` }}
                          />
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}

            {/* Network view */}
            {view === 'network' && (
              <div className="relative">
                <div className="absolute top-4 left-4 z-10 p-3 rounded-lg bg-amber-900/50 border border-amber-700/30 backdrop-blur-sm">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="w-3 h-3 rounded-full bg-amber-400" />
                    <span className="text-xs text-amber-200">Divin</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="w-2 h-2 rounded-full bg-amber-600" />
                    <span className="text-xs text-amber-300/70">Humain</span>
                  </div>
                </div>

                <canvas
                  ref={canvasRef}
                  width={1200}
                  height={700}
                  className="w-full rounded-xl border border-amber-800/30"
                />

                <p className="text-center text-sm text-amber-500/60 mt-4">
                  {network.nodes.length} orateurs • {network.links.length} connections
                </p>
              </div>
            )}
          </>
        )}
      </main>

      {/* Stats footer */}
      <div className="fixed bottom-4 right-4 p-4 rounded-xl bg-amber-950/80 border border-amber-800/30 backdrop-blur-sm">
        <div className="flex items-center gap-6 text-sm">
          <div>
            <span className="text-amber-500/70">Total discours: </span>
            <span className="text-amber-200 font-medium">{speeches.length}</span>
          </div>
          <div>
            <span className="text-amber-500/70">Divins: </span>
            <span className="text-amber-400 font-medium">
              {speeches.filter(s => s.is_divine).length}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
