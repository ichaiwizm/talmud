import { useState, useEffect } from 'react'
import Hub from './components/Hub'
import DivineObservatory from './components/interfaces/DivineObservatory'
import Constellation from './components/interfaces/Constellation'
import LivingScroll from './components/interfaces/LivingScroll'
import VoiceChamber from './components/interfaces/VoiceChamber'
import GematriaLab from './components/interfaces/GematriaLab'
import EmotionalTopology from './components/interfaces/EmotionalTopology'
import JourneyAtlas from './components/interfaces/JourneyAtlas'
import ShoreshNavigator from './components/interfaces/ShoreshNavigator'
import PatternForge from './components/interfaces/PatternForge'

type View = 'hub' | 'divine-observatory' | 'constellation' | 'living-scroll' | 'voice-chamber' | 'gematria-lab' | 'emotional-topology' | 'journey-atlas' | 'shoresh-navigator' | 'pattern-forge'

interface Stats {
  verses: number
  books: number
  names: number
  divine_names: number
}

export default function App() {
  const [view, setView] = useState<View>('hub')
  const [stats, setStats] = useState<Stats | null>(null)

  useEffect(() => {
    fetch('/api/stats').then(r => r.json()).then(setStats).catch(console.error)
  }, [])

  return (
    <div className="min-h-screen">
      {view === 'hub' && <Hub stats={stats} onSelect={(id) => setView(id as View)} />}
      {view === 'divine-observatory' && <DivineObservatory onBack={() => setView('hub')} />}
      {view === 'constellation' && <Constellation onBack={() => setView('hub')} />}
      {view === 'living-scroll' && <LivingScroll onBack={() => setView('hub')} />}
      {view === 'voice-chamber' && <VoiceChamber onBack={() => setView('hub')} />}
      {view === 'gematria-lab' && <GematriaLab onBack={() => setView('hub')} />}
      {view === 'emotional-topology' && <EmotionalTopology onBack={() => setView('hub')} />}
      {view === 'journey-atlas' && <JourneyAtlas onBack={() => setView('hub')} />}
      {view === 'shoresh-navigator' && <ShoreshNavigator onBack={() => setView('hub')} />}
      {view === 'pattern-forge' && <PatternForge onBack={() => setView('hub')} />}
    </div>
  )
}
