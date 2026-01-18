import { useState, useEffect, useRef, useCallback } from 'react'
import {
  ArrowLeft, Calculator, Network, Star, BarChart3,
  Search, Sparkles, Hash
} from 'lucide-react'

const BOOKS = ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy']

// Hebrew letters in traditional order
const HEBREW_LETTERS = 'אבגדהוזחטיכלמנסעפצקרשת'

// Gematria values for each letter
const LETTER_VALUES: Record<string, number> = {
  'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5,
  'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9, 'י': 10,
  'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60,
  'ע': 70, 'פ': 80, 'צ': 90, 'ק': 100, 'ר': 200,
  'ש': 300, 'ת': 400, 'ך': 20, 'ם': 40, 'ן': 50, 'ף': 80, 'ץ': 90
}

interface Props {
  onBack: () => void
}

interface CalculationResult {
  input: string
  values: {
    standard: number
    katan: number
    ordinal: number
    atbash: number
  }
  letter_count: number
  breakdown: Array<{ letter: string; standard: number }>
}

interface NotableNumber {
  value: number
  hebrew: string
  name: string
  description: string
  computed_standard?: number
}

interface Connection {
  word: string
  word_normalized: string
  occurrences: number
  sample_refs: string[]
}

interface Distribution {
  value: number
  count: number
}

type ViewMode = 'calculator' | 'connections' | 'notable' | 'distribution'

export default function GematriaLab({ onBack }: Props) {
  const [view, setView] = useState<ViewMode>('calculator')
  const [input, setInput] = useState('')
  const [calculation, setCalculation] = useState<CalculationResult | null>(null)
  const [notableNumbers, setNotableNumbers] = useState<NotableNumber[]>([])
  const [distribution, setDistribution] = useState<Distribution[]>([])
  const [connections, setConnections] = useState<Connection[]>([])
  const [selectedValue, setSelectedValue] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [book, setBook] = useState<string | null>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  // Debounced calculation
  useEffect(() => {
    if (!input.trim()) {
      setCalculation(null)
      return
    }

    const timer = setTimeout(() => {
      fetch(`/api/gematria/calculate?text=${encodeURIComponent(input)}`)
        .then(r => r.json())
        .then(setCalculation)
        .catch(console.error)
    }, 300)

    return () => clearTimeout(timer)
  }, [input])

  // Load notable numbers on mount
  useEffect(() => {
    fetch('/api/gematria/notable-numbers')
      .then(r => r.json())
      .then(setNotableNumbers)
      .catch(console.error)
  }, [])

  // Load distribution when view changes or book changes
  useEffect(() => {
    if (view === 'distribution') {
      setLoading(true)
      const params = new URLSearchParams()
      if (book) params.set('book', book)
      params.set('limit', '25')

      fetch(`/api/gematria/distribution?${params}`)
        .then(r => r.json())
        .then(data => {
          setDistribution(data)
          setLoading(false)
        })
        .catch(console.error)
    }
  }, [view, book])

  // Load connections for a value
  const loadConnections = useCallback((value: number) => {
    setSelectedValue(value)
    setLoading(true)
    setView('connections')

    fetch(`/api/gematria/connections?value=${value}&limit=40`)
      .then(r => r.json())
      .then(data => {
        setConnections(data.connections)
        setLoading(false)
      })
      .catch(console.error)
  }, [])

  // Draw connections network on canvas
  useEffect(() => {
    if (view !== 'connections' || !canvasRef.current || connections.length === 0) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const width = canvas.width
    const height = canvas.height
    const centerX = width / 2
    const centerY = height / 2

    // Clear with dark background
    ctx.fillStyle = '#0a0f1a'
    ctx.fillRect(0, 0, width, height)

    // Draw geometric grid pattern
    ctx.strokeStyle = 'rgba(212, 168, 83, 0.05)'
    ctx.lineWidth = 1
    for (let i = 0; i < width; i += 40) {
      ctx.beginPath()
      ctx.moveTo(i, 0)
      ctx.lineTo(i, height)
      ctx.stroke()
    }
    for (let i = 0; i < height; i += 40) {
      ctx.beginPath()
      ctx.moveTo(0, i)
      ctx.lineTo(width, i)
      ctx.stroke()
    }

    // Draw golden spiral (simplified)
    ctx.strokeStyle = 'rgba(212, 168, 83, 0.15)'
    ctx.lineWidth = 2
    ctx.beginPath()
    let r = 10
    let angle = 0
    const phi = 1.618033988749
    for (let i = 0; i < 500; i++) {
      const x = centerX + r * Math.cos(angle)
      const y = centerY + r * Math.sin(angle)
      if (i === 0) ctx.moveTo(x, y)
      else ctx.lineTo(x, y)
      angle += 0.1
      r = r * (1 + 0.01 * phi)
    }
    ctx.stroke()

    // Draw center value
    if (selectedValue) {
      ctx.fillStyle = '#d4a853'
      ctx.font = 'bold 48px "Cinzel", serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(selectedValue.toString(), centerX, centerY)

      // Glow effect
      ctx.shadowColor = '#d4a853'
      ctx.shadowBlur = 20
      ctx.fillText(selectedValue.toString(), centerX, centerY)
      ctx.shadowBlur = 0
    }

    // Position words around in golden spiral layout
    const positions: Array<{ x: number; y: number; word: string; count: number }> = []
    connections.forEach((conn, i) => {
      const angle = (i / connections.length) * Math.PI * 2 + Math.PI / 6
      const distance = 150 + (i % 3) * 60
      positions.push({
        x: centerX + Math.cos(angle) * distance,
        y: centerY + Math.sin(angle) * distance,
        word: conn.word,
        count: conn.occurrences
      })
    })

    // Draw connections to center
    positions.forEach(pos => {
      ctx.beginPath()
      ctx.moveTo(centerX, centerY)
      ctx.lineTo(pos.x, pos.y)
      ctx.strokeStyle = 'rgba(212, 168, 83, 0.2)'
      ctx.lineWidth = 1
      ctx.stroke()
    })

    // Draw word nodes
    positions.forEach(pos => {
      // Node circle
      const nodeSize = 8 + Math.min(pos.count, 10) * 2
      const gradient = ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, nodeSize * 1.5)
      gradient.addColorStop(0, 'rgba(212, 168, 83, 0.6)')
      gradient.addColorStop(1, 'transparent')
      ctx.beginPath()
      ctx.arc(pos.x, pos.y, nodeSize * 1.5, 0, Math.PI * 2)
      ctx.fillStyle = gradient
      ctx.fill()

      ctx.beginPath()
      ctx.arc(pos.x, pos.y, nodeSize, 0, Math.PI * 2)
      ctx.fillStyle = '#b87333'
      ctx.fill()

      // Hebrew word
      ctx.font = '18px "Frank Ruhl Libre", serif'
      ctx.fillStyle = '#b8c5d6'
      ctx.textAlign = 'center'
      ctx.fillText(pos.word, pos.x, pos.y + nodeSize + 18)

      // Occurrence count
      ctx.font = '10px "JetBrains Mono", monospace'
      ctx.fillStyle = 'rgba(184, 197, 214, 0.6)'
      ctx.fillText(`${pos.count}x`, pos.x, pos.y + nodeSize + 32)
    })
  }, [view, connections, selectedValue])

  // Get active letters in current input
  const getActiveLetters = useCallback(() => {
    const active = new Set<string>()
    for (const char of input) {
      if (LETTER_VALUES[char]) active.add(char)
    }
    return active
  }, [input])

  const activeLetters = getActiveLetters()

  return (
    <div className="min-h-screen bg-[#0a0f1a] gematria-grid">
      {/* Subtle gradient overlays */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-[#d4a853]/5 via-transparent to-transparent" />
        <div className="absolute bottom-0 right-0 w-1/2 h-1/2 bg-gradient-to-tl from-[#4a90d9]/5 via-transparent to-transparent" />
      </div>

      {/* Header */}
      <header className="sticky top-0 z-30 backdrop-blur-md bg-[#0a0f1a]/80 border-b border-[#d4a853]/20">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={onBack}
              className="p-2.5 rounded-xl bg-[#141e2d] hover:bg-[#1c2a3d] border border-[#d4a853]/20 transition-all"
            >
              <ArrowLeft className="w-5 h-5 text-[#b8c5d6]" />
            </button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#d4a853] to-[#b87333] flex items-center justify-center shadow-lg shadow-[#d4a853]/20">
                <Calculator className="w-5 h-5 text-[#0a0f1a]" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-[#b8c5d6] font-cinzel">GematriaLab</h1>
                <p className="text-sm text-[#d4a853]/70">L'atelier de numérologie sacrée</p>
              </div>
            </div>
          </div>

          {/* View switcher - brass dial style */}
          <div className="flex items-center gap-3">
            <div className="flex gap-1 p-1 rounded-xl bg-[#141e2d] border border-[#9b7b4d]/30">
              {[
                { id: 'calculator' as ViewMode, icon: Calculator, label: 'Calcul' },
                { id: 'connections' as ViewMode, icon: Network, label: 'Liens' },
                { id: 'notable' as ViewMode, icon: Star, label: 'Nombres' },
                { id: 'distribution' as ViewMode, icon: BarChart3, label: 'Stats' },
              ].map(v => (
                <button
                  key={v.id}
                  onClick={() => setView(v.id)}
                  className={`
                    flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all
                    ${view === v.id
                      ? 'bg-gradient-to-r from-[#d4a853] to-[#b87333] text-[#0a0f1a]'
                      : 'text-[#b8c5d6]/60 hover:text-[#b8c5d6]'}
                  `}
                >
                  <v.icon className="w-3.5 h-3.5" />
                  {v.label}
                </button>
              ))}
            </div>

            {view === 'distribution' && (
              <select
                value={book || ''}
                onChange={e => setBook(e.target.value || null)}
                className="px-3 py-2 rounded-lg bg-[#141e2d] border border-[#9b7b4d]/30 text-[#b8c5d6] text-sm focus:outline-none focus:ring-2 focus:ring-[#d4a853]/50"
              >
                <option value="">Tous les livres</option>
                {BOOKS.map(b => (
                  <option key={b} value={b}>{b}</option>
                ))}
              </select>
            )}
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-6xl mx-auto px-6 py-8 relative z-10">
        {/* Calculator View */}
        {view === 'calculator' && (
          <div className="space-y-8">
            {/* Hebrew Letter Wheel */}
            <div className="flex justify-center">
              <div className="relative">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-24 h-24 rounded-full bg-gradient-to-br from-[#d4a853]/20 to-[#b87333]/10 border border-[#d4a853]/30 flex items-center justify-center">
                    <span className="text-3xl font-bold text-[#d4a853] mono">
                      {calculation?.values.standard || 0}
                    </span>
                  </div>
                </div>
                <div className="relative w-[320px] h-[320px]">
                  {HEBREW_LETTERS.split('').map((letter, i) => {
                    const angle = (i / 22) * Math.PI * 2 - Math.PI / 2
                    const radius = 140
                    const x = 160 + Math.cos(angle) * radius
                    const y = 160 + Math.sin(angle) * radius
                    const isActive = activeLetters.has(letter)

                    return (
                      <div
                        key={letter}
                        className={`
                          absolute w-10 h-10 -ml-5 -mt-5 rounded-full flex items-center justify-center
                          transition-all duration-300 cursor-pointer
                          ${isActive
                            ? 'bg-[#d4a853] text-[#0a0f1a] scale-125 shadow-lg shadow-[#d4a853]/40'
                            : 'bg-[#141e2d] text-[#b8c5d6]/70 hover:bg-[#1c2a3d] border border-[#9b7b4d]/20'}
                        `}
                        style={{ left: x, top: y }}
                        onClick={() => setInput(prev => prev + letter)}
                      >
                        <span className="hebrew text-lg font-medium">{letter}</span>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>

            {/* Input and Results */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Input Card */}
              <div className="bg-[#141e2d] rounded-2xl border border-[#9b7b4d]/20 p-6">
                <h3 className="text-lg font-semibold text-[#d4a853] mb-4 font-cinzel">Entrée</h3>
                <div className="relative">
                  <input
                    type="text"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    placeholder="Entrez du texte hébreu..."
                    className="w-full px-4 py-4 rounded-xl bg-[#0a0f1a] border border-[#9b7b4d]/20 text-[#b8c5d6] text-2xl text-right hebrew focus:outline-none focus:ring-2 focus:ring-[#d4a853]/50 placeholder:text-[#b8c5d6]/30"
                    dir="rtl"
                  />
                  {input && (
                    <button
                      onClick={() => setInput('')}
                      className="absolute left-3 top-1/2 -translate-y-1/2 text-[#b8c5d6]/50 hover:text-[#b8c5d6]"
                    >
                      &times;
                    </button>
                  )}
                </div>

                {calculation && (
                  <div className="mt-6 space-y-4">
                    {/* Method values */}
                    <div className="grid grid-cols-2 gap-3">
                      {[
                        { key: 'standard', label: 'Standard', value: calculation.values.standard },
                        { key: 'katan', label: 'Katan', value: calculation.values.katan },
                        { key: 'ordinal', label: 'Ordinal', value: calculation.values.ordinal },
                        { key: 'atbash', label: 'Atbash', value: calculation.values.atbash },
                      ].map(m => (
                        <div
                          key={m.key}
                          className="p-3 rounded-lg bg-[#0a0f1a] border border-[#9b7b4d]/10"
                        >
                          <div className="text-xs text-[#b8c5d6]/50 mb-1">{m.label}</div>
                          <div className="text-xl font-bold text-[#d4a853] mono">{m.value}</div>
                        </div>
                      ))}
                    </div>

                    {/* Find matches button */}
                    <button
                      onClick={() => loadConnections(calculation.values.standard)}
                      className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-gradient-to-r from-[#d4a853] to-[#b87333] text-[#0a0f1a] font-medium hover:opacity-90 transition-opacity"
                    >
                      <Search className="w-4 h-4" />
                      Trouver les correspondances
                    </button>
                  </div>
                )}
              </div>

              {/* Letter Breakdown Card */}
              <div className="bg-[#141e2d] rounded-2xl border border-[#9b7b4d]/20 p-6">
                <h3 className="text-lg font-semibold text-[#d4a853] mb-4 font-cinzel">Décomposition</h3>
                {calculation?.breakdown && calculation.breakdown.length > 0 ? (
                  <div className="space-y-2 max-h-[300px] overflow-y-auto">
                    {calculation.breakdown.map((item, i) => (
                      <div
                        key={i}
                        className="flex items-center justify-between p-3 rounded-lg bg-[#0a0f1a] border border-[#9b7b4d]/10"
                      >
                        <span className="text-2xl hebrew text-[#b8c5d6]">{item.letter}</span>
                        <div className="flex items-center gap-3">
                          <span className="text-sm text-[#b8c5d6]/50">
                            Position {HEBREW_LETTERS.indexOf(item.letter) + 1}
                          </span>
                          <span className="text-lg font-bold text-[#d4a853] mono w-12 text-right">
                            {item.standard}
                          </span>
                        </div>
                      </div>
                    ))}
                    <div className="flex items-center justify-between p-3 rounded-lg bg-[#d4a853]/10 border border-[#d4a853]/30">
                      <span className="text-sm font-medium text-[#d4a853]">Total</span>
                      <span className="text-xl font-bold text-[#d4a853] mono">
                        {calculation.values.standard}
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-48 text-[#b8c5d6]/30">
                    <Hash className="w-12 h-12 mb-3" />
                    <p>Entrez du texte pour voir la décomposition</p>
                  </div>
                )}
              </div>
            </div>

          </div>
        )}

        {/* Connections View */}
        {view === 'connections' && (
          <div className="space-y-6">
            {/* Value input */}
            <div className="flex items-center gap-4">
              <div className="flex-1 relative">
                <input
                  type="number"
                  value={selectedValue || ''}
                  onChange={e => {
                    const val = parseInt(e.target.value)
                    if (!isNaN(val) && val > 0) loadConnections(val)
                  }}
                  placeholder="Entrez une valeur numérique..."
                  className="w-full px-4 py-3 rounded-xl bg-[#141e2d] border border-[#9b7b4d]/20 text-[#b8c5d6] text-lg mono focus:outline-none focus:ring-2 focus:ring-[#d4a853]/50"
                />
                <Search className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#b8c5d6]/30" />
              </div>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-20">
                <div className="flex flex-col items-center gap-4">
                  <div className="w-12 h-12 rounded-full border-2 border-[#9b7b4d]/30 border-t-[#d4a853] animate-spin" />
                  <span className="text-[#d4a853]/70 text-sm">Analyse des connexions...</span>
                </div>
              </div>
            ) : connections.length > 0 ? (
              <div className="space-y-6">
                <canvas
                  ref={canvasRef}
                  width={1200}
                  height={600}
                  className="w-full rounded-2xl border border-[#9b7b4d]/20"
                />
                <div className="text-center text-sm text-[#b8c5d6]/50">
                  {connections.length} mots distincts partagent la valeur {selectedValue}
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-20 text-[#b8c5d6]/30">
                <Network className="w-16 h-16 mb-4" />
                <p className="text-lg">Entrez une valeur pour voir les connexions</p>
                <p className="text-sm mt-2">ou calculez d'abord un mot dans l'onglet Calcul</p>
              </div>
            )}
          </div>
        )}

        {/* Notable Numbers View */}
        {view === 'notable' && (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-[#d4a853] font-cinzel mb-2">
                Nombres Sacrés
              </h2>
              <p className="text-[#b8c5d6]/60">
                Les valeurs numériques porteuses de signification spirituelle
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {notableNumbers.map((num, i) => (
                <button
                  key={i}
                  onClick={() => loadConnections(num.value)}
                  className="group p-5 rounded-2xl bg-[#141e2d] border border-[#9b7b4d]/20 hover:border-[#d4a853]/40 transition-all text-left"
                >
                  <div className="flex items-start justify-between mb-3">
                    <span className="text-3xl font-bold text-[#d4a853] mono">{num.value}</span>
                    <Sparkles className="w-5 h-5 text-[#d4a853]/30 group-hover:text-[#d4a853]/60 transition-colors" />
                  </div>
                  <div className="text-2xl hebrew text-[#b8c5d6] mb-1">{num.hebrew}</div>
                  <div className="text-sm font-medium text-[#b8c5d6]/80 mb-1">{num.name}</div>
                  <div className="text-xs text-[#b8c5d6]/50">{num.description}</div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Distribution View */}
        {view === 'distribution' && (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-[#d4a853] font-cinzel mb-2">
                Distribution des Valeurs
              </h2>
              <p className="text-[#b8c5d6]/60">
                Les valeurs de gematria les plus fréquentes dans la Torah
              </p>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-20">
                <div className="flex flex-col items-center gap-4">
                  <div className="w-12 h-12 rounded-full border-2 border-[#9b7b4d]/30 border-t-[#d4a853] animate-spin" />
                  <span className="text-[#d4a853]/70 text-sm">Chargement des statistiques...</span>
                </div>
              </div>
            ) : (
              <div className="bg-[#141e2d] rounded-2xl border border-[#9b7b4d]/20 p-6">
                <div className="space-y-3">
                  {distribution.map((item) => {
                    const maxCount = distribution[0]?.count || 1
                    const percentage = (item.count / maxCount) * 100

                    return (
                      <button
                        key={item.value}
                        onClick={() => loadConnections(item.value)}
                        className="w-full group"
                      >
                        <div className="flex items-center gap-4">
                          <span className="w-16 text-right text-lg font-bold text-[#d4a853] mono">
                            {item.value}
                          </span>
                          <div className="flex-1 h-8 bg-[#0a0f1a] rounded-lg overflow-hidden relative">
                            <div
                              className="h-full bg-gradient-to-r from-[#d4a853] to-[#b87333] transition-all group-hover:opacity-80"
                              style={{ width: `${percentage}%` }}
                            />
                            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-[#b8c5d6]/70 mono">
                              {item.count.toLocaleString()}
                            </span>
                          </div>
                        </div>
                      </button>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Stats footer */}
      {calculation && view === 'calculator' && (
        <div className="fixed bottom-4 right-4 p-4 rounded-xl bg-[#141e2d]/90 border border-[#9b7b4d]/20 backdrop-blur-sm">
          <div className="flex items-center gap-6 text-sm">
            <div>
              <span className="text-[#b8c5d6]/50">Lettres: </span>
              <span className="text-[#d4a853] font-medium mono">{calculation.letter_count}</span>
            </div>
            <div>
              <span className="text-[#b8c5d6]/50">Valeur: </span>
              <span className="text-[#d4a853] font-medium mono">{calculation.values.standard}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
