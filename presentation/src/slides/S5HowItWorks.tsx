const phase1Steps = [
  { title: 'Upload Contract', desc: 'PDF or text — SLA, privacy docs, custom instructions' },
  { title: 'LLM Extraction', desc: 'Frontier model reads and parses all constraints from the document' },
  { title: 'Customer AI Profile', desc: 'Region, providers, latency target, cost sensitivity, routing tiers — all structured' },
  { title: 'Endpoint Live', desc: '/{customer}/v1/chat/completions — OpenAI-compatible, ready immediately' },
]

const tiers = [
  {
    label: 'Simple',
    models: ['GPT 5.4 nano', 'Gemini 3.1 Flash Lite', 'Haiku 4.5'],
    note: 'FAQ, greetings, status — ~300ms',
  },
  {
    label: 'Medium',
    models: ['GPT 5.4 mini', 'Sonnet 4.6', 'Grok 4.1 Fast'],
    note: 'Summarize, explain, analyze — ~700ms',
  },
  {
    label: 'Complex',
    models: ['GPT 5.4', 'Opus 4.6', 'Gemini 3.1 Pro'],
    note: 'Multi-doc reasoning, code, legal — ~1500ms',
  },
]

export default function S5HowItWorks() {
  return (
    <div className="slide-inner" style={{ position: 'relative' }}>
      <span className="display-num" style={{ top: -30, right: -20, opacity: 0.3 }}>05</span>

      <div className="fade-up" style={{ marginBottom: 24 }}>
        <span className="eyebrow">System Architecture</span>
        <h2 style={{
          fontFamily: 'var(--font-serif)',
          fontSize: 'clamp(22px, 3vw, 36px)',
          fontWeight: 400,
          color: 'var(--text)',
        }}>
          Two phases. Fully automated. No ongoing effort.
        </h2>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32, flex: 1 }}>
        {/* Phase 1 */}
        <div className="fade-up stagger-1">
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            marginBottom: 20,
            paddingBottom: 12,
            borderBottom: '1px solid var(--border)',
          }}>
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 10,
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
              color: 'var(--text-3)',
            }}>Phase 01</span>
            <span style={{
              fontFamily: 'var(--font-serif)',
              fontSize: 17,
              color: 'var(--text)',
            }}>Onboarding</span>
            <span className="tag" style={{ marginLeft: 'auto' }}>≈ 30 seconds</span>
          </div>

          <div className="flow">
            {phase1Steps.map((step, i) => (
              <div key={i} style={{ display: 'flex', gap: 0, marginBottom: 0 }}>
                {/* Connector column */}
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  width: 32,
                  flexShrink: 0,
                }}>
                  <div style={{
                    width: 6,
                    height: 6,
                    borderRadius: '50%',
                    border: '1px solid var(--border-2)',
                    background: 'var(--bg)',
                    marginTop: 16,
                    flexShrink: 0,
                    position: 'relative',
                    zIndex: 1,
                  }} />
                  {i < phase1Steps.length - 1 && (
                    <div style={{
                      width: 1,
                      flex: 1,
                      background: 'var(--border)',
                      minHeight: 16,
                    }} />
                  )}
                </div>

                {/* Content */}
                <div style={{
                  flex: 1,
                  padding: '10px 0 16px 12px',
                }}>
                  <div style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: 11,
                    color: 'var(--text)',
                    fontWeight: 600,
                    marginBottom: 3,
                    letterSpacing: '0.04em',
                  }}>{step.title}</div>
                  <div style={{
                    fontFamily: 'var(--font-sans)',
                    fontSize: 12,
                    color: 'var(--text-3)',
                    lineHeight: 1.5,
                  }}>{step.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Phase 2 */}
        <div className="fade-up stagger-2">
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            marginBottom: 20,
            paddingBottom: 12,
            borderBottom: '1px solid var(--border)',
          }}>
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 10,
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
              color: 'var(--text-3)',
            }}>Phase 02</span>
            <span style={{
              fontFamily: 'var(--font-serif)',
              fontSize: 17,
              color: 'var(--text)',
            }}>Runtime Routing</span>
            <span className="tag" style={{ marginLeft: 'auto' }}>~50ms overhead</span>
          </div>

          {/* Pipeline */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            marginBottom: 24,
            flexWrap: 'wrap',
          }}>
            {['Prompt In', 'Classify', 'Filter Policy', 'Score', 'Route', 'Response'].map((step, i, arr) => (
              <div key={step} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <div style={{
                  padding: '5px 10px',
                  border: '1px solid var(--border)',
                  fontFamily: 'var(--font-mono)',
                  fontSize: 10,
                  color: i === 0 || i === arr.length - 1 ? 'var(--text)' : 'var(--text-2)',
                  letterSpacing: '0.06em',
                  background: i === 0 || i === arr.length - 1 ? 'var(--surface-2)' : 'var(--bg)',
                }}>{step}</div>
                {i < arr.length - 1 && (
                  <span style={{ color: 'var(--text-3)', fontSize: 10 }}>→</span>
                )}
              </div>
            ))}
          </div>

          {/* Tier table */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 1, background: 'var(--border)' }}>
            {tiers.map((tier) => (
              <div key={tier.label} style={{
                background: 'var(--bg)',
                padding: '14px 16px',
                display: 'grid',
                gridTemplateColumns: '60px 1fr',
                gap: 12,
              }}>
                <div style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: 9,
                  letterSpacing: '0.14em',
                  textTransform: 'uppercase',
                  color: 'var(--text-3)',
                  border: '1px solid var(--border)',
                  padding: '3px 6px',
                  alignSelf: 'start',
                  textAlign: 'center',
                }}>{tier.label}</div>
                <div>
                  <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap', marginBottom: 5 }}>
                    {tier.models.map(m => (
                      <span key={m} className="tag tag--lit" style={{ fontSize: 10 }}>{m}</span>
                    ))}
                  </div>
                  <div style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: 10,
                    color: 'var(--text-3)',
                  }}>{tier.note}</div>
                </div>
              </div>
            ))}
          </div>

          <div style={{ marginTop: 12 }}>
            <p style={{
              fontFamily: 'var(--font-sans)',
              fontSize: 12,
              color: 'var(--text-3)',
              lineHeight: 1.5,
            }}>
              Classifier: <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-2)' }}>katanemo/Arch-Router-1.5B</span> on GPU,
              with keyword heuristic fallback. Filter enforces region, provider allowlist, forbidden providers.
              Score optimises for customer objective (latency / cost / quality).
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
