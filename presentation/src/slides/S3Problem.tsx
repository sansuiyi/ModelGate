const rows = [
  {
    who: 'Developers & Product Teams',
    scale: 'Millions globally',
    problem: 'No time to evaluate 200+ models — pick one premium option and never revisit it.',
    cost: 'Overpay by 10–30×',
  },
  {
    who: 'Enterprise Customers',
    scale: 'Every AI contract signed',
    problem: 'Contract constraints manually translated into config — or silently ignored. Compliance risk.',
    cost: 'Legal exposure',
  },
  {
    who: 'End Users',
    scale: 'Billions of requests/day',
    problem: 'Simple queries routed to slow premium models. "What is your return policy?" waits 2 seconds.',
    cost: 'Poor experience',
  },
  {
    who: 'AI Data Centers',
    scale: 'Global GPU clusters',
    problem: 'Unnecessary load on premium GPU clusters from queries that a small model would answer perfectly.',
    cost: 'Wasted capacity',
  },
  {
    who: 'The Environment',
    scale: 'Planetary scale',
    problem: 'Premium reasoning models use ~39 Wh/query vs ~0.22 Wh for small models. 180× difference.',
    cost: '415 TWh/yr & rising',
  },
]

export default function S3Problem() {
  return (
    <div className="slide-inner" style={{ position: 'relative' }}>
      <span className="display-num" style={{ top: -30, right: -20, opacity: 0.3 }}>03</span>

      <div className="fade-up" style={{ marginBottom: 24 }}>
        <span className="eyebrow">The Problem Is Universal</span>
        <h2 style={{
          fontFamily: 'var(--font-serif)',
          fontSize: 'clamp(24px, 3.5vw, 38px)',
          fontWeight: 400,
          color: 'var(--text)',
          lineHeight: 1.2,
        }}>
          Every layer of the AI stack is affected.
        </h2>
      </div>

      <div className="fade-up stagger-1" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Table header */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '200px 1fr 160px',
          gap: 24,
          padding: '8px 0',
          borderBottom: '1px solid var(--border)',
          marginBottom: 0,
        }}>
          {['Affected Party', 'The Problem Today', 'Consequence'].map(h => (
            <span key={h} style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 10,
              letterSpacing: '0.14em',
              color: 'var(--text-3)',
              textTransform: 'uppercase',
            }}>{h}</span>
          ))}
        </div>

        {/* Table rows */}
        {rows.map((row, i) => (
          <div key={i} className={`fade-up stagger-${i + 2}`} style={{
            display: 'grid',
            gridTemplateColumns: '200px 1fr 160px',
            gap: 24,
            padding: '16px 0',
            borderBottom: '1px solid var(--border)',
            alignItems: 'start',
          }}>
            <div>
              <div style={{
                fontFamily: 'var(--font-sans)',
                fontSize: 14,
                fontWeight: 500,
                color: 'var(--text)',
                marginBottom: 4,
              }}>{row.who}</div>
              <div style={{
                fontFamily: 'var(--font-mono)',
                fontSize: 10,
                color: 'var(--text-3)',
              }}>{row.scale}</div>
            </div>
            <p style={{
              fontFamily: 'var(--font-sans)',
              fontSize: 13,
              color: 'var(--text-2)',
              lineHeight: 1.55,
            }}>{row.problem}</p>
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 11,
              color: 'var(--text-2)',
              borderLeft: '1px solid var(--border)',
              paddingLeft: 16,
              lineHeight: 1.5,
            }}>{row.cost}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
