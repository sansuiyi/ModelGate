export default function S4Solution() {
  const benefits = [
    { label: 'API Compatible', desc: 'Full OpenAI spec — no SDK changes, no rewrites.' },
    { label: 'Policy Enforced', desc: 'Contract constraints become routing rules, automatically.' },
    { label: 'Always Optimal', desc: 'Cheapest model that satisfies every constraint, per request.' },
  ]

  return (
    <div className="slide-inner" style={{ position: 'relative' }}>
      <span className="display-num" style={{ top: -30, right: -20, opacity: 0.3 }}>04</span>

      <div className="fade-up" style={{ marginBottom: 28 }}>
        <span className="eyebrow">The Fix</span>
        <h2 style={{
          fontFamily: 'var(--font-serif)',
          fontSize: 'clamp(24px, 3.5vw, 40px)',
          fontWeight: 400,
          color: 'var(--text)',
          lineHeight: 1.15,
        }}>
          One line of code.<br />
          <span style={{ color: 'var(--text-3)', fontStyle: 'italic' }}>We handle everything else.</span>
        </h2>
      </div>

      {/* Code comparison */}
      <div className="fade-up stagger-1" style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: 12,
        marginBottom: 28,
      }}>
        {/* Before */}
        <div className="code-block">
          <div className="code-block__header">
            <span className="code-block__label">Before — every team today</span>
            <span className="tag" style={{ fontSize: 9 }}>status quo</span>
          </div>
          <div className="code-block__body">
            <pre>{`<span class="cm"># Direct provider call</span>
<span class="kw">from</span> openai <span class="kw">import</span> <span class="fn">OpenAI</span>

client = <span class="fn">OpenAI</span>(
    api_key=<span class="str">"sk-proj-..."</span>,
    base_url=<span class="str">"https://api.openai.com/v1"</span>
)

<span class="cm"># Same model. Every request. Forever.</span>
response = client.chat.completions.<span class="fn">create</span>(
    model=<span class="str">"gpt-5-4"</span>,
    messages=messages
)`}</pre>
          </div>
        </div>

        {/* After */}
        <div className="code-block" style={{ borderColor: 'var(--border-2)' }}>
          <div className="code-block__header" style={{ background: 'var(--surface-3)' }}>
            <span className="code-block__label code-block__label--after">After ModelGate</span>
            <span className="tag tag--lit" style={{ fontSize: 9 }}>one change</span>
          </div>
          <div className="code-block__body">
            <pre>{`<span class="cm"># Same code. Different URL.</span>
<span class="kw">from</span> openai <span class="kw">import</span> <span class="fn">OpenAI</span>

client = <span class="fn">OpenAI</span>(
    api_key=<span class="str">"&lt;your-token&gt;"</span>,
<span class="hl">    base_url=<span class="str">"https://gate/acme/v1"</span></span>
)

<span class="cm"># Right model. Every request. Automatically.</span>
response = client.chat.completions.<span class="fn">create</span>(
    model=<span class="str">"auto"</span>,
    messages=messages
)`}</pre>
          </div>
        </div>
      </div>

      {/* Arrow separator */}
      <div className="fade-up stagger-2" style={{
        display: 'flex',
        alignItems: 'center',
        gap: 16,
        marginBottom: 28,
      }}>
        <hr className="rule" style={{ flex: 1 }} />
        <span style={{
          fontFamily: 'var(--font-mono)',
          fontSize: 10,
          color: 'var(--text-3)',
          letterSpacing: '0.14em',
          textTransform: 'uppercase',
          whiteSpace: 'nowrap',
        }}>
          ModelGate intercepts, classifies, routes, responds
        </span>
        <hr className="rule" style={{ flex: 1 }} />
      </div>

      {/* Benefits row */}
      <div className="fade-up stagger-3" style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: 1,
        background: 'var(--border)',
        border: '1px solid var(--border)',
      }}>
        {benefits.map((b) => (
          <div key={b.label} style={{
            background: 'var(--bg)',
            padding: '18px 20px',
          }}>
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 10,
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
              color: 'var(--text-2)',
              marginBottom: 8,
            }}>{b.label}</div>
            <p style={{
              fontFamily: 'var(--font-sans)',
              fontSize: 13,
              color: 'var(--text-2)',
              lineHeight: 1.5,
            }}>{b.desc}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
