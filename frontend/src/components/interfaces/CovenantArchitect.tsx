import { useState, useEffect, useRef } from 'react'
import { ArrowLeft, Building, Scroll, Gift, Shield, ChevronRight, Clock } from 'lucide-react'

interface Props {
  onBack: () => void
}

interface Covenant {
  id: number
  name: string
  name_hebrew: string | null
  party_divine: string
  party_human: string | null
  sign: string | null
  type: string
  is_conditional: boolean
  summary: string | null
  element_count: number
  verse_ref?: string
}

interface ElementTypeInfo {
  name: string
  name_hebrew: string
  description: string
  color: string
}

interface CovenantElement {
  id: number
  content: string
  content_hebrew: string | null
  verse_ref: string | null
}

interface ElementGroup {
  type: string
  type_info: ElementTypeInfo
  elements: CovenantElement[]
}

interface CovenantDetails {
  id: number
  name: string
  name_hebrew: string | null
  party_divine: string
  party_human: string | null
  sign: string | null
  type: string
  is_conditional: boolean
  summary: string | null
  elements_by_type: ElementGroup[]
  verses: Array<{
    id: number
    ref: string
    hebrew: string
    english: string
  }>
}

interface BlessingCurse {
  id: number
  type: string
  is_blessing: boolean
  category: string | null
  giver: string | null
  recipient: string | null
  content: string
  content_hebrew: string | null
  is_conditional: boolean
  condition: string | null
  is_divine: boolean
  is_prophetic: boolean
  verse_ref: string
}

interface Stats {
  total_covenants: number
  total_elements: number
  total_blessings: number
  total_curses: number
}

interface StructureNode {
  id: string
  type: string
  label: string
  color: string
  x?: number
  y?: number
}

interface StructureEdge {
  source: string
  target: string
  label: string
}

type View = 'covenants' | 'timeline' | 'blessings' | 'compare'

export default function CovenantArchitect({ onBack }: Props) {
  const [view, setView] = useState<View>('covenants')
  const [covenants, setCovenants] = useState<Covenant[]>([])
  const [timeline, setTimeline] = useState<Covenant[]>([])
  const [blessings, setBlessings] = useState<BlessingCurse[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [selectedCovenant, setSelectedCovenant] = useState<CovenantDetails | null>(null)
  const [structureNodes, setStructureNodes] = useState<StructureNode[]>([])
  const [structureEdges, setStructureEdges] = useState<StructureEdge[]>([])
  const [blessingFilter, setBlessingFilter] = useState<'all' | 'blessing' | 'curse'>('all')
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    fetch('/api/covenants/stats').then(r => r.json()).then(setStats)
    fetch('/api/covenants/covenants').then(r => r.json()).then(setCovenants)
  }, [])

  useEffect(() => {
    if (view === 'timeline') {
      fetch('/api/covenants/timeline').then(r => r.json()).then(setTimeline)
    } else if (view === 'blessings') {
      const url = blessingFilter === 'all'
        ? '/api/covenants/blessings?limit=50'
        : `/api/covenants/blessings?blessing_type=${blessingFilter}&limit=50`
      fetch(url).then(r => r.json()).then(data => setBlessings(data.items || []))
    }
  }, [view, blessingFilter])

  const loadCovenantDetails = async (id: number) => {
    const details = await fetch(`/api/covenants/covenant/${id}`).then(r => r.json())
    setSelectedCovenant(details)

    // Load structure for visualization
    const structure = await fetch(`/api/covenants/structure/${id}`).then(r => r.json())
    setStructureNodes(structure.nodes || [])
    setStructureEdges(structure.edges || [])
  }

  // Draw covenant structure visualization
  useEffect(() => {
    if (!canvasRef.current || structureNodes.length === 0) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const rect = canvas.getBoundingClientRect()
    canvas.width = rect.width * window.devicePixelRatio
    canvas.height = rect.height * window.devicePixelRatio
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio)

    const width = rect.width
    const height = rect.height
    const centerX = width / 2
    const centerY = height / 2

    // Position nodes
    const nodeMap = new Map<string, StructureNode>()
    const covenantNode = structureNodes.find(n => n.type === 'covenant')
    const partyNodes = structureNodes.filter(n => n.type === 'party')
    const signNode = structureNodes.find(n => n.type === 'sign')
    const elementNodes = structureNodes.filter(n => !['covenant', 'party', 'sign'].includes(n.type))

    // Position covenant in center
    if (covenantNode) {
      covenantNode.x = centerX
      covenantNode.y = centerY - 20
      nodeMap.set(covenantNode.id, covenantNode)
    }

    // Position parties on sides
    partyNodes.forEach((node, i) => {
      const angle = i === 0 ? Math.PI : 0
      node.x = centerX + Math.cos(angle) * 120
      node.y = centerY - 60
      nodeMap.set(node.id, node)
    })

    // Position sign below covenant
    if (signNode) {
      signNode.x = centerX
      signNode.y = centerY + 80
      nodeMap.set(signNode.id, signNode)
    }

    // Position elements in arc below
    elementNodes.forEach((node, i) => {
      const angle = (Math.PI / 4) + (i / Math.max(elementNodes.length - 1, 1)) * (Math.PI / 2)
      const radius = 140
      node.x = centerX + Math.cos(angle) * radius
      node.y = centerY + 40 + Math.sin(angle) * (radius * 0.6)
      nodeMap.set(node.id, node)
    })

    // Clear and draw background
    ctx.fillStyle = '#1a1510'
    ctx.fillRect(0, 0, width, height)

    // Draw edges
    structureEdges.forEach(edge => {
      const source = nodeMap.get(edge.source)
      const target = nodeMap.get(edge.target)
      if (!source || !target || source.x === undefined || target.x === undefined) return

      ctx.beginPath()
      ctx.moveTo(source.x, source.y!)
      ctx.lineTo(target.x, target.y!)
      ctx.strokeStyle = '#d4a85340'
      ctx.lineWidth = 2
      ctx.stroke()

      // Edge label
      const midX = (source.x + target.x) / 2
      const midY = (source.y! + target.y!) / 2
      ctx.fillStyle = '#94a3b8'
      ctx.font = '10px Plus Jakarta Sans'
      ctx.textAlign = 'center'
      ctx.fillText(edge.label, midX, midY - 5)
    })

    // Draw nodes
    structureNodes.forEach(node => {
      if (node.x === undefined) return

      const isMain = node.type === 'covenant'
      const radius = isMain ? 40 : 25

      // Glow effect
      const gradient = ctx.createRadialGradient(node.x, node.y!, 0, node.x, node.y!, radius * 2)
      gradient.addColorStop(0, node.color + '40')
      gradient.addColorStop(1, 'transparent')
      ctx.fillStyle = gradient
      ctx.beginPath()
      ctx.arc(node.x, node.y!, radius * 2, 0, Math.PI * 2)
      ctx.fill()

      // Node circle
      ctx.beginPath()
      ctx.arc(node.x, node.y!, radius, 0, Math.PI * 2)
      ctx.fillStyle = '#1a1510'
      ctx.fill()
      ctx.strokeStyle = node.color
      ctx.lineWidth = isMain ? 3 : 2
      ctx.stroke()

      // Label
      ctx.fillStyle = node.color
      ctx.font = isMain ? 'bold 12px Plus Jakarta Sans' : '10px Plus Jakarta Sans'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'

      // Wrap text
      const words = node.label.split(' ')
      const lines: string[] = []
      let currentLine = ''
      words.forEach(word => {
        if (currentLine.length + word.length > 15) {
          lines.push(currentLine)
          currentLine = word
        } else {
          currentLine = currentLine ? currentLine + ' ' + word : word
        }
      })
      if (currentLine) lines.push(currentLine)

      lines.forEach((line, i) => {
        const y = node.y! + (i - (lines.length - 1) / 2) * 12
        ctx.fillText(line, node.x!, y)
      })
    })
  }, [structureNodes, structureEdges, selectedCovenant])

  const getCovenantColor = (name: string): string => {
    const n = name.toLowerCase()
    if (n.includes('noah')) return '#60a5fa'
    if (n.includes('abraham')) return '#d4a853'
    if (n.includes('sinai') || n.includes('moses')) return '#8b5cf6'
    if (n.includes('priest') || n.includes('levi')) return '#f59e0b'
    if (n.includes('land')) return '#22c55e'
    return '#94a3b8'
  }

  return (
    <div className="min-h-screen covenant-bg stone-texture pillar-pattern">
      {/* Header */}
      <header className="border-b border-amber-900/30 bg-void/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={onBack}
              className="p-2 hover:bg-amber-500/10 rounded-lg transition-colors text-amber-400"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-amber-400 font-cinzel tracking-wide">
                COVENANT ARCHITECT
              </h1>
              <p className="text-sm text-amber-600/80">Divine Covenant Architecture</p>
            </div>
          </div>

          {/* View Tabs */}
          <div className="flex gap-1 bg-surface/50 p-1 rounded-lg border border-amber-900/30">
            {[
              { id: 'covenants', label: 'Covenants', icon: Building },
              { id: 'timeline', label: 'Timeline', icon: Clock },
              { id: 'blessings', label: 'Blessings', icon: Gift },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => {
                  setView(tab.id as View)
                  setSelectedCovenant(null)
                }}
                className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                  view === tab.id
                    ? 'bg-amber-500/20 text-amber-400 shadow-lg shadow-amber-500/10'
                    : 'text-subtle hover:text-amber-400 hover:bg-amber-500/10'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Stats Banner */}
      {stats && (
        <div className="border-b border-amber-900/20 bg-amber-500/5">
          <div className="max-w-7xl mx-auto px-6 py-3 flex items-center gap-8 text-sm">
            <div className="flex items-center gap-2">
              <Building className="w-4 h-4 text-amber-400" />
              <span className="text-amber-400 font-mono">{stats.total_covenants}</span>
              <span className="text-subtle">covenants</span>
            </div>
            <div className="flex items-center gap-2">
              <Scroll className="w-4 h-4 text-purple-400" />
              <span className="text-purple-400 font-mono">{stats.total_elements}</span>
              <span className="text-subtle">elements</span>
            </div>
            <div className="flex items-center gap-2">
              <Gift className="w-4 h-4 text-emerald-400" />
              <span className="text-emerald-400 font-mono">{stats.total_blessings}</span>
              <span className="text-subtle">blessings</span>
            </div>
            <div className="flex items-center gap-2">
              <Shield className="w-4 h-4 text-red-400" />
              <span className="text-red-400 font-mono">{stats.total_curses}</span>
              <span className="text-subtle">curses</span>
            </div>
          </div>
        </div>
      )}

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Covenants View */}
        {view === 'covenants' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Covenant List */}
            <div className="space-y-4">
              <h3 className="text-sm font-cinzel text-amber-400 uppercase tracking-wider">
                Biblical Covenants
              </h3>
              {covenants.length === 0 ? (
                <div className="text-center py-12 text-subtle">
                  <Building className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No covenants found</p>
                  <p className="text-sm mt-2">Data may need to be extracted first</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {covenants.map((c, i) => (
                    <button
                      key={c.id}
                      onClick={() => loadCovenantDetails(c.id)}
                      className={`w-full text-left p-4 rounded-xl border transition-all animate-covenant-reveal group ${
                        selectedCovenant?.id === c.id
                          ? 'covenant-border bg-amber-500/10'
                          : 'border-amber-900/20 hover:border-amber-500/30 bg-surface/30'
                      }`}
                      style={{ animationDelay: `${i * 100}ms` }}
                    >
                      <div className="flex items-start gap-3">
                        <div
                          className="w-12 h-12 rounded-lg flex items-center justify-center text-2xl font-cinzel mt-1"
                          style={{
                            backgroundColor: getCovenantColor(c.name) + '20',
                            color: getCovenantColor(c.name),
                            border: `2px solid ${getCovenantColor(c.name)}40`,
                          }}
                        >
                          {c.name.charAt(0)}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-text">{c.name}</span>
                            {c.is_conditional && (
                              <span className="text-xs px-2 py-0.5 bg-amber-500/10 text-amber-400 rounded">
                                Conditional
                              </span>
                            )}
                          </div>
                          {c.name_hebrew && (
                            <div className="text-sm text-amber-400/70 hebrew">{c.name_hebrew}</div>
                          )}
                          <div className="text-xs text-subtle mt-1">
                            with {c.party_human || 'Unknown'}
                            {c.sign && ` · Sign: ${c.sign}`}
                          </div>
                          <div className="text-xs text-muted mt-1">
                            {c.element_count} elements
                          </div>
                        </div>
                        <ChevronRight className="w-5 h-5 text-muted group-hover:text-amber-400 transition-colors" />
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Covenant Details */}
            <div className="lg:col-span-2">
              {selectedCovenant ? (
                <div className="space-y-6 animate-fade-in">
                  {/* Structure Visualization */}
                  <div className="bg-surface/30 rounded-xl covenant-border overflow-hidden">
                    <div className="p-4 border-b border-amber-900/20">
                      <h3 className="text-lg font-cinzel text-amber-400">
                        {selectedCovenant.name}
                      </h3>
                      {selectedCovenant.name_hebrew && (
                        <div className="text-sm text-amber-400/70 hebrew mt-1">
                          {selectedCovenant.name_hebrew}
                        </div>
                      )}
                    </div>
                    <canvas
                      ref={canvasRef}
                      className="w-full h-64"
                    />
                  </div>

                  {/* Summary */}
                  {selectedCovenant.summary && (
                    <div className="p-4 bg-amber-500/5 rounded-xl border border-amber-900/20">
                      <p className="text-text/80">{selectedCovenant.summary}</p>
                    </div>
                  )}

                  {/* Elements by Type */}
                  <div className="space-y-4">
                    <h4 className="text-sm font-cinzel text-amber-400 uppercase tracking-wider">
                      Covenant Elements
                    </h4>
                    {selectedCovenant.elements_by_type.length === 0 ? (
                      <div className="text-subtle text-sm">No elements recorded</div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {selectedCovenant.elements_by_type.map((group, gi) => (
                          <div
                            key={group.type}
                            className="p-4 rounded-xl border animate-covenant-reveal"
                            style={{
                              borderColor: group.type_info.color + '40',
                              backgroundColor: group.type_info.color + '10',
                              animationDelay: `${gi * 100}ms`,
                            }}
                          >
                            <div className="flex items-center gap-2 mb-3">
                              <div
                                className="w-8 h-8 rounded-lg flex items-center justify-center"
                                style={{
                                  backgroundColor: group.type_info.color + '20',
                                  color: group.type_info.color,
                                }}
                              >
                                {group.type_info.name.charAt(0)}
                              </div>
                              <div>
                                <div
                                  className="text-sm font-medium"
                                  style={{ color: group.type_info.color }}
                                >
                                  {group.type_info.name}
                                </div>
                                <div className="text-xs text-subtle">{group.type_info.description}</div>
                              </div>
                            </div>
                            <div className="space-y-2">
                              {group.elements.map((el, ei) => (
                                <div
                                  key={el.id}
                                  className="text-sm text-text/80 p-2 bg-night/50 rounded"
                                >
                                  {el.content}
                                  {el.verse_ref && (
                                    <span className="text-xs text-subtle ml-2">({el.verse_ref})</span>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Key Verses */}
                  {selectedCovenant.verses.length > 0 && (
                    <div className="space-y-4">
                      <h4 className="text-sm font-cinzel text-amber-400 uppercase tracking-wider">
                        Key Verses
                      </h4>
                      <div className="space-y-3 max-h-60 overflow-y-auto">
                        {selectedCovenant.verses.slice(0, 10).map((v, i) => (
                          <div
                            key={v.id}
                            className="p-3 bg-surface/30 rounded-lg border border-amber-900/10 animate-fade-in"
                            style={{ animationDelay: `${i * 50}ms` }}
                          >
                            <div className="text-xs text-amber-400 font-mono mb-1">{v.ref}</div>
                            <div className="hebrew text-sm text-text/80">{v.hebrew}</div>
                            <div className="text-xs text-subtle mt-1">{v.english}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="h-full flex items-center justify-center text-subtle">
                  <div className="text-center">
                    <Building className="w-16 h-16 mx-auto mb-4 opacity-30" />
                    <p className="text-lg">Select a covenant to explore</p>
                    <p className="text-sm mt-2">View structure, elements, and key verses</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Timeline View */}
        {view === 'timeline' && (
          <div className="relative">
            {/* Timeline Line */}
            <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-amber-500/20" />

            {timeline.length === 0 ? (
              <div className="text-center py-12 text-subtle">
                <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No timeline data available</p>
              </div>
            ) : (
              <div className="space-y-8">
                {timeline.map((c, i) => (
                  <div
                    key={c.id}
                    className="relative pl-20 animate-covenant-reveal"
                    style={{ animationDelay: `${i * 150}ms` }}
                  >
                    {/* Timeline Node */}
                    <div
                      className="absolute left-4 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold animate-seal-stamp"
                      style={{
                        backgroundColor: getCovenantColor(c.name),
                        boxShadow: `0 0 20px ${getCovenantColor(c.name)}40`,
                        animationDelay: `${i * 150 + 100}ms`,
                      }}
                    >
                      {i + 1}
                    </div>

                    {/* Content Card */}
                    <div className="p-6 bg-surface/50 rounded-xl covenant-border">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="text-xl font-cinzel text-text">{c.name}</h3>
                          {c.name_hebrew && (
                            <div className="text-sm text-amber-400/70 hebrew">{c.name_hebrew}</div>
                          )}
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-mono text-amber-400">{c.verse_ref}</div>
                          <div className="text-xs text-subtle">
                            {c.is_conditional ? 'Conditional' : 'Unconditional'}
                          </div>
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-3 mb-3">
                        <div className="flex items-center gap-2 text-sm">
                          <span className="text-subtle">With:</span>
                          <span className="text-text">{c.party_human || 'All Humanity'}</span>
                        </div>
                        {c.sign && (
                          <div className="flex items-center gap-2 text-sm">
                            <span className="text-subtle">Sign:</span>
                            <span className="text-amber-400">{c.sign}</span>
                          </div>
                        )}
                      </div>

                      {c.summary && (
                        <p className="text-sm text-text/70">{c.summary}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Blessings View */}
        {view === 'blessings' && (
          <div className="space-y-6">
            {/* Filter Tabs */}
            <div className="flex gap-2">
              {[
                { id: 'all', label: 'All' },
                { id: 'blessing', label: 'Blessings', color: '#22c55e' },
                { id: 'curse', label: 'Curses', color: '#ef4444' },
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setBlessingFilter(tab.id as typeof blessingFilter)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    blessingFilter === tab.id
                      ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                      : 'text-subtle hover:text-text hover:bg-surface/50 border border-transparent'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Blessings Grid */}
            {blessings.length === 0 ? (
              <div className="text-center py-12 text-subtle">
                <Gift className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No blessings or curses found</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {blessings.map((b, i) => (
                  <div
                    key={b.id}
                    className={`p-4 rounded-xl border animate-covenant-reveal ${
                      b.is_blessing
                        ? 'border-emerald-500/30 bg-emerald-500/5'
                        : 'border-red-500/30 bg-red-500/5'
                    }`}
                    style={{ animationDelay: `${i * 50}ms` }}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        {b.is_blessing ? (
                          <Gift className="w-5 h-5 text-emerald-400" />
                        ) : (
                          <Shield className="w-5 h-5 text-red-400" />
                        )}
                        <span className={b.is_blessing ? 'text-emerald-400' : 'text-red-400'}>
                          {b.is_blessing ? 'Blessing' : 'Curse'}
                        </span>
                        {b.category && (
                          <span className="text-xs px-2 py-0.5 bg-surface/50 text-subtle rounded">
                            {b.category}
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-amber-400 font-mono">{b.verse_ref}</span>
                    </div>

                    {(b.giver || b.recipient) && (
                      <div className="flex items-center gap-4 text-sm mb-2">
                        {b.giver && (
                          <div>
                            <span className="text-subtle">From: </span>
                            <span className="text-text">{b.giver}</span>
                          </div>
                        )}
                        {b.recipient && (
                          <div>
                            <span className="text-subtle">To: </span>
                            <span className="text-text">{b.recipient}</span>
                          </div>
                        )}
                      </div>
                    )}

                    <p className="text-sm text-text/80">{b.content}</p>

                    {b.content_hebrew && (
                      <p className="text-sm text-text/60 hebrew mt-2">{b.content_hebrew}</p>
                    )}

                    {b.is_conditional && b.condition && (
                      <div className="mt-3 p-2 bg-amber-500/10 rounded text-xs">
                        <span className="text-amber-400">Condition: </span>
                        <span className="text-text/70">{b.condition}</span>
                      </div>
                    )}

                    <div className="flex gap-2 mt-3">
                      {b.is_divine && (
                        <span className="text-xs px-2 py-0.5 bg-purple-500/20 text-purple-400 rounded">
                          Divine
                        </span>
                      )}
                      {b.is_prophetic && (
                        <span className="text-xs px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded">
                          Prophetic
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
