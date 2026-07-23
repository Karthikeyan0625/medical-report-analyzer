import './AmbientBackground.css'

/**
 * Fixed, full-viewport backdrop: two soft blurred fields (pine + clay) that
 * drift very slowly, plus a faint pulse-line watermark. Sits behind every
 * screen (login and the main app) so the whole product shares one calm,
 * clinical atmosphere instead of a flat white page.
 */
export default function AmbientBackground() {
  return (
    <div className="ambient-bg" aria-hidden="true">
      <div className="ambient-bg__blob ambient-bg__blob--pine" />
      <div className="ambient-bg__blob ambient-bg__blob--clay" />
      <svg className="ambient-bg__trace" viewBox="0 0 1200 400" preserveAspectRatio="xMidYMid slice">
        <path
          d="M0,200 L420,200 L450,200 L468,150 L486,250 L504,200 L540,200 L1200,200"
          fill="none"
          stroke="var(--clinical-teal)"
          strokeWidth="1.5"
        />
      </svg>
    </div>
  )
}
