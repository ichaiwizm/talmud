import { useState, useEffect, useRef, useCallback } from 'react'
import {
  ArrowLeft, Map, MapPin, Route, Users, Compass,
  Eye, EyeOff, Info
} from 'lucide-react'

// Journey figure colors
const FIGURE_COLORS: Record<string, string> = {
  Abraham: '#d4a853',
  Isaac: '#b87333',
  Jacob: '#4a90d9',
  Joseph: '#22c55e',
  Moses: '#ef4444',
  Israel: '#8b5cf6',
}

// Region colors for the map
const REGION_COLORS: Record<string, string> = {
  Mesopotamia: '#8b7355',
  Canaan: '#6b8e23',
  Egypt: '#daa520',
  Sinai: '#cd853f',
  'Trans-Jordan': '#a0522d',
  Arabia: '#d2691e',
  Unknown: '#708090',
}

interface Props {
  onBack: () => void
}

interface Location {
  id: number
  name: string
  name_hebrew: string | null
  description: string | null
  first_mention: string | null
  occurrence_count: number
  x: number | null
  y: number | null
  region: string
  has_coordinates: boolean
}

interface JourneyPoint {
  location_id: number
  location_name: string
  location_hebrew: string | null
  relationship: string
  verse_ref: string | null
  verse_id: number | null
  x: number | null
  y: number | null
  has_coordinates: boolean
}

interface Journey {
  figure: string
  figure_id: number
  color: string
  order: number
  point_count: number
  points: JourneyPoint[]
}

interface LocationEvent {
  id: number
  event_type: string
  description: string | null
  location: string | null
  location_hebrew: string | null
  verse_ref: string
  text_preview: string | null
  is_miraculous: boolean
  divine_involvement: string | null
  x: number | null
  y: number | null
}

interface Stats {
  total_locations: number
  locations_with_coords: number
  spatial_relationships: number
  journey_events: number
  located_events: number
  tracked_figures: number
}

type ViewMode = 'map' | 'journeys' | 'locations' | 'events'

export default function JourneyAtlas({ onBack }: Props) {
  const [view, setView] = useState<ViewMode>('map')
  const [locations, setLocations] = useState<Location[]>([])
  const [journeys, setJourneys] = useState<Journey[]>([])
  const [events, setEvents] = useState<LocationEvent[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null)
  const [visibleJourneys, setVisibleJourneys] = useState<Set<string>>(new Set(['Abraham', 'Jacob', 'Moses']))
  const [hoveredLocation, setHoveredLocation] = useState<string | null>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  // Load data
  useEffect(() => {
    setLoading(true)

    Promise.all([
      fetch('/api/journey-atlas/locations').then(r => r.json()),
      fetch('/api/journey-atlas/journeys').then(r => r.json()),
      fetch('/api/journey-atlas/events?limit=50').then(r => r.json()),
      fetch('/api/journey-atlas/stats').then(r => r.json()),
    ]).then(([locData, journeyData, eventData, statsData]) => {
      setLocations(locData)
      setJourneys(journeyData)
      setEvents(eventData)
      setStats(statsData)
      setLoading(false)
    }).catch(console.error)
  }, [])

  // Draw map on canvas
  const drawMap = useCallback(() => {
    if (!canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const width = canvas.width
    const height = canvas.height

    // Clear with parchment-like background
    const bgGradient = ctx.createLinearGradient(0, 0, width, height)
    bgGradient.addColorStop(0, '#2a2520')
    bgGradient.addColorStop(0.5, '#352f28')
    bgGradient.addColorStop(1, '#1f1b18')
    ctx.fillStyle = bgGradient
    ctx.fillRect(0, 0, width, height)

    // Draw subtle grid
    ctx.strokeStyle = 'rgba(139, 115, 85, 0.1)'
    ctx.lineWidth = 1
    for (let x = 0; x < width; x += 50) {
      ctx.beginPath()
      ctx.moveTo(x, 0)
      ctx.lineTo(x, height)
      ctx.stroke()
    }
    for (let y = 0; y < height; y += 50) {
      ctx.beginPath()
      ctx.moveTo(0, y)
      ctx.lineTo(width, y)
      ctx.stroke()
    }

    // Draw region labels
    const regions = [
      { name: 'Mesopotamia', x: 78, y: 35 },
      { name: 'Canaan', x: 45, y: 50 },
      { name: 'Egypt', x: 30, y: 68 },
      { name: 'Sinai', x: 40, y: 78 },
    ]

    ctx.font = 'italic 14px "Plus Jakarta Sans", sans-serif'
    ctx.fillStyle = 'rgba(139, 115, 85, 0.5)'
    regions.forEach(region => {
      const x = (region.x / 100) * width
      const y = (region.y / 100) * height
      ctx.fillText(region.name, x, y)
    })

    // Draw journey paths
    journeys.forEach(journey => {
      if (!visibleJourneys.has(journey.figure)) return

      const points = journey.points.filter(p => p.x !== null && p.y !== null)
      if (points.length < 2) return

      ctx.beginPath()
      ctx.strokeStyle = journey.color
      ctx.lineWidth = 3
      ctx.setLineDash([10, 5])

      points.forEach((point, i) => {
        const x = (point.x! / 100) * width
        const y = (point.y! / 100) * height

        if (i === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
      })
      ctx.stroke()
      ctx.setLineDash([])

      // Draw arrowheads at journey points
      points.forEach((point, i) => {
        if (i === 0) return
        const prev = points[i - 1]
        const x = (point.x! / 100) * width
        const y = (point.y! / 100) * height
        const px = (prev.x! / 100) * width
        const py = (prev.y! / 100) * height

        const angle = Math.atan2(y - py, x - px)
        const arrowSize = 8

        ctx.beginPath()
        ctx.moveTo(x, y)
        ctx.lineTo(
          x - arrowSize * Math.cos(angle - Math.PI / 6),
          y - arrowSize * Math.sin(angle - Math.PI / 6)
        )
        ctx.lineTo(
          x - arrowSize * Math.cos(angle + Math.PI / 6),
          y - arrowSize * Math.sin(angle + Math.PI / 6)
        )
        ctx.closePath()
        ctx.fillStyle = journey.color
        ctx.fill()
      })
    })

    // Draw location markers
    const locationsWithCoords = locations.filter(l => l.x !== null && l.y !== null)

    locationsWithCoords.forEach(location => {
      const x = (location.x! / 100) * width
      const y = (location.y! / 100) * height
      const isHovered = hoveredLocation === location.name
      const isSelected = selectedLocation?.id === location.id

      // Size based on occurrence count
      const baseSize = 6 + Math.min(location.occurrence_count / 5, 8)
      const size = isHovered || isSelected ? baseSize * 1.3 : baseSize

      // Glow for hovered/selected
      if (isHovered || isSelected) {
        const glowGradient = ctx.createRadialGradient(x, y, 0, x, y, size * 2)
        glowGradient.addColorStop(0, 'rgba(212, 168, 83, 0.6)')
        glowGradient.addColorStop(1, 'transparent')
        ctx.beginPath()
        ctx.arc(x, y, size * 2, 0, Math.PI * 2)
        ctx.fillStyle = glowGradient
        ctx.fill()
      }

      // Marker
      ctx.beginPath()
      ctx.arc(x, y, size, 0, Math.PI * 2)
      ctx.fillStyle = REGION_COLORS[location.region] || '#8b7355'
      ctx.fill()
      ctx.strokeStyle = '#d4a853'
      ctx.lineWidth = 2
      ctx.stroke()

      // Label for significant locations
      if (location.occurrence_count > 5 || isHovered || isSelected) {
        ctx.font = `${isHovered || isSelected ? 'bold ' : ''}12px "Plus Jakarta Sans", sans-serif`
        ctx.fillStyle = isHovered || isSelected ? '#d4a853' : '#a89070'
        ctx.textAlign = 'center'
        ctx.fillText(location.name, x, y - size - 5)
      }
    })

    // Draw compass rose
    const compassX = width - 60
    const compassY = height - 60
    const compassSize = 40

    ctx.save()
    ctx.translate(compassX, compassY)

    // Compass circle
    ctx.beginPath()
    ctx.arc(0, 0, compassSize, 0, Math.PI * 2)
    ctx.strokeStyle = 'rgba(139, 115, 85, 0.5)'
    ctx.lineWidth = 2
    ctx.stroke()

    // N/S/E/W
    ctx.font = 'bold 12px "Plus Jakarta Sans", sans-serif'
    ctx.fillStyle = '#8b7355'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText('N', 0, -compassSize + 12)
    ctx.fillText('S', 0, compassSize - 12)
    ctx.fillText('E', compassSize - 12, 0)
    ctx.fillText('W', -compassSize + 12, 0)

    ctx.restore()

    // Title cartouche
    ctx.fillStyle = 'rgba(42, 37, 32, 0.9)'
    ctx.fillRect(20, 20, 200, 50)
    ctx.strokeStyle = '#8b7355'
    ctx.lineWidth = 2
    ctx.strokeRect(20, 20, 200, 50)

    ctx.font = 'bold 18px "Plus Jakarta Sans", sans-serif'
    ctx.fillStyle = '#d4a853'
    ctx.textAlign = 'left'
    ctx.fillText('Biblical Journeys', 35, 50)
  }, [locations, journeys, visibleJourneys, hoveredLocation, selectedLocation])

  // Redraw when data changes
  useEffect(() => {
    if (view === 'map' && !loading) {
      drawMap()
    }
  }, [view, loading, drawMap])

  // Handle canvas click
  const handleCanvasClick = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current) return

    const canvas = canvasRef.current
    const rect = canvas.getBoundingClientRect()
    const x = ((e.clientX - rect.left) / rect.width) * 100
    const y = ((e.clientY - rect.top) / rect.height) * 100

    // Find nearest location
    let nearest: Location | null = null
    let minDist = Infinity

    locations.forEach(loc => {
      if (loc.x === null || loc.y === null) return
      const dist = Math.sqrt((x - loc.x) ** 2 + (y - loc.y) ** 2)
      if (dist < minDist && dist < 5) {
        minDist = dist
        nearest = loc
      }
    })

    setSelectedLocation(nearest)
  }, [locations])

  // Handle canvas mouse move
  const handleCanvasMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current) return

    const canvas = canvasRef.current
    const rect = canvas.getBoundingClientRect()
    const x = ((e.clientX - rect.left) / rect.width) * 100
    const y = ((e.clientY - rect.top) / rect.height) * 100

    let hovered: string | null = null

    locations.forEach(loc => {
      if (loc.x === null || loc.y === null) return
      const dist = Math.sqrt((x - loc.x) ** 2 + (y - loc.y) ** 2)
      if (dist < 5) {
        hovered = loc.name
      }
    })

    setHoveredLocation(hovered)
  }, [locations])

  // Toggle journey visibility
  const toggleJourney = (figure: string) => {
    setVisibleJourneys(prev => {
      const next = new Set(prev)
      if (next.has(figure)) {
        next.delete(figure)
      } else {
        next.add(figure)
      }
      return next
    })
  }

  return (
    <div className="min-h-screen parchment-bg parchment-texture">
      {/* Decorative corners */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 w-32 h-32 bg-gradient-to-br from-amber-900/20 to-transparent" />
        <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-amber-900/20 to-transparent" />
        <div className="absolute bottom-0 left-0 w-32 h-32 bg-gradient-to-tr from-amber-900/20 to-transparent" />
        <div className="absolute bottom-0 right-0 w-32 h-32 bg-gradient-to-tl from-amber-900/20 to-transparent" />
      </div>

      {/* Header */}
      <header className="sticky top-0 z-30 backdrop-blur-md bg-[#2a2520]/80 border-b border-amber-900/30">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={onBack}
              className="p-2.5 rounded-xl bg-amber-900/30 hover:bg-amber-900/50 border border-amber-700/30 transition-all"
            >
              <ArrowLeft className="w-5 h-5 text-amber-200/70" />
            </button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-600 to-amber-800 flex items-center justify-center shadow-lg shadow-amber-900/50">
                <Map className="w-5 h-5 text-amber-100" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-amber-100">Journey Atlas</h1>
                <p className="text-sm text-amber-500/70">Carte des voyages patriarcaux</p>
              </div>
            </div>
          </div>

          {/* View switcher */}
          <div className="flex items-center gap-3">
            <div className="flex gap-1 p-1 rounded-xl bg-amber-900/30 border border-amber-700/30">
              {[
                { id: 'map' as ViewMode, icon: Compass, label: 'Carte' },
                { id: 'journeys' as ViewMode, icon: Route, label: 'Voyages' },
                { id: 'locations' as ViewMode, icon: MapPin, label: 'Lieux' },
                { id: 'events' as ViewMode, icon: Info, label: 'Événements' },
              ].map(v => (
                <button
                  key={v.id}
                  onClick={() => setView(v.id)}
                  className={`
                    flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all
                    ${view === v.id
                      ? 'bg-gradient-to-r from-amber-600 to-amber-700 text-white'
                      : 'text-amber-300/60 hover:text-amber-200'}
                  `}
                >
                  <v.icon className="w-3.5 h-3.5" />
                  {v.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-6xl mx-auto px-6 py-8 relative z-10">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="flex flex-col items-center gap-4">
              <Compass className="w-12 h-12 text-amber-500 animate-compass" />
              <span className="text-amber-400/70 text-sm">Préparation de l'atlas...</span>
            </div>
          </div>
        ) : (
          <>
            {/* Map View */}
            {view === 'map' && (
              <div className="space-y-6">
                {/* Journey toggles */}
                <div className="flex flex-wrap gap-2 p-4 rounded-xl bg-amber-900/20 border border-amber-800/30">
                  <span className="text-sm text-amber-400/70 mr-2">Voyages:</span>
                  {journeys.map(j => (
                    <button
                      key={j.figure}
                      onClick={() => toggleJourney(j.figure)}
                      className={`
                        flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all
                        ${visibleJourneys.has(j.figure)
                          ? 'ring-2 ring-white/30'
                          : 'opacity-50'}
                      `}
                      style={{
                        backgroundColor: j.color + '30',
                        color: j.color,
                      }}
                    >
                      {visibleJourneys.has(j.figure) ? (
                        <Eye className="w-3 h-3" />
                      ) : (
                        <EyeOff className="w-3 h-3" />
                      )}
                      {j.figure}
                    </button>
                  ))}
                </div>

                {/* Canvas map */}
                <div className="relative">
                  <canvas
                    ref={canvasRef}
                    width={1200}
                    height={700}
                    onClick={handleCanvasClick}
                    onMouseMove={handleCanvasMouseMove}
                    className="w-full rounded-xl map-border cursor-crosshair"
                  />

                  {/* Selected location popup */}
                  {selectedLocation && (
                    <div className="absolute top-4 right-4 p-4 rounded-xl bg-[#2a2520]/95 border border-amber-700/50 backdrop-blur-sm max-w-xs">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <MapPin className="w-4 h-4 text-amber-500" />
                          <span className="font-medium text-amber-100">{selectedLocation.name}</span>
                        </div>
                        <button
                          onClick={() => setSelectedLocation(null)}
                          className="text-amber-400 hover:text-amber-200"
                        >
                          &times;
                        </button>
                      </div>
                      {selectedLocation.name_hebrew && (
                        <p className="text-lg hebrew text-amber-300/80 mb-2">{selectedLocation.name_hebrew}</p>
                      )}
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-amber-500/70">Région:</span>
                          <span className="text-amber-200">{selectedLocation.region}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-amber-500/70">Mentions:</span>
                          <span className="text-amber-200 mono">{selectedLocation.occurrence_count}</span>
                        </div>
                        {selectedLocation.first_mention && (
                          <div className="flex justify-between">
                            <span className="text-amber-500/70">Première mention:</span>
                            <span className="text-amber-200">{selectedLocation.first_mention}</span>
                          </div>
                        )}
                      </div>
                      {selectedLocation.description && (
                        <p className="text-xs text-amber-400/60 mt-3 pt-3 border-t border-amber-800/30">
                          {selectedLocation.description}
                        </p>
                      )}
                    </div>
                  )}
                </div>

                {/* Stats */}
                {stats && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {[
                      { label: 'Lieux bibliques', value: stats.total_locations },
                      { label: 'Avec coordonnées', value: stats.locations_with_coords },
                      { label: 'Relations spatiales', value: stats.spatial_relationships },
                      { label: 'Figures suivies', value: stats.tracked_figures },
                    ].map(stat => (
                      <div key={stat.label} className="p-4 rounded-xl bg-amber-900/20 border border-amber-800/30">
                        <div className="text-xs text-amber-500/70 mb-1">{stat.label}</div>
                        <div className="text-2xl font-bold text-amber-400 mono">{stat.value}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Journeys View */}
            {view === 'journeys' && (
              <div className="space-y-6">
                <div className="text-center mb-8">
                  <h2 className="text-2xl font-bold text-amber-100 mb-2">
                    Voyages des Patriarches
                  </h2>
                  <p className="text-amber-400/60">
                    Les itinéraires des figures majeures de la Torah
                  </p>
                </div>

                <div className="space-y-6">
                  {journeys.map(journey => (
                    <div
                      key={journey.figure}
                      className="p-5 rounded-xl bg-amber-900/20 border border-amber-800/30"
                    >
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <div
                            className="w-4 h-4 rounded-full"
                            style={{ backgroundColor: journey.color }}
                          />
                          <h3 className="text-lg font-semibold text-amber-100">{journey.figure}</h3>
                        </div>
                        <span className="text-sm text-amber-500/70">
                          {journey.point_count} étapes
                        </span>
                      </div>

                      {/* Journey timeline */}
                      <div className="relative pl-6 space-y-3">
                        <div
                          className="absolute left-2 top-0 bottom-0 w-0.5"
                          style={{ backgroundColor: journey.color + '50' }}
                        />

                        {journey.points.slice(0, 10).map((point, i) => (
                          <div key={i} className="relative">
                            <div
                              className="absolute -left-4 w-3 h-3 rounded-full border-2"
                              style={{
                                backgroundColor: '#2a2520',
                                borderColor: journey.color,
                              }}
                            />
                            <div className="flex items-center justify-between">
                              <div>
                                <span className="text-amber-200">{point.location_name}</span>
                                {point.location_hebrew && (
                                  <span className="text-amber-400/60 hebrew text-sm ml-2">
                                    {point.location_hebrew}
                                  </span>
                                )}
                              </div>
                              <span className="text-xs text-amber-500/50 capitalize">
                                {point.relationship.replace('_', ' ')}
                              </span>
                            </div>
                            {point.verse_ref && (
                              <span className="text-xs text-amber-500/40">{point.verse_ref}</span>
                            )}
                          </div>
                        ))}

                        {journey.points.length > 10 && (
                          <div className="text-xs text-amber-500/50 pl-2">
                            ... et {journey.points.length - 10} autres étapes
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Locations View */}
            {view === 'locations' && (
              <div className="space-y-6">
                <div className="text-center mb-8">
                  <h2 className="text-2xl font-bold text-amber-100 mb-2">
                    Lieux Bibliques
                  </h2>
                  <p className="text-amber-400/60">
                    Tous les lieux mentionnés dans la Torah
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {locations.slice(0, 30).map(location => (
                    <div
                      key={location.id}
                      className="p-4 rounded-xl bg-amber-900/20 border border-amber-800/30 hover:border-amber-600/50 transition-all cursor-pointer"
                      onClick={() => setSelectedLocation(location)}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <MapPin
                            className="w-4 h-4"
                            style={{ color: REGION_COLORS[location.region] || '#8b7355' }}
                          />
                          <span className="font-medium text-amber-100">{location.name}</span>
                        </div>
                        <span className="text-xs px-2 py-0.5 rounded-full bg-amber-800/30 text-amber-300/70">
                          {location.region}
                        </span>
                      </div>

                      {location.name_hebrew && (
                        <p className="text-sm hebrew text-amber-400/70 mb-2">{location.name_hebrew}</p>
                      )}

                      <div className="flex items-center justify-between text-xs">
                        <span className="text-amber-500/50">
                          {location.occurrence_count} mentions
                        </span>
                        {location.first_mention && (
                          <span className="text-amber-500/50">{location.first_mention}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Events View */}
            {view === 'events' && (
              <div className="space-y-6">
                <div className="text-center mb-8">
                  <h2 className="text-2xl font-bold text-amber-100 mb-2">
                    Événements Localisés
                  </h2>
                  <p className="text-amber-400/60">
                    Les événements majeurs et leur localisation
                  </p>
                </div>

                <div className="space-y-3">
                  {events.map(event => (
                    <div
                      key={event.id}
                      className={`
                        p-4 rounded-xl border transition-all
                        ${event.is_miraculous
                          ? 'bg-gradient-to-r from-amber-900/30 to-amber-800/20 border-amber-500/30'
                          : 'bg-amber-900/20 border-amber-800/30'}
                      `}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-3">
                          <span className="px-2 py-1 rounded text-xs font-medium bg-amber-800/50 text-amber-200 capitalize">
                            {event.event_type.replace('_', ' ')}
                          </span>
                          {event.is_miraculous && (
                            <span className="text-amber-500 text-xs">Miraculeux</span>
                          )}
                        </div>
                        <span className="text-xs text-amber-500/60">{event.verse_ref}</span>
                      </div>

                      {event.description && (
                        <p className="text-amber-200/80 text-sm mb-2">{event.description}</p>
                      )}

                      {event.location && (
                        <div className="flex items-center gap-2 text-xs text-amber-500/70">
                          <MapPin className="w-3 h-3" />
                          <span>{event.location}</span>
                          {event.location_hebrew && (
                            <span className="hebrew">{event.location_hebrew}</span>
                          )}
                        </div>
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
      {stats && (
        <div className="fixed bottom-4 right-4 p-4 rounded-xl bg-[#2a2520]/90 border border-amber-800/30 backdrop-blur-sm">
          <div className="flex items-center gap-6 text-sm">
            <div>
              <span className="text-amber-500/50">Lieux: </span>
              <span className="text-amber-400 font-medium mono">{stats.total_locations}</span>
            </div>
            <div>
              <span className="text-amber-500/50">Voyages: </span>
              <span className="text-amber-400 font-medium mono">{journeys.length}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
