const impact = [
  { layer: 'Business',     desc: 'Eliminates 60–98% of AI inference spend through intelligent right-sizing',      stat: '60–98% saved' },
  { layer: 'Users',        desc: 'Simple queries get fast answers. Complex queries get powerful models.',           stat: 'Right model, always' },
  { layer: 'Data Centers', desc: 'Less unnecessary load on premium GPU clusters. Resources freed for real work.',   stat: 'Less waste' },
  { layer: 'Energy Grid',  desc: 'Up to 180× less energy per routed-away premium call. Thousands of calls saved.', stat: '180× difference' },
  { layer: 'Compliance',   desc: 'Contract constraints become routing rules. Enforced per request, automatically.', stat: 'Zero human error' },
]

export default function S8Close() {
  return (
    <div className="slide-inner" style={{ position: 'relative' }}>
      <span className="display-num" style={{ top: -30, right: -20, opacity: 0.3 }}>08</span>

      <div className="fade-up" style={{ marginBottom: 24 }}>
        <span className="eyebrow">Impact & Close</span>
        <h2 style={{
          fontFamily: 'var(--font-serif)',
          fontSize: 'clamp(22px, 3vw, 36px)',
          fontWeight: 400,
          color: 'var(--text)',
          lineHeight: 1.2,
        }}>
          One change. Benefits at every layer of the stack.
        </h2>
      </div>

      {/* Impact table */}
      <div className="fade-up stagger-1" style={{ flex: 1 }}>
        {/* Header */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '140px 1fr 160px',
          gap: 24,
          padding: '8px 0',
          borderBottom: '1px solid var(--border)',
        }}>
          {['Layer', 'How ModelGate Helps', 'Headline'].map(h => (
            <span key={h} style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 10,
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
              color: 'var(--text-3)',
            }}>{h}</span>
          ))}
        </div>

        {impact.map((row, i) => (
          <div key={row.layer} className={`fade-up stagger-${i + 2}`} style={{
            display: 'grid',
            gridTemplateColumns: '140px 1fr 160px',
            gap: 24,
            padding: '14px 0',
            borderBottom: '1px solid var(--border)',
            alignItems: 'center',
          }}>
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 11,
              letterSpacing: '0.1em',
              textTransform: 'uppercase',
              color: 'var(--text-2)',
            }}>{row.layer}</div>
            <p style={{
              fontFamily: 'var(--font-sans)',
              fontSize: 13,
              color: 'var(--text-2)',
              lineHeight: 1.5,
            }}>{row.desc}</p>
            <div style={{
              fontFamily: 'var(--font-serif)',
              fontSize: 14,
              color: 'var(--text)',
              fontStyle: 'italic',
              borderLeft: '1px solid var(--border)',
              paddingLeft: 16,
            }}>{row.stat}</div>
          </div>
        ))}
      </div>

      {/* Closing statement */}
      <div className="fade-up" style={{
        marginTop: 28,
        display: 'flex',
        alignItems: 'flex-end',
        justifyContent: 'space-between',
        gap: 32,
      }}>
        <div>
          <hr className="rule rule--short" style={{ marginBottom: 16 }} />
          <p style={{
            fontFamily: 'var(--font-serif)',
            fontStyle: 'italic',
            fontSize: 16,
            color: 'var(--text-2)',
            lineHeight: 1.6,
            maxWidth: 600,
          }}>
            "ModelGate is the lowest-friction AI optimization available today.
            You change one line of code. We eliminate thousands of wasteful premium model calls,
            automatically, before you finish reading this sentence."
          </p>
        </div>
        <div style={{ textAlign: 'right', flexShrink: 0 }}>
          <div style={{
            fontFamily: 'var(--font-serif)',
            fontSize: 48,
            fontWeight: 700,
            color: 'var(--text)',
            lineHeight: 1,
            letterSpacing: '-0.02em',
          }}>Thank you.</div>
          <div style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 10,
            letterSpacing: '0.14em',
            textTransform: 'uppercase',
            color: 'var(--text-3)',
            marginTop: 8,
          }}>KSU · Assurant Track · 2026</div>
        </div>
      </div>
    </div>
  )
}
