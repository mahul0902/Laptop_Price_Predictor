import { useState, useEffect } from 'react'

const DEFAULTS = {
  brand: 'HP',
  processor: '12th Gen Intel Core i5 12450H',
  ram: '8GB',
  ram_type: 'DDR4',
  rom: '512GB',
  rom_type: 'SSD',
  gpu: 'Intel Iris Xe Graphics',
  display_size: '15.6',
  resolution: '1920x1080',
  os: 'Windows 11',
  warranty: '1',
}

function Field({ label, children }) {
  return (
    <div className="field">
      <label>{label}</label>
      {children}
    </div>
  )
}

export default function App() {
  const [options, setOptions] = useState(null)
  const [form, setForm]       = useState(DEFAULTS)
  const [loading, setLoading] = useState(false)
  const [result, setResult]   = useState(null)
  const [error, setError]     = useState(null)

  // Fetch dropdown options from backend
  useEffect(() => {
    fetch('/api/options')
      .then(r => r.json())
      .then(setOptions)
      .catch(() => setError('Could not connect to backend. Make sure the server is running.'))
  }, [])

  const set = (key) => (e) => setForm(f => ({ ...f, [key]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    setError(null)

    // Parse resolution
    const [rw, rh] = form.resolution.split('x').map(Number)

    try {
      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          brand:            form.brand,
          processor:        form.processor,
          ram:              form.ram,
          ram_type:         form.ram_type,
          rom:              form.rom,
          rom_type:         form.rom_type,
          gpu:              form.gpu,
          display_size:     form.display_size,
          resolution_width: rw,
          resolution_height:rh,
          os:               form.os,
          warranty:         form.warranty,
        }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Prediction failed')
      setResult(data.price)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (!options && !error) {
    return (
      <div className="page">
        <div className="hero"><span className="spinner" /> Loading options…</div>
      </div>
    )
  }

  return (
    <div className="page">
      {/* ── hero ── */}
      <div className="hero">
        <div className="badge">ML-Powered</div>
        <h1>💻 Laptop Price Predictor</h1>
        <p>Enter your laptop specifications below and get an instant price estimate.</p>
      </div>

      {/* ── form card ── */}
      <div className="card">
        <form onSubmit={handleSubmit}>

          {/* Brand & OS */}
          <div className="section-title">Brand &amp; Platform</div>
          <div className="form-grid">
            <Field label="Brand">
              <select value={form.brand} onChange={set('brand')}>
                {(options?.brands || []).map(b => <option key={b}>{b}</option>)}
              </select>
            </Field>

            <Field label="Operating System">
              <select value={form.os} onChange={set('os')}>
                {(options?.os_options || []).map(o => <option key={o}>{o}</option>)}
              </select>
            </Field>

            <Field label="Warranty (years)">
              <select value={form.warranty} onChange={set('warranty')}>
                {(options?.warranty_options || []).map(w => <option key={w}>{w}</option>)}
              </select>
            </Field>
          </div>

          {/* Processor */}
          <div className="section-title">Processor</div>
          <div className="form-grid" style={{ gridTemplateColumns: '1fr' }}>
            <Field label="Processor model (e.g. 12th Gen Intel Core i5 12450H)">
              <input
                type="text"
                value={form.processor}
                onChange={set('processor')}
                placeholder="e.g. 13th Gen Intel Core i7 13700H"
              />
            </Field>
          </div>

          {/* Memory */}
          <div className="section-title">Memory &amp; Storage</div>
          <div className="form-grid">
            <Field label="RAM">
              <select value={form.ram} onChange={set('ram')}>
                {(options?.ram_options || []).map(r => <option key={r}>{r}</option>)}
              </select>
            </Field>

            <Field label="RAM Type">
              <select value={form.ram_type} onChange={set('ram_type')}>
                {(options?.ram_types || []).map(r => <option key={r}>{r}</option>)}
              </select>
            </Field>

            <Field label="Storage">
              <select value={form.rom} onChange={set('rom')}>
                {(options?.rom_options || []).map(r => <option key={r}>{r}</option>)}
              </select>
            </Field>

            <Field label="Storage Type">
              <select value={form.rom_type} onChange={set('rom_type')}>
                {(options?.rom_types || []).map(r => <option key={r}>{r}</option>)}
              </select>
            </Field>
          </div>

          {/* GPU */}
          <div className="section-title">Graphics</div>
          <div className="form-grid" style={{ gridTemplateColumns: '1fr' }}>
            <Field label="GPU (e.g. 4GB NVIDIA GeForce RTX 3050 or Intel Iris Xe)">
              <input
                type="text"
                value={form.gpu}
                onChange={set('gpu')}
                placeholder="e.g. 6GB NVIDIA GeForce RTX 4060"
              />
            </Field>
          </div>

          {/* Display */}
          <div className="section-title">Display</div>
          <div className="form-grid">
            <Field label="Display Size (inches)">
              <select value={form.display_size} onChange={set('display_size')}>
                {(options?.display_sizes || []).map(d => <option key={d}>{d}</option>)}
              </select>
            </Field>

            <Field label="Resolution">
              <select value={form.resolution} onChange={set('resolution')}>
                {(options?.resolutions || []).map(r => (
                  <option key={r.label} value={`${r.width}x${r.height}`}>{r.label}</option>
                ))}
              </select>
            </Field>
          </div>

          {/* Submit */}
          <div className="submit-row">
            <button className="btn-predict" type="submit" disabled={loading}>
              {loading && <span className="spinner" />}
              {loading ? 'Predicting…' : 'Predict Price'}
            </button>
          </div>
        </form>

        {/* ── Result ── */}
        {result !== null && (
          <div className="result-box">
            <div className="label">Estimated Price</div>
            <div className="price">
              ₹{Math.round(result).toLocaleString('en-IN')}
            </div>
            <div className="note">Prediction based on Gradient Boosting Regression on 893 laptops</div>
          </div>
        )}

        {/* ── Error ── */}
        {error && <div className="error-box">⚠ {error}</div>}
      </div>
    </div>
  )
}
