import React, { useState } from 'react'

/**
 * Collapsible section card matching Image 2:
 * Number badge, title, chevron button, and content body.
 */
export default function CollapsibleCard({
  number,
  title,
  children,
  defaultOpen = true,
  className = '',
}) {
  const [open, setOpen] = useState(defaultOpen)

  return (
    <div className={`swift-card-section ${className}`}>
      <div
        className={`swift-card-header ${open ? 'is-open' : ''}`}
        onClick={() => setOpen(!open)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && setOpen(!open)}
      >
        <div className="swift-card-header-left">
          {number && <span className="swift-num-badge">{number}</span>}
          <span className="swift-card-title">{title}</span>
        </div>
        <span className="swift-chevron">{open ? '▾' : '▸'}</span>
      </div>
      {open && <div className="swift-card-body">{children}</div>}
    </div>
  )
}
