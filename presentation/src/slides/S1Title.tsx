export default function S1Title() {
  return (
    <div className="slide-inner" style={{ position: 'relative', justifyContent: 'center' }}>

      {/* Background ghost number */}
      <span className="display-num" style={{ top: -20, left: -10, opacity: 0.35 }}>01</span>

      {/* Top rule + eyebrow */}
      <div style={{ position: 'absolute', top: 52, left: 40, right: 40 }}>
        <hr className="rule" />
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 14 }}>
          <span className="eyebrow" style={{ marginBottom: 0 }}>KSU Social Good Hackathon 2026</span>
          <span className="eyebrow" style={{ marginBottom: 0 }}>Assurant Track</span>
        </div>
      </div>

      {/* Hero */}
      <div className="fade-up" style={{ position: 'relative', zIndex: 1 }}>
        <div style={{ marginBottom: 8 }}>
          <span className="eyebrow">Contract-Aware AI Control Plane</span>
        </div>
        <h1 style={{
          fontFamily: 'var(--font-serif)',
          fontSize: 'clamp(64px, 11vw, 128px)',
          fontWeight: 700,
          lineHeight: 0.9,
          letterSpacing: '-0.02em',
          color: 'var(--text)',
          marginBottom: 32,
        }}>
          Model<br />Gate
        </h1>
        <hr className="rule rule--short" style={{ marginBottom: 28 }} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {['One line of code.', 'Immediate savings.', 'No friction.'].map((line, i) => (
            <p key={i} className={`fade-up stagger-${i + 2}`} style={{
              fontFamily: 'var(--font-sans)',
              fontSize: 18,
              fontWeight: 300,
              color: i === 0 ? 'var(--text)' : 'var(--text-3)',
              letterSpacing: '0.01em',
            }}>
              {line}
            </p>
          ))}
        </div>
      </div>

      {/* Bottom rule */}
      <div style={{ position: 'absolute', bottom: 72, left: 40, right: 40 }}>
        <hr className="rule" />
        <div style={{ marginTop: 14, display: 'flex', gap: 12 }}>
          <span className="tag tag--lit">FastAPI + Python</span>
          <span className="tag tag--lit">Next.js + TypeScript</span>
          <span className="tag tag--lit">Arch-Router-1.5B</span>
          <span className="tag tag--lit">OpenRouter</span>
          <span className="tag tag--lit">Docker</span>
        </div>
      </div>
    </div>
  )
}
