import { useState, useEffect, useCallback } from 'react'
import {
  ArrowLeft, GitBranch, Search, BookOpen, Layers,
  TreeDeciduous, Leaf, ChevronRight
} from 'lucide-react'

// Binyan colors
const BINYAN_COLORS: Record<string, string> = {
  qal: '#22c55e',
  niphal: '#3b82f6',
  piel: '#f59e0b',
  pual: '#8b5cf6',
  hiphil: '#ef4444',
  hophal: '#ec4899',
  hitpael: '#14b8a6',
  other: '#94a3b8',
}

interface Props {
  onBack: () => void
}

interface Root {
  id: number
  letters: string
  transliteration: string
  meaning: string
  meaning_hebrew: string | null
  occurrence_count: number
  semantic_field: string | null
  color: string
  related_roots: number[] | null
}

interface SemanticField {
  field: string
  root_count: number
  total_occurrences: number
  color: string
}

interface VerbFormInfo {
  name: string
  description: string
  color: string
}

interface VerbFormData {
  form: string
  count: number
  info: VerbFormInfo
}

interface WordExample {
  word: string
  word_normalized: string
  verse_ref: string
  meaning: string | null
  gematria: number
}

interface RootDetail {
  id: number
  letters: string
  transliteration: string
  meaning: string
  meaning_hebrew: string | null
  occurrence_count: number
  semantic_field: string | null
  color: string
  notes: string | null
  related_roots: Array<{ id: number; letters: string; meaning: string }>
  by_verb_form: Record<string, {
    count: number
    info: VerbFormInfo
    examples: WordExample[]
  }>
  unique_words: Array<{
    word: string
    word_normalized: string
    count: number
    meaning: string | null
  }>
}

interface Stats {
  total_roots: number
  total_word_mappings: number
  semantic_field_count: number
  top_roots: Array<{ letters: string; meaning: string; count: number }>
}

type ViewMode = 'browse' | 'search' | 'fields' | 'binyanim'

export default function ShoreshNavigator({ onBack }: Props) {
  const [view, setView] = useState<ViewMode>('browse')
  const [roots, setRoots] = useState<Root[]>([])
  const [fields, setFields] = useState<SemanticField[]>([])
  const [binyanim, setBinyanim] = useState<VerbFormData[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedRoot, setSelectedRoot] = useState<RootDetail | null>(null)
  const [selectedField, setSelectedField] = useState<string | null>(null)

  // Load initial data
  useEffect(() => {
    setLoading(true)

    Promise.all([
      fetch('/api/shoresh/roots?limit=50').then(r => r.json()),
      fetch('/api/shoresh/semantic-fields').then(r => r.json()),
      fetch('/api/shoresh/verb-forms').then(r => r.json()),
      fetch('/api/shoresh/stats').then(r => r.json()),
    ]).then(([rootData, fieldData, binyanData, statsData]) => {
      setRoots(rootData.roots)
      setFields(fieldData)
      setBinyanim(binyanData)
      setStats(statsData)
      setLoading(false)
    }).catch(console.error)
  }, [])

  // Search roots
  const handleSearch = useCallback(async () => {
    if (!searchQuery.trim()) return

    setLoading(true)
    try {
      const res = await fetch(`/api/shoresh/search?q=${encodeURIComponent(searchQuery)}`)
      const data = await res.json()
      setRoots(data)
      setView('search')
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }, [searchQuery])

  // Load roots by semantic field
  const loadByField = useCallback(async (field: string) => {
    setLoading(true)
    setSelectedField(field)
    try {
      const res = await fetch(`/api/shoresh/roots?semantic_field=${encodeURIComponent(field)}&limit=100`)
      const data = await res.json()
      setRoots(data.roots)
      setView('browse')
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }, [])

  // Load root details
  const loadRootDetails = useCallback(async (rootId: number) => {
    setLoading(true)
    try {
      const res = await fetch(`/api/shoresh/root/${rootId}`)
      const data = await res.json()
      setSelectedRoot(data)
    } catch (e) {
      console.error(e)
    }
    setLoading(false)
  }, [])

  // Clear selection
  const clearSelection = () => {
    setSelectedRoot(null)
    setSelectedField(null)
  }

  return (
    <div className="min-h-screen root-bg tree-rings">
      {/* Gradient overlays */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-0 w-full h-64 bg-gradient-to-b from-green-900/10 to-transparent" />
        <div className="absolute bottom-0 left-0 w-full h-64 bg-gradient-to-t from-green-950/20 to-transparent" />
      </div>

      {/* Header */}
      <header className="sticky top-0 z-30 backdrop-blur-md bg-[#1a1f16]/80 border-b border-green-900/30">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={onBack}
              className="p-2.5 rounded-xl bg-green-900/30 hover:bg-green-900/50 border border-green-700/30 transition-all"
            >
              <ArrowLeft className="w-5 h-5 text-green-200/70" />
            </button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-green-900/50">
                <GitBranch className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-green-100">Shoresh Navigator</h1>
                <p className="text-sm text-green-400/70">Exploration des racines hébraïques</p>
              </div>
            </div>
          </div>

          {/* View switcher */}
          <div className="flex items-center gap-3">
            <div className="flex gap-1 p-1 rounded-xl bg-green-900/30 border border-green-700/30">
              {[
                { id: 'browse' as ViewMode, icon: TreeDeciduous, label: 'Racines' },
                { id: 'fields' as ViewMode, icon: Layers, label: 'Champs' },
                { id: 'binyanim' as ViewMode, icon: BookOpen, label: 'Binyanim' },
              ].map(v => (
                <button
                  key={v.id}
                  onClick={() => { setView(v.id); clearSelection() }}
                  className={`
                    flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all
                    ${view === v.id
                      ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white'
                      : 'text-green-300/60 hover:text-green-200'}
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

      {/* Search bar */}
      <div className="max-w-6xl mx-auto px-6 py-4">
        <div className="relative">
          <input
            type="text"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            placeholder="Rechercher une racine (lettres, translittération ou sens)..."
            className="w-full px-4 py-3 pl-12 rounded-xl bg-green-900/20 border border-green-700/30 text-green-100 placeholder:text-green-500/50 focus:outline-none focus:ring-2 focus:ring-green-500/50"
          />
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-green-500/50" />
          <button
            onClick={handleSearch}
            className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-1.5 rounded-lg bg-green-600 text-white text-sm hover:bg-green-500 transition-colors"
          >
            Rechercher
          </button>
        </div>
      </div>

      {/* Main content */}
      <main className="max-w-6xl mx-auto px-6 py-4 relative z-10">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="flex flex-col items-center gap-4">
              <TreeDeciduous className="w-12 h-12 text-green-500 animate-pulse" />
              <span className="text-green-400/70 text-sm">Exploration des racines...</span>
            </div>
          </div>
        ) : selectedRoot ? (
          /* Root Detail View */
          <div className="space-y-6">
            <button
              onClick={() => setSelectedRoot(null)}
              className="flex items-center gap-2 text-green-400 hover:text-green-300 text-sm"
            >
              <ArrowLeft className="w-4 h-4" />
              Retour aux racines
            </button>

            {/* Root header */}
            <div className="p-6 rounded-2xl bg-green-900/20 border border-green-700/30">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-4xl font-bold hebrew text-green-100 mb-2">
                    {selectedRoot.letters}
                  </h2>
                  <p className="text-lg text-green-300">{selectedRoot.transliteration}</p>
                </div>
                <div
                  className="px-4 py-2 rounded-full text-sm font-medium"
                  style={{ backgroundColor: selectedRoot.color + '30', color: selectedRoot.color }}
                >
                  {selectedRoot.semantic_field || 'general'}
                </div>
              </div>

              <p className="text-xl text-green-200 mb-4">{selectedRoot.meaning}</p>

              <div className="flex items-center gap-6 text-sm text-green-400/70">
                <span>{selectedRoot.occurrence_count} occurrences</span>
                {selectedRoot.notes && <span>{selectedRoot.notes}</span>}
              </div>
            </div>

            {/* Verb forms breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(selectedRoot.by_verb_form).map(([form, data]) => (
                <div
                  key={form}
                  className="p-4 rounded-xl bg-green-900/20 border border-green-700/30"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <span
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: data.info.color }}
                      />
                      <span className="font-medium text-green-100">{data.info.name}</span>
                    </div>
                    <span className="text-sm text-green-400/70 mono">{data.count}</span>
                  </div>
                  <p className="text-xs text-green-500/70 mb-3">{data.info.description}</p>

                  {data.examples.length > 0 && (
                    <div className="space-y-2">
                      {data.examples.slice(0, 3).map((ex, i) => (
                        <div key={i} className="flex items-center justify-between text-sm">
                          <span className="hebrew text-green-200">{ex.word}</span>
                          <span className="text-green-500/50">{ex.verse_ref}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Derived words */}
            {selectedRoot.unique_words.length > 0 && (
              <div className="p-6 rounded-2xl bg-green-900/20 border border-green-700/30">
                <h3 className="text-lg font-semibold text-green-100 mb-4">
                  Mots dérivés ({selectedRoot.unique_words.length})
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                  {selectedRoot.unique_words.map((w, i) => (
                    <div
                      key={i}
                      className="p-3 rounded-lg bg-green-950/50 border border-green-800/30"
                    >
                      <div className="text-lg hebrew text-green-200 mb-1">{w.word}</div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-green-500/50">{w.count}x</span>
                        {w.meaning && (
                          <span className="text-green-400/70 truncate ml-2">{w.meaning}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Related roots */}
            {selectedRoot.related_roots.length > 0 && (
              <div className="p-6 rounded-2xl bg-green-900/20 border border-green-700/30">
                <h3 className="text-lg font-semibold text-green-100 mb-4">
                  Racines apparentées
                </h3>
                <div className="flex flex-wrap gap-3">
                  {selectedRoot.related_roots.map(rel => (
                    <button
                      key={rel.id}
                      onClick={() => loadRootDetails(rel.id)}
                      className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-800/30 border border-green-700/30 hover:border-green-500/50 transition-all"
                    >
                      <span className="text-xl hebrew text-green-200">{rel.letters}</span>
                      <span className="text-sm text-green-400/70">{rel.meaning}</span>
                      <ChevronRight className="w-4 h-4 text-green-500/50" />
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <>
            {/* Stats bar */}
            {stats && view === 'browse' && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                {[
                  { label: 'Racines', value: stats.total_roots, color: 'text-green-400' },
                  { label: 'Mots mappés', value: stats.total_word_mappings, color: 'text-emerald-400' },
                  { label: 'Champs sémantiques', value: stats.semantic_field_count, color: 'text-teal-400' },
                  { label: 'Top racine', value: stats.top_roots[0]?.letters || '-', color: 'text-lime-400' },
                ].map(stat => (
                  <div key={stat.label} className="p-4 rounded-xl bg-green-900/20 border border-green-800/30">
                    <div className="text-xs text-green-500/70 mb-1">{stat.label}</div>
                    <div className={`text-2xl font-bold mono ${stat.color}`}>{stat.value}</div>
                  </div>
                ))}
              </div>
            )}

            {/* Filter indicator */}
            {selectedField && (
              <div className="flex items-center gap-2 mb-4 p-3 rounded-lg bg-green-800/20 border border-green-700/30">
                <span className="text-sm text-green-400">Champ sémantique:</span>
                <span className="text-sm font-medium text-green-200">{selectedField}</span>
                <button
                  onClick={() => { setSelectedField(null); setView('browse') }}
                  className="ml-auto text-green-500 hover:text-green-300 text-sm"
                >
                  Effacer
                </button>
              </div>
            )}

            {/* Browse View - Root list */}
            {(view === 'browse' || view === 'search') && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {roots.map(root => (
                  <button
                    key={root.id}
                    onClick={() => loadRootDetails(root.id)}
                    className="p-4 rounded-xl bg-green-900/20 border border-green-700/30 hover:border-green-500/50 transition-all text-left group"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <Leaf className="w-5 h-5 text-green-500/50 group-hover:text-green-400 transition-colors" />
                        <span className="text-2xl hebrew text-green-100">{root.letters}</span>
                      </div>
                      <span className="text-xs text-green-500/50 mono">{root.occurrence_count}</span>
                    </div>

                    <p className="text-sm text-green-300 mb-2">{root.transliteration}</p>
                    <p className="text-sm text-green-400/70 line-clamp-2">{root.meaning}</p>

                    {root.semantic_field && (
                      <div className="mt-3 pt-3 border-t border-green-800/30">
                        <span
                          className="px-2 py-1 rounded text-xs"
                          style={{ backgroundColor: root.color + '20', color: root.color }}
                        >
                          {root.semantic_field}
                        </span>
                      </div>
                    )}
                  </button>
                ))}
              </div>
            )}

            {/* Fields View */}
            {view === 'fields' && (
              <div className="space-y-6">
                <div className="text-center mb-8">
                  <h2 className="text-2xl font-bold text-green-100 mb-2">
                    Champs Sémantiques
                  </h2>
                  <p className="text-green-400/60">
                    Les racines groupées par domaine de sens
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {fields.map(field => (
                    <button
                      key={field.field}
                      onClick={() => loadByField(field.field)}
                      className="p-5 rounded-xl bg-green-900/20 border border-green-700/30 hover:border-green-500/50 transition-all text-left"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <span
                            className="w-4 h-4 rounded-full"
                            style={{ backgroundColor: field.color }}
                          />
                          <span className="font-medium text-green-100 capitalize">{field.field}</span>
                        </div>
                        <ChevronRight className="w-5 h-5 text-green-500/30" />
                      </div>

                      <div className="flex items-center justify-between text-sm">
                        <span className="text-green-400/70">{field.root_count} racines</span>
                        <span className="text-green-500/50 mono">{field.total_occurrences} occ.</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Binyanim View */}
            {view === 'binyanim' && (
              <div className="space-y-6">
                <div className="text-center mb-8">
                  <h2 className="text-2xl font-bold text-green-100 mb-2">
                    Les Sept Binyanim
                  </h2>
                  <p className="text-green-400/60">
                    Les formes verbales de l'hébreu biblique
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {binyanim.map(b => (
                    <div
                      key={b.form}
                      className="p-5 rounded-xl bg-green-900/20 border border-green-700/30"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <span
                            className="w-4 h-4 rounded-full"
                            style={{ backgroundColor: b.info.color }}
                          />
                          <span className="font-semibold text-green-100">{b.info.name}</span>
                        </div>
                        <span className="text-sm text-green-400/70 mono">{b.count}</span>
                      </div>

                      <p className="text-green-300/80 mb-3">{b.info.description}</p>

                      <div className="h-2 bg-green-950/50 rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full"
                          style={{
                            width: `${(b.count / binyanim[0].count) * 100}%`,
                            backgroundColor: b.info.color,
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                {/* Binyan explanation */}
                <div className="p-6 rounded-2xl bg-green-900/20 border border-green-700/30">
                  <h3 className="text-lg font-semibold text-green-100 mb-4">
                    À propos des Binyanim
                  </h3>
                  <p className="text-green-300/80 leading-relaxed">
                    Les binyanim (בִּנְיָנִים) sont les sept formes verbales de l'hébreu.
                    Chaque racine trilitère peut être conjuguée dans différents binyanim
                    pour exprimer des nuances de sens : actif/passif, simple/intensif, causatif.
                    Par exemple, la racine ק-ד-ש (qof-dalet-shin, "saint") donne :
                    <span className="text-green-200"> קָדַשׁ</span> (Qal: être saint),
                    <span className="text-green-200"> קִדֵּשׁ</span> (Piel: sanctifier),
                    <span className="text-green-200"> הִקְדִּישׁ</span> (Hiphil: consacrer).
                  </p>
                </div>
              </div>
            )}
          </>
        )}
      </main>

      {/* Stats footer */}
      {stats && !selectedRoot && (
        <div className="fixed bottom-4 right-4 p-4 rounded-xl bg-[#1a1f16]/90 border border-green-800/30 backdrop-blur-sm">
          <div className="flex items-center gap-6 text-sm">
            <div>
              <span className="text-green-500/50">Racines: </span>
              <span className="text-green-400 font-medium mono">{stats.total_roots}</span>
            </div>
            <div>
              <span className="text-green-500/50">Mappages: </span>
              <span className="text-green-400 font-medium mono">{stats.total_word_mappings}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
