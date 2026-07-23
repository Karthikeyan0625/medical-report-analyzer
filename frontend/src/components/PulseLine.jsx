import './PulseLine.css'

/**
 * A traveling ECG-style trace. Used in the header (idle, slow) and
 * during analysis (faster, "reading" the uploaded report).
 */
export default function PulseLine({ active = false }) {
  return (
    <div className={`pulse-line ${active ? 'pulse-line--active' : ''}`}>
      <svg viewBox="0 0 600 60" preserveAspectRatio="none" className="pulse-line__svg">
        <path
          className="pulse-line__path"
          d="M0,30 L140,30 L160,30 L172,8 L184,52 L196,30 L216,30 L600,30"
          fill="none"
          strokeWidth="2"
        />
      </svg>
    </div>
  )
}
