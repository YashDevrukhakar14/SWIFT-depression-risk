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
      <div className="auth-card">
        <div className="auth-logo">
          <div className="auth-logo-mark">SS</div>
          <div>
            <div className="auth-brand">SPIT SWIFT</div>
            <div className="auth-sub">Clinical Screening System</div>
          </div>
        </div>

        <h2 className="auth-title">Sign in to your account</h2>
        <p className="auth-desc">
          Multi-Domain Passive EHR Screening Model for Major Depressive Disorder
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
            {loading ? 'Authenticating…' : 'Sign In'}
          </button>
        </form>

        <p className="auth-switch">
          Don't have an account?{' '}
          <Link to="/signup">Create one</Link>
        </p>
      </div>

      <div className="auth-footer">
        <span>SPIT SWIFT v2.0</span>
        <span>·</span>
        <span>Optuna-tuned Logistic Regression</span>
        <span>·</span>
        <span>ROC-AUC 0.7507</span>
      </div>
    </div>
  )
}
