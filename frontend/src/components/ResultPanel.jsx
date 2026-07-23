import './ResultPanel.css'

const REPORT_TYPE_LABELS = {
  lab_report: 'Blood / Lab Report',
  xray: 'X-Ray',
  ct_scan: 'CT Scan',
  mri_scan: 'MRI Scan',
}

function FlagChip({ status }) {
  const styles = {
    high: { label: 'High', className: 'flag-chip--alert' },
    low: { label: 'Low', className: 'flag-chip--alert' },
    normal: { label: 'Normal', className: 'flag-chip--normal' },
    unknown_range: { label: '—', className: 'flag-chip--neutral' },
  }
  const { label, className } = styles[status] || styles.unknown_range
  return <span className={`flag-chip ${className}`}>{label}</span>
}

/** Left-hand box: the actual uploaded image, or a document icon for PDFs. */
function PreviewBox({ previewUrl, fileType, reportType }) {
  return (
    <div className="preview-box">
      {previewUrl ? (
        <img src={previewUrl} alt="Uploaded report" className="preview-box__image" />
      ) : (
        <div className="preview-box__icon">
          <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 4h16l10 10v28a2 2 0 0 1-2 2H12a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2Z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
            <path d="M28 4v10h10" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
            <path d="M16 26h16M16 32h16M16 20h8" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
          </svg>
        </div>
      )}
      <span className="preview-box__tag">{REPORT_TYPE_LABELS[reportType] || reportType}</span>
    </div>
  )
}

/** Doctor / specialist suggestion, shown as its own card so it stands out. */
function ConsultCard({ consult }) {
  if (!consult) return null
  return (
    <div className="consult-card">
      <div className="consult-card__icon">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z" stroke="currentColor" strokeWidth="1.6"/>
          <path d="M4 20c1.2-3.8 4.4-6 8-6s6.8 2.2 8 6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
        </svg>
      </div>
      <div>
        <p className="consult-card__label">Recommended consult</p>
        <p className="consult-card__value">{consult}</p>
      </div>
    </div>
  )
}

function LabFindings({ result }) {
  const entries = Object.entries(result.extracted_values || {})

  return (
    <>
      <div className="lab-table">
        <div className="lab-table__head">
          <span>Marker</span>
          <span>Value</span>
          <span>Status</span>
        </div>
        {entries.length === 0 && (
          <p className="result-panel__empty">
            No recognized lab markers were found in this document. Try a clearer scan,
            or a report that includes standard marker names (Glucose, Cholesterol, etc.)
          </p>
        )}
        {entries.map(([marker, value]) => (
          <div className="lab-table__row" key={marker}>
            <span className="lab-table__marker">{marker.replace('_', ' ')}</span>
            <span className="lab-table__value">{value}</span>
            <FlagChip status={result.flags?.[marker]} />
          </div>
        ))}
      </div>

      {(result.findings || []).map((finding) => (
        <div className="finding-block" key={finding.marker}>
          <p className="finding-block__title">
            {finding.marker.replace('_', ' ')} — {finding.status}
          </p>
          <p className="finding-block__desc">{finding.description}</p>
        </div>
      ))}
    </>
  )
}

function ScanConfidence({ result }) {
  return (
    <div className="scan-result__confidence">
      <div className="scan-result__ring" style={{ '--pct': result.confidence }}>
        <span>{Math.round(result.confidence * 100)}%</span>
      </div>
      <div>
        <p className="scan-result__label">Model confidence</p>
        <p className="scan-result__sub">
          {result.disease_detected ? finLabel(result.disease_name) : 'No abnormality detected'}
        </p>
      </div>
    </div>
  )
}

function finLabel(name) {
  if (!name) return ''
  return name.charAt(0).toUpperCase() + name.slice(1).replace('_', ' ')
}

export default function ResultPanel({ result, fileName, previewUrl, fileType, onReset }) {
  const isLab = result.report_type === 'lab_report'
  const statusLabel = result.disease_detected ? 'Findings flagged' : 'Nothing flagged'
  const statusClass = result.disease_detected ? 'result-panel__status--alert' : 'result-panel__status--clear'

  return (
    <div className="result-panel">
      <PreviewBox previewUrl={previewUrl} fileType={fileType} reportType={result.report_type} />

      <div className="result-panel__body">
        <div className="result-panel__header">
          <div>
            <span className="result-panel__eyebrow">02 — Reading complete</span>
            <h2 className="result-panel__title">
              {result.disease_detected ? finLabel(result.disease_name) || 'Finding detected' : 'No abnormality detected'}
            </h2>
            <p className="result-panel__filename">{fileName}</p>
          </div>
          <span className={`result-panel__status ${statusClass}`}>{statusLabel}</span>
        </div>

        {typeof result.description === 'string' && (
          <p className="result-panel__description">{result.description}</p>
        )}

        {!isLab && <ScanConfidence result={result} />}
        {isLab && <LabFindings result={result} />}

        <ConsultCard consult={result.consult} />

        <div className="result-panel__disclaimer">
          <span className="result-panel__disclaimer-mark">!</span>
          <p>{result.disclaimer}</p>
        </div>

        <button className="result-panel__reset" onClick={onReset}>
          Analyze another report
        </button>
      </div>
    </div>
  )
}
