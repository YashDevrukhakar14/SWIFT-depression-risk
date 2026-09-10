import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'

export default function SignupPage() {
  const nav = useNavigate()
  const [form, setForm] = useState({
    name: '', username: '', email: '', password: '', confirm: ''
  })
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)

  const handle = (k, v) => setForm(p => ({ ...p, [k]: v }))

  const submit = async (e) => {
    e.preventDefault()
    if (form.password !== form.confirm) {
      setError('Passwords do not match.')
      return
    }
    if (form.password.length < 6) {
      setError('Password must be at least 6 characters.')
      return
    }
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: form.name, username: form.username, email: form.email, password: form.password }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Sign-up failed')
      localStorage.setItem('spit_user', JSON.stringify({ username: form.username, name: form.name }))
      nav('/dashboard')
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-shell">
      <div className="auth-card auth-card-wide">
        <div className="auth-logo">
          <div className="auth-logo-mark">SS</div>
          <div>
            <div className="auth-brand">SPIT SWIFT</div>
            <div className="auth-sub">Clinical Screening System</div>
          </div>
        </div>

        <h2 className="auth-title">Create your account</h2>
        <p className="auth-desc">
          Register to access the clinical depression screening dashboard.
        </p>

        {error && <div className="auth-error">{error}</div>}

        <form className="auth-form" onSubmit={submit}>
          <div className="auth-grid-2">
            <div className="auth-field">
              <label htmlFor="signup-name">Full Name</label>
              <input
                id="signup-name"
                type="text"
                required
                value={form.name}
                onChange={e => handle('name', e.target.value)}
                placeholder="Dr. / Prof. / Mr. / Ms."
              />
            </div>
            <div className="auth-field">
              <label htmlFor="signup-username">Username</label>
              <input
                id="signup-username"
                type="text"
                required
                value={form.username}
                onChange={e => handle('username', e.target.value)}
                placeholder="Unique username"
              />
            </div>
          </div>
          <div className="auth-field">
            <label htmlFor="signup-email">Institutional Email</label>
            <input
              id="signup-email"
              type="email"
              required
              value={form.email}
              onChange={e => handle('email', e.target.value)}
              placeholder="you@institution.edu"
            />
          </div>
          <div className="auth-grid-2">
            <div className="auth-field">
              <label htmlFor="signup-password">Password</label>
              <input
                id="signup-password"
                type="password"
                required
                value={form.password}
                onChange={e => handle('password', e.target.value)}
                placeholder="Min. 6 characters"
              />
            </div>
            <div className="auth-field">
              <label htmlFor="signup-confirm">Confirm Password</label>
              <input
                id="signup-confirm"
                type="password"
                required
                value={form.confirm}
                onChange={e => handle('confirm', e.target.value)}
                placeholder="Re-enter password"
              />
            </div>
          </div>
          <button className="auth-btn" type="submit" disabled={loading}>
            {loading ? 'Creating Account…' : 'Create Account'}
          </button>
        </form>

        <p className="auth-switch">
          Already have an account?{' '}
          <Link to="/">Sign in</Link>
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
