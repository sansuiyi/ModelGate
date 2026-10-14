const personas = [
  {
    num: '01',
    role: 'Persona 1',
    title: 'The Developer / Product Team',
    quote: '"I just want AI to work. I don\'t have time to evaluate every new model that ships each week."',
    before: 'Picks one premium model, overpays forever. No visibility into cost. Hope it\'s compliant.',
    after: 'One URL change. Automatic right-sizing every request. Done forever.',
  },
  {
    num: '02',
    role: 'Persona 2',
    title: 'The Enterprise Compliance Team',
    quote: '"Our contracts say EU-only data processing. I cannot trust that engineers will remember this."',
    before: 'Manual config per customer. Human error risk. One mistake = compliance violation.',
    after: 'Upload the contract. Routing enforces it automatically. Every request. Always.',
  },
  {
    num: '03',
    role: 'Persona 3',
    title: 'The Operations / Platform Team',
    quote: '"I have no idea what our AI is actually costing us, which models we\'re using, or why."',
    before: 'No visibility, no cost tracking, no routing logic, no model distribution data.',
    after: 'Live dashboard. Cost savings vs premium. Per-request routing explanations.',
  },
]

export default function S6Personas() {
  return (
    <div className="slide-inner" style={{ position: 'relative' }}>
      <span className="display-num" style={{ top: -30, right: -20, opacity: 0.3 }}>06</span>

      <div className="fade-up" style={{ marginBottom: 24 }}>
        <span className="eyebrow">Who It Serves</span>
        <h2 style={{
          fontFamily: 'var(--font-serif)',
          fontSize: 'clamp(22px, 3vw, 36px)',
          fontWeight: 400,
          color: 'var(--text)',
        }}>
          Three personas. One solution. Simultaneous benefit.
        </h2>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: 12,
        flex: 1,
      }}>
        {personas.map((p, i) => (
          <div key={p.num} className={`persona-card fade-up stagger-${i + 1}`}>
            <div className="persona-card__num">{p.num}</div>

            <div className="persona-card__header">
              <div className="persona-card__role">{p.role}</div>
              <div className="persona-card__title">{p.title}</div>
            </div>

            <div className="persona-card__quote">
              <p>{p.quote}</p>
            </div>

            <div className="persona-card__before-after">
              <div className="before-after-row">
                <span className="before-after-row__label">Before</span>
                <p className="before-after-row__text">{p.before}</p>
              </div>
              <hr style={{ border: 'none', borderTop: '1px solid var(--border)' }} />
              <div className="before-after-row">
                <span className="before-after-row__label">After</span>
                <p className="before-after-row__text after">{p.after}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
