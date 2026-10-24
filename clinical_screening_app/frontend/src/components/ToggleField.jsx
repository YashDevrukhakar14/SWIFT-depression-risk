import React from 'react'

/**
 * ToggleField matching Image 2:
 * Pill track with knob and internal "Yes" / "No" text.
 */
export default function ToggleField({ label, id, value, onChange }) {
  return (
    <div className="swift-toggle-field">
      {label && <label htmlFor={id} className="swift-toggle-label">{label}</label>}
      <button
        id={id}
        type="button"
        role="switch"
        aria-checked={value}
        className={`swift-toggle-btn ${value ? 'active-yes' : 'active-no'}`}
        onClick={() => onChange(!value)}
      >
        <span className="swift-toggle-track">
          {value ? (
            <>
              <span className="swift-toggle-text text-yes">Yes</span>
              <span className="swift-toggle-thumb thumb-right" />
            </>
          ) : (
            <>
              <span className="swift-toggle-thumb thumb-left" />
              <span className="swift-toggle-text text-no">No</span>
            </>
          )}
        </span>
      </button>
    </div>
  )
}
