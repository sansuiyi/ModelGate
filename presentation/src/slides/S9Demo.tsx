const steps = [
  {
    num: '01',
    title: 'Onboard ACME Support',
    action: 'Upload contract → Click "Extract Profile"',
    expect: [
      'Region: EU-only (from GDPR clause)',
      'DeepSeek blocked (China-based provider restriction)',
      'Latency target: 1000ms',
      'Privacy tier: High (PII handling)',
      'Routing tiers auto-generated',
    ],
  },
  {
    num: '02',
    title: 'Copy the Endpoint',
    action: 'Profile page → Click copy on endpoint URL',
    expect: [
      'http://localhost:8000/acme-support/v1/chat/completions',
      'Drop into any OpenAI client',
      'No other code changes needed',
    ],
  },
  {
    num: '03',
    title: 'Send a Simple Prompt',
    action: 'Playground → Quick Prompt: "What is your return policy?"',
    expect: [
      'Classification: simple',
      'Routes to: GPT 5.4 nano',
      'Latency: ~300ms',
      'Cost: fraction of a cent',
    ],
  },
  {
    num: '04',
    title: 'Send a Complex Prompt',
    action: 'Playground → Quick Prompt: "Analyze liability exposure..."',
    expect: [
      'Classification: complex',
      'Routes to: Claude Opus 4.6',
      'Latency: ~1.5s',
      'Same endpoint. Different model. Automatic.',
    ],
  },
  {
    num: '05',
    title: 'View Dashboard Metrics',
    action: 'Navigate to main dashboard',
    expect: [
      'Model distribution pie chart',
      'Cost savings banner (ModelGate vs always-premium)',
      'Live request feed with routing explanations',
      'Provider breakdown by request count',
    ],
  },
]

export default function S9Demo() {
  return (
    <div className="slide-inner" style={{ position: 'relative' }}>
      <span className="display-num" style={{ top: -30, right: -20, opacity: 0.3 }}>09</span>

      <div className="fade-up" style={{ marginBottom: 24 }}>
        <span className="eyebrow">Live Demo</span>
        <h2 style={{
          fontFamily: 'var(--font-serif)',
          fontSize: 'clamp(22px, 3vw, 36px)',
          fontWeight: 400,
          color: 'var(--text)',
        }}>
          Five steps. One contract. Immediate routing.
        </h2>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(5, 1fr)',
        gap: 1,
        background: 'var(--border)',
        flex: 1,
      }}>
        {steps.map((step, i) => (
          <div key={step.num} className={`fade-up stagger-${i + 1}`} style={{
            background: 'var(--bg)',
            padding: '20px 16px',
            display: 'flex',
            flexDirection: 'column',
            gap: 12,
          }}>
            <div style={{
              fontFamily: 'var(--font-serif)',
              fontSize: 40,
              fontWeight: 700,
              color: 'var(--surface-3)',
              lineHeight: 1,
            }}>{step.num}</div>

            <div>
              <div style={{
                fontFamily: 'var(--font-sans)',
                fontSize: 14,
                fontWeight: 500,
                color: 'var(--text)',
                marginBottom: 6,
                lineHeight: 1.3,
              }}>{step.title}</div>
              <div style={{
                fontFamily: 'var(--font-mono)',
                fontSize: 10,
                color: 'var(--text-3)',
                lineHeight: 1.5,
                letterSpacing: '0.04em',
              }}>{step.action}</div>
            </div>

            <hr style={{ border: 'none', borderTop: '1px solid var(--border)' }} />

            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 6 }}>
              {step.expect.map((e, j) => (
                <li key={j} style={{ display: 'flex', gap: 8, alignItems: 'start' }}>
                  <span style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: 9,
                    color: 'var(--text-3)',
                    marginTop: 3,
                    flexShrink: 0,
                  }}>→</span>
                  <span style={{
                    fontFamily: 'var(--font-sans)',
                    fontSize: 12,
                    color: 'var(--text-2)',
                    lineHeight: 1.5,
                  }}>{e}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  )
}
