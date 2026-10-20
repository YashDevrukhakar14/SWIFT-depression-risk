import { useLocation, useNavigate } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, ReferenceLine,
} from 'recharts'

const ZONE_COLOR = { green: '#16a34a', yellow: '#d97706', red: '#dc2626' }
const ZONE_BG    = { green: 'rgba(240, 253, 244, 0.85)', yellow: 'rgba(255, 251, 235, 0.85)', red: 'rgba(254, 242, 242, 0.85)' }
const ZONE_BORDER = { green: 'rgba(187, 247, 208, 0.9)', yellow: 'rgba(253, 230, 138, 0.9)', red: 'rgba(254, 202, 202, 0.9)' }

export default function ReportPage() {
  const { state } = useLocation()
  const nav = useNavigate()
  const result = state?.result
  const form   = state?.form
  const user   = JSON.parse(localStorage.getItem('spit_user') || '{}')
  const now    = new Date().toLocaleString('en-IN', { dateStyle: 'long', timeStyle: 'short' })

  if (!result) {
    return (
      <div className="report-empty">
        <div className="report-card" style={{ maxWidth: '420px', textAlign: 'center', padding: '2.5rem' }}>
          <p style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--gray-700)', marginBottom: '1.25rem' }}>
            No assessment report loaded.
          </p>
          <button onClick={() => nav('/dashboard')} className="back-btn">
            ← Return to Dashboard
          </button>
        </div>
      </div>
    )
  }

  const chartData = result.explanation?.map(e => ({
    name: e.feature.length > 26 ? e.feature.slice(0, 24) + '…' : e.feature,
    fullName: e.feature,
    contribution: e.contribution,
    fill: e.contribution >= 0 ? '#ef4444' : '#22c55e',
  })) || []

  const zone = result.risk_zone || 'green'

  return (
    <div className="report-shell">

      {/* ── Report Glass Toolbar ── */}
      <div className="report-toolbar">
        <div className="toolbar-brand">
          <img
            src="/assets/swift-logo.jpg"
            alt="SWIFT Report Logo"
            className="toolbar-logo-img"
          />
          <span className="nav-title sm">SWIFT — Clinical Report</span>
        </div>
        <div className="toolbar-actions">
          <button className="tool-btn" onClick={() => window.print()}>
            🖨 Print / Export PDF
          </button>
          <button className="tool-btn primary" onClick={() => nav('/dashboard')}>
            ← New Assessment
          </button>
        </div>
      </div>

      <div className="report-body" id="report-content">

        {/* ── Header Card with Official Logo ── */}
        <div className="report-header">
          <div className="report-header-left">
            <div className="report-logo-row">
              <img
                src="/assets/swift-logo.jpg"
                alt="SWIFT Report Logo"
                className="report-header-logo-img"
              />
              <div>
                <div className="report-org">SWIFT — Completed Wellness Report</div>
                <div className="report-model">Multi-Domain Passive EHR Screening · Major Depressive Disorder</div>
              </div>
            </div>
          </div>
          <div className="report-header-right">
            <div className="report-meta-row"><span>Clinician:</span><span>{user.name || user.username || 'Healthcare Practitioner'}</span></div>
            <div className="report-meta-row"><span>Generated:</span><span>{now}</span></div>
            <div className="report-meta-row"><span>Engine:</span><span>Optuna Logistic Regression</span></div>
          </div>
        </div>

        {/* ── Glass Risk Banner ── */}
        <div
          className="risk-banner"
          style={{
            background: ZONE_BG[zone],
            borderColor: ZONE_BORDER[zone],
          }}
        >
          <div className="risk-banner-left">
            <div className="risk-zone-dot" style={{ background: ZONE_COLOR[zone] }} />
            <div>
              <div className="risk-label-text" style={{ color: ZONE_COLOR[zone] }}>
                {result.risk_label}
              </div>
              <div className="risk-status">{result.clinical_status}</div>
            </div>
          </div>
          <div className="risk-banner-right">
            <div className="risk-pct" style={{ color: ZONE_COLOR[zone] }}>
              {result.probability_percent}%
            </div>
            <div className="risk-pct-label">Depressive Symptom Probability</div>
            <div className="risk-zone-chip" style={{ background: ZONE_COLOR[zone] }}>
              {result.risk_zone_label}
            </div>
          </div>
        </div>

        <div className="risk-zone-desc">{result.risk_zone_description}</div>

        {/* ── Two-column Glass Grid ── */}
        <div className="report-grid">

          {/* Left col */}
          <div className="report-col">

            {/* Calibration Metrics */}
            <div className="report-card">
              <div className="rcard-title">Model Calibration & Diagnostic Integrity</div>
              <div className="metrics-3">
                <div className="metric-box">
                  <div className="metric-val">{result.calibration_metrics.roc_auc.toFixed(4)}</div>
                  <div className="metric-lbl">ROC-AUC</div>
                </div>
                <div className="metric-box">
                  <div className="metric-val">{result.calibration_metrics.mcc.toFixed(4)}</div>
                  <div className="metric-lbl">MCC</div>
                </div>
                <div className="metric-box">
                  <div className="metric-val">{result.calibration_metrics.brier_score.toFixed(4)}</div>
                  <div className="metric-lbl">Brier Score</div>
                  <div className="brier-bar">
                    <div className="brier-fill" style={{ width: `${Math.min(100, (1 - result.calibration_metrics.brier_score) * 100)}%` }} />
                  </div>
                </div>
              </div>
              <div className="metrics-sub">
                Decision Threshold: <strong>{(result.decision_threshold * 100).toFixed(1)}%</strong> ·{' '}
                Traffic-light Threshold: <strong>{result.risk_threshold_percent}%</strong>
              </div>
            </div>

            {/* Engineered Features */}
            <div className="report-card">
              <div className="rcard-title">Computed Biomedical Features</div>
              <table className="eng-table">
                <tbody>
                  <tr><td>Body Mass Index (BMI)</td><td><strong>{result.engineered_features.bmi}</strong></td><td><span className="tag">{result.engineered_features.bmi_cat}</span></td></tr>
                  <tr><td>SBP / DBP Ratio</td><td><strong>{result.engineered_features.sbp_dbp_ratio}</strong></td><td></td></tr>
                  <tr><td>Heart Rate / BMI Ratio</td><td><strong>{result.engineered_features.heart_rate_bmi_ratio}</strong></td><td></td></tr>
                  <tr><td>Blood Pressure Category</td><td colSpan={2}><span className="tag">{result.engineered_features.bp_cat}</span></td></tr>
                </tbody>
              </table>
            </div>

            {/* Patient Input Summary */}
            {form && (
              <div className="report-card">
                <div className="rcard-title">Patient Input Summary</div>
                <table className="input-summary-table">
                  <tbody>
                    <tr><td>Age Group</td><td>{form.age}</td></tr>
                    <tr><td>Gender</td><td style={{ textTransform: 'capitalize' }}>{form.gender}</td></tr>
                    <tr><td>Field of Study</td><td style={{ textTransform: 'capitalize' }}>{form.field_of_study}</td></tr>
                    <tr><td>Year of University</td><td style={{ textTransform: 'capitalize' }}>{form.year_of_university}</td></tr>
                    <tr><td>Financial Difficulties</td><td>{form.financial_difficulties ? 'Yes' : 'No'}</td></tr>
                    <tr><td>Learning Disabilities</td><td>{form.learning_disabilities ? 'Yes' : 'No'}</td></tr>
                    <tr><td>Physical Activity</td><td style={{ textTransform: 'capitalize' }}>{form.physical_activity_3}</td></tr>
                    <tr><td>Cigarette Smoker</td><td style={{ textTransform: 'capitalize' }}>{form.cigarette_smoker_5}</td></tr>
                    <tr><td>Alcohol Drinker</td><td style={{ textTransform: 'capitalize' }}>{form.drinker_3}</td></tr>
                    <tr><td>Anxiety Symptoms</td><td>{form.anxiety_symptoms ? 'Yes' : 'No'}</td></tr>
                    <tr><td>Panic Attacks</td><td>{form.panic_attack_symptoms ? 'Yes' : 'No'}</td></tr>
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Right col */}
          <div className="report-col">

            {/* Feature Attribution Chart */}
            <div className="report-card">
              <div className="rcard-title">Feature Contribution Analysis (Log-odds Attribution)</div>
              <div className="chart-legend">
                <span><span className="legend-dot" style={{ background: '#ef4444' }} /> Risk-increasing</span>
                <span><span className="legend-dot" style={{ background: '#22c55e' }} /> Risk-reducing</span>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 16, top: 4, bottom: 4 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(226, 232, 240, 0.7)" horizontal={false} />
                  <XAxis type="number" stroke="#94a3b8" tick={{ fontSize: 10, fill: '#64748b' }} />
                  <YAxis
                    type="category" dataKey="name" width={162}
                    stroke="#94a3b8" tick={{ fontSize: 9, fill: '#64748b' }}
                  />
                  <ReferenceLine x={0} stroke="#475569" strokeWidth={1.5} />
                  <Tooltip
                    contentStyle={{ background: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)', border: '1px solid rgba(226, 232, 240, 0.9)', fontSize: '0.75rem', borderRadius: '8px', boxShadow: '0 8px 24px rgba(0,0,0,0.1)' }}
                    formatter={v => [v.toFixed(4), 'Log-odds shift']}
                    labelFormatter={(_, payload) => payload?.[0]?.payload?.fullName || ''}
                  />
                  <Bar dataKey="contribution" radius={[0, 4, 4, 0]}>
                    {chartData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Counterfactual Suggestions */}
            <div className="report-card">
              <div className="rcard-title">Clinical Counterfactual Intervention Suggestions</div>
              <div className="cf-list">
                {result.counterfactuals.map((cf, i) => (
                  <div key={i} className={`cf-item ${cf.probability_delta_percent > 0 ? 'cf-positive' : 'cf-neutral'}`}>
                    {cf.message && !cf.intervention ? (
                      <p className="cf-msg">{cf.message}</p>
                    ) : (
                      <>
                        <div className="cf-header">
                          <strong>{cf.intervention}</strong>
                          {cf.probability_delta_percent > 0 && (
                            <span className="cf-delta">−{cf.probability_delta_percent}%</span>
                          )}
                        </div>
                        <p className="cf-desc">{cf.message || `Projected probability: ${(cf.new_probability * 100).toFixed(1)}%`}</p>
                      </>
                    )}
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>{/* end report-grid */}

        {/* ── Disclaimer ── */}
        <div className="report-disclaimer">
          <strong>Clinical Disclaimer:</strong> This report is generated by a machine learning model
          trained on population-level observational data and is intended solely for research and
          academic screening purposes. It does not constitute a clinical diagnosis. All findings must
          be interpreted by a qualified healthcare professional.
        </div>

      </div>{/* end report-body */}
    </div>
  )
}
