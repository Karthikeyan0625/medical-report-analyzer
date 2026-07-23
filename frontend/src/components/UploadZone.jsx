import { useRef, useState } from 'react'
import './UploadZone.css'

const REPORT_HINTS = [
  { label: 'Blood test', ext: 'PDF' },
  { label: 'X-ray', ext: 'JPG / PNG' },
  { label: 'CT scan', ext: 'DCM / JPG' },
  { label: 'MRI scan', ext: 'DCM / JPG' },
]

export default function UploadZone({ onFileSelected, disabled }) {
  const inputRef = useRef(null)
  const [isDragging, setIsDragging] = useState(false)

  function handleFiles(fileList) {
    const file = fileList?.[0]
    if (file) onFileSelected(file)
  }

  return (
    <div
      className={`upload-zone ${isDragging ? 'upload-zone--dragging' : ''} ${disabled ? 'upload-zone--disabled' : ''}`}
      onDragOver={(e) => { e.preventDefault(); if (!disabled) setIsDragging(true) }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => {
        e.preventDefault()
        setIsDragging(false)
        if (!disabled) handleFiles(e.dataTransfer.files)
      }}
      onClick={() => !disabled && inputRef.current?.click()}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => { if (!disabled && (e.key === 'Enter' || e.key === ' ')) inputRef.current?.click() }}
      aria-label="Upload a medical report"
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.jpg,.jpeg,.png,.dcm"
        hidden
        onChange={(e) => handleFiles(e.target.files)}
        disabled={disabled}
      />

      <span className="upload-zone__eyebrow">01 — Submit a report</span>
      <h2 className="upload-zone__title">Drop any report here</h2>
      <p className="upload-zone__subtitle">
        One box, any modality. We work out what it is and read it accordingly.
      </p>

      <div className="upload-zone__hints">
        {REPORT_HINTS.map((hint) => (
          <div className="upload-zone__hint" key={hint.label}>
            <span className="upload-zone__hint-label">{hint.label}</span>
            <span className="upload-zone__hint-ext">{hint.ext}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
