import { useState, useEffect, useRef, useCallback } from 'react'
import { ArrowLeft, Sparkles, ZoomIn, ZoomOut, RotateCcw, Filter } from 'lucide-react'

const EMOTION_COLORS: Record<string, string> = {
  joy: '#fbbf24',
  love: '#ec4899',
  awe: '#a78bfa',
  hope: '#22c55e',
  gratitude: '#14b8a6',
  fear: '#6366f1',
  anger: '#ef4444',
  sorrow: '#3b82f6',
  despair: '#6b7280',
  shame: '#f97316',
  jealousy: '#84cc16',
  compassion: '#f472b6',
  neutral: '#9ca3af',
}

const BOOK_COLORS: Record<string, string> = {
  Genesis: '#22c55e',
  Exodus: '#3b82f6',
  Leviticus: '#a855f7',
  Numbers: '#f59e0b',
  Deuteronomy: '#ef4444',
}

interface Verse {
  id: number
  ref: string
  book: string
  chapter: number
  verse_num: number
  text_preview: string
  gematria: number
  emotion: string | null
  intensity: number
  polarity: number
}

interface Connection {
  source_id: number
  target_id: number
  type: string
  strength: number
}

interface Props {
  onBack: () => void
}

export default function Constellation({ onBack }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [verses, setVerses] = useState<Verse[]>([])
  const [connections, setConnections] = useState<Connection[]>([])
  const [books, setBooks] = useState<{ book: string; count: number }[]>([])
  const [selectedBook, setSelectedBook] = useState<string | null>(null)
  const [hoveredVerse, setHoveredVerse] = useState<Verse | null>(null)
  const [zoom, setZoom] = useState(1)
  const [offset, setOffset] = useState({ x: 0, y: 0 })
  const [loading, setLoading] = useState(true)
  const [colorMode, setColorMode] = useState<'emotion' | 'book'>('book')

  // Star positions (calculated once)
  const starPositions = useRef<Map<number, { x: number; y: number }>>(new Map())

  useEffect(() => {
    Promise.all([
      fetch('/api/constellation/book-summary').then(r => r.json()),
    ]).then(([bookData]) => {
      setBooks(bookData)
      loadVerses(null)
    }).catch(console.error)
  }, [])

  const loadVerses = async (book: string | null) => {
    setLoading(true)
    const params = new URLSearchParams({ limit: '300' })
    if (book) params.set('book', book)

    const [verseData, connData] = await Promise.all([
      fetch(`/api/constellation/verses?${params}`).then(r => r.json()),
      fetch(`/api/constellation/connections?${params}`).then(r => r.json()),
    ])

    setVerses(verseData.verses)
    setConnections(connData)

    // Calculate star positions in a spiral galaxy pattern
    const positions = new Map<number, { x: number; y: number }>()
    verseData.verses.forEach((v: Verse, i: number) => {
      const angle = (i / verseData.verses.length) * Math.PI * 8 + (v.chapter * 0.1)
      const radius = 100 + (i / verseData.verses.length) * 300 + Math.random() * 50
      const x = Math.cos(angle) * radius + (Math.random() - 0.5) * 40
      const y = Math.sin(angle) * radius + (Math.random() - 0.5) * 40
      positions.set(v.id, { x, y })
    })
    starPositions.current = positions

    setLoading(false)
  }

  const handleBookChange = (book: string | null) => {
    setSelectedBook(book)
    loadVerses(book)
  }

  // Canvas drawing
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || verses.length === 0) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const width = canvas.width
    const height = canvas.height
    const centerX = width / 2 + offset.x
    const centerY = height / 2 + offset.y

    // Clear
    ctx.fillStyle = '#050510'
    ctx.fillRect(0, 0, width, height)

    // Draw nebula background
    const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, 400 * zoom)
    gradient.addColorStop(0, 'rgba(99, 102, 241, 0.1)')
    gradient.addColorStop(0.5, 'rgba(139, 92, 246, 0.05)')
    gradient.addColorStop(1, 'transparent')
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, width, height)

    // Draw connections first (behind stars)
    ctx.globalAlpha = 0.15
    connections.forEach(conn => {
      const source = starPositions.current.get(conn.source_id)
      const target = starPositions.current.get(conn.target_id)
      if (!source || !target) return

      ctx.beginPath()
      ctx.moveTo(centerX + source.x * zoom, centerY + source.y * zoom)
      ctx.lineTo(centerX + target.x * zoom, centerY + target.y * zoom)
      ctx.strokeStyle = '#6366f1'
      ctx.lineWidth = conn.strength * 2
      ctx.stroke()
    })
    ctx.globalAlpha = 1

    // Draw stars
    verses.forEach(verse => {
      const pos = starPositions.current.get(verse.id)
      if (!pos) return

      const x = centerX + pos.x * zoom
      const y = centerY + pos.y * zoom

      // Star size based on gematria (normalized)
      const baseSize = 2 + (verse.gematria / 5000) * 4
      const size = baseSize * (0.8 + verse.intensity * 0.4)

      // Color based on mode
      const color = colorMode === 'emotion'
        ? EMOTION_COLORS[verse.emotion || 'neutral'] || '#9ca3af'
        : BOOK_COLORS[verse.book] || '#9ca3af'

      // Glow effect
      const glowGradient = ctx.createRadialGradient(x, y, 0, x, y, size * 3)
      glowGradient.addColorStop(0, color)
      glowGradient.addColorStop(0.3, color + '80')
      glowGradient.addColorStop(1, 'transparent')

      ctx.beginPath()
      ctx.arc(x, y, size * 3, 0, Math.PI * 2)
      ctx.fillStyle = glowGradient
      ctx.fill()

      // Core
      ctx.beginPath()
      ctx.arc(x, y, size, 0, Math.PI * 2)
      ctx.fillStyle = color
      ctx.fill()

      // Bright center
      ctx.beginPath()
      ctx.arc(x, y, size * 0.4, 0, Math.PI * 2)
      ctx.fillStyle = '#ffffff'
      ctx.fill()
    })
  }, [verses, connections, zoom, offset, colorMode])

  // Mouse handling for hover
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const mouseX = e.clientX - rect.left
    const mouseY = e.clientY - rect.top
    const centerX = canvas.width / 2 + offset.x
    const centerY = canvas.height / 2 + offset.y

    let closest: Verse | null = null
    let closestDist = 20 // Max distance to select

    verses.forEach(verse => {
      const pos = starPositions.current.get(verse.id)
      if (!pos) return

      const x = centerX + pos.x * zoom
      const y = centerY + pos.y * zoom
      const dist = Math.sqrt((mouseX - x) ** 2 + (mouseY - y) ** 2)

      if (dist < closestDist) {
        closest = verse
        closestDist = dist
      }
    })

    setHoveredVerse(closest)
  }, [verses, zoom, offset])

  return (
    <div className="min-h-screen bg-[#050510] overflow-hidden">
      {/* Header */}
      <header className="absolute top-0 left-0 right-0 z-20 flex items-center justify-between p-4 bg-gradient-to-b from-black/80 to-transparent">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 transition-all"
          >
            <ArrowLeft className="w-5 h-5 text-white/70" />
          </button>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/20 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-indigo-400" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-white">Torah Constellation</h1>
              <p className="text-sm text-white/40">{verses.length} versets affichés</p>
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-3">
          {/* Color mode */}
          <div className="flex gap-1 p-1 rounded-lg bg-white/5 border border-white/10">
            <button
              onClick={() => setColorMode('book')}
              className={`px-3 py-1.5 rounded text-xs font-medium transition-all ${colorMode === 'book' ? 'bg-white/10 text-white' : 'text-white/40'}`}
            >
              Par Livre
            </button>
            <button
              onClick={() => setColorMode('emotion')}
              className={`px-3 py-1.5 rounded text-xs font-medium transition-all ${colorMode === 'emotion' ? 'bg-white/10 text-white' : 'text-white/40'}`}
            >
              Par Émotion
            </button>
          </div>

          {/* Zoom controls */}
          <div className="flex gap-1 p-1 rounded-lg bg-white/5 border border-white/10">
            <button onClick={() => setZoom(z => Math.min(z * 1.2, 3))} className="p-2 text-white/60 hover:text-white">
              <ZoomIn className="w-4 h-4" />
            </button>
            <button onClick={() => setZoom(z => Math.max(z / 1.2, 0.3))} className="p-2 text-white/60 hover:text-white">
              <ZoomOut className="w-4 h-4" />
            </button>
            <button onClick={() => { setZoom(1); setOffset({ x: 0, y: 0 }) }} className="p-2 text-white/60 hover:text-white">
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Book filter */}
      <div className="absolute top-20 left-4 z-20 flex flex-col gap-2">
        <button
          onClick={() => handleBookChange(null)}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${!selectedBook ? 'bg-white/15 text-white' : 'bg-white/5 text-white/50 hover:bg-white/10'}`}
        >
          Tous
        </button>
        {books.map(b => (
          <button
            key={b.book}
            onClick={() => handleBookChange(b.book)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${selectedBook === b.book ? 'bg-white/15 text-white' : 'bg-white/5 text-white/50 hover:bg-white/10'}`}
          >
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: BOOK_COLORS[b.book] }} />
            {b.book}
          </button>
        ))}
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-20 p-4 rounded-xl bg-black/50 border border-white/10 backdrop-blur-sm">
        <h3 className="text-xs font-medium text-white/50 mb-3">
          {colorMode === 'book' ? 'Livres' : 'Émotions'}
        </h3>
        <div className="flex flex-wrap gap-3 max-w-xs">
          {colorMode === 'book'
            ? Object.entries(BOOK_COLORS).map(([name, color]) => (
              <div key={name} className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                <span className="text-xs text-white/60">{name}</span>
              </div>
            ))
            : Object.entries(EMOTION_COLORS).slice(0, 8).map(([name, color]) => (
              <div key={name} className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                <span className="text-xs text-white/60 capitalize">{name}</span>
              </div>
            ))
          }
        </div>
      </div>

      {/* Hovered verse info */}
      {hoveredVerse && (
        <div className="absolute bottom-4 right-4 z-20 p-4 rounded-xl bg-black/70 border border-white/10 backdrop-blur-sm max-w-sm">
          <div className="flex items-center gap-2 mb-2">
            <span
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: colorMode === 'book' ? BOOK_COLORS[hoveredVerse.book] : EMOTION_COLORS[hoveredVerse.emotion || 'neutral'] }}
            />
            <span className="text-sm font-medium text-white">{hoveredVerse.ref}</span>
            {hoveredVerse.emotion && (
              <span className="text-xs text-white/40 capitalize">• {hoveredVerse.emotion}</span>
            )}
          </div>
          <p className="text-sm text-white/70 leading-relaxed">
            {hoveredVerse.text_preview}
          </p>
          <div className="flex gap-4 mt-2 text-xs text-white/40">
            <span>Gematria: {hoveredVerse.gematria}</span>
            <span>Intensité: {Math.round(hoveredVerse.intensity * 100)}%</span>
          </div>
        </div>
      )}

      {/* Canvas */}
      {loading ? (
        <div className="flex items-center justify-center h-screen">
          <div className="flex flex-col items-center gap-4">
            <div className="w-12 h-12 rounded-full border-2 border-indigo-500/30 border-t-indigo-500 animate-spin" />
            <span className="text-white/50 text-sm">Chargement des étoiles...</span>
          </div>
        </div>
      ) : (
        <canvas
          ref={canvasRef}
          width={1400}
          height={900}
          className="w-full h-screen"
          onMouseMove={handleMouseMove}
          style={{ cursor: hoveredVerse ? 'pointer' : 'default' }}
        />
      )}
    </div>
  )
}
