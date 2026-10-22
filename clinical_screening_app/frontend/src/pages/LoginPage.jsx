import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'

export default function LoginPage() {
  const nav = useNavigate()
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handle = (k, v) => setForm(p => ({ ...p, [k]: v }))

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Login failed')
      localStorage.setItem('spit_user', JSON.stringify({ username: data.username, name: data.name }))
      nav('/dashboard')
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-shell">

      {/* ── Left panel — Brand + illustration ── */}
      <div className="auth-panel-left">
        <div className="auth-panel-left-inner">

          {/* SPIT SWIFT logo */}
          <img
            src="/assets/spit-swift-logo.jpg"
            alt="SPIT SWIFT"
            className="auth-hero-logo"
          />

          {/* Illustration */}
          <img
            src="/assets/students-wellness.png"
            alt="Student Wellness Collaboration"
            className="auth-hero-image"
          />

          <h2 className="auth-panel-tagline">Student Wellness, Elevated.</h2>
          <p className="auth-panel-sub">
            AI-powered clinical screening for Major Depressive Disorder — designed for academic institutions.
          </p>

          <div className="auth-stats">
            <span className="auth-stat-chip"><strong>ROC-AUC</strong> 0.7507</span>
            <span className="auth-stat-chip"><strong>Optuna</strong> Tuned</span>
            <span className="auth-stat-chip"><strong>7</strong> Clinical Domains</span>
          </div>
        </div>
      </div>

      {/* ── Right panel — Glass form ── */}
      <div className="auth-panel-right">
        <div className="auth-card">

          <div className="auth-logo">
            <div className="auth-logo-mark">SS</div>
            <div>
              <div className="auth-brand">SPIT SWIFT</div>
              <div className="auth-sub">Clinical Screening System</div>
            </div>
          </div>

          <div className="auth-logo-divider" />

          <h2 className="auth-title">Welcome back</h2>
          <p className="auth-desc">
            Sign in to access your clinical depression screening dashboard.
          </p>

          {error && <div className="auth-error">{error}</div>}

          <form className="auth-form" onSubmit={submit}>
            <div className="auth-field">
              <label htmlFor="login-username">Username</label>
              <input
                id="login-username"
                type="text"
                autoComplete="username"
                required
                value={form.username}
                onChange={e => handle('username', e.target.value)}
                placeholder="Enter your username"
              />
            </div>
            <div className="auth-field">
              <label htmlFor="login-password">Password</label>
              <input
                id="login-password"
                type="password"
                autoComplete="current-password"
                required
                value={form.password}
                onChange={e => handle('password', e.target.value)}
                placeholder="Enter your password"
              />
            </div>
            <button className="auth-btn" type="submit" disabled={loading}>
              {loading ? 'Authenticating…' : 'Sign In →'}
            </button>
          </form>

          <p className="auth-switch">
            Don't have an account?{' '}
            <Link to="/signup">Create one</Link>
          </p>
        </div>

        <div className="auth-footer">
          <span>SPIT SWIFT v2.0</span>
          <span className="auth-footer-dot">·</span>
          <span>Optuna-tuned LR</span>
          <span className="auth-footer-dot">·</span>
          <span>ROC-AUC 0.7507</span>
        </div>
      </div>

    </div>
  )
}
