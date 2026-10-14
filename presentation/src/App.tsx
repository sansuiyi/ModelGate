import { useState, useEffect, useCallback } from 'react'
import ProgressBar from './components/ProgressBar'
import Navigation from './components/Navigation'
import S1Title from './slides/S1Title'
import S2Connected from './slides/S2Connected'
import S3Problem from './slides/S3Problem'
import S4Solution from './slides/S4Solution'
import S5HowItWorks from './slides/S5HowItWorks'
import S6Personas from './slides/S6Personas'
import S7Evidence from './slides/S7Evidence'
import S8Close from './slides/S8Close'
import S9Demo from './slides/S9Demo'
import S10Planning from './slides/S10Planning'

const SLIDES = [
  { component: S1Title,      label: 'Title' },
  { component: S2Connected,  label: 'The Assurant Way' },
  { component: S3Problem,    label: 'The Problem' },
  { component: S4Solution,   label: 'One Line of Code' },
  { component: S5HowItWorks, label: 'How It Works' },
  { component: S6Personas,   label: 'Three Personas' },
  { component: S7Evidence,   label: 'Evidence' },
  { component: S8Close,      label: 'Impact & Close' },
  { component: S9Demo,       label: 'Demo' },
  { component: S10Planning,  label: 'Planning' },
]

export default function App() {
  const [current, setCurrent] = useState(0)
  const [exiting, setExiting] = useState(false)
  const total = SLIDES.length

  const goTo = useCallback((idx: number) => {
    if (idx < 0 || idx >= total || idx === current || exiting) return
    setExiting(true)
    setTimeout(() => {
      setCurrent(idx)
      setExiting(false)
    }, 280)
  }, [current, exiting, total])

  const next = useCallback(() => goTo(current + 1), [current, goTo])
  const prev = useCallback(() => goTo(current - 1), [current, goTo])

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'ArrowDown') { e.preventDefault(); next() }
      if (e.key === 'ArrowLeft'  || e.key === 'ArrowUp')                   { e.preventDefault(); prev() }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [next, prev])

  const SlideComponent = SLIDES[current].component

  return (
    <div className="presentation">
      <ProgressBar current={current} total={total} />

      <div className="slide-label">
        {SLIDES[current].label}
      </div>

      <div key={current} className={`slide ${exiting ? 'exit' : ''}`}>
        <SlideComponent />
      </div>

      <Navigation
        current={current}
        total={total}
        onPrev={prev}
        onNext={next}
        onGoTo={goTo}
      />
    </div>
  )
}
