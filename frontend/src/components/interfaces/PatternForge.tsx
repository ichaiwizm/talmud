import { useState, useEffect, useRef } from 'react'
import { ArrowLeft, Layers, FileText, Network, Repeat, ChevronRight, Search } from 'lucide-react'

interface Props {
  onBack: () => void
}

interface StructureTypeInfo {
  name: string
  description: string
  example: string
  color: string
}

interface Structure {
  id: number
  type: string
  type_info: StructureTypeInfo
  pattern: string | null
  start_ref: string | null
  end_ref: string | null
  focal_ref: string | null
  description: string | null
  elements: Array<{ label: string; verse_refs: string[]; content: string }> | null
  confidence: number | null
}

interface FormulaTypeInfo {
  name: string
  description: string
  example: string
  color: string
}

interface Formula {
  id: number
  hebrew: string
  english: string
  transliteration: string | null
  type: string
  type_info: FormulaTypeInfo
  function: string | null
  occurrence_count: number
}

interface CrossRefTypeInfo {
  name: string
  description: string
  color: string
}

interface CrossReference {
  id: number
  source_ref: string
  target_ref: string
  type: string
  type_info: CrossRefTypeInfo
  similarity_score: number | null
  shared_vocabulary: string[] | null
  shared_themes: string[] | null
  is_bidirectional: boolean
}

interface Motif {
  id: number
  name: string
  name_hebrew: string | null
  description: string
  thematic_significance: string | null
  occurrence_count: number
  first_occurrence: string | null
}

interface StructureType {
  type: string
  count: number
  info: StructureTypeInfo
}

interface NetworkNode {
  id: string
  ref: string
  x?: number
  y?: number
}

interface NetworkEdge {
  source: string
  target: string
  type: string
  color: string
  strength: number
}

interface Stats {
  total_structures: number
  total_formulas: number
  total_formula_occurrences: number
  total_cross_references: number
  total_motifs: number
  total_motif_occurrences: number
}

type View = 'structures' | 'formulas' | 'connections' | 'motifs'

export default function PatternForge({ onBack }: Props) {
  const [view, setView] = useState<View>('structures')
  const [structures, setStructures] = useState<Structure[]>([])
  const [structureTypes, setStructureTypes] = useState<StructureType[]>([])
  const [formulas, setFormulas] = useState<Formula[]>([])
  const [crossRefs, setCrossRefs] = useState<CrossReference[]>([])
  const [motifs, setMotifs] = useState<Motif[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [selectedType, setSelectedType] = useState<string | null>(null)
  const [selectedStructure, setSelectedStructure] = useState<Structure | null>(null)
  const [selectedFormula, setSelectedFormula] = useState<Formula | null>(null)
  const [formulaOccurrences, setFormulaOccurrences] = useState<Array<{
    verse_ref: string
    verse_hebrew: string
    verse_english: string
    surface_form: string | null
  }>>([])
  const [networkNodes, setNetworkNodes] = useState<NetworkNode[]>([])
  const [networkEdges, setNetworkEdges] = useState<NetworkEdge[]>([])
  const [search, setSearch] = useState('')
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    fetch('/api/patterns/stats').then(r => r.json()).then(setStats)
    fetch('/api/patterns/structure-types').then(r => r.json()).then(setStructureTypes)
  }, [])

  useEffect(() => {
    if (view === 'structures') {
      const url = selectedType
        ? `/api/patterns/structures?structure_type=${selectedType}&limit=50`
        : '/api/patterns/structures?limit=50'
      fetch(url).then(r => r.json()).then(data => setStructures(data.structures || []))
    } else if (view === 'formulas') {
      fetch('/api/patterns/formulas?limit=50').then(r => r.json()).then(data => setFormulas(data.formulas || []))
    } else if (view === 'connections') {
      fetch('/api/patterns/network?limit=150').then(r => r.json()).then(data => {
        setNetworkNodes(data.nodes || [])
        setNetworkEdges(data.edges || [])
      })
      fetch('/api/patterns/cross-references?limit=50').then(r => r.json()).then(data => setCrossRefs(data.references || []))
    } else if (view === 'motifs') {
      fetch('/api/patterns/motifs?limit=50').then(r => r.json()).then(data => setMotifs(data.motifs || []))
    }
  }, [view, selectedType])

  useEffect(() => {
    if (selectedFormula) {
      fetch(`/api/patterns/formula/${selectedFormula.id}?limit=20`)
        .then(r => r.json())
        .then(data => setFormulaOccurrences(data.occurrences || []))
    }
  }, [selectedFormula])

  // Draw network visualization
  useEffect(() => {
    if (view !== 'connections' || !canvasRef.current || networkNodes.length === 0) return

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

    // Position nodes in a circular layout
    const nodeMap = new Map<string, NetworkNode>()
    networkNodes.forEach((node, i) => {
      const angle = (i / networkNodes.length) * Math.PI * 2 - Math.PI / 2
      const radius = Math.min(width, height) * 0.35
      node.x = centerX + Math.cos(angle) * radius
      node.y = centerY + Math.sin(angle) * radius
      nodeMap.set(node.id, node)
    })

    // Clear and draw background
    ctx.fillStyle = '#0a1628'
    ctx.fillRect(0, 0, width, height)

    // Draw edges
    networkEdges.forEach(edge => {
      const source = nodeMap.get(edge.source)
      const target = nodeMap.get(edge.target)
      if (!source || !target || source.x === undefined || target.x === undefined) return

      ctx.beginPath()
      ctx.moveTo(source.x, source.y!)
      ctx.lineTo(target.x, target.y!)
      ctx.strokeStyle = edge.color + '60'
      ctx.lineWidth = edge.strength * 2
      ctx.stroke()
    })

    // Draw nodes
    networkNodes.forEach(node => {
      if (node.x === undefined) return

      // Glow effect
      const gradient = ctx.createRadialGradient(node.x, node.y!, 0, node.x, node.y!, 20)
      gradient.addColorStop(0, '#06b6d4')
      gradient.addColorStop(0.5, '#06b6d440')
      gradient.addColorStop(1, 'transparent')
      ctx.fillStyle = gradient
      ctx.beginPath()
      ctx.arc(node.x, node.y!, 20, 0, Math.PI * 2)
      ctx.fill()

      // Node circle
      ctx.beginPath()
      ctx.arc(node.x, node.y!, 6, 0, Math.PI * 2)
      ctx.fillStyle = '#06b6d4'
      ctx.fill()
      ctx.strokeStyle = '#0a1628'
      ctx.lineWidth = 2
      ctx.stroke()

      // Label
      ctx.fillStyle = '#94a3b8'
      ctx.font = '10px JetBrains Mono'
      ctx.textAlign = 'center'
      ctx.fillText(node.ref, node.x, node.y! + 20)
    })
  }, [view, networkNodes, networkEdges])

  const renderStructureDiagram = (structure: Structure) => {
    const elements = structure.elements || []
    if (elements.length === 0) return null

    const isChiasmus = structure.type === 'chiasmus'
    const isParallelism = structure.type === 'parallelism'

    return (
      <div className="mt-4 p-4 rounded-lg border border-cyan-500/20 bg-cyan-500/5">
        <div className="text-xs text-cyan-400 mb-3 font-mono uppercase tracking-wider">
          Structure Diagram
        </div>
        <div className={`space-y-2 ${isChiasmus ? 'flex flex-col items-center' : ''}`}>
          {elements.map((el, i) => {
            const indent = isChiasmus
              ? Math.abs(i - (elements.length - 1) / 2) * 40
              : isParallelism && i % 2 === 1 ? 20 : 0

            return (
              <div
                key={i}
                className="flex items-center gap-3 animate-fade-in"
                style={{
                  animationDelay: `${i * 100}ms`,
                  marginLeft: indent,
                }}
              >
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center font-mono text-sm font-bold border-2"
                  style={{
                    borderColor: structure.type_info.color,
                    color: structure.type_info.color,
                    backgroundColor: structure.type_info.color + '20',
                  }}
                >
                  {el.label}
                </div>
                <div className="flex-1">
                  <div className="text-sm text-text">{el.content}</div>
                  <div className="text-xs text-subtle font-mono">{el.verse_refs?.join(', ')}</div>
                </div>
              </div>
            )
          })}
        </div>
        {isChiasmus && (
          <div className="mt-4 text-center text-xs text-cyan-400/60 font-mono">
            ↔ Mirror Structure ↔
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="min-h-screen blueprint-bg blueprint-grid">
      {/* Header */}
      <header className="border-b border-cyan-500/20 bg-void/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={onBack}
              className="p-2 hover:bg-cyan-500/10 rounded-lg transition-colors text-cyan-400"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-cyan-400 font-mono tracking-tight">
                PATTERN FORGE
              </h1>
              <p className="text-sm text-cyan-600/80">Literary Structure Analysis</p>
            </div>
          </div>

          {/* View Tabs */}
          <div className="flex gap-1 bg-surface/50 p-1 rounded-lg border border-cyan-500/20">
            {[
              { id: 'structures', label: 'Structures', icon: Layers },
              { id: 'formulas', label: 'Formulas', icon: FileText },
              { id: 'connections', label: 'Connections', icon: Network },
              { id: 'motifs', label: 'Motifs', icon: Repeat },
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setView(tab.id as View)}
                className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                  view === tab.id
                    ? 'bg-cyan-500/20 text-cyan-400 shadow-lg shadow-cyan-500/10'
                    : 'text-subtle hover:text-cyan-400 hover:bg-cyan-500/10'
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
        <div className="border-b border-cyan-500/10 bg-cyan-500/5">
          <div className="max-w-7xl mx-auto px-6 py-3 flex items-center gap-8 text-sm">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-cyan-400" />
              <span className="text-cyan-400 font-mono">{stats.total_structures}</span>
              <span className="text-subtle">structures</span>
            </div>
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-purple-400" />
              <span className="text-purple-400 font-mono">{stats.total_formulas}</span>
              <span className="text-subtle">formulas</span>
            </div>
            <div className="flex items-center gap-2">
              <Network className="w-4 h-4 text-amber-400" />
              <span className="text-amber-400 font-mono">{stats.total_cross_references}</span>
              <span className="text-subtle">connections</span>
            </div>
            <div className="flex items-center gap-2">
              <Repeat className="w-4 h-4 text-emerald-400" />
              <span className="text-emerald-400 font-mono">{stats.total_motifs}</span>
              <span className="text-subtle">motifs</span>
            </div>
          </div>
        </div>
      )}

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Structures View */}
        {view === 'structures' && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Type Filter */}
            <div className="space-y-4">
              <h3 className="text-sm font-mono text-cyan-400 uppercase tracking-wider">
                Structure Types
              </h3>
              <div className="space-y-2">
                <button
                  onClick={() => setSelectedType(null)}
                  className={`w-full text-left px-4 py-3 rounded-lg border transition-all ${
                    !selectedType
                      ? 'border-cyan-500 bg-cyan-500/10 text-cyan-400'
                      : 'border-muted/20 hover:border-cyan-500/50 text-text'
                  }`}
                >
                  <div className="font-medium">All Types</div>
                  <div className="text-xs text-subtle">{stats?.total_structures || 0} total</div>
                </button>
                {structureTypes.map(st => (
                  <button
                    key={st.type}
                    onClick={() => setSelectedType(st.type)}
                    className={`w-full text-left px-4 py-3 rounded-lg border transition-all ${
                      selectedType === st.type
                        ? 'border-cyan-500 bg-cyan-500/10'
                        : 'border-muted/20 hover:border-cyan-500/50'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: st.info.color }}
                      />
                      <span className="font-medium text-text">{st.info.name}</span>
                    </div>
                    <div className="text-xs text-subtle mt-1">
                      {st.info.example && <span className="font-mono">{st.info.example}</span>}
                      {' · '}{st.count} found
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Structure List / Details */}
            <div className="lg:col-span-3">
              {selectedStructure ? (
                <div className="animate-fade-in">
                  <button
                    onClick={() => setSelectedStructure(null)}
                    className="flex items-center gap-2 text-cyan-400 hover:text-cyan-300 mb-4"
                  >
                    <ArrowLeft className="w-4 h-4" />
                    Back to list
                  </button>

                  <div className="bg-surface/50 rounded-xl border border-cyan-500/20 p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <div
                          className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium mb-2"
                          style={{
                            backgroundColor: selectedStructure.type_info.color + '20',
                            color: selectedStructure.type_info.color,
                          }}
                        >
                          {selectedStructure.type_info.name}
                        </div>
                        <h2 className="text-xl text-text font-medium">
                          {selectedStructure.start_ref} — {selectedStructure.end_ref}
                        </h2>
                        {selectedStructure.pattern && (
                          <div className="text-cyan-400 font-mono text-lg mt-1">
                            {selectedStructure.pattern}
                          </div>
                        )}
                      </div>
                      {selectedStructure.confidence && (
                        <div className="text-xs text-subtle">
                          {Math.round(selectedStructure.confidence * 100)}% confidence
                        </div>
                      )}
                    </div>

                    {selectedStructure.description && (
                      <p className="text-text/80 mb-4">{selectedStructure.description}</p>
                    )}

                    {selectedStructure.focal_ref && (
                      <div className="px-4 py-2 bg-amber-500/10 border border-amber-500/20 rounded-lg mb-4">
                        <span className="text-amber-400 text-sm font-mono">Focal Point:</span>
                        <span className="text-text ml-2">{selectedStructure.focal_ref}</span>
                      </div>
                    )}

                    {renderStructureDiagram(selectedStructure)}
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {structures.length === 0 ? (
                    <div className="text-center py-12 text-subtle">
                      <Layers className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p>No literary structures found</p>
                      <p className="text-sm mt-2">Data may need to be extracted first</p>
                    </div>
                  ) : (
                    structures.map((s, i) => (
                      <button
                        key={s.id}
                        onClick={() => setSelectedStructure(s)}
                        className="w-full text-left p-4 bg-surface/30 hover:bg-surface/50 rounded-xl border border-cyan-500/10 hover:border-cyan-500/30 transition-all animate-fade-in group"
                        style={{ animationDelay: `${i * 50}ms` }}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-3">
                            <div
                              className="w-10 h-10 rounded-lg flex items-center justify-center text-lg font-mono font-bold mt-1"
                              style={{
                                backgroundColor: s.type_info.color + '20',
                                color: s.type_info.color,
                              }}
                            >
                              {s.pattern?.charAt(0) || s.type_info.name.charAt(0)}
                            </div>
                            <div>
                              <div className="flex items-center gap-2">
                                <span
                                  className="text-xs px-2 py-0.5 rounded-full"
                                  style={{
                                    backgroundColor: s.type_info.color + '20',
                                    color: s.type_info.color,
                                  }}
                                >
                                  {s.type_info.name}
                                </span>
                                <span className="text-text font-medium">
                                  {s.start_ref} — {s.end_ref}
                                </span>
                              </div>
                              {s.pattern && (
                                <div className="text-cyan-400/70 font-mono text-sm mt-1">
                                  {s.pattern}
                                </div>
                              )}
                              {s.description && (
                                <p className="text-sm text-subtle mt-1 line-clamp-2">
                                  {s.description}
                                </p>
                              )}
                            </div>
                          </div>
                          <ChevronRight className="w-5 h-5 text-muted group-hover:text-cyan-400 transition-colors" />
                        </div>
                      </button>
                    ))
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Formulas View */}
        {view === 'formulas' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Formula List */}
            <div className="space-y-4">
              <div className="flex items-center gap-4 mb-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
                  <input
                    type="text"
                    placeholder="Search formulas..."
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-surface/50 border border-cyan-500/20 rounded-lg text-text placeholder:text-muted focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              {formulas.length === 0 ? (
                <div className="text-center py-12 text-subtle">
                  <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No formulaic expressions found</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {formulas
                    .filter(f =>
                      !search ||
                      f.hebrew.includes(search) ||
                      f.english.toLowerCase().includes(search.toLowerCase())
                    )
                    .map((f, i) => (
                      <button
                        key={f.id}
                        onClick={() => setSelectedFormula(f)}
                        className={`w-full text-left p-4 rounded-xl border transition-all animate-fade-in ${
                          selectedFormula?.id === f.id
                            ? 'bg-purple-500/10 border-purple-500/30'
                            : 'bg-surface/30 border-cyan-500/10 hover:border-purple-500/30'
                        }`}
                        style={{ animationDelay: `${i * 50}ms` }}
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <div className="hebrew text-xl text-text mb-1">{f.hebrew}</div>
                            <div className="text-sm text-text/80">{f.english}</div>
                            <div className="flex items-center gap-2 mt-2">
                              <span
                                className="text-xs px-2 py-0.5 rounded-full"
                                style={{
                                  backgroundColor: f.type_info.color + '20',
                                  color: f.type_info.color,
                                }}
                              >
                                {f.type_info.name}
                              </span>
                              <span className="text-xs text-subtle">
                                {f.occurrence_count} occurrences
                              </span>
                            </div>
                          </div>
                          <ChevronRight className="w-5 h-5 text-muted" />
                        </div>
                      </button>
                    ))}
                </div>
              )}
            </div>

            {/* Formula Details */}
            <div>
              {selectedFormula ? (
                <div className="bg-surface/50 rounded-xl border border-purple-500/20 p-6 sticky top-32 animate-fade-in">
                  <div
                    className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium mb-4"
                    style={{
                      backgroundColor: selectedFormula.type_info.color + '20',
                      color: selectedFormula.type_info.color,
                    }}
                  >
                    {selectedFormula.type_info.name}
                  </div>

                  <div className="hebrew text-3xl text-text mb-2">{selectedFormula.hebrew}</div>
                  <div className="text-lg text-text/80 mb-2">{selectedFormula.english}</div>
                  {selectedFormula.transliteration && (
                    <div className="text-sm text-subtle italic mb-4">
                      {selectedFormula.transliteration}
                    </div>
                  )}

                  {selectedFormula.function && (
                    <div className="p-3 bg-cyan-500/5 border border-cyan-500/10 rounded-lg mb-4">
                      <div className="text-xs text-cyan-400 uppercase tracking-wider mb-1">
                        Function
                      </div>
                      <div className="text-sm text-text">{selectedFormula.function}</div>
                    </div>
                  )}

                  <div className="text-sm text-subtle mb-3">
                    Found in {selectedFormula.occurrence_count} verses
                  </div>

                  {/* Occurrences */}
                  <div className="space-y-3 max-h-80 overflow-y-auto">
                    {formulaOccurrences.map((occ, i) => (
                      <div
                        key={i}
                        className="p-3 bg-night/50 rounded-lg border border-muted/10 animate-fade-in"
                        style={{ animationDelay: `${i * 50}ms` }}
                      >
                        <div className="text-xs text-cyan-400 font-mono mb-1">{occ.verse_ref}</div>
                        <div className="hebrew text-sm text-text/80 line-clamp-2">
                          {occ.verse_hebrew}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="h-full flex items-center justify-center text-subtle">
                  <div className="text-center">
                    <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Select a formula to view details</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Connections View */}
        {view === 'connections' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Network Canvas */}
            <div className="lg:col-span-2">
              <div className="bg-surface/30 rounded-xl border border-cyan-500/20 overflow-hidden">
                <div className="p-4 border-b border-cyan-500/10">
                  <h3 className="text-sm font-mono text-cyan-400 uppercase tracking-wider">
                    Cross-Reference Network
                  </h3>
                  <p className="text-xs text-subtle mt-1">
                    {networkNodes.length} verses · {networkEdges.length} connections
                  </p>
                </div>
                <canvas
                  ref={canvasRef}
                  className="w-full h-96"
                />
              </div>

              {/* Connection Type Legend */}
              <div className="flex flex-wrap gap-3 mt-4">
                {[
                  { type: 'parallel', color: '#8b5cf6', name: 'Parallel' },
                  { type: 'thematic', color: '#3b82f6', name: 'Thematic' },
                  { type: 'verbal', color: '#06b6d4', name: 'Verbal' },
                  { type: 'fulfillment', color: '#d4a853', name: 'Fulfillment' },
                  { type: 'contrast', color: '#ef4444', name: 'Contrast' },
                  { type: 'typology', color: '#f59e0b', name: 'Typology' },
                ].map(t => (
                  <div key={t.type} className="flex items-center gap-2 text-sm">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: t.color }}
                    />
                    <span className="text-subtle">{t.name}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Cross-Reference List */}
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              <h3 className="text-sm font-mono text-cyan-400 uppercase tracking-wider sticky top-0 bg-void py-2">
                Recent Connections
              </h3>
              {crossRefs.length === 0 ? (
                <div className="text-center py-8 text-subtle">
                  <Network className="w-10 h-10 mx-auto mb-3 opacity-50" />
                  <p>No cross-references found</p>
                </div>
              ) : (
                crossRefs.map((r, i) => (
                  <div
                    key={r.id}
                    className="p-3 bg-surface/30 rounded-lg border border-cyan-500/10 animate-fade-in"
                    style={{ animationDelay: `${i * 30}ms` }}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm font-mono text-text">{r.source_ref}</span>
                      <div
                        className="flex-1 h-px"
                        style={{ backgroundColor: r.type_info.color }}
                      />
                      <span
                        className="text-xs px-2 py-0.5 rounded-full"
                        style={{
                          backgroundColor: r.type_info.color + '20',
                          color: r.type_info.color,
                        }}
                      >
                        {r.type_info.name}
                      </span>
                      <div
                        className="flex-1 h-px"
                        style={{ backgroundColor: r.type_info.color }}
                      />
                      <span className="text-sm font-mono text-text">{r.target_ref}</span>
                    </div>
                    {r.shared_vocabulary && r.shared_vocabulary.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {r.shared_vocabulary.slice(0, 3).map((word, wi) => (
                          <span
                            key={wi}
                            className="text-xs px-2 py-0.5 bg-cyan-500/10 text-cyan-400 rounded hebrew"
                          >
                            {word}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Motifs View */}
        {view === 'motifs' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {motifs.length === 0 ? (
              <div className="col-span-full text-center py-12 text-subtle">
                <Repeat className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No recurring motifs found</p>
              </div>
            ) : (
              motifs.map((m, i) => (
                <div
                  key={m.id}
                  className="p-4 bg-surface/30 rounded-xl border border-emerald-500/20 hover:border-emerald-500/40 transition-all animate-fade-in"
                  style={{ animationDelay: `${i * 50}ms` }}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="text-lg font-medium text-text">{m.name}</h3>
                      {m.name_hebrew && (
                        <div className="text-sm text-emerald-400 hebrew">{m.name_hebrew}</div>
                      )}
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-mono text-emerald-400">
                        {m.occurrence_count}
                      </div>
                      <div className="text-xs text-subtle">occurrences</div>
                    </div>
                  </div>

                  <p className="text-sm text-text/70 mb-3 line-clamp-2">{m.description}</p>

                  {m.first_occurrence && (
                    <div className="text-xs text-subtle">
                      First: <span className="text-emerald-400 font-mono">{m.first_occurrence}</span>
                    </div>
                  )}

                  {m.thematic_significance && (
                    <div className="mt-3 p-2 bg-emerald-500/5 rounded-lg border border-emerald-500/10">
                      <div className="text-xs text-emerald-400/70 uppercase tracking-wider mb-1">
                        Significance
                      </div>
                      <div className="text-xs text-text/70 line-clamp-2">
                        {m.thematic_significance}
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </main>
    </div>
  )
}
