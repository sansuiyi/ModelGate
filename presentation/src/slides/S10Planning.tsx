const mvpItems = [
  'Contract ingestion + LLM extraction pipeline',
  'Structured CustomerProfile JSON schema',
  'OpenAI-compatible proxy endpoint',
  'Arch-Router-1.5B GPU classifier + heuristic fallback',
  'Policy-filtered, objective-scored routing engine',
  'Full dashboard: stats, profiles, logs, playground',
]

const nextItems = [
  'Vector search over large contract doc sets',
  'Live provider health signals in routing',
  'Managed SaaS deployment (no Docker)',
  'Automatic model catalog updates',
  'Streaming response support',
]

const artifacts = [
  { num: '01', name: 'Architecture Diagram', desc: 'Full backend service map and routing pipeline' },
  { num: '02', name: 'Customer Profile Schema', desc: 'JSON schema for constraints, performance, routing preferences' },
  { num: '03', name: 'Routing Decision Flowchart', desc: 'Policy filter → score → select decision tree' },
  { num: '04', name: 'Dashboard Wireframes → UI', desc: 'All 5 views: overview, customers, profile, logs, playground' },
  { num: '05', name: 'Demo Script', desc: 'Step-by-step walkthrough with expected outputs and fallback plan' },
]

const team = [
  { domain: 'Backend Routing', items: 'Classifier, router engine, provider registry, policy filtering' },
  { domain: 'LLM Extraction', items: 'Extractor service, prompt engineering, profile schema, fallback profiles' },
  { domain: 'Frontend Dashboard', items: 'All Next.js pages, shadcn/ui components, Recharts visualizations' },
  { domain: 'Integration & Demo', items: 'Docker compose, OpenRouter integration, end-to-end testing, demo prep' },
]

export default function S10Planning() {
  return (
    <div className="slide-inner" style={{ position: 'relative' }}>
      <span className="display-num" style={{ top: -30, right: -20, opacity: 0.3 }}>10</span>

      <div className="fade-up" style={{ marginBottom: 20 }}>
        <span className="eyebrow">Planning & Execution</span>
        <h2 style={{
          fontFamily: 'var(--font-serif)',
          fontSize: 'clamp(20px, 2.8vw, 32px)',
          fontWeight: 400,
          color: 'var(--text)',
        }}>
          MVP scoped, artifacts produced, team distributed by domain.
        </h2>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, flex: 1, overflow: 'hidden' }}>
        {/* Left column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20, overflow: 'hidden' }}>
          {/* MVP Scope */}
          <div className="fade-up stagger-1">
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 10,
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
              color: 'var(--text-3)',
              marginBottom: 12,
              paddingBottom: 8,
              borderBottom: '1px solid var(--border)',
            }}>MVP Delivered</div>
            <ul style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {mvpItems.map((item, i) => (
                <li key={i} style={{ display: 'flex', gap: 10, alignItems: 'start' }}>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--text-3)', marginTop: 3 }}>✓</span>
                  <span style={{ fontFamily: 'var(--font-sans)', fontSize: 12, color: 'var(--text-2)', lineHeight: 1.5 }}>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Next iterations */}
          <div className="fade-up stagger-2">
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 10,
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
              color: 'var(--text-3)',
              marginBottom: 12,
              paddingBottom: 8,
              borderBottom: '1px solid var(--border)',
            }}>Subsequent Iterations</div>
            <ul style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {nextItems.map((item, i) => (
                <li key={i} style={{ display: 'flex', gap: 10, alignItems: 'start' }}>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--text-3)', marginTop: 3 }}>○</span>
                  <span style={{ fontFamily: 'var(--font-sans)', fontSize: 12, color: 'var(--text-3)', lineHeight: 1.5 }}>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Right column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20, overflow: 'hidden' }}>
          {/* Artifacts */}
          <div className="fade-up stagger-2">
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 10,
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
              color: 'var(--text-3)',
              marginBottom: 12,
              paddingBottom: 8,
              borderBottom: '1px solid var(--border)',
            }}>Design Artifacts (5)</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {artifacts.map((a) => (
                <div key={a.num} style={{ display: 'grid', gridTemplateColumns: '24px 1fr', gap: 8 }}>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 9, color: 'var(--text-3)', paddingTop: 1 }}>{a.num}</span>
                  <div>
                    <span style={{ fontFamily: 'var(--font-sans)', fontSize: 12, color: 'var(--text)', fontWeight: 500 }}>{a.name}</span>
                    <span style={{ fontFamily: 'var(--font-sans)', fontSize: 11, color: 'var(--text-3)', display: 'block' }}>{a.desc}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Team distribution */}
          <div className="fade-up stagger-3">
            <div style={{
              fontFamily: 'var(--font-mono)',
              fontSize: 10,
              letterSpacing: '0.14em',
              textTransform: 'uppercase',
              color: 'var(--text-3)',
              marginBottom: 12,
              paddingBottom: 8,
              borderBottom: '1px solid var(--border)',
            }}>Team Distribution (4 members)</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 1, background: 'var(--border)' }}>
              {team.map((t) => (
                <div key={t.domain} style={{
                  background: 'var(--bg)',
                  display: 'grid',
                  gridTemplateColumns: '160px 1fr',
                  gap: 12,
                  padding: '10px 12px',
                }}>
                  <div style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: 10,
                    color: 'var(--text-2)',
                    letterSpacing: '0.06em',
                  }}>{t.domain}</div>
                  <div style={{
                    fontFamily: 'var(--font-sans)',
                    fontSize: 11,
                    color: 'var(--text-3)',
                    lineHeight: 1.4,
                  }}>{t.items}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
