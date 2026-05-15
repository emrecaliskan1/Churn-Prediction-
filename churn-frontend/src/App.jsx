import { useState } from 'react'
import './App.css'

const INITIAL_FORM = {
  gender: 'Male',
  seniorcitizen: 0,
  partner: 'No',
  dependents: 'No',
  tenure: '',
  phoneservice: 'Yes',
  multiplelines: 'No',
  internetservice: 'DSL',
  onlinesecurity: 'No',
  onlinebackup: 'No',
  deviceprotection: 'No',
  techsupport: 'No',
  streamingtv: 'No',
  streamingmovies: 'No',
  contract: 'Month-to-month',
  paperlessbilling: 'Yes',
  paymentmethod: 'Electronic check',
  monthlycharges: '',
  totalcharges: '',
}

function SelectField({ label, name, value, onChange, options }) {
  return (
    <div className="field">
      <label htmlFor={name}>{label}</label>
      <select id={name} name={name} value={value} onChange={onChange}>
        {options.map((opt) => (
          <option key={opt.value ?? opt} value={opt.value ?? opt}>
            {opt.label ?? opt}
          </option>
        ))}
      </select>
    </div>
  )
}

function NumberField({ label, name, value, onChange, min, max, step = 1, placeholder }) {
  return (
    <div className="field">
      <label htmlFor={name}>{label}</label>
      <input
        id={name}
        type="number"
        name={name}
        value={value}
        onChange={onChange}
        min={min}
        max={max}
        step={step}
        placeholder={placeholder}
      />
    </div>
  )
}

function ResultCard({ result }) {
  const churn = result.churn
  const prob = result.probability
  const risk = result.risk_level

  return (
    <div className={`result-card ${churn ? 'churn-yes' : 'churn-no'}`}>
      <div className="result-icon">{churn ? '⚠️' : '✅'}</div>
      <h2 className="result-title">
        {churn ? 'Churn Riski Var' : 'Müşteri Kalıcı'}
      </h2>
      <p className="result-message">{result.message}</p>

      <div className="result-stats">
        <div className="stat">
          <span className="stat-label">Ayrılma Olasılığı</span>
          <span className="stat-value">{prob}%</span>
        </div>
        <div className="stat">
          <span className="stat-label">Risk Seviyesi</span>
          <span className={`stat-value risk-${risk.toLowerCase()}`}>{risk}</span>
        </div>
      </div>

      <div className="prob-bar-wrap">
        <div
          className="prob-bar"
          style={{ width: `${prob}%`, backgroundColor: churn ? '#ef4444' : '#22c55e' }}
        />
      </div>
    </div>
  )
}

export default function App() {
  const [form, setForm] = useState(INITIAL_FORM)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  function handleChange(e) {
    const { name, value } = e.target
    setForm((prev) => ({ ...prev, [name]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          seniorcitizen: Number(form.seniorcitizen),
          tenure: Number(form.tenure),
          monthlycharges: Number(form.monthlycharges),
          totalcharges: Number(form.totalcharges),
        }),
      })

      const text = await res.text()

      if (!text) {
        throw new Error(`Sunucu boş yanıt döndürdü (HTTP ${res.status}). Backend çalışıyor mu?`)
      }

      let data
      try {
        data = JSON.parse(text)
      } catch {
        throw new Error(`Geçersiz yanıt: ${text.slice(0, 120)}`)
      }

      if (!res.ok) {
        throw new Error(data.detail || `HTTP ${res.status}`)
      }

      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const yesNo = [
    { value: 'Yes', label: 'Evet' },
    { value: 'No', label: 'Hayır' },
  ]
  const yesNoNone = [
    { value: 'No', label: 'Hayır' },
    { value: 'No phone service', label: 'Telefon hizmeti yok' },
    { value: 'Yes', label: 'Evet' },
  ]
  const yesNoNet = [
    { value: 'No', label: 'Hayır' },
    { value: 'No internet service', label: 'İnternet hizmeti yok' },
    { value: 'Yes', label: 'Evet' },
  ]

  return (
    <div className="app">
      <header className="app-header">
        <h1>Müşteri Kayıp Tahmini</h1>
        <p>CatBoost tabanlı makine öğrenmesi modeli ile müşteri kaybı tahmini yapın.</p>
      </header>

      <main className="app-main">
        <form className="churn-form" onSubmit={handleSubmit}>
     
          <section className="form-section">
            <h3 className="section-title">
              <span className="section-num">01</span> Müşteri Bilgileri
            </h3>
            <div className="field-grid">
              <SelectField
                label="Cinsiyet"
                name="gender"
                value={form.gender}
                onChange={handleChange}
                options={[
                  { value: 'Male', label: 'Erkek' },
                  { value: 'Female', label: 'Kadın' },
                ]}
              />
              <SelectField
                label="65 Yaş Üstü"
                name="seniorcitizen"
                value={form.seniorcitizen}
                onChange={handleChange}
                options={[
                  { value: 0, label: 'Hayır' },
                  { value: 1, label: 'Evet' },
                ]}
              />
              <SelectField
                label="Eş / Partner Var mı?"
                name="partner"
                value={form.partner}
                onChange={handleChange}
                options={yesNo}
              />
              <SelectField
                label="Bakmakla Yükümlü Kişi Var mı?"
                name="dependents"
                value={form.dependents}
                onChange={handleChange}
                options={yesNo}
              />
              <NumberField
                label="Abonelik Süresi (Ay)"
                name="tenure"
                value={form.tenure}
                onChange={handleChange}
                min={0}
                max={72}
                placeholder="örn: 24"
              />
            </div>
          </section>

         
          <section className="form-section">
            <h3 className="section-title">
              <span className="section-num">02</span> Telefon Hizmetleri
            </h3>
            <div className="field-grid">
              <SelectField
                label="Telefon Hizmeti"
                name="phoneservice"
                value={form.phoneservice}
                onChange={handleChange}
                options={yesNo}
              />
              <SelectField
                label="Çoklu Hat"
                name="multiplelines"
                value={form.multiplelines}
                onChange={handleChange}
                options={yesNoNone}
              />
            </div>
          </section>

         
          <section className="form-section">
            <h3 className="section-title">
              <span className="section-num">03</span> İnternet Hizmetleri
            </h3>
            <div className="field-grid">
              <SelectField
                label="İnternet Hizmeti"
                name="internetservice"
                value={form.internetservice}
                onChange={handleChange}
                options={[
                  { value: 'DSL', label: 'DSL' },
                  { value: 'Fiber optic', label: 'Fiber Optik' },
                  { value: 'No', label: 'Yok' },
                ]}
              />
              <SelectField
                label="Çevrimiçi Güvenlik"
                name="onlinesecurity"
                value={form.onlinesecurity}
                onChange={handleChange}
                options={yesNoNet}
              />
              <SelectField
                label="Çevrimiçi Yedekleme"
                name="onlinebackup"
                value={form.onlinebackup}
                onChange={handleChange}
                options={yesNoNet}
              />
              <SelectField
                label="Cihaz Koruması"
                name="deviceprotection"
                value={form.deviceprotection}
                onChange={handleChange}
                options={yesNoNet}
              />
              <SelectField
                label="Teknik Destek"
                name="techsupport"
                value={form.techsupport}
                onChange={handleChange}
                options={yesNoNet}
              />
              <SelectField
                label="TV Yayını"
                name="streamingtv"
                value={form.streamingtv}
                onChange={handleChange}
                options={yesNoNet}
              />
              <SelectField
                label="Film Yayını"
                name="streamingmovies"
                value={form.streamingmovies}
                onChange={handleChange}
                options={yesNoNet}
              />
            </div>
          </section>

         
          <section className="form-section">
            <h3 className="section-title">
              <span className="section-num">04</span> Sözleşme & Ödeme
            </h3>
            <div className="field-grid">
              <SelectField
                label="Sözleşme Türü"
                name="contract"
                value={form.contract}
                onChange={handleChange}
                options={[
                  { value: 'Month-to-month', label: 'Aylık' },
                  { value: 'One year', label: '1 Yıllık' },
                  { value: 'Two year', label: '2 Yıllık' },
                ]}
              />
              <SelectField
                label="Dijital Fatura (E-Fatura)"
                name="paperlessbilling"
                value={form.paperlessbilling}
                onChange={handleChange}
                options={yesNo}
              />
              <SelectField
                label="Ödeme Yöntemi"
                name="paymentmethod"
                value={form.paymentmethod}
                onChange={handleChange}
                options={[
                  { value: 'Bank transfer (automatic)', label: 'Banka Transferi (Otomatik)' },
                  { value: 'Credit card (automatic)', label: 'Kredi Kartı (Otomatik)' },
                  { value: 'Electronic check', label: 'Elektronik Çek' },
                  { value: 'Mailed check', label: 'Posta Çeki' },
                ]}
              />
              <NumberField
                label="Aylık Ücret ($)"
                name="monthlycharges"
                value={form.monthlycharges}
                onChange={handleChange}
                min={0}
                step={0.01}
                placeholder="örn: 75.50"
              />
              <NumberField
                label="Toplam Ücret ($)"
                name="totalcharges"
                value={form.totalcharges}
                onChange={handleChange}
                min={0}
                step={0.01}
                placeholder="örn: 1200.00"
              />
            </div>
          </section>

          <button className="submit-btn" type="submit" disabled={loading}>
            {loading ? (
              <span className="spinner-wrap">
                <span className="spinner" /> Tahmin yapılıyor...
              </span>
            ) : (
              'Churn Tahmini Yap'
            )}
          </button>
        </form>

        {error && (
          <div className="error-box">
            <strong>Hata:</strong> {error}
          </div>
        )}

        {result && <ResultCard result={result} />}
      </main>

      <footer className="app-footer">
        CatBoost · FastAPI · React · Vite
      </footer>
    </div>
  )
}
