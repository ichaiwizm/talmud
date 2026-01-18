import { useState, useEffect, useMemo } from 'react'
import { ArrowLeft, Telescope, Filter, BarChart3, PieChart, Grid3X3 } from 'lucide-react'

const NAME_CONFIG: Record<string, { color: string; hebrew: string; label: string }> = {
  yhwh: { color: '#3b82f6', hebrew: 'יהוה', label: 'YHWH' },
  elohim: { color: '#eab308', hebrew: 'אלהים', label: 'Elohim' },
  el_shaddai: { color: '#a855f7', hebrew: 'אל שדי', label: 'El Shaddai' },
  el_elyon: { color: '#22c55e', hebrew: 'אל עליון', label: 'El Elyon' },
  adonai: { color: '#ec4899', hebrew: 'אדני', label: 'Adonai' },
  el: { color: '#f97316', hebrew: 'אל', label: 'El' },
  ehyeh: { color: '#06b6d4', hebrew: 'אהיה', label: 'Ehyeh' },
  other: { color: '#6b7280', hebrew: 'אחר', label: 'Autre' }
}

const BOOKS = ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy']
const CONTEXTS = ['creation', 'covenant', 'judgment', 'mercy', 'revelation', 'blessing', 'command', 'narrative']
const CONTEXT_LABELS: Record<string, string> = {
  creation: 'Création', covenant: 'Alliance', judgment: 'Jugement', mercy: 'Miséricorde',
  revelation: 'Révélation', blessing: 'Bénédiction', command: 'Commandement', narrative: 'Récit'
}

interface Props {
  onBack: () => void
}

export default function DivineObservatory({ onBack }: Props) {
  const [distribution, setDistribution] = useState<Record<string, Record<string, number>>>({})
  const [byContext, setByContext] = useState<Record<string, Record<string, number>>>({})
  const [selectedName, setSelectedName] = useState<string | null>(null)
  const [view, setView] = useState<'bars' | 'rings' | 'grid'>('bars')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      fetch('/api/divine-names/distribution').then(r => r.json()),
      fetch('/api/divine-names/by-context').then(r => r.json())
    ]).then(([dist, ctx]) => {
      setDistribution(dist)
      setByContext(ctx)
      setLoading(false)
    }).catch(console.error)
  }, [])

  const totals = useMemo(() => {
    const result: Record<string, number> = {}
    for (const book of BOOKS) {
      for (const name of Object.keys(NAME_CONFIG)) {
        result[name] = (result[name] || 0) + (distribution[book]?.[name] || 0)
      }
    }
    return result
  }, [distribution])

  const grandTotal = Object.values(totals).reduce((a, b) => a + b, 0)
  const maxTotal = Math.max(...Object.values(totals), 1)
  const activeNames = Object.keys(NAME_CONFIG).filter(n => totals[n] > 0)

  return (
    <div className="min-h-screen" style={{ background: 'linear-gradient(180deg, #0a0a1a 0%, #0f0f2a 50%, #0a0a1a 100%)' }}>
      {/* Starfield background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {[...Array(100)].map((_, i) => (
          <div
            key={i}
            className="absolute rounded-full"
            style={{
              width: Math.random() > 0.9 ? '2px' : '1px',
              height: Math.random() > 0.9 ? '2px' : '1px',
              background: `rgba(255,255,255,${0.2 + Math.random() * 0.5})`,
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animation: `pulse-glow ${2 + Math.random() * 3}s ease-in-out infinite`,
              animationDelay: `${Math.random() * 2}s`
            }}
          />
        ))}
        {/* Nebula effects */}
        <div className="absolute top-0 right-0 w-[600px] h-[600px] rounded-full opacity-20"
          style={{ background: 'radial-gradient(circle, #3b82f620 0%, transparent 70%)' }} />
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] rounded-full opacity-15"
          style={{ background: 'radial-gradient(circle, #a855f720 0%, transparent 70%)' }} />
      </div>

      {/* Header */}
      <header className="relative z-10 flex items-center justify-between p-4 border-b border-white/5">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 transition-all"
          >
            <ArrowLeft className="w-5 h-5 text-white/70" />
          </button>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center">
              <Telescope className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-white">Observatoire des Noms</h1>
              <p className="text-sm text-white/40">Distribution dans la Torah</p>
            </div>
          </div>
        </div>

        {/* View switcher */}
        <div className="flex gap-1 p-1 rounded-xl bg-white/5 border border-white/10">
          {[
            { id: 'bars', icon: BarChart3, label: 'Barres' },
            { id: 'rings', icon: PieChart, label: 'Anneaux' },
            { id: 'grid', icon: Grid3X3, label: 'Grille' },
          ].map(v => (
            <button
              key={v.id}
              onClick={() => setView(v.id as typeof view)}
              className={`p-2 rounded-lg transition-all ${view === v.id ? 'bg-white/10 text-white' : 'text-white/40 hover:text-white/70'}`}
              title={v.label}
            >
              <v.icon className="w-4 h-4" />
            </button>
          ))}
        </div>
      </header>

      {loading ? (
        <div className="flex items-center justify-center h-96">
          <div className="flex flex-col items-center gap-4">
            <div className="w-12 h-12 rounded-full border-2 border-blue-500/30 border-t-blue-500 animate-spin" />
            <span className="text-white/50 text-sm">Chargement des données...</span>
          </div>
        </div>
      ) : (
        <main className="relative z-10 p-6 max-w-7xl mx-auto space-y-8">
          {/* Name selector - Orbital style */}
          <section className="flex flex-wrap justify-center gap-3">
            {activeNames.map((name, i) => {
              const cfg = NAME_CONFIG[name]
              const isSelected = selectedName === name
              const isActive = !selectedName || isSelected

              return (
                <button
                  key={name}
                  onClick={() => setSelectedName(isSelected ? null : name)}
                  className={`
                    group relative flex items-center gap-2.5 px-4 py-2.5 rounded-full
                    border transition-all duration-300
                    ${isActive ? 'opacity-100' : 'opacity-30'}
                  `}
                  style={{
                    borderColor: isSelected ? cfg.color : 'rgba(255,255,255,0.1)',
                    backgroundColor: isSelected ? `${cfg.color}15` : 'rgba(255,255,255,0.03)'
                  }}
                >
                  <span
                    className="w-3 h-3 rounded-full transition-transform duration-300 group-hover:scale-125"
                    style={{ backgroundColor: cfg.color, boxShadow: `0 0 10px ${cfg.color}50` }}
                  />
                  <span className="hebrew text-base" style={{ color: isActive ? cfg.color : '#ffffff50' }}>
                    {cfg.hebrew}
                  </span>
                  <span className="mono text-xs text-white/40 tabular-nums">
                    {totals[name].toLocaleString()}
                  </span>
                </button>
              )
            })}
          </section>

          {/* Main visualization */}
          {view === 'bars' && (
            <section className="p-6 rounded-2xl bg-white/[0.02] border border-white/5">
              <h2 className="text-sm font-medium text-white/50 mb-6 flex items-center gap-2">
                <BarChart3 className="w-4 h-4" />
                Distribution par Livre
              </h2>
              <div className="space-y-5">
                {BOOKS.map(book => {
                  const bookData = distribution[book] || {}
                  const bookTotal = Object.values(bookData).reduce((a, b) => a + b, 0)

                  return (
                    <div key={book} className="group">
                      <div className="flex items-baseline justify-between mb-2">
                        <span className="text-white/80 font-medium">{book}</span>
                        <span className="mono text-xs text-white/30">{bookTotal.toLocaleString()}</span>
                      </div>
                      <div className="relative h-10 rounded-lg bg-white/5 overflow-hidden">
                        <div className="absolute inset-0 flex">
                          {activeNames.map(name => {
                            const count = bookData[name] || 0
                            if (count === 0) return null
                            if (selectedName && selectedName !== name) return null
                            const width = (count / bookTotal) * 100
                            const cfg = NAME_CONFIG[name]

                            return (
                              <div
                                key={name}
                                className="h-full relative group/bar transition-all duration-500"
                                style={{
                                  width: `${width}%`,
                                  backgroundColor: cfg.color,
                                  minWidth: '4px'
                                }}
                              >
                                <div className="absolute inset-0 bg-white/0 hover:bg-white/20 transition-colors" />
                                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2.5 py-1.5 rounded-lg bg-black/90 text-xs text-white whitespace-nowrap opacity-0 group-hover/bar:opacity-100 transition-opacity pointer-events-none z-10 border border-white/10">
                                  <span className="hebrew">{cfg.hebrew}</span>
                                  <span className="text-white/50 ml-2">{count}</span>
                                </div>
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </section>
          )}

          {view === 'rings' && (
            <section className="p-6 rounded-2xl bg-white/[0.02] border border-white/5">
              <h2 className="text-sm font-medium text-white/50 mb-6 flex items-center gap-2">
                <PieChart className="w-4 h-4" />
                Vue Orbitale
              </h2>
              <div className="flex justify-center py-8">
                <div className="relative w-80 h-80">
                  {/* Orbital rings */}
                  {[1, 2, 3].map(ring => (
                    <div
                      key={ring}
                      className="absolute inset-0 rounded-full border border-white/5"
                      style={{ transform: `scale(${0.4 + ring * 0.2})` }}
                    />
                  ))}
                  {/* Center */}
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-20 h-20 rounded-full bg-gradient-to-br from-blue-500/30 to-purple-500/30 flex items-center justify-center border border-white/10">
                    <span className="mono text-lg font-bold text-white">{grandTotal.toLocaleString()}</span>
                  </div>
                  {/* Name planets */}
                  {activeNames.slice(0, 7).map((name, i) => {
                    const cfg = NAME_CONFIG[name]
                    const angle = (i / 7) * Math.PI * 2 - Math.PI / 2
                    const radius = 120
                    const x = Math.cos(angle) * radius
                    const y = Math.sin(angle) * radius
                    const size = 20 + (totals[name] / maxTotal) * 30
                    const isActive = !selectedName || selectedName === name

                    return (
                      <button
                        key={name}
                        onClick={() => setSelectedName(selectedName === name ? null : name)}
                        className={`absolute transition-all duration-500 ${isActive ? 'opacity-100' : 'opacity-20'}`}
                        style={{
                          left: `calc(50% + ${x}px - ${size / 2}px)`,
                          top: `calc(50% + ${y}px - ${size / 2}px)`,
                          width: size,
                          height: size
                        }}
                      >
                        <div
                          className="w-full h-full rounded-full flex items-center justify-center transition-transform hover:scale-110"
                          style={{
                            backgroundColor: cfg.color,
                            boxShadow: `0 0 20px ${cfg.color}60`
                          }}
                        >
                          <span className="hebrew text-[10px] text-white font-medium">{cfg.hebrew.charAt(0)}</span>
                        </div>
                      </button>
                    )
                  })}
                </div>
              </div>
              {/* Legend below */}
              <div className="flex flex-wrap justify-center gap-4 mt-4">
                {activeNames.map(name => {
                  const cfg = NAME_CONFIG[name]
                  return (
                    <div key={name} className="flex items-center gap-2 text-xs">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: cfg.color }} />
                      <span className="text-white/60">{cfg.label}</span>
                      <span className="mono text-white/30">{Math.round((totals[name] / grandTotal) * 100)}%</span>
                    </div>
                  )
                })}
              </div>
            </section>
          )}

          {view === 'grid' && (
            <section className="p-6 rounded-2xl bg-white/[0.02] border border-white/5">
              <h2 className="text-sm font-medium text-white/50 mb-6 flex items-center gap-2">
                <Grid3X3 className="w-4 h-4" />
                Distribution par Contexte
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {CONTEXTS.map(ctx => {
                  const ctxData = byContext[ctx] || {}
                  const ctxTotal = Object.values(ctxData).reduce((a, b) => a + b, 0)
                  if (ctxTotal === 0) return null

                  return (
                    <div
                      key={ctx}
                      className="p-4 rounded-xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-colors"
                    >
                      <h3 className="text-sm text-white/60 mb-3">{CONTEXT_LABELS[ctx]}</h3>
                      <div className="space-y-2">
                        {activeNames
                          .filter(n => ctxData[n] > 0)
                          .sort((a, b) => (ctxData[b] || 0) - (ctxData[a] || 0))
                          .slice(0, 3)
                          .map(name => {
                            const cfg = NAME_CONFIG[name]
                            const count = ctxData[name] || 0
                            const pct = (count / ctxTotal) * 100

                            return (
                              <div key={name} className="flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: cfg.color }} />
                                <span className="text-xs text-white/50 flex-1 truncate">{cfg.label}</span>
                                <span className="mono text-xs text-white/30">{count}</span>
                              </div>
                            )
                          })}
                      </div>
                      <div className="mt-3 pt-3 border-t border-white/5">
                        <span className="mono text-sm font-medium text-white/70">{ctxTotal}</span>
                        <span className="text-xs text-white/30 ml-1">total</span>
                      </div>
                    </div>
                  )
                })}
              </div>
            </section>
          )}

          {/* Summary cards */}
          <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {activeNames.slice(0, 4).map(name => {
              const cfg = NAME_CONFIG[name]
              const count = totals[name]
              const pct = Math.round((count / grandTotal) * 100)

              return (
                <div
                  key={name}
                  className="p-5 rounded-2xl border border-white/5 transition-all hover:border-white/10"
                  style={{ background: `linear-gradient(135deg, ${cfg.color}08 0%, transparent 100%)` }}
                >
                  <div className="flex items-center justify-between mb-4">
                    <span
                      className="w-10 h-10 rounded-xl flex items-center justify-center"
                      style={{ backgroundColor: `${cfg.color}20` }}
                    >
                      <span className="hebrew text-lg" style={{ color: cfg.color }}>{cfg.hebrew.charAt(0)}</span>
                    </span>
                    <span className="mono text-2xl font-bold text-white">{pct}%</span>
                  </div>
                  <div className="hebrew text-lg text-white/80 mb-1">{cfg.hebrew}</div>
                  <div className="mono text-sm text-white/40">{count.toLocaleString()} occurrences</div>
                  <div className="mt-4 h-1.5 rounded-full bg-white/5">
                    <div
                      className="h-full rounded-full transition-all duration-700"
                      style={{ width: `${pct}%`, backgroundColor: cfg.color }}
                    />
                  </div>
                </div>
              )
            })}
          </section>
        </main>
      )}
    </div>
  )
}
