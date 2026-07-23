import { useEffect, useState } from 'react'
import { fetchHistory } from '../api.js'
import './History.css'

const REPORT_TYPE_LABELS = {
  lab_report: 'Blood / Lab Report',
  xray: 'X-Ray',
  ct_scan: 'CT Scan',
  mri_scan: 'MRI Scan',
}

function formatDate(isoString) {
  try {
    return new Date(isoString).toLocaleString(undefined, {
      day: 'numeric', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    })
  } catch {
    return isoString
  }
}

export default function History({ onBack }) {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchHistory()
      .then(setReports)
      .catch((err) => setError(err.message || 'Could not load history.'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="history">
      <div className="history__header">
        <div>
          <span className="history__eyebrow">Your past reports</span>
          <h2 className="history__title">History</h2>
        </div>
        <button className="history__back" onClick={onBack}>New report</button>
      </div>

      {loading && <p className="history__empty">Loading…</p>}
      {error && <p className="history__empty">{error}</p>}

      {!loading && !error && reports.length === 0 && (
        <p className="history__empty">No reports analyzed yet. Upload one to see it here.</p>
      )}

      <div className="history__list">
        {reports.map((report) => {
          const result = report.result || {}
          const flagged = result.disease_detected
          return (
            <div className="history__row" key={report.id}>
              <div className="history__row-main">
                <span className={`history__dot ${flagged ? 'history__dot--alert' : 'history__dot--clear'}`} />
                <div>
                  <p className="history__row-title">
                    {REPORT_TYPE_LABELS[report.report_type] || report.report_type}
                    {result.disease_name ? ` — ${result.disease_name}` : ''}
                  </p>
                  <p className="history__row-file">{report.filename}</p>
                </div>
              </div>
              <span className="history__row-date">{formatDate(report.created_at)}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
