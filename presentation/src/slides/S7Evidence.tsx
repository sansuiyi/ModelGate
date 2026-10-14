const research = [
  {
    source: 'FrugalGPT\nStanford · 2023',
    finding: 'Up to <strong>98% cost reduction</strong> while matching GPT-4 quality, by cascading through cheaper models first.',
  },
  {
    source: 'RouteLLM\nLMSYS · ICLR 2025',
    finding: '<strong>>85% cost reduction</strong> at 95% of GPT-4 performance using a trained routing model.',
  },
  {
    source: 'RouteLLM\nMatrix Factorization',
    finding: 'Only <strong>14% of queries</strong> actually require the most capable model. 86% can be answered by smaller ones.',
  },
  {
    source: 'IEA · 2025',
    finding: 'Global data center consumption <strong>415 TWh in 2024</strong>, projected to exceed 1,000 TWh by 2026.',
  },
]

const liveMetrics = [
  { label: 'Onboarding Time', placeholder: 'CONTRACT → ENDPOINT', unit: '< 30s' },
  { label: 'Classification Latency', placeholder: 'ARCH-ROUTER-1.5B', unit: '~50ms' },
  { label: 'Simple Tier Requests', placeholder: 'FILL IN AFTER DEMO', unit: '___%' },
  { label: 'Cost vs Always-Premium', placeholder: 'FILL IN AFTER DEMO', unit: '___%' },
]

export default function S7Evidence() {
  return (
    <div className="slide-inner" style={{ position: 'relative' }}>
      <span className="display-num" style={{ top: -30, right: -20, opacity: 0.3 }}>07</span>

      <div className="fade-up" style={{ marginBottom: 24 }}>
        <span className="eyebrow">Evidence</span>
        <h2 style={{
          fontFamily: 'var(--font-serif)',
          fontSize: 'clamp(22px, 3vw, 36px)',
          fontWeight: 400,
          color: 'var(--text)',
        }}>
          Academic validation + live system results.
        </h2>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 40, flex: 1 }}>
        {/* Research */}
        <div className="fade-up stagger-1">
          <div style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 10,
            letterSpacing: '0.14em',
            textTransform: 'uppercase',
            color: 'var(--text-3)',
            marginBottom: 16,
            paddingBottom: 10,
            borderBottom: '1px solid var(--border)',
          }}>
            Published Research
          </div>

          {research.map((r, i) => (
            <div key={i} style={{
              display: 'grid',
              gridTemplateColumns: '120px 1fr',
              gap: 20,
              padding: '14px 0',
              borderBottom: '1px solid var(--border)',
              alignItems: 'start',
            }}>
              <div style={{
                fontFamily: 'var(--font-mono)',
                fontSize: 10,
                color: 'var(--text-3)',
                letterSpacing: '0.04em',
                lineHeight: 1.6,
                whiteSpace: 'pre-line',
              }}>{r.source}</div>
              <p
                style={{
                  fontFamily: 'var(--font-sans)',
                  fontSize: 13,
                  color: 'var(--text-2)',
                  lineHeight: 1.6,
                }}
                dangerouslySetInnerHTML={{ __html: r.finding }}
              />
            </div>
          ))}
        </div>

        {/* Live results */}
        <div className="fade-up stagger-2" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <div style={{
            fontFamily: 'var(--font-mono)',
            fontSize: 10,
            letterSpacing: '0.14em',
            textTransform: 'uppercase',
            color: 'var(--text-3)',
            marginBottom: 6,
            paddingBottom: 10,
            borderBottom: '1px solid var(--border)',
          }}>
            ModelGate Live Results
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: 1,
            background: 'var(--border)',
            flex: 1,
          }}>
            {liveMetrics.map((m) => (
              <div key={m.label} style={{
                background: 'var(--bg)',
                padding: '20px',
                display: 'flex',
                flexDirection: 'column',
                gap: 8,
              }}>
                <div style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 9,
                  letterSpacing: '0.14em',
                  textTransform: 'uppercase',
                  color: 'var(--text-3)',
                }}>{m.label}</div>
                <div style={{
                  fontFamily: 'var(--font-serif)',
                  fontSize: 32,
                  fontWeight: 700,
                  color: 'var(--text)',
                  lineHeight: 1,
                }}>{m.unit}</div>
                <div style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 9,
                  color: 'var(--text-3)',
                  letterSpacing: '0.08em',
                }}>{m.placeholder}</div>
              </div>
            ))}
          </div>

          <div style={{
            border: '1px solid var(--border)',
            padding: '14px 16px',
            background: 'var(--surface)',
          }}>
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 9,
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
              color: 'var(--text-3)',
              marginBottom: 8,
            }}>Research Conclusion</div>
            <p style={{
              fontFamily: 'var(--font-serif)',
              fontStyle: 'italic',
              fontSize: 14,
              color: 'var(--text-2)',
              lineHeight: 1.6,
            }}>
              "Smart routing consistently delivers 85–98% cost reduction while maintaining quality indistinguishable from always-premium routing."
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
