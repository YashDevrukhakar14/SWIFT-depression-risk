import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const INITIAL_FORM = {
  // Section 1 – Demographics & Academic
  age: '20 and more',
  gender: 'female',
  field_of_study: 'medicine and allied programs',
  year_of_university: 'first',

  // Section 2 – Cognitive & Academic Performance
  learning_disabilities: false,
  difficulty_memorizing_lessons: false,
  professional_objective: true,

  // Section 3 – Social & Housing
  satisfied_with_living_conditions: true,
  living_with_partner_child: false,
  parental_home: true,
  having_only_one_parent: false,
  siblings: true,
  long_commute: false,
  mode_of_transportation: 'by public transportation',

  // Section 4 – Financial & Support
  financial_difficulties: false,
  additional_income: false,
  cmu: false,

  // Section 5 – Dietary & Lifestyle
  irregular_rhythm_of_meals: false,
  unbalanced_meals: false,
  eating_junk_food: false,
  on_a_diet: false,
  physical_activity_3: 'no',
  physical_activity_2: 'no activity or occasionally',

  // Section 6 – Biomedical Vitals
  height_cm: 169,
  weight_kg: 62,
  systolic_blood_pressure_mmhg: 120,
  diastolic_blood_pressure_mmhg: 80,
  heart_rate_bpm: 73,

  // Section 7 – Clinical & Substance Screening
  urinalysis_glycosuria: false,
  urinalysis_proteinuria: false,
  urinalysis_hematuria: false,
  urinalysis_leukocyturia: false,
  urinalysis_nitrite: false,
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
}

function SelectField({ label, id, value, onChange, options }) {
  return (
    <div className="form-field">
      <label htmlFor={id}>{label}</label>
      <select id={id} value={value} onChange={e => onChange(e.target.value)}>
        {options.map(o => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </div>
  )
}

function NumberField({ label, id, value, onChange, unit, min, max, step }) {
  return (
    <div className="form-field">
      <label htmlFor={id}>{label}{unit && <span className="field-unit">{unit}</span>}</label>
      <input
        id={id}
        type="number"
        value={value}
        min={min}
        max={max}
        step={step || 1}
        onChange={e => onChange(parseFloat(e.target.value) || 0)}
      />
    </div>
  )
}

function ToggleField({ label, id, value, onChange }) {
  return (
    <div className="form-field form-field-toggle">
      <label htmlFor={id}>{label}</label>
      <button
        id={id}
        type="button"
        role="switch"
        aria-checked={value}
        className={`toggle-sw ${value ? 'toggle-on' : ''}`}
        onClick={() => onChange(!value)}
      >
        <span className="toggle-thumb" />
        <span className="toggle-label">{value ? 'Yes' : 'No'}</span>
      </button>
    </div>
  )
}

function Section({ title, number, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="form-section">
      <button
        type="button"
        className={`form-section-head ${open ? 'open' : ''}`}
        onClick={() => setOpen(o => !o)}
        aria-expanded={open}
      >
        <span className="section-num">{number}</span>
        <span className="section-lbl">{title}</span>
        <span className="section-chevron">{open ? '▾' : '▸'}</span>
      </button>
      {open && <div className="form-section-body">{children}</div>}
    </div>
  )
}

export default function DashboardPage() {
  const nav = useNavigate()
  const user = JSON.parse(localStorage.getItem('spit_user') || '{}')
  const [form, setForm] = useState(INITIAL_FORM)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const upd = (k, v) => setForm(p => ({ ...p, [k]: v }))

  const logout = () => {
    localStorage.removeItem('spit_user')
    nav('/')
  }

  const yn = v => v ? 'yes' : 'no'

  const runEngine = async () => {
    setLoading(true)
    setError(null)
    try {
      const payload = {
        gender: form.gender,
        age: form.age,
        field_of_study: form.field_of_study,
        year_of_university: form.year_of_university,
        financial_difficulties: form.financial_difficulties,
        satisfied_with_living_conditions: form.satisfied_with_living_conditions,
        learning_disabilities: form.learning_disabilities,
        difficulty_memorizing_lessons: form.difficulty_memorizing_lessons,
        professional_objective: form.professional_objective,
        living_with_partner_child: form.living_with_partner_child,
        parental_home: form.parental_home,
        having_only_one_parent: form.having_only_one_parent,
        siblings: form.siblings,
        long_commute: form.long_commute,
        mode_of_transportation: form.mode_of_transportation,
        additional_income: form.additional_income,
        cmu: form.cmu,
        unbalanced_meals: form.unbalanced_meals,
        irregular_rhythm_of_meals: form.irregular_rhythm_of_meals,
        eating_junk_food: form.eating_junk_food,
        on_a_diet: form.on_a_diet,
        physical_activity_3: form.physical_activity_3,
        physical_activity_2: form.physical_activity_2,
        height_cm: form.height_cm,
        weight_kg: form.weight_kg,
        systolic_blood_pressure_mmhg: form.systolic_blood_pressure_mmhg,
        diastolic_blood_pressure_mmhg: form.diastolic_blood_pressure_mmhg,
        heart_rate_bpm: form.heart_rate_bpm,
        urinalysis_glycosuria: form.urinalysis_glycosuria,
        urinalysis_proteinuria: form.urinalysis_proteinuria,
        urinalysis_hematuria: form.urinalysis_hematuria,
        urinalysis_leukocyturia: form.urinalysis_leukocyturia,
        urinalysis_nitrite: form.urinalysis_nitrite,
        abnormal_urinalysis: form.abnormal_urinalysis,
        cigarette_smoker_5: form.cigarette_smoker_5,
        cigarette_smoker_3: form.cigarette_smoker_3,
        drinker_3: form.drinker_3,
        drinker_2: form.drinker_2,
        binge_drinking: form.binge_drinking,
        marijuana_use: form.marijuana_use,
        other_recreational_drugs: form.other_recreational_drugs,
        anxiety_symptoms: form.anxiety_symptoms,
        panic_attack_symptoms: form.panic_attack_symptoms,
      }
      const res = await fetch('/api/predict_clinical', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!res.ok) throw new Error(`Engine returned ${res.status}`)
      const data = await res.json()
      nav('/report', { state: { result: data, form } })
    } catch (e) {
      setError(e.message || 'Clinical engine unavailable. Ensure the FastAPI backend is running on port 8000.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="dash-shell">
      {/* ── Navbar ── */}
      <header className="dash-nav">
        <div className="nav-brand">
          <span className="nav-logo-mark">SS</span>
          <div>
            <span className="nav-title">SPIT SWIFT</span>
            <span className="nav-tagline">Clinical Screening System</span>
          </div>
        </div>
        <div className="nav-right">
          <span className="nav-user">
            <span className="nav-user-dot" />
            {user.name || user.username || 'Clinician'}
          </span>
          <button className="nav-logout" onClick={logout}>Sign Out</button>
        </div>
      </header>

      <div className="dash-body">
        {/* ── Page title ── */}
        <div className="dash-hero">
          <h1>Patient Clinical Assessment</h1>
          <p>
            Complete all sections below and click <strong>Generate Report</strong> to run the
            Optuna-tuned Logistic Regression screening engine and view the full clinical analysis.
          </p>
        </div>

        {error && <div className="dash-error">{error}</div>}

        <div className="form-wrapper">

          {/* ── Section 1 ── */}
          <Section number="01" title="Demographics & Academic Profile" defaultOpen>
            <div className="field-grid-2">
              <SelectField
                label="Age Group" id="f-age" value={form.age}
                onChange={v => upd('age', v)}
                options={[
                  { value: 'less 18', label: 'Under 18' },
                  { value: '18', label: '18 years' },
                  { value: '19', label: '19 years' },
                  { value: '20 and more', label: '20 years and above' },
                ]}
              />
              <SelectField
                label="Gender" id="f-gender" value={form.gender}
                onChange={v => upd('gender', v)}
                options={[
                  { value: 'female', label: 'Female' },
                  { value: 'male', label: 'Male' },
                ]}
              />
              <SelectField
                label="Field of Study" id="f-field" value={form.field_of_study}
                onChange={v => upd('field_of_study', v)}
                options={[
                  { value: 'humanities', label: 'Humanities' },
                  { value: 'medicine and allied programs', label: 'Medicine & Allied Programs' },
                  { value: 'sciences', label: 'Sciences' },
                  { value: 'law and political sciences', label: 'Law & Political Sciences' },
                  { value: 'sports science', label: 'Sports Science' },
                  { value: 'other programs', label: 'Other Programs' },
                ]}
              />
              <SelectField
                label="Year of University" id="f-year" value={form.year_of_university}
                onChange={v => upd('year_of_university', v)}
                options={[
                  { value: 'first', label: 'First Year' },
                  { value: 'second', label: 'Second Year' },
                  { value: 'third', label: 'Third Year' },
                ]}
              />
            </div>
          </Section>

          {/* ── Section 2 ── */}
          <Section number="02" title="Cognitive & Academic Performance">
            <div className="field-grid-2">
              <ToggleField label="Learning Disabilities" id="f-ld" value={form.learning_disabilities} onChange={v => upd('learning_disabilities', v)} />
              <ToggleField label="Difficulty Memorizing Lessons" id="f-dm" value={form.difficulty_memorizing_lessons} onChange={v => upd('difficulty_memorizing_lessons', v)} />
              <ToggleField label="Has Clear Professional Objective" id="f-po" value={form.professional_objective} onChange={v => upd('professional_objective', v)} />
            </div>
          </Section>

          {/* ── Section 3 ── */}
          <Section number="03" title="Social & Housing Conditions">
            <div className="field-grid-2">
              <ToggleField label="Satisfied with Living Conditions" id="f-slc" value={form.satisfied_with_living_conditions} onChange={v => upd('satisfied_with_living_conditions', v)} />
              <ToggleField label="Living with Partner / Child" id="f-lwpc" value={form.living_with_partner_child} onChange={v => upd('living_with_partner_child', v)} />
              <ToggleField label="Currently at Parental Home" id="f-ph" value={form.parental_home} onChange={v => upd('parental_home', v)} />
              <ToggleField label="Having Only One Parent" id="f-hop" value={form.having_only_one_parent} onChange={v => upd('having_only_one_parent', v)} />
              <ToggleField label="Has Siblings" id="f-sib" value={form.siblings} onChange={v => upd('siblings', v)} />
              <ToggleField label="Long Daily Commute" id="f-lc" value={form.long_commute} onChange={v => upd('long_commute', v)} />
              <SelectField
                label="Mode of Transportation" id="f-mot" value={form.mode_of_transportation}
                onChange={v => upd('mode_of_transportation', v)}
                options={[
                  { value: 'on foot', label: 'On Foot' },
                  { value: 'by public transportation', label: 'Public Transportation' },
                  { value: 'by car', label: 'By Car' },
                ]}
              />
            </div>
          </Section>

          {/* ── Section 4 ── */}
          <Section number="04" title="Financial & Institutional Support">
            <div className="field-grid-2">
              <ToggleField label="Financial Difficulties" id="f-fd" value={form.financial_difficulties} onChange={v => upd('financial_difficulties', v)} />
              <ToggleField label="Additional Income Source" id="f-ai" value={form.additional_income} onChange={v => upd('additional_income', v)} />
              <ToggleField label="C.M.U. (Complémentaire Santé)" id="f-cmu" value={form.cmu} onChange={v => upd('cmu', v)} />
            </div>
          </Section>

          {/* ── Section 5 ── */}
          <Section number="05" title="Dietary Habits & Physical Activity">
            <div className="field-grid-2">
              <ToggleField label="Irregular Meal Rhythm" id="f-irm" value={form.irregular_rhythm_of_meals} onChange={v => upd('irregular_rhythm_of_meals', v)} />
              <ToggleField label="Unbalanced / Poor-quality Meals" id="f-um" value={form.unbalanced_meals} onChange={v => upd('unbalanced_meals', v)} />
              <ToggleField label="Frequent Junk Food Consumption" id="f-jf" value={form.eating_junk_food} onChange={v => upd('eating_junk_food', v)} />
              <ToggleField label="Currently on a Diet" id="f-od" value={form.on_a_diet} onChange={v => upd('on_a_diet', v)} />
              <SelectField
                label="Physical Activity (3 levels)" id="f-pa3" value={form.physical_activity_3}
                onChange={v => upd('physical_activity_3', v)}
                options={[
                  { value: 'no', label: 'None' },
                  { value: 'occasionally', label: 'Occasionally' },
                  { value: 'regularly', label: 'Regularly' },
                ]}
              />
              <SelectField
                label="Physical Activity (2 levels)" id="f-pa2" value={form.physical_activity_2}
                onChange={v => upd('physical_activity_2', v)}
                options={[
                  { value: 'no activity or occasionally', label: 'None / Occasional' },
                  { value: 'regularly', label: 'Regular' },
                ]}
              />
            </div>
          </Section>

          {/* ── Section 6 ── */}
          <Section number="06" title="Biomedical Vitals & Anthropometrics">
            <div className="field-grid-2">
              <NumberField label="Height" id="f-ht" unit="cm" value={form.height_cm} onChange={v => upd('height_cm', v)} min={100} max={230} />
              <NumberField label="Weight" id="f-wt" unit="kg" value={form.weight_kg} onChange={v => upd('weight_kg', v)} min={30} max={200} />
              <NumberField label="Systolic Blood Pressure" id="f-sbp" unit="mmHg" value={form.systolic_blood_pressure_mmhg} onChange={v => upd('systolic_blood_pressure_mmhg', v)} min={60} max={250} />
              <NumberField label="Diastolic Blood Pressure" id="f-dbp" unit="mmHg" value={form.diastolic_blood_pressure_mmhg} onChange={v => upd('diastolic_blood_pressure_mmhg', v)} min={40} max={160} />
              <NumberField label="Heart Rate" id="f-hr" unit="bpm" value={form.heart_rate_bpm} onChange={v => upd('heart_rate_bpm', v)} min={30} max={220} />
            </div>
            {/* Live BMI preview */}
            {form.height_cm > 0 && form.weight_kg > 0 && (() => {
              const bmi = (form.weight_kg / Math.pow(form.height_cm / 100, 2)).toFixed(1)
              const cat = bmi < 18.5 ? 'Underweight' : bmi < 25 ? 'Normal' : bmi < 30 ? 'Overweight' : 'Obese'
              return (
                <div className="bmi-preview">
                  <span className="bmi-label">Computed BMI</span>
                  <span className="bmi-value">{bmi}</span>
                  <span className={`bmi-badge bmi-${cat.toLowerCase()}`}>{cat}</span>
                </div>
              )
            })()}
          </Section>

          {/* ── Section 7 ── */}
          <Section number="07" title="Clinical Screening & Substance Use">
            <p className="section-note">Urinalysis Results</p>
            <div className="field-grid-2">
              <ToggleField label="Glycosuria (Glucose in Urine)" id="f-gly" value={form.urinalysis_glycosuria} onChange={v => upd('urinalysis_glycosuria', v)} />
              <ToggleField label="Proteinuria (Protein in Urine)" id="f-pro" value={form.urinalysis_proteinuria} onChange={v => upd('urinalysis_proteinuria', v)} />
              <ToggleField label="Hematuria (Blood in Urine)" id="f-hem" value={form.urinalysis_hematuria} onChange={v => upd('urinalysis_hematuria', v)} />
              <ToggleField label="Leukocyturia (WBC in Urine)" id="f-leu" value={form.urinalysis_leukocyturia} onChange={v => upd('urinalysis_leukocyturia', v)} />
              <ToggleField label="Positive Nitrite Test" id="f-nit" value={form.urinalysis_nitrite} onChange={v => upd('urinalysis_nitrite', v)} />
              <ToggleField label="Abnormal Urinalysis (Overall)" id="f-abu" value={form.abnormal_urinalysis} onChange={v => upd('abnormal_urinalysis', v)} />
            </div>

            <p className="section-note" style={{ marginTop: '1.25rem' }}>Substance Use</p>
            <div className="field-grid-2">
              <SelectField
                label="Cigarette Smoker (5 levels)" id="f-cs5" value={form.cigarette_smoker_5}
                onChange={v => upd('cigarette_smoker_5', v)}
                options={[
                  { value: 'no', label: 'Non-smoker' },
                  { value: 'occasionally', label: 'Occasional' },
                  { value: 'regularly', label: 'Regular' },
                  { value: 'frequently', label: 'Frequent' },
                  { value: 'heavily', label: 'Heavy' },
                ]}
              />
              <SelectField
                label="Cigarette Smoker (3 levels)" id="f-cs3" value={form.cigarette_smoker_3}
                onChange={v => upd('cigarette_smoker_3', v)}
                options={[
                  { value: 'no', label: 'Non-smoker' },
                  { value: 'occasionally to regularly', label: 'Occasional to Regular' },
                  { value: 'frequently to heavily', label: 'Frequent to Heavy' },
                ]}
              />
              <SelectField
                label="Alcohol — Drinker (3 levels)" id="f-d3" value={form.drinker_3}
                onChange={v => upd('drinker_3', v)}
                options={[
                  { value: 'no', label: 'Non-drinker' },
                  { value: 'occasionally', label: 'Occasional' },
                  { value: 'regularly', label: 'Regular' },
                ]}
              />
              <SelectField
                label="Alcohol — Drinker (2 levels)" id="f-d2" value={form.drinker_2}
                onChange={v => upd('drinker_2', v)}
                options={[
                  { value: 'no or occasionally', label: 'None / Occasional' },
                  { value: 'regularly to heavily', label: 'Regular to Heavy' },
                ]}
              />
              <ToggleField label="Binge Drinking Episodes" id="f-bd" value={form.binge_drinking} onChange={v => upd('binge_drinking', v)} />
              <ToggleField label="Marijuana Use" id="f-mj" value={form.marijuana_use} onChange={v => upd('marijuana_use', v)} />
              <ToggleField label="Other Recreational Drugs" id="f-ord" value={form.other_recreational_drugs} onChange={v => upd('other_recreational_drugs', v)} />
            </div>

            <p className="section-note" style={{ marginTop: '1.25rem' }}>Mental Health Indicators</p>
            <div className="field-grid-2">
              <ToggleField label="Anxiety Symptoms Present" id="f-anx" value={form.anxiety_symptoms} onChange={v => upd('anxiety_symptoms', v)} />
              <ToggleField label="Panic Attack Symptoms Present" id="f-pan" value={form.panic_attack_symptoms} onChange={v => upd('panic_attack_symptoms', v)} />
            </div>
          </Section>

        </div>{/* end form-wrapper */}

        {/* ── Generate Report CTA ── */}
        <div className="generate-bar">
          {error && <p className="generate-error">{error}</p>}
          <div className="generate-info">
            <span>All sections complete</span>
            <span>·</span>
            <span>Optuna LR · ROC-AUC 0.7507</span>
          </div>
          <button
            id="generate-report-btn"
            className="generate-btn"
            onClick={runEngine}
            disabled={loading}
          >
            {loading
              ? <><span className="btn-spinner" /> Computing…</>
              : <>Generate Report  →</>
            }
          </button>
        </div>
      </div>
    </div>
  )
}
