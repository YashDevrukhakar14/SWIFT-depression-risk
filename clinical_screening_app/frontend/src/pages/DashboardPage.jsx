import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import CollapsibleCard from '../components/CollapsibleCard'
import ToggleField from '../components/ToggleField'

const INITIAL_FORM = {
  // Section 01 – Demographics & Household
  age: '20 and more',
  gender: 'female',
  field_of_study: 'medicine and allied programs',
  year_of_university: 'first',
  parental_home: true,
  having_only_one_parent: false,
  siblings: true,
  long_commute: true,
  mode_of_transportation: 'by public transportation',

  // Section 02 – Cognitive & Academic Performance
  learning_disabilities: false,
  difficulty_memorizing_lessons: false,
  professional_objective: true,

  // Section 03 – Social & Housing Conditions
  satisfied_with_living_conditions: true,
  living_with_partner_child: false,
  eating_junk_food: true,
  on_a_diet: false,

  // Section 04 – Financial & Institutional Support
  financial_difficulties: false,
  additional_income: false,
  cmu: false,

  // Section 06 – Biomedical Vitals & Anthropometrics
  height_cm: 168,
  weight_kg: 63.3,
  systolic_blood_pressure_mmhg: 118,
  diastolic_blood_pressure_mmhg: 76,
  heart_rate_bpm: 72,

  // Section 07 – Health Behaviours & Symptom Questionnaire
  urinalysis_glycosuria: false,
  abnormal_urinalysis: false,
  cigarette_smoker_5: 'no',
  cigarette_smoker_3: 'no',
  drinker_3: 'no',
  drinker_2: 'no or occasionally',
  binge_drinking: false,
  marijuana_use: false,
  other_recreational_drugs: false,
  anxiety_symptoms: false,
  panic_attack_symptoms: false,
  physical_activity_3: 'regularly',
  physical_activity_2: 'regularly',
}

export default function DashboardPage() {
  const nav = useNavigate()
  const user = JSON.parse(localStorage.getItem('spit_user') || '{}')
  const [form, setForm] = useState(INITIAL_FORM)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const upd = (k, v) => setForm((p) => ({ ...p, [k]: v }))

  const logout = () => {
    localStorage.removeItem('spit_user')
    nav('/')
  }

  const runEngine = async () => {
    setLoading(true)
    setError(null)
    try {
      const payload = { ...form }
      const res = await fetch('/api/predict_clinical', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!res.ok) throw new Error(`Engine returned ${res.status}`)
      const data = await res.json()
      nav('/report', { state: { result: data, form } })
    } catch (e) {
      // If backend is offline or on port difference, navigate with local fallback data
      nav('/report', { state: { result: null, form } })
    } finally {
      setLoading(false)
    }
  }

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
          <span className="swift-user-name">
            {user.name || user.username || 'Yash Devrukhakar'}
          </span>
          <span className="swift-user-divider">|</span>
          <button className="swift-logout-btn" onClick={logout}>
            Sign Out
          </button>
        </div>
      </header>

      {/* ── Main Form Content ── */}
      <main className="swift-main-container">
        <div className="swift-header-block">
          <h1 className="swift-page-heading">
            Student Wellness Risk Assessment
          </h1>
          <p className="swift-page-subtext">
            Complete all sections below and click{' '}
            <strong>Generate Report</strong> to run the Baseline Logistic
            Regression (C = 1.0, balanced) risk-estimation model and view the
            full analysis.
          </p>
        </div>

        {error && <div className="swift-alert-error">{error}</div>}

        <div className="swift-form-layout">
          {/* ── Section 01: Demographics & Academic Profile ── */}
          <CollapsibleCard
            number="01"
            title="Demographics & Academic Profile"
            className="card-full-width"
            defaultOpen={true}
          >
            <div className="swift-split-grid">
              {/* Left Column: Dropdowns */}
              <div className="swift-dropdown-col">
                <div className="swift-field">
                  <label htmlFor="f-age">Age Group</label>
                  <select
                    id="f-age"
                    value={form.age}
                    onChange={(e) => upd('age', e.target.value)}
                  >
                    <option value="20 and more">20 years and above</option>
                    <option value="19">19 years</option>
                    <option value="18">18 years</option>
                    <option value="less 18">Under 18</option>
                  </select>
                </div>

                <div className="swift-field">
                  <label htmlFor="f-gender">Gender</label>
                  <select
                    id="f-gender"
                    value={form.gender}
                    onChange={(e) => upd('gender', e.target.value)}
                  >
                    <option value="female">Female</option>
                    <option value="male">Male</option>
                  </select>
                </div>

                <div className="swift-field">
                  <label htmlFor="f-field">Field of Study</label>
                  <select
                    id="f-field"
                    value={form.field_of_study}
                    onChange={(e) => upd('field_of_study', e.target.value)}
                  >
                    <option value="medicine and allied programs">
                      Medicine & Allied Programs
                    </option>
                    <option value="sciences">Sciences</option>
                    <option value="humanities">Humanities</option>
                    <option value="law and political sciences">
                      Law & Political Sciences
                    </option>
                    <option value="sports science">Sports Science</option>
                    <option value="other programs">Other Programs</option>
                  </select>
                </div>

                <div className="swift-field">
                  <label htmlFor="f-year">Year of University</label>
                  <select
                    id="f-year"
                    value={form.year_of_university}
                    onChange={(e) => upd('year_of_university', e.target.value)}
                  >
                    <option value="first">First Year</option>
                    <option value="second">Second Year</option>
                    <option value="third">Third Year</option>
                  </select>
                </div>
              </div>

              {/* Right Column: Toggles & Transport */}
              <div className="swift-toggles-col">
                <div className="swift-toggles-2col">
                  <ToggleField
                    label="Currently at Parental Home"
                    id="f-ph"
                    value={form.parental_home}
                    onChange={(v) => upd('parental_home', v)}
                  />
                  <ToggleField
                    label="Having Only One Parent"
                    id="f-hop"
                    value={form.having_only_one_parent}
                    onChange={(v) => upd('having_only_one_parent', v)}
                  />
                  <ToggleField
                    label="Has Siblings"
                    id="f-sib"
                    value={form.siblings}
                    onChange={(v) => upd('siblings', v)}
                  />
                  <ToggleField
                    label="Long Daily Commute"
                    id="f-lc"
                    value={form.long_commute}
                    onChange={(v) => upd('long_commute', v)}
                  />
                </div>

                <div className="swift-field transport-field">
                  <label htmlFor="f-mot">Mode of Transportation</label>
                  <select
                    id="f-mot"
                    value={form.mode_of_transportation}
                    onChange={(e) => upd('mode_of_transportation', e.target.value)}
                  >
                    <option value="by public transportation">
                      Public Transportation
                    </option>
                    <option value="on foot">On Foot</option>
                    <option value="by car">By Car</option>
                  </select>
                </div>
              </div>
            </div>
          </CollapsibleCard>

          {/* ── Mid Row: 2 Columns ── */}
          <div className="swift-mid-grid">
            {/* Left Mid Col */}
            <div className="swift-mid-col">
              {/* Section 02 */}
              <CollapsibleCard
                number="02"
                title="Cognitive & Academic Performance"
                defaultOpen={true}
              >
                <div className="swift-toggles-2col">
                  <ToggleField
                    label="Learning Disabilities"
                    id="f-ld"
                    value={form.learning_disabilities}
                    onChange={(v) => upd('learning_disabilities', v)}
                  />
                  <ToggleField
                    label="Difficulty Memorizing Lessons"
                    id="f-dm"
                    value={form.difficulty_memorizing_lessons}
                    onChange={(v) => upd('difficulty_memorizing_lessons', v)}
                  />
                  <ToggleField
                    label="Has Clear Professional Objective"
                    id="f-po"
                    value={form.professional_objective}
                    onChange={(v) => upd('professional_objective', v)}
                  />
                </div>
              </CollapsibleCard>

              {/* Section 03 */}
              <CollapsibleCard
                number="03"
                title="Social & Housing Conditions"
                defaultOpen={true}
              >
                <div className="swift-toggles-2col">
                  <ToggleField
                    label="Satisfied with Living Conditions"
                    id="f-slc"
                    value={form.satisfied_with_living_conditions}
                    onChange={(v) => upd('satisfied_with_living_conditions', v)}
                  />
                  <ToggleField
                    label="Living with Partner / Child"
                    id="f-lwpc"
                    value={form.living_with_partner_child}
                    onChange={(v) => upd('living_with_partner_child', v)}
                  />
                  <ToggleField
                    label="Frequent Junk Food Consumption"
                    id="f-jf"
                    value={form.eating_junk_food}
                    onChange={(v) => upd('eating_junk_food', v)}
                  />
                  <ToggleField
                    label="Currently on a Diet"
                    id="f-od"
                    value={form.on_a_diet}
                    onChange={(v) => upd('on_a_diet', v)}
                  />
                </div>
              </CollapsibleCard>
            </div>

            {/* Right Mid Col */}
            <div className="swift-mid-col">
              {/* Section 04 */}
              <CollapsibleCard
                number="04"
                title="Financial & Institutional Support"
                defaultOpen={true}
              >
                <div className="swift-toggles-2col">
                  <ToggleField
                    label="Financial Difficulties"
                    id="f-fd"
                    value={form.financial_difficulties}
                    onChange={(v) => upd('financial_difficulties', v)}
                  />
                  <ToggleField
                    label="Additional Income Source"
                    id="f-ai"
                    value={form.additional_income}
                    onChange={(v) => upd('additional_income', v)}
                  />
                  <ToggleField
                    label="C.M.U. (Complémentaire Santé)"
                    id="f-cmu"
                    value={form.cmu}
                    onChange={(v) => upd('cmu', v)}
                  />
                </div>
              </CollapsibleCard>

              {/* Section 06 */}
              <CollapsibleCard
                number="06"
                title="Biomedical Vitals & Anthropometrics"
                defaultOpen={true}
              >
                <div className="swift-vitals-grid">
                  <div className="swift-vitals-field">
                    <label htmlFor="f-ht">Height (cm)</label>
                    <input
                      id="f-ht"
                      type="number"
                      value={form.height_cm}
                      onChange={(e) =>
                        upd('height_cm', parseFloat(e.target.value) || 0)
                      }
                    />
                  </div>
                  <div className="swift-vitals-field">
                    <label htmlFor="f-sbp">Systolic BP (mmHg)</label>
                    <input
                      id="f-sbp"
                      type="number"
                      value={form.systolic_blood_pressure_mmhg}
                      onChange={(e) =>
                        upd(
                          'systolic_blood_pressure_mmhg',
                          parseFloat(e.target.value) || 0
                        )
                      }
                    />
                  </div>
                  <div className="swift-vitals-field">
                    <label htmlFor="f-dbp">Diastolic BP (mmHg)</label>
                    <input
                      id="f-dbp"
                      type="number"
                      value={form.diastolic_blood_pressure_mmhg}
                      onChange={(e) =>
                        upd(
                          'diastolic_blood_pressure_mmhg',
                          parseFloat(e.target.value) || 0
                        )
                      }
                    />
                  </div>
                  <div className="swift-vitals-field">
                    <label htmlFor="f-hr">Heart rate (bpm)</label>
                    <input
                      id="f-hr"
                      type="number"
                      value={form.heart_rate_bpm}
                      onChange={(e) =>
                        upd('heart_rate_bpm', parseFloat(e.target.value) || 0)
                      }
                    />
                  </div>
                </div>
              </CollapsibleCard>
            </div>
          </div>

          {/* ── Section 07: Health Behaviours & Symptom Questionnaire ── */}
          <CollapsibleCard
            number="07"
            title="Health Behaviours & Symptom Questionnaire"
            className="card-full-width"
            defaultOpen={true}
          >
            <div className="swift-three-col-section">
              {/* Col 1: Urinalysis */}
              <div className="swift-subgroup-col">
                <h4 className="swift-subgroup-title">Urinalysis Results</h4>
                <div className="swift-subgroup-content">
                  <ToggleField
                    label="Urinalysis"
                    id="f-uri"
                    value={form.urinalysis_glycosuria}
                    onChange={(v) => upd('urinalysis_glycosuria', v)}
                  />
                  <ToggleField
                    label="AbnormalUrinalysis"
                    id="f-aburi"
                    value={form.abnormal_urinalysis}
                    onChange={(v) => upd('abnormal_urinalysis', v)}
                  />
                </div>
              </div>

              {/* Col 2: Substance Use */}
              <div className="swift-subgroup-col substance-col">
                <h4 className="swift-subgroup-title">Substance Use</h4>
                <div className="swift-subgroup-content">
                  <div className="swift-field">
                    <label htmlFor="f-cs5">Cigarette (5 levels)</label>
                    <select
                      id="f-cs5"
                      value={form.cigarette_smoker_5}
                      onChange={(e) => upd('cigarette_smoker_5', e.target.value)}
                    >
                      <option value="no">No (0)</option>
                      <option value="occasionally">Occasionally (1)</option>
                      <option value="regularly">Regularly (2)</option>
                      <option value="frequently">Frequently (3)</option>
                      <option value="heavily">Heavily (4)</option>
                    </select>
                  </div>

                  <div className="swift-field">
                    <label htmlFor="f-cs3">Substance Use (3 levels)</label>
                    <select
                      id="f-cs3"
                      value={form.cigarette_smoker_3}
                      onChange={(e) => upd('cigarette_smoker_3', e.target.value)}
                    >
                      <option value="no">No (0)</option>
                      <option value="occasionally to regularly">
                        Occasional to Regular (1)
                      </option>
                      <option value="frequently to heavily">
                        Frequent to Heavy (2)
                      </option>
                    </select>
                  </div>

                  <div className="swift-field">
                    <label htmlFor="f-d3">Alcohol (3 levels)</label>
                    <select
                      id="f-d3"
                      value={form.drinker_3}
                      onChange={(e) => upd('drinker_3', e.target.value)}
                    >
                      <option value="no">No (0)</option>
                      <option value="occasionally">Occasional (1)</option>
                      <option value="regularly">Regular (2)</option>
                    </select>
                  </div>

                  <div className="swift-sub-toggles-row">
                    <div className="swift-field compact-select">
                      <label htmlFor="f-binge">Binge</label>
                      <select
                        id="f-binge"
                        value={form.binge_drinking ? 'yes' : 'no'}
                        onChange={(e) =>
                          upd('binge_drinking', e.target.value === 'yes')
                        }
                      >
                        <option value="no">No</option>
                        <option value="yes">Yes</option>
                      </select>
                    </div>

                    <div className="swift-field compact-select">
                      <label htmlFor="f-marijuana">Marijuana</label>
                      <select
                        id="f-marijuana"
                        value={form.marijuana_use ? 'yes' : 'no'}
                        onChange={(e) =>
                          upd('marijuana_use', e.target.value === 'yes')
                        }
                      >
                        <option value="no">No</option>
                        <option value="yes">Yes</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              {/* Col 3: Mental Health */}
              <div className="swift-subgroup-col">
                <h4 className="swift-subgroup-title">Mental Health</h4>
                <div className="swift-subgroup-content">
                  <ToggleField
                    label="Anxiety"
                    id="f-anx"
                    value={form.anxiety_symptoms}
                    onChange={(v) => upd('anxiety_symptoms', v)}
                  />
                  <ToggleField
                    label="Panic attack"
                    id="f-pan"
                    value={form.panic_attack_symptoms}
                    onChange={(v) => upd('panic_attack_symptoms', v)}
                  />
                  <ToggleField
                    label="other drug"
                    id="f-other-drug"
                    value={form.other_recreational_drugs}
                    onChange={(v) => upd('other_recreational_drugs', v)}
                  />
                </div>
              </div>
            </div>
          </CollapsibleCard>
        </div>
      </main>

      {/* ── Fixed Bottom Bar ── */}
      <footer className="swift-bottom-bar">
        <div className="swift-bar-text">
          Baseline Logistic Regression (C = 1.0, balanced) · held-out ROC-AUC
          0.7500
        </div>
        <button
          className="swift-generate-btn"
          onClick={runEngine}
          disabled={loading}
        >
          {loading ? 'Running Engine…' : 'Generate Report →'}
        </button>
      </footer>
    </div>
  )
}
