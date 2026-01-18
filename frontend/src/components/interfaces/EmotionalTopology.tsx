import { useState, useEffect, useRef, useCallback } from 'react'
import {
  ArrowLeft, Mountain, BarChart3, Users, TrendingUp,
  Waves, Filter, Sparkles
} from 'lucide-react'

const BOOKS = ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy']

// Emotion colors matching the backend
const EMOTION_COLORS: Record<string, string> = {
  joy: '#22c55e',
  fear: '#7c3aed',
  anger: '#ef4444',
  sorrow: '#3b82f6',
  love: '#ec4899',
  awe: '#f59e0b',
  gratitude: '#14b8a6',
  jealousy: '#84cc16',
  shame: '#6b7280',
  hope: '#06b6d4',
  despair: '#1e293b',
  compassion: '#f97316',
  neutral: '#94a3b8',
}

interface Props {
  onBack: () => void
}

interface TerrainPoint {
  verse_id: number
  ref: string
  book: string
  chapter: number
  verse_num: number
  x: number
  y: number
  z: number
  polarity: number
  emotion: string
  secondary_emotion: string | null
  divine_sentiment: string | null
  color: string
  text_preview: string
}

interface ChapterEmotion {
  book: string
  chapter: number
  avg_intensity: number
  avg_polarity: number
  avg_tension: number
  verse_count: number
}

interface EmotionDistribution {
  emotion: string
  count: number
  avg_intensity: number
  color: string
}

interface CharacterData {
  name: string
  emotions: Record<string, number>
  total: number
}

interface Peak {
  verse_id: number
  ref: string
  book: string
  chapter: number
  intensity: number
  polarity: number
  tension: number
  emotion: string
  color: string
  text_hebrew: string
  text_english: string
  context: string | null
}

interface Stats {
  book: string
  total_verses_analyzed: number
  character_emotions_count: number
  avg_intensity: number
  avg_polarity: number
  avg_tension: number
  max_intensity: number
  min_intensity: number
}

type ViewMode = 'terrain' | 'distribution' | 'characters' | 'peaks'

export default function EmotionalTopology({ onBack }: Props) {
  const [view, setView] = useState<ViewMode>('terrain')
  const [book, setBook] = useState<string | null>(null)
  const [terrain, setTerrain] = useState<TerrainPoint[]>([])
  const [chapters, setChapters] = useState<ChapterEmotion[]>([])
  const [distribution, setDistribution] = useState<EmotionDistribution[]>([])
  const [characters, setCharacters] = useState<CharacterData[]>([])
  const [peaks, setPeaks] = useState<Peak[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedPoint, setSelectedPoint] = useState<TerrainPoint | null>(null)
  const [hoveredEmotion, setHoveredEmotion] = useState<string | null>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  // Load data based on view
  useEffect(() => {
    setLoading(true)
    const params = new URLSearchParams()
    if (book) params.set('book', book)

    const fetchPromises: Promise<void>[] = []

    // Always load stats
    fetchPromises.push(
      fetch(`/api/emotional-topology/stats?${params}`)
        .then(r => r.json())
        .then(setStats)
    )

    if (view === 'terrain') {
      params.set('limit', '300')
      fetchPromises.push(
        fetch(`/api/emotional-topology/terrain?${params}`)
          .then(r => r.json())
          .then(data => setTerrain(data.points))
      )
      fetchPromises.push(
        fetch(`/api/emotional-topology/chapters?${params}`)
          .then(r => r.json())
          .then(setChapters)
      )
    } else if (view === 'distribution') {
      fetchPromises.push(
        fetch(`/api/emotional-topology/distribution?${params}`)
          .then(r => r.json())
          .then(setDistribution)
      )
    } else if (view === 'characters') {
      fetchPromises.push(
        fetch(`/api/emotional-topology/characters?${params}`)
          .then(r => r.json())
          .then(setCharacters)
      )
    } else if (view === 'peaks') {
      params.set('threshold', '0.7')
      params.set('limit', '30')
      fetchPromises.push(
        fetch(`/api/emotional-topology/peaks?${params}`)
          .then(r => r.json())
          .then(setPeaks)
      )
    }

    Promise.all(fetchPromises)
      .then(() => setLoading(false))
      .catch(console.error)
  }, [view, book])

  // Draw terrain on canvas
  const drawTerrain = useCallback(() => {
    if (!canvasRef.current || terrain.length === 0) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const width = canvas.width
    const height = canvas.height
    const padding = 60

    // Clear with dark gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, height)
    gradient.addColorStop(0, '#0f172a')
    gradient.addColorStop(0.5, '#1e293b')
    gradient.addColorStop(1, '#0f172a')
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, width, height)

    // Draw grid lines (contour lines effect)
    ctx.strokeStyle = 'rgba(16, 185, 129, 0.1)'
    ctx.lineWidth = 1
    for (let y = padding; y < height - padding; y += 40) {
      ctx.beginPath()
      ctx.moveTo(padding, y)
      ctx.lineTo(width - padding, y)
      ctx.stroke()
    }

    if (terrain.length < 2) return

    // Calculate bounds
    const minX = Math.min(...terrain.map(p => p.x))
    const maxX = Math.max(...terrain.map(p => p.x))
    const xRange = maxX - minX || 1

    // Map terrain points to canvas coordinates
    const points = terrain.map(p => ({
      ...p,
      canvasX: padding + ((p.x - minX) / xRange) * (width - padding * 2),
      canvasY: height - padding - (p.y * (height - padding * 2)),
    }))

    // Draw the "mountain range" as a filled area
    ctx.beginPath()
    ctx.moveTo(points[0].canvasX, height - padding)
    points.forEach((p, i) => {
      if (i === 0) {
        ctx.lineTo(p.canvasX, p.canvasY)
      } else {
        // Smooth curve between points
        const prev = points[i - 1]
        const cpX = (prev.canvasX + p.canvasX) / 2
        ctx.quadraticCurveTo(prev.canvasX, prev.canvasY, cpX, (prev.canvasY + p.canvasY) / 2)
        if (i === points.length - 1) {
          ctx.lineTo(p.canvasX, p.canvasY)
        }
      }
    })
    ctx.lineTo(points[points.length - 1].canvasX, height - padding)
    ctx.closePath()

    // Gradient fill based on average polarity
    const terrainGradient = ctx.createLinearGradient(0, padding, 0, height - padding)
    terrainGradient.addColorStop(0, 'rgba(34, 197, 94, 0.6)')  // Peak: green (positive)
    terrainGradient.addColorStop(0.5, 'rgba(59, 130, 246, 0.4)')  // Middle: blue
    terrainGradient.addColorStop(1, 'rgba(30, 41, 59, 0.8)')  // Base: dark
    ctx.fillStyle = terrainGradient
    ctx.fill()

    // Draw peaks with emotion colors
    points.forEach((p, i) => {
      // Only draw significant points
      if (p.y > 0.6 || i % 5 === 0) {
        const color = EMOTION_COLORS[p.emotion] || '#94a3b8'
        const size = 4 + p.y * 8

        // Glow effect for high intensity
        if (p.y > 0.7) {
          ctx.beginPath()
          ctx.arc(p.canvasX, p.canvasY, size * 2, 0, Math.PI * 2)
          const glowGradient = ctx.createRadialGradient(
            p.canvasX, p.canvasY, 0,
            p.canvasX, p.canvasY, size * 2
          )
          glowGradient.addColorStop(0, color + '80')
          glowGradient.addColorStop(1, 'transparent')
          ctx.fillStyle = glowGradient
          ctx.fill()
        }

        // Point
        ctx.beginPath()
        ctx.arc(p.canvasX, p.canvasY, size, 0, Math.PI * 2)
        ctx.fillStyle = color
        ctx.fill()
      }
    })

    // Draw chapter boundaries
    let lastChapter = points[0]?.chapter
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)'
    ctx.setLineDash([5, 5])
    points.forEach(p => {
      if (p.chapter !== lastChapter) {
        ctx.beginPath()
        ctx.moveTo(p.canvasX, padding)
        ctx.lineTo(p.canvasX, height - padding)
        ctx.stroke()
        lastChapter = p.chapter
      }
    })
    ctx.setLineDash([])

    // Draw legend
    ctx.font = '12px "Plus Jakarta Sans", sans-serif'
    ctx.fillStyle = '#94a3b8'
    ctx.textAlign = 'left'
    ctx.fillText('Intensité', padding, padding - 10)
    ctx.textAlign = 'right'
    ctx.fillText('Progression narrative', width - padding, height - padding + 20)

    // Y-axis labels
    ctx.textAlign = 'right'
    ctx.fillText('1.0', padding - 10, padding + 5)
    ctx.fillText('0.5', padding - 10, height / 2)
    ctx.fillText('0.0', padding - 10, height - padding + 5)
  }, [terrain])

  // Redraw terrain when data changes
  useEffect(() => {
    if (view === 'terrain') {
      drawTerrain()
    }
  }, [view, terrain, drawTerrain])

  // Handle canvas click
  const handleCanvasClick = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current || terrain.length === 0) return

    const canvas = canvasRef.current
    const rect = canvas.getBoundingClientRect()
    const x = (e.clientX - rect.left) * (canvas.width / rect.width)
    const y = (e.clientY - rect.top) * (canvas.height / rect.height)

    const padding = 60
    const width = canvas.width
    const height = canvas.height

    const minX = Math.min(...terrain.map(p => p.x))
    const maxX = Math.max(...terrain.map(p => p.x))
    const xRange = maxX - minX || 1

    // Find nearest point
    let nearestPoint: TerrainPoint | null = null
    let minDist = Infinity

    terrain.forEach(p => {
      const canvasX = padding + ((p.x - minX) / xRange) * (width - padding * 2)
      const canvasY = height - padding - (p.y * (height - padding * 2))
      const dist = Math.sqrt((x - canvasX) ** 2 + (y - canvasY) ** 2)
      if (dist < minDist && dist < 30) {
        minDist = dist
        nearestPoint = p
      }
    })

    setSelectedPoint(nearestPoint)
  }, [terrain])

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0f172a] via-[#1e293b] to-[#0f172a] topo-lines">
      {/* Decorative gradient overlays */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 w-full h-64 bg-gradient-to-b from-emerald-900/10 to-transparent" />
        <div className="absolute bottom-0 left-0 w-full h-64 bg-gradient-to-t from-slate-900/50 to-transparent" />
      </div>

      {/* Header */}
      <header className="sticky top-0 z-30 backdrop-blur-md bg-[#0f172a]/80 border-b border-emerald-900/30">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={onBack}
              className="p-2.5 rounded-xl bg-slate-800/50 hover:bg-slate-800 border border-emerald-900/30 transition-all"
            >
              <ArrowLeft className="w-5 h-5 text-slate-300" />
            </button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-900/50">
                <Mountain className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-slate-100">Emotional Topology</h1>
                <p className="text-sm text-emerald-400/70">Terrain des émotions bibliques</p>
              </div>
            </div>
          </div>

          {/* View switcher */}
          <div className="flex items-center gap-3">
            <div className="flex gap-1 p-1 rounded-xl bg-slate-800/50 border border-emerald-900/30">
              {[
                { id: 'terrain' as ViewMode, icon: Waves, label: 'Terrain' },
                { id: 'distribution' as ViewMode, icon: BarChart3, label: 'Distribution' },
                { id: 'characters' as ViewMode, icon: Users, label: 'Personnages' },
                { id: 'peaks' as ViewMode, icon: TrendingUp, label: 'Sommets' },
              ].map(v => (
                <button
                  key={v.id}
                  onClick={() => setView(v.id)}
                  className={`
                    flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all
                    ${view === v.id
                      ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white'
                      : 'text-slate-400 hover:text-slate-200'}
                  `}
                >
                  <v.icon className="w-3.5 h-3.5" />
                  {v.label}
                </button>
              ))}
            </div>

            {/* Book filter */}
            <select
              value={book || ''}
              onChange={e => setBook(e.target.value || null)}
              className="px-3 py-2 rounded-lg bg-slate-800/50 border border-emerald-900/30 text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/50"
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
      <main className="max-w-6xl mx-auto px-6 py-8 relative z-10">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="flex flex-col items-center gap-4">
              <div className="w-12 h-12 rounded-full border-2 border-emerald-900/30 border-t-emerald-500 animate-spin" />
              <span className="text-emerald-400/70 text-sm">Cartographie du terrain émotionnel...</span>
            </div>
          </div>
        ) : (
          <>
            {/* Stats bar */}
            {stats && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                {[
                  { label: 'Versets analysés', value: stats.total_verses_analyzed, color: 'text-emerald-400' },
                  { label: 'Intensité moyenne', value: stats.avg_intensity.toFixed(2), color: 'text-amber-400' },
                  { label: 'Polarité moyenne', value: stats.avg_polarity.toFixed(2), color: 'text-blue-400' },
                  { label: 'Tension moyenne', value: stats.avg_tension.toFixed(2), color: 'text-rose-400' },
                ].map(stat => (
                  <div key={stat.label} className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/30">
                    <div className="text-xs text-slate-400 mb-1">{stat.label}</div>
                    <div className={`text-2xl font-bold mono ${stat.color}`}>{stat.value}</div>
                  </div>
                ))}
              </div>
            )}

            {/* Terrain View */}
            {view === 'terrain' && (
              <div className="space-y-6">
                {/* Emotion legend */}
                <div className="flex flex-wrap gap-2 p-4 rounded-xl bg-slate-800/30 border border-slate-700/30">
                  {Object.entries(EMOTION_COLORS).slice(0, 10).map(([emotion, color]) => (
                    <button
                      key={emotion}
                      onMouseEnter={() => setHoveredEmotion(emotion)}
                      onMouseLeave={() => setHoveredEmotion(null)}
                      className={`
                        flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all
                        ${hoveredEmotion === emotion ? 'ring-2 ring-white/30' : ''}
                      `}
                      style={{ backgroundColor: color + '30', color }}
                    >
                      <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                      {emotion}
                    </button>
                  ))}
                </div>

                {/* Canvas terrain */}
                <div className="relative">
                  <canvas
                    ref={canvasRef}
                    width={1200}
                    height={500}
                    onClick={handleCanvasClick}
                    className="w-full rounded-2xl border border-slate-700/30 cursor-crosshair"
                  />

                  {/* Selected point popup */}
                  {selectedPoint && (
                    <div className="absolute top-4 right-4 p-4 rounded-xl bg-slate-900/90 border border-slate-700/50 backdrop-blur-sm max-w-xs">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-sm font-medium text-slate-200">{selectedPoint.ref}</span>
                        <button
                          onClick={() => setSelectedPoint(null)}
                          className="text-slate-400 hover:text-slate-200"
                        >
                          &times;
                        </button>
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <span
                            className="px-2 py-0.5 rounded text-xs font-medium text-white"
                            style={{ backgroundColor: EMOTION_COLORS[selectedPoint.emotion] || '#94a3b8' }}
                          >
                            {selectedPoint.emotion}
                          </span>
                          {selectedPoint.secondary_emotion && (
                            <span className="text-xs text-slate-400">
                              + {selectedPoint.secondary_emotion}
                            </span>
                          )}
                        </div>
                        <div className="grid grid-cols-3 gap-2 text-xs">
                          <div>
                            <span className="text-slate-500">Intensité</span>
                            <div className="text-amber-400 font-medium">{selectedPoint.y.toFixed(2)}</div>
                          </div>
                          <div>
                            <span className="text-slate-500">Polarité</span>
                            <div className="text-blue-400 font-medium">{selectedPoint.polarity.toFixed(2)}</div>
                          </div>
                          <div>
                            <span className="text-slate-500">Tension</span>
                            <div className="text-rose-400 font-medium">{selectedPoint.z.toFixed(2)}</div>
                          </div>
                        </div>
                        {selectedPoint.text_preview && (
                          <p className="text-xs text-slate-400 hebrew text-right mt-2">
                            {selectedPoint.text_preview}...
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* Chapter overview */}
                {chapters.length > 0 && (
                  <div className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/30">
                    <h3 className="text-sm font-medium text-slate-200 mb-4">Apercu par chapitre</h3>
                    <div className="flex gap-1 h-20 items-end">
                      {chapters.map((ch, i) => (
                        <div
                          key={`${ch.book}-${ch.chapter}`}
                          className="flex-1 rounded-t transition-all hover:opacity-80"
                          style={{
                            height: `${ch.avg_intensity * 100}%`,
                            backgroundColor: ch.avg_polarity > 0 ? '#22c55e' : ch.avg_polarity < -0.2 ? '#ef4444' : '#3b82f6',
                            opacity: 0.3 + ch.avg_intensity * 0.7,
                          }}
                          title={`${ch.book} ${ch.chapter}: intensity=${ch.avg_intensity.toFixed(2)}`}
                        />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Distribution View */}
            {view === 'distribution' && (
              <div className="space-y-6">
                <div className="text-center mb-8">
                  <h2 className="text-2xl font-bold text-slate-100 mb-2">
                    Distribution des Emotions
                  </h2>
                  <p className="text-slate-400">
                    Fréquence et intensité moyenne de chaque émotion
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {distribution.map(item => {
                    const maxCount = distribution[0]?.count || 1
                    const percentage = (item.count / maxCount) * 100

                    return (
                      <div
                        key={item.emotion}
                        className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/30 hover:border-slate-600/50 transition-all"
                      >
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <span
                              className="w-4 h-4 rounded-full"
                              style={{ backgroundColor: item.color }}
                            />
                            <span className="font-medium text-slate-200 capitalize">{item.emotion}</span>
                          </div>
                          <span className="text-slate-400 text-sm mono">{item.count}</span>
                        </div>
                        <div className="h-3 bg-slate-900/50 rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all"
                            style={{
                              width: `${percentage}%`,
                              backgroundColor: item.color,
                            }}
                          />
                        </div>
                        <div className="mt-2 text-xs text-slate-500">
                          Intensité moyenne: <span style={{ color: item.color }}>{item.avg_intensity.toFixed(2)}</span>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Characters View */}
            {view === 'characters' && (
              <div className="space-y-6">
                <div className="text-center mb-8">
                  <h2 className="text-2xl font-bold text-slate-100 mb-2">
                    Emotions par Personnage
                  </h2>
                  <p className="text-slate-400">
                    Les protagonistes et leurs profils émotionnels
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {characters.map(char => {
                    const emotionEntries = Object.entries(char.emotions).sort((a, b) => b[1] - a[1])
                    const topEmotion = emotionEntries[0]

                    return (
                      <div
                        key={char.name}
                        className="p-5 rounded-xl bg-slate-800/30 border border-slate-700/30 hover:border-slate-600/50 transition-all"
                      >
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="font-semibold text-slate-100">{char.name}</h3>
                          <span className="text-xs text-slate-500 mono">{char.total} occurrences</span>
                        </div>

                        {/* Emotion bars */}
                        <div className="space-y-2">
                          {emotionEntries.slice(0, 4).map(([emotion, count]) => (
                            <div key={emotion} className="flex items-center gap-2">
                              <span className="text-xs text-slate-400 w-20 truncate capitalize">{emotion}</span>
                              <div className="flex-1 h-2 bg-slate-900/50 rounded-full overflow-hidden">
                                <div
                                  className="h-full rounded-full"
                                  style={{
                                    width: `${(count / char.total) * 100}%`,
                                    backgroundColor: EMOTION_COLORS[emotion] || '#94a3b8',
                                  }}
                                />
                              </div>
                              <span className="text-xs text-slate-500 w-6 text-right">{count}</span>
                            </div>
                          ))}
                        </div>

                        {/* Dominant emotion badge */}
                        {topEmotion && (
                          <div className="mt-4 pt-3 border-t border-slate-700/30">
                            <span className="text-xs text-slate-500">Emotion dominante: </span>
                            <span
                              className="text-xs font-medium capitalize"
                              style={{ color: EMOTION_COLORS[topEmotion[0]] || '#94a3b8' }}
                            >
                              {topEmotion[0]}
                            </span>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {/* Peaks View */}
            {view === 'peaks' && (
              <div className="space-y-6">
                <div className="text-center mb-8">
                  <h2 className="text-2xl font-bold text-slate-100 mb-2">
                    Sommets Emotionnels
                  </h2>
                  <p className="text-slate-400">
                    Les moments de plus haute intensité émotionnelle
                  </p>
                </div>

                <div className="space-y-4">
                  {peaks.map((peak, i) => (
                    <div
                      key={peak.verse_id}
                      className={`
                        p-5 rounded-xl border transition-all
                        ${i === 0
                          ? 'bg-gradient-to-r from-slate-800/50 to-slate-800/30 border-amber-500/30'
                          : 'bg-slate-800/30 border-slate-700/30 hover:border-slate-600/50'}
                      `}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-3">
                          {i === 0 && <Sparkles className="w-5 h-5 text-amber-400" />}
                          <span className="font-medium text-slate-100">{peak.ref}</span>
                          <span
                            className="px-2 py-0.5 rounded text-xs font-medium text-white"
                            style={{ backgroundColor: peak.color }}
                          >
                            {peak.emotion}
                          </span>
                        </div>
                        <div className="flex items-center gap-4 text-xs">
                          <div>
                            <span className="text-slate-500">Intensité: </span>
                            <span className="text-amber-400 font-medium mono">{peak.intensity?.toFixed(2)}</span>
                          </div>
                          <div>
                            <span className="text-slate-500">Tension: </span>
                            <span className="text-rose-400 font-medium mono">{peak.tension?.toFixed(2)}</span>
                          </div>
                        </div>
                      </div>

                      {peak.text_hebrew && (
                        <p className="text-slate-300 hebrew text-right text-lg leading-relaxed mb-2">
                          {peak.text_hebrew}
                        </p>
                      )}
                      {peak.text_english && (
                        <p className="text-slate-400 text-sm italic">
                          {peak.text_english}
                        </p>
                      )}
                      {peak.context && (
                        <p className="text-slate-500 text-xs mt-2">
                          {peak.context}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </main>

      {/* Stats footer */}
      <div className="fixed bottom-4 right-4 p-4 rounded-xl bg-slate-900/90 border border-slate-700/30 backdrop-blur-sm">
        <div className="flex items-center gap-6 text-sm">
          <div>
            <span className="text-slate-500">Livre: </span>
            <span className="text-emerald-400 font-medium">{book || 'Tous'}</span>
          </div>
          <div>
            <span className="text-slate-500">Max intensité: </span>
            <span className="text-amber-400 font-medium mono">{stats?.max_intensity.toFixed(2) || '-'}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
