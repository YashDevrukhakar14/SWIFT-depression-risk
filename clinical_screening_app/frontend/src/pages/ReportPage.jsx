import { useLocation, useNavigate } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, ReferenceLine,
} from 'recharts'

const ZONE_COLOR = { green: '#16a34a', yellow: '#ca8a04', red: '#dc2626' }
const ZONE_BG    = { green: '#f0fdf4', yellow: '#fefce8', red: '#fef2f2' }

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
        <p>No report data found.</p>
        <button onClick={() => nav('/dashboard')} className="back-btn">← Return to Dashboard</button>
      </div>
    )
  }

  const chartData = result.explanation?.map(e => ({
    name: e.feature.length > 26 ? e.feature.slice(0, 24) + '…' : e.feature,
    fullName: e.feature,
    contribution: e.contribution,
    fill: e.contribution >= 0 ? '#dc2626' : '#16a34a',
  })) || []

  const zone = result.risk_zone || 'green'

  return (
    <div className="report-shell">

      {/* ── Report Toolbar ── */}
      <div className="report-toolbar">
        <div className="toolbar-brand">
          <span className="nav-logo-mark sm">SS</span>
          <span className="nav-title sm">SPIT SWIFT — Clinical Report</span>
        </div>
        <div className="toolbar-actions">
          <button className="tool-btn" onClick={() => window.print()}>🖨 Print / Export PDF</button>
          <button className="tool-btn primary" onClick={() => nav('/dashboard')}>← New Assessment</button>
        </div>
      </div>

      <div className="report-body" id="report-content">

        {/* ── Header ── */}
        <div className="report-header">
          <div className="report-header-left">
            <div className="report-logo-row">
              <span className="nav-logo-mark">SS</span>
              <div>
                <div className="report-org">SPIT SWIFT — Clinical Screening System</div>
                <div className="report-model">Multi-Domain Passive EHR Screening · Major Depressive Disorder</div>
              </div>
            </div>
          </div>
          <div className="report-header-right">
            <div className="report-meta-row"><span>Clinician</span><span>{user.name || user.username || '—'}</span></div>
            <div className="report-meta-row"><span>Generated</span><span>{now}</span></div>
            <div className="report-meta-row"><span>Model</span><span>Optuna-tuned Logistic Regression</span></div>
          </div>
        </div>

        <hr className="report-divider" />

        {/* ── Risk Banner ── */}
        <div className="risk-banner" style={{ background: ZONE_BG[zone], borderColor: ZONE_COLOR[zone] }}>
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
            <div className="risk-pct" style={{ color: ZONE_COLOR[zone] }}>{result.probability_percent}%</div>
            <div className="risk-pct-label">Depressive Symptom Probability</div>
            <div className="risk-zone-chip" style={{ background: ZONE_COLOR[zone] }}>
              {result.risk_zone_label}
            </div>
          </div>
        </div>

        <div className="risk-zone-desc">{result.risk_zone_description}</div>

        {/* ── Two-column layout ── */}
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
                Decision Threshold: <strong>{(result.decision_threshold * 100).toFixed(1)}%</strong> ·
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
                <span><span className="legend-dot" style={{ background: '#dc2626' }} /> Risk-increasing</span>
                <span><span className="legend-dot" style={{ background: '#16a34a' }} /> Risk-reducing</span>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 16, top: 4, bottom: 4 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" horizontal={false} />
                  <XAxis type="number" stroke="#9ca3af" tick={{ fontSize: 10, fill: '#6b7280' }} />
                  <YAxis
                    type="category" dataKey="name" width={160}
                    stroke="#9ca3af" tick={{ fontSize: 9, fill: '#6b7280' }}
                  />
                  <ReferenceLine x={0} stroke="#374151" strokeWidth={1.5} />
                  <Tooltip
                    contentStyle={{ background: '#fff', border: '1px solid #e5e7eb', fontSize: '0.75rem', borderRadius: '4px' }}
                    formatter={v => [v.toFixed(4), 'Log-odds shift']}
                    labelFormatter={(_, payload) => payload?.[0]?.payload?.fullName || ''}
                  />
                  <Bar dataKey="contribution" radius={[0, 3, 3, 0]}>
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
                    {cf.message ? (
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
