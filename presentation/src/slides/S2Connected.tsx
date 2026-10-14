export default function S2Connected() {
  const stats = [
    { num: '180×', label: 'more energy consumed by premium models vs small models per query' },
    { num: '50–90%', label: 'of enterprise AI inference spend wasted on overprovisioned models' },
    { num: '$37B', label: 'enterprise GenAI spend in 2025 — up 3.2× year-over-year' },
    { num: '51%', label: 'of organizations can actually measure their AI ROI' },
  ]

  return (
    <div className="slide-inner" style={{ position: 'relative' }}>
      <span className="display-num" style={{ top: -30, right: -20, opacity: 0.3 }}>02</span>

      {/* Header */}
      <div className="fade-up" style={{ marginBottom: 40 }}>
        <span className="eyebrow">The Assurant Way</span>
        <h2 style={{
          fontFamily: 'var(--font-serif)',
          fontSize: 'clamp(28px, 4vw, 44px)',
          fontWeight: 400,
          lineHeight: 1.2,
          color: 'var(--text)',
          maxWidth: 640,
          marginBottom: 8,
        }}>
          Helping people thrive in a connected world.
        </h2>
        <p style={{
          fontFamily: 'var(--font-sans)',
          fontSize: 15,
          color: 'var(--text-3)',
          fontStyle: 'italic',
        }}>
          The connected world runs on AI. AI is expensive, wasteful, and impossible to configure correctly at scale.
        </p>
      </div>

      <hr className="rule fade-up stagger-1" style={{ marginBottom: 32 }} />

      {/* Stats grid */}
      <div className="fade-up stagger-2" style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: 1,
        background: 'var(--border)',
        border: '1px solid var(--border)',
        flex: 1,
      }}>
        {stats.map((s, i) => (
          <div key={i} style={{
            background: 'var(--bg)',
            padding: '28px 32px',
            display: 'flex',
            flexDirection: 'column',
            gap: 10,
          }}>
            <div style={{
              fontFamily: 'var(--font-serif)',
              fontSize: 'clamp(36px, 5vw, 56px)',
              fontWeight: 700,
              lineHeight: 1,
              color: 'var(--text)',
            }}>
              {s.num}
            </div>
            <p style={{
              fontFamily: 'var(--font-sans)',
              fontSize: 13,
              color: 'var(--text-2)',
              lineHeight: 1.55,
              maxWidth: 280,
            }}>
              {s.label}
            </p>
          </div>
        ))}
      </div>

      {/* Footer note */}
      <div className="fade-up stagger-3" style={{ marginTop: 20 }}>
        <p style={{
          fontFamily: 'var(--font-serif)',
          fontStyle: 'italic',
          fontSize: 14,
          color: 'var(--text-3)',
        }}>
          "Without security and efficient application infrastructure, we are at risk of increasing the waste and consumption with our day-to-day tools." — Assurant Challenge Statement
        </p>
      </div>
    </div>
  )
}
