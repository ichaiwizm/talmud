import { useState, useEffect } from 'react'
import {
  Telescope, Sparkles, ScrollText, Mountain, MessageCircle,
  Map, GitBranch, Layers, Building, Calculator, Workflow,
  Activity, Lock, ChevronRight, Database, BookOpen, Users, Hash
} from 'lucide-react'

const ICONS: Record<string, React.ElementType> = {
  star: Telescope, sparkles: Sparkles, scroll: ScrollText, mountain: Mountain,
  'message-circle': MessageCircle, map: Map, 'git-branch': GitBranch,
  layers: Layers, building: Building, calculator: Calculator,
  workflow: Workflow, activity: Activity
}

interface Interface {
  id: string
  name: string
  description: string
  icon: string
  color: string
  ready: boolean
}

interface Stats {
  verses: number
  books: number
  names: number
  divine_names: number
}

interface Props {
  stats: Stats | null
  onSelect: (id: string) => void
}

export default function Hub({ stats, onSelect }: Props) {
  const [interfaces, setInterfaces] = useState<Interface[]>([])
  const [hoveredId, setHoveredId] = useState<string | null>(null)
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    fetch('/api/stats/interfaces')
      .then(r => r.json())
      .then(data => {
        setInterfaces(data)
        setTimeout(() => setLoaded(true), 100)
      })
      .catch(console.error)
  }, [])

  const statItems = stats ? [
    { icon: BookOpen, label: 'Versets', value: stats.verses, color: '#60a5fa' },
    { icon: Database, label: 'Livres', value: stats.books, color: '#a78bfa' },
    { icon: Users, label: 'Entités', value: stats.names, color: '#34d399' },
    { icon: Hash, label: 'Noms Divins', value: stats.divine_names, color: '#fbbf24' },
  ] : []

  return (
    <div className="min-h-screen bg-void">
      {/* Subtle gradient background */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-accent/3 via-transparent to-transparent" />
        <div className="absolute bottom-0 right-0 w-1/2 h-1/2 bg-gradient-to-tl from-shaddai/3 via-transparent to-transparent" />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-6 py-12">
        {/* Header */}
        <header className="mb-16">
          <div
            className="opacity-0 animate-fade-in"
            style={{ animationDelay: '0ms' }}
          >
            <p className="text-subtle text-sm font-medium tracking-wide mb-2">
              Plateforme d'Analyse
            </p>
            <h1 className="text-4xl md:text-5xl font-bold text-bright tracking-tight mb-4">
              Torah Analysis
            </h1>
            <p className="text-subtle text-lg max-w-xl">
              Explorez les textes à travers 12 interfaces de visualisation uniques
            </p>
          </div>

          {/* Stats Row */}
          {stats && (
            <div
              className="flex flex-wrap gap-6 mt-10 opacity-0 animate-fade-in"
              style={{ animationDelay: '100ms' }}
            >
              {statItems.map((stat, i) => (
                <div
                  key={stat.label}
                  className="flex items-center gap-3 px-4 py-3 rounded-xl bg-surface/50 border border-muted/20"
                >
                  <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center"
                    style={{ backgroundColor: `${stat.color}15` }}
                  >
                    <stat.icon className="w-5 h-5" style={{ color: stat.color }} />
                  </div>
                  <div>
                    <div className="text-xl font-semibold text-bright mono">
                      {stat.value.toLocaleString()}
                    </div>
                    <div className="text-xs text-subtle">{stat.label}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </header>

        {/* Interface Grid */}
        <section>
          <div
            className="flex items-center justify-between mb-6 opacity-0 animate-fade-in"
            style={{ animationDelay: '200ms' }}
          >
            <h2 className="text-lg font-semibold text-text">
              Interfaces de Visualisation
            </h2>
            <span className="text-sm text-subtle">
              {interfaces.filter(i => i.ready).length} / {interfaces.length} disponibles
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {interfaces.map((iface, index) => {
              const Icon = ICONS[iface.icon] || Telescope
              const isHovered = hoveredId === iface.id
              const isReady = iface.ready

              return (
                <button
                  key={iface.id}
                  onClick={() => isReady && onSelect(iface.id)}
                  onMouseEnter={() => setHoveredId(iface.id)}
                  onMouseLeave={() => setHoveredId(null)}
                  disabled={!isReady}
                  className={`
                    group relative p-5 rounded-2xl text-left transition-all duration-300
                    opacity-0 animate-fade-in
                    ${isReady
                      ? 'bg-surface hover:bg-elevated cursor-pointer'
                      : 'bg-surface/30 cursor-not-allowed'
                    }
                  `}
                  style={{
                    animationDelay: `${300 + index * 50}ms`,
                    border: isHovered && isReady
                      ? `1px solid ${iface.color}40`
                      : '1px solid transparent'
                  }}
                >
                  {/* Top row: Icon + Status */}
                  <div className="flex items-start justify-between mb-4">
                    <div
                      className={`
                        w-12 h-12 rounded-xl flex items-center justify-center
                        transition-transform duration-300
                        ${isHovered && isReady ? 'scale-110' : ''}
                      `}
                      style={{
                        backgroundColor: isReady ? `${iface.color}15` : 'var(--color-muted)',
                        opacity: isReady ? 1 : 0.3
                      }}
                    >
                      <Icon
                        className="w-6 h-6"
                        style={{ color: isReady ? iface.color : 'var(--color-subtle)' }}
                      />
                    </div>

                    {!isReady ? (
                      <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-muted/30">
                        <Lock className="w-3 h-3 text-subtle" />
                        <span className="text-xs text-subtle">Bientôt</span>
                      </div>
                    ) : (
                      <div
                        className={`
                          flex items-center gap-1 px-2 py-1 rounded-full
                          transition-all duration-300
                          ${isHovered ? 'bg-accent/20 text-accent-bright' : 'bg-transparent text-subtle'}
                        `}
                      >
                        <span className="text-xs font-medium">Ouvrir</span>
                        <ChevronRight className={`w-3 h-3 transition-transform duration-300 ${isHovered ? 'translate-x-0.5' : ''}`} />
                      </div>
                    )}
                  </div>

                  {/* Title */}
                  <h3 className={`
                    font-semibold mb-1.5 transition-colors duration-300
                    ${isReady ? 'text-bright' : 'text-subtle'}
                  `}>
                    {iface.name}
                  </h3>

                  {/* Description */}
                  <p className={`
                    text-sm leading-relaxed
                    ${isReady ? 'text-subtle' : 'text-muted'}
                  `}>
                    {iface.description}
                  </p>

                  {/* Bottom accent line */}
                  {isReady && (
                    <div
                      className="absolute bottom-0 left-4 right-4 h-0.5 rounded-full transition-all duration-500"
                      style={{
                        background: isHovered
                          ? `linear-gradient(90deg, transparent, ${iface.color}, transparent)`
                          : 'transparent',
                        opacity: isHovered ? 1 : 0
                      }}
                    />
                  )}
                </button>
              )
            })}
          </div>
        </section>

        {/* Footer */}
        <footer className="mt-20 pt-8 border-t border-muted/20 text-center">
          <p className="text-sm text-muted">
            Torah Analysis • Visualisation de données textuelles
          </p>
        </footer>
      </div>
    </div>
  )
}
