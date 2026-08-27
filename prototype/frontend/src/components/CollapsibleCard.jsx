import { useState } from 'react'

export default function CollapsibleCard({ title, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen)

  return (
    <div className="section-card">
      <div
        className={`section-header ${open ? 'open' : ''}`}
        onClick={() => setOpen(!open)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && setOpen(!open)}
      >
        <span className="section-title">{title}</span>
        <span className="section-chevron">{open ? '▾' : '▸'}</span>
      </div>
      {open && <div className="section-body">{children}</div>}
    </div>
  )
}
