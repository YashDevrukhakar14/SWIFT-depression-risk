export default function ToggleField({ label, value, onChange }) {
  return (
    <div className="field-row">
      <label>{label}</label>
      <div
        className={`toggle ${value ? 'on' : ''}`}
        onClick={() => onChange(!value)}
        role="switch"
        aria-checked={value}
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && onChange(!value)}
      >
        <div className="toggle-knob" />
      </div>
    </div>
  )
}
