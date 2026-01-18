import { useState, useEffect, useCallback } from 'react'
import { ArrowLeft, BookOpen, ChevronLeft, ChevronRight, Sparkles } from 'lucide-react'

const BOOKS = ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy']

const EMOTION_GRADIENTS: Record<string, string> = {
  joy: 'from-amber-100/40 to-yellow-50/20',
  love: 'from-rose-100/40 to-pink-50/20',
  awe: 'from-violet-100/40 to-purple-50/20',
  hope: 'from-emerald-100/40 to-green-50/20',
  fear: 'from-indigo-100/40 to-blue-50/20',
  anger: 'from-red-100/40 to-orange-50/20',
  sorrow: 'from-blue-100/40 to-slate-50/20',
  neutral: 'from-stone-100/30 to-stone-50/10',
}

interface Verse {
  id: number
  number: number
  ref: string
  text_hebrew: string
  text_english: string
  emotion: string | null
  intensity: number
  tension: number
  polarity: number
}

interface Word {
  id: number
  position: number
  word: string
  normalized: string
  gematria: number
  root: string | null
  root_meaning: string | null
  root_id: number | null
}

interface Speech {
  verse_id: number
  verse_num: number
  speaker_name: string
  speech_type: string | null
  is_divine: boolean
  text: string
}

interface Chapter {
  number: number
  verses: number
}

interface Props {
  onBack: () => void
}

export default function LivingScroll({ onBack }: Props) {
  const [book, setBook] = useState('Genesis')
  const [chapter, setChapter] = useState(1)
  const [chapters, setChapters] = useState<Chapter[]>([])
  const [verses, setVerses] = useState<Verse[]>([])
  const [words, setWords] = useState<Map<number, Word[]>>(new Map())
  const [speech, setSpeech] = useState<Speech[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedVerseId, setSelectedVerseId] = useState<number | null>(null)
  const [highlightedRootId, setHighlightedRootId] = useState<number | null>(null)
  const [hoveredWord, setHoveredWord] = useState<Word | null>(null)

  // Load chapters for book
  useEffect(() => {
    fetch(`/api/scroll/chapters?book=${book}`)
      .then(r => r.json())
      .then(data => {
        setChapters(data)
        setChapter(1)
      })
      .catch(console.error)
  }, [book])

  // Load verses and speech for chapter
  useEffect(() => {
    setLoading(true)
    Promise.all([
      fetch(`/api/scroll/verses?book=${book}&chapter=${chapter}`).then(r => r.json()),
      fetch(`/api/scroll/speech?book=${book}&chapter=${chapter}`).then(r => r.json()),
    ]).then(([verseData, speechData]) => {
      setVerses(verseData)
      setSpeech(speechData)
      setWords(new Map())
      setSelectedVerseId(null)
      setLoading(false)
    }).catch(console.error)
  }, [book, chapter])

  // Load words for a verse when selected
  const loadWords = useCallback(async (verseId: number) => {
    if (words.has(verseId)) return
    const data = await fetch(`/api/scroll/words/${verseId}`).then(r => r.json())
    setWords(prev => new Map(prev).set(verseId, data))
  }, [words])

  const handleVerseClick = (verseId: number) => {
    if (selectedVerseId === verseId) {
      setSelectedVerseId(null)
    } else {
      setSelectedVerseId(verseId)
      loadWords(verseId)
    }
  }

  const handleWordHover = (word: Word | null) => {
    setHoveredWord(word)
    setHighlightedRootId(word?.root_id || null)
  }

  // Get speech for a verse
  const getVerseSpeeches = (verseId: number) => speech.filter(s => s.verse_id === verseId)

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50/50 to-yellow-50">
      {/* Parchment texture overlay */}
      <div
        className="fixed inset-0 pointer-events-none opacity-30"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%' height='100%' filter='url(%23noise)' opacity='0.4'/%3E%3C/svg%3E")`,
        }}
      />

      {/* Header */}
      <header className="sticky top-0 z-30 backdrop-blur-sm bg-amber-50/80 border-b border-amber-200/50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={onBack}
              className="p-2.5 rounded-xl bg-amber-100 hover:bg-amber-200 border border-amber-300/50 transition-all"
            >
              <ArrowLeft className="w-5 h-5 text-amber-800" />
            </button>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shadow-lg shadow-amber-300/30">
                <BookOpen className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-amber-900" style={{ fontFamily: 'Frank Ruhl Libre, serif' }}>
                  Living Scroll
                </h1>
                <p className="text-sm text-amber-600">Le texte qui respire</p>
              </div>
            </div>
          </div>

          {/* Book & Chapter selector */}
          <div className="flex items-center gap-3">
            <select
              value={book}
              onChange={e => setBook(e.target.value)}
              className="px-4 py-2 rounded-lg bg-white/80 border border-amber-300 text-amber-900 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-amber-400"
            >
              {BOOKS.map(b => (
                <option key={b} value={b}>{b}</option>
              ))}
            </select>

            <div className="flex items-center gap-1 bg-white/80 rounded-lg border border-amber-300 p-1">
              <button
                onClick={() => setChapter(c => Math.max(1, c - 1))}
                disabled={chapter === 1}
                className="p-1.5 rounded hover:bg-amber-100 disabled:opacity-30 transition-all"
              >
                <ChevronLeft className="w-4 h-4 text-amber-700" />
              </button>
              <span className="px-3 text-sm font-medium text-amber-900 min-w-[60px] text-center">
                Ch. {chapter}
              </span>
              <button
                onClick={() => setChapter(c => Math.min(chapters.length, c + 1))}
                disabled={chapter === chapters.length}
                className="p-1.5 rounded hover:bg-amber-100 disabled:opacity-30 transition-all"
              >
                <ChevronRight className="w-4 h-4 text-amber-700" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main scroll area */}
      <main className="max-w-4xl mx-auto px-6 py-8">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="flex flex-col items-center gap-4">
              <div className="w-12 h-12 rounded-full border-2 border-amber-300 border-t-amber-600 animate-spin" />
              <span className="text-amber-600 text-sm">Déroulement du parchemin...</span>
            </div>
          </div>
        ) : (
          <div className="space-y-1">
            {verses.map((verse, idx) => {
              const verseSpeeches = getVerseSpeeches(verse.id)
              const isSelected = selectedVerseId === verse.id
              const verseWords = words.get(verse.id) || []
              const emotionGradient = EMOTION_GRADIENTS[verse.emotion || 'neutral']

              return (
                <div
                  key={verse.id}
                  className="relative"
                  style={{ animationDelay: `${idx * 30}ms` }}
                >
                  {/* Divine speech indicator */}
                  {verseSpeeches.some(s => s.is_divine) && (
                    <div className="absolute -left-8 top-4">
                      <Sparkles className="w-5 h-5 text-amber-500" />
                    </div>
                  )}

                  {/* Verse card */}
                  <div
                    onClick={() => handleVerseClick(verse.id)}
                    className={`
                      relative p-5 rounded-xl cursor-pointer transition-all duration-300
                      bg-gradient-to-r ${emotionGradient}
                      border border-amber-200/50
                      hover:border-amber-300 hover:shadow-lg hover:shadow-amber-200/30
                      ${isSelected ? 'ring-2 ring-amber-400 shadow-xl shadow-amber-200/40' : ''}
                    `}
                    style={{
                      transform: `scale(${1 + verse.intensity * 0.02})`,
                    }}
                  >
                    {/* Verse number */}
                    <span className="absolute top-2 right-3 text-xs font-medium text-amber-500/70">
                      {verse.number}
                    </span>

                    {/* Hebrew text */}
                    <p
                      className="text-2xl leading-relaxed text-amber-950 text-right mb-3"
                      style={{ fontFamily: 'Frank Ruhl Libre, serif' }}
                      dir="rtl"
                    >
                      {verse.text_hebrew}
                    </p>

                    {/* English translation */}
                    <p className="text-sm text-amber-700/80 leading-relaxed">
                      {verse.text_english}
                    </p>

                    {/* Emotion & tension indicators */}
                    <div className="flex items-center gap-4 mt-3 pt-3 border-t border-amber-200/50">
                      {verse.emotion && (
                        <span className="text-xs text-amber-600 capitalize">
                          {verse.emotion}
                        </span>
                      )}
                      <div className="flex-1 h-1 bg-amber-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-amber-400 to-orange-400 rounded-full transition-all"
                          style={{ width: `${verse.tension * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-amber-500">
                        Tension: {Math.round(verse.tension * 100)}%
                      </span>
                    </div>

                    {/* Direct speech badges */}
                    {verseSpeeches.length > 0 && (
                      <div className="flex flex-wrap gap-2 mt-3">
                        {verseSpeeches.map((s, i) => (
                          <span
                            key={i}
                            className={`
                              px-2 py-1 rounded-full text-xs font-medium
                              ${s.is_divine
                                ? 'bg-gradient-to-r from-amber-400 to-yellow-300 text-amber-900 shadow-sm'
                                : 'bg-amber-100 text-amber-700'}
                            `}
                          >
                            {s.is_divine ? '✨ Divine' : s.speech_type || 'Speech'}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Expanded word analysis */}
                  {isSelected && verseWords.length > 0 && (
                    <div className="mt-2 p-4 rounded-xl bg-white/60 border border-amber-200 backdrop-blur-sm animate-[fadeIn_0.3s_ease-out]">
                      <h4 className="text-xs font-medium text-amber-600 mb-3 uppercase tracking-wider">
                        Analyse des mots
                      </h4>
                      <div className="flex flex-wrap gap-2 justify-end" dir="rtl">
                        {verseWords.map(word => {
                          const isHighlighted = highlightedRootId && word.root_id === highlightedRootId
                          return (
                            <div
                              key={word.id}
                              onMouseEnter={() => handleWordHover(word)}
                              onMouseLeave={() => handleWordHover(null)}
                              className={`
                                group relative px-3 py-2 rounded-lg cursor-pointer transition-all
                                ${isHighlighted
                                  ? 'bg-amber-400 text-amber-950 scale-110 shadow-lg'
                                  : 'bg-amber-50 hover:bg-amber-100 text-amber-800'}
                              `}
                            >
                              <span
                                className="text-lg block"
                                style={{ fontFamily: 'Frank Ruhl Libre, serif' }}
                              >
                                {word.word}
                              </span>
                              <span className="text-[10px] text-amber-500 block text-center">
                                {word.gematria}
                              </span>

                              {/* Tooltip */}
                              {hoveredWord?.id === word.id && (
                                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 p-3 rounded-lg bg-amber-900 text-white text-xs whitespace-nowrap z-10 shadow-xl">
                                  <div className="font-medium mb-1">Gematria: {word.gematria}</div>
                                  {word.root && (
                                    <>
                                      <div className="text-amber-200">Racine: {word.root}</div>
                                      {word.root_meaning && (
                                        <div className="text-amber-300 italic">{word.root_meaning}</div>
                                      )}
                                    </>
                                  )}
                                  <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-amber-900" />
                                </div>
                              )}
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </main>

      {/* Bottom legend */}
      <div className="fixed bottom-4 left-4 p-4 rounded-xl bg-white/80 border border-amber-200 backdrop-blur-sm shadow-lg">
        <h3 className="text-xs font-medium text-amber-600 mb-2 uppercase tracking-wider">
          Couleurs d'émotion
        </h3>
        <div className="grid grid-cols-2 gap-2">
          {Object.entries(EMOTION_GRADIENTS).slice(0, 6).map(([emotion, gradient]) => (
            <div key={emotion} className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${gradient} border border-amber-300/50`} />
              <span className="text-xs text-amber-700 capitalize">{emotion}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
