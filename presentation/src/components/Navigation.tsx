interface Props {
  current: number
  total: number
  onPrev: () => void
  onNext: () => void
  onGoTo: (i: number) => void
}

export default function Navigation({ current, total, onPrev, onNext, onGoTo }: Props) {
  return (
    <div className="nav">
      <span className="nav__counter">
        {String(current + 1).padStart(2, '0')} / {String(total).padStart(2, '0')}
      </span>

      <div className="nav__dots">
        {Array.from({ length: total }).map((_, i) => (
          <button
            key={i}
            className={`nav__dot ${i === current ? 'active' : ''}`}
            onClick={() => onGoTo(i)}
            aria-label={`Go to slide ${i + 1}`}
          />
        ))}
      </div>

      <div className="nav__arrows">
        <button className="nav__arrow" onClick={onPrev} aria-label="Previous slide">←</button>
        <button className="nav__arrow" onClick={onNext} aria-label="Next slide">→</button>
      </div>
    </div>
  )
}
