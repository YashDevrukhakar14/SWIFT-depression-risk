import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import DivergingBarChart from '../components/DivergingBarChart'

// Publication verified data matching Image 1 exactly
const GLOBAL_SHAP_DATA = [
  { label: 'Financial Difficulties', value: 0.412 },
  { label: 'Anxiety Symptoms', value: 0.305 },
  { label: 'Panic Attack Symptoms', value: 0.274 },
  { label: 'Univ Year (First Year)', value: 0.168 },
  { label: 'Satisfaction With Living', value: -0.182 },
  { label: 'Physical Activity', value: -0.226 },
  { label: 'Learning Disabilities', value: -0.241 },
  { label: 'Field of Study (Sciences)', value: -0.276 },
  { label: 'Sleep Quality', value: -0.318 },
  { label: 'Alcohol Consumption', value: -0.421 },
]

const LIME_LOCAL_DATA = [
  { label: 'Financial Difficulties', value: 0.138 },
  { label: 'Anxiety Symptoms', value: 0.112 },
  { label: 'Panic Attack Symptoms', value: 0.084 },
  { label: 'Learning Disabilities', value: 0.061 },
  { label: 'Physical Activity', value: -0.048 },
  { label: 'Satisfaction With Living', value: -0.037 },
  { label: 'Sleep Quality', value: -0.029 },
  { label: 'Field of Study (Sciences)', value: -0.021 },
  { label: 'Alcohol Consumption', value: -0.016 },
  { label: 'Univ Year (First Year)', value: -0.012 },
]

const MODEL_COEFFICIENTS = [
  { feature: 'Financial Difficulties', coef: '+0.812' },
  { feature: 'Anxiety Symptoms', coef: '+0.654' },
  { feature: 'Panic Attack Symptoms', coef: '+0.498' },
  { feature: 'Univ Year (First Year)', coef: '+0.372' },
  { feature: 'Satisfaction With Living', coef: '+0.291' },
]

export default function ReportPage() {
  const { state } = useLocation()
  const nav = useNavigate()
  const result = state?.result
  const form = state?.form

  const logout = () => {
    localStorage.removeItem('spit_user')
    nav('/')
  }

  // Model probability: default to the verified 34.8% illustrative example
  const riskPercent = result?.probability_percent !== undefined
    ? result.probability_percent
    : 34.8

  const formattedDate = '21 October 2026 at 1:37 pm'

  return (
    <div className="swift-page-wrapper">
      {/* ── Top Navbar ── */}
      <header className="swift-navbar">
        <div className="swift-brand-group">
          <div className="swift-logo-box">SS</div>
          <div className="swift-brand-text">
            <span className="swift-brand-title">SPIT SWIFT</span>
            <span className="swift-brand-subtitle">
              Student Wellness Decision-Support System
            </span>
          </div>
        </div>

        <div className="swift-nav-user-actions">
          <span className="swift-user-name">Authorised Reviewer</span>
          <span className="swift-user-divider">|</span>
          <button className="swift-logout-btn" onClick={logout}>
            Sign Out
          </button>
        </div>
      </header>

      {/* ── Main Report Content ── */}
      <main className="swift-main-container report-main-container">
        {/* Title and Metadata Header */}
        <div className="report-title-row">
          <div className="report-title-left">
            <button
              className="swift-back-circle-btn"
              onClick={() => nav('/dashboard')}
              title="Return to Assessment Form"
            >
              ←
            </button>
            <div>
              <h1 className="swift-page-heading">
                Individual Student Risk Assessment
              </h1>
              <p className="swift-page-subtext">
                View the model prediction, risk score, and key factors for this
                student.
              </p>
            </div>
          </div>

          <div className="report-metadata-box">
            <div className="meta-line">
              <span className="meta-key">Model</span>
              <span className="meta-colon">:</span>
              <span className="meta-val">
                Baseline Logistic Regression (C = 1.0, balanced)
              </span>
            </div>
            <div className="meta-line">
              <span className="meta-key">Generated</span>
              <span className="meta-colon">:</span>
              <span className="meta-val">{formattedDate}</span>
            </div>
            <div className="meta-line">
              <span className="meta-key">Reviewer</span>
              <span className="meta-colon">:</span>
              <span className="meta-val">Authorised Reviewer</span>
            </div>
          </div>
        </div>

        {/* ── Green Risk Alert Banner ── */}
        <div className="swift-risk-banner">
          <div className="risk-banner-left-area">
            <div className="risk-banner-indicator-dot" />
            <div className="risk-banner-text-content">
              <div className="risk-banner-headline">
                <span>
                  Model risk score {riskPercent}% (&lt; 0.5 threshold;
                  uncalibrated)
                </span>
                <span className="illustrative-pill">Illustrative example</span>
              </div>
              <p className="risk-banner-subtext">
                This risk score is generated by the baseline Logistic Regression
                model and should be interpreted as an estimate based on the
                student's current responses and recorded attributes. It is not a
                clinical diagnosis and is not calibrated.
              </p>
            </div>
          </div>

          <div className="risk-banner-right-area">
            <div className="risk-score-giant">{riskPercent}%</div>
            <div className="risk-score-caption">Estimated Risk Score</div>
            <div className="risk-threshold-pill">Threshold: 0.5</div>
          </div>
        </div>

        {/* ── 3-Column Report Grid ── */}
        <div className="report-three-columns-grid">
          {/* ════ COLUMN 1: Profile & Metrics ════ */}
          <div className="report-column">
            {/* 1. Student Information */}
            <div className="report-panel-card">
              <div className="panel-card-header">
                <span className="panel-icon-badge">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                    <circle cx="12" cy="7" r="4" />
                  </svg>
                </span>
                <h3 className="panel-card-title">Student Information</h3>
              </div>
              <table className="swift-info-table">
                <tbody>
                  <tr>
                    <td>Age Group</td>
                    <td className="info-val">20 years and above</td>
                  </tr>
                  <tr>
                    <td>Gender</td>
                    <td className="info-val">Female</td>
                  </tr>
                  <tr>
                    <td>Field of Study</td>
                    <td className="info-val">Medicine &amp; Allied Programs</td>
                  </tr>
                  <tr>
                    <td>Year of University</td>
                    <td className="info-val">First Year</td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* 2. Model Performance (Test Set) */}
            <div className="report-panel-card">
              <div className="panel-card-header">
                <span className="panel-icon-badge">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                    <path d="M3 3v18h18" />
                    <path d="M18 17l-5-5-3 3-4-4" />
                  </svg>
                </span>
                <h3 className="panel-card-title">Model Performance (Test Set)</h3>
              </div>

              <div className="model-metrics-row">
                <div className="metric-cell">
                  <div className="metric-score">0.7500</div>
                  <div className="metric-tag">ROC-AUC</div>
                </div>
                <div className="metric-cell">
                  <div className="metric-score">0.2716</div>
                  <div className="metric-tag">MCC</div>
                </div>
                <div className="metric-cell">
                  <div className="metric-score">0.1828</div>
                  <div className="metric-tag">Brier Score</div>
                </div>
              </div>

              <div className="metrics-threshold-note">
                Decision Threshold: <strong>0.5 (Default)</strong>
              </div>
            </div>

            {/* 3. Student Profile (Input Summary) */}
            <div className="report-panel-card">
              <div className="panel-card-header">
                <span className="panel-icon-badge">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                    <line x1="16" y1="2" x2="16" y2="6" />
                    <line x1="8" y1="2" x2="8" y2="6" />
                    <line x1="3" y1="10" x2="21" y2="10" />
                  </svg>
                </span>
                <h3 className="panel-card-title">Student Profile (Input Summary)</h3>
              </div>
              <table className="swift-info-table input-summary-table">
                <tbody>
                  <tr>
                    <td>Age Group</td>
                    <td className="info-val">20 and more</td>
                  </tr>
                  <tr>
                    <td>Gender</td>
                    <td className="info-val">Female</td>
                  </tr>
                  <tr>
                    <td>Field of Study</td>
                    <td className="info-val">Medicine &amp; Allied Programs</td>
                  </tr>
                  <tr>
                    <td>Year of University</td>
                    <td className="info-val">First Year</td>
                  </tr>
                  <tr>
                    <td>Learning Disabilities</td>
                    <td className="info-val">No</td>
                  </tr>
                  <tr>
                    <td>Physical Activity</td>
                    <td className="info-val">Yes</td>
                  </tr>
                  <tr>
                    <td>Cigarette Smoker</td>
                    <td className="info-val">No</td>
                  </tr>
                  <tr>
                    <td>Alcohol Drinker</td>
                    <td className="info-val">No</td>
                  </tr>
                  <tr>
                    <td>Anxiety Symptoms</td>
                    <td className="info-val">No</td>
                  </tr>
                  <tr>
                    <td>Panic Attacks</td>
                    <td className="info-val">No</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* ════ COLUMN 2: SHAP & Model Coefficients ════ */}
          <div className="report-column">
            {/* 1. SHAP Feature Contributions */}
            <div className="report-panel-card">
              <div className="panel-card-header">
                <span className="panel-icon-badge">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                    <polygon points="12 2 2 7 12 12 22 7 12 2" />
                    <polyline points="2 17 12 22 22 17" />
                    <polyline points="2 12 12 17 22 12" />
                  </svg>
                </span>
                <h3 className="panel-card-title">
                  SHAP Feature Contributions (Global View)
                </h3>
              </div>

              <DivergingBarChart
                data={GLOBAL_SHAP_DATA}
                minDomain={-0.6}
                maxDomain={0.6}
                ticks={[-0.6, -0.3, 0, 0.3, 0.6]}
                axisLabel="SHAP value (impact on model output)"
                legend={{
                  positive: 'Higher risk association',
                  negative: 'Lower risk association',
                }}
              />
            </div>

            {/* 2. Model Coefficients */}
            <div className="report-panel-card">
              <div className="panel-card-header">
                <span className="panel-icon-badge">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                    <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
                    <line x1="8" y1="21" x2="16" y2="21" />
                    <line x1="12" y1="17" x2="12" y2="21" />
                  </svg>
                </span>
                <h3 className="panel-card-title">
                  Model Coefficients (Logistic Regression)
                </h3>
              </div>

              <table className="swift-coef-table">
                <thead>
                  <tr>
                    <th>Feature</th>
                    <th className="th-right">Coefficient (β)</th>
                  </tr>
                </thead>
                <tbody>
                  {MODEL_COEFFICIENTS.map((c, i) => (
                    <tr key={i}>
                      <td>{c.feature}</td>
                      <td className="td-right coef-val">{c.coef}</td>
                    </tr>
                  ))}
                  <tr>
                    <td colSpan={2} className="td-ellipsis">…</td>
                  </tr>
                </tbody>
              </table>

              <div className="swift-info-callout">
                <span className="callout-info-icon">ℹ</span>
                <span>
                  Coefficients are from the baseline Logistic Regression model
                  and should be interpreted in the transformed feature space.
                </span>
              </div>
            </div>
          </div>

          {/* ════ COLUMN 3: LIME & Additional Info ════ */}
          <div className="report-column">
            {/* 1. LIME Local Explanation */}
            <div className="report-panel-card">
              <div className="panel-card-header">
                <span className="panel-icon-badge">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="12" y1="8" x2="12" y2="12" />
                    <line x1="12" y1="16" x2="12.01" y2="16" />
                  </svg>
                </span>
                <h3 className="panel-card-title">
                  LIME Local Explanation (Instance View)
                </h3>
              </div>

              <div className="lime-table-head">
                <span>Feature</span>
                <span className="head-right">Contribution</span>
              </div>

              <DivergingBarChart
                data={LIME_LOCAL_DATA}
                minDomain={-0.15}
                maxDomain={0.15}
                ticks={[-0.15, -0.10, -0.05, 0, 0.05, 0.10, 0.15]}
                axisLabel="Contribution to prediction"
                legend={{
                  positive: 'Increases risk',
                  negative: 'Decreases risk',
                }}
              />
            </div>

            {/* 2. Additional Information */}
            <div className="report-panel-card">
              <div className="panel-card-header">
                <span className="panel-icon-badge">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
                    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
                  </svg>
                </span>
                <h3 className="panel-card-title">Additional Information</h3>
              </div>

              <div className="additional-info-list">
                <div className="add-info-item">
                  <span className="check-icon">✓</span>
                  <span>SHAP: Global and local feature attribution</span>
                </div>
                <div className="add-info-item">
                  <span className="check-icon">✓</span>
                  <span>Model coefficients: Interpretable feature contributions</span>
                </div>
                <div className="add-info-item">
                  <span className="check-icon">✓</span>
                  <span>LIME: Local surrogate explanation for this instance</span>
                </div>
              </div>

              <div className="swift-warning-callout">
                <div className="warning-heading">
                  <span className="warning-icon">!</span>
                  <strong>Important Note</strong>
                </div>
                <p className="warning-text">
                  This output is generated by the baseline Logistic Regression
                  model and is intended for research and educational
                  decision-support purposes only. It does not constitute a
                  clinical diagnosis or treatment recommendation.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* ── Figure Caption / Footnote at Bottom Right ── */}
        <div className="report-bottom-caption">
          Fig. 9: Illustrative output of the baseline LR (C = 1.0, balanced),
          threshold 0.5; not a real student record.
        </div>
      </main>
    </div>
  )
}
