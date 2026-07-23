import { useState } from 'react'
import PulseLine from './components/PulseLine.jsx'
import UploadZone from './components/UploadZone.jsx'
import ResultPanel from './components/ResultPanel.jsx'
import AmbientBackground from './components/AmbientBackground.jsx'
import Login from './components/Login.jsx'
import History from './components/History.jsx'
import { useAuth } from './context/AuthContext.jsx'
import { analyzeReport } from './api.js'
import './App.css'

const STAGES = {
  IDLE: 'idle',
  ANALYZING: 'analyzing',
  RESULT: 'result',
  ERROR: 'error',
}

export default function App() {
  const { user, checkingAuth, logout } = useAuth()

  const [view, setView] = useState('upload') // 'upload' | 'history'
  const [stage, setStage] = useState(STAGES.IDLE)
  const [fileName, setFileName] = useState('')
  const [fileType, setFileType] = useState('')
  const [previewUrl, setPreviewUrl] = useState(null)
  const [result, setResult] = useState(null)
  const [errorMessage, setErrorMessage] = useState('')

  async function handleFileSelected(file) {
    setFileName(file.name)
    setFileType(file.type)
    setStage(STAGES.ANALYZING)
    setErrorMessage('')

    if (file.type.startsWith('image/')) {
      setPreviewUrl(URL.createObjectURL(file))
    } else {
      setPreviewUrl(null)
    }

    try {
      const data = await analyzeReport(file)
      setResult(data)
      setStage(STAGES.RESULT)
    } catch (err) {
      setErrorMessage(err.message || 'Something went wrong while analyzing the report.')
      setStage(STAGES.ERROR)
    }
  }

  function handleReset() {
    setStage(STAGES.IDLE)
    setResult(null)
    setFileName('')
    setFileType('')
    if (previewUrl) URL.revokeObjectURL(previewUrl)
    setPreviewUrl(null)
    setErrorMessage('')
  }

  if (checkingAuth) {
    return (
      <div className="app-loading">
        <AmbientBackground />
        <span className="app-loading__text">Loading Vitals…</span>
      </div>
    )
  }

  if (!user) {
    return <Login />
  }

  return (
    <div className={`app ${stage === STAGES.RESULT ? 'app--wide' : ''}`}>
      <AmbientBackground />

      <header className="app__header">
        <div className="app__brand">
          <span className="app__brand-mark">VITALS</span>
          <span className="app__brand-sub">Universal Report Reader</span>
        </div>

        <nav className="app__nav">
          <button
            className={`app__nav-btn ${view === 'upload' ? 'app__nav-btn--active' : ''}`}
            onClick={() => setView('upload')}
          >
            Analyze
          </button>
          <button
            className={`app__nav-btn ${view === 'history' ? 'app__nav-btn--active' : ''}`}
            onClick={() => setView('history')}
          >
            History
          </button>
        </nav>

        <div className="app__account">
          {user.photoURL && <img src={user.photoURL} alt="" className="app__avatar" />}
          <span className="app__account-name">{user.displayName?.split(' ')[0] || 'Account'}</span>
          <button className="app__logout" onClick={logout}>Sign out</button>
        </div>
      </header>

      {view === 'history' ? (
        <main className="app__main">
          <History onBack={() => setView('upload')} />
        </main>
      ) : (
        <>
          <PulseLine active={stage === STAGES.ANALYZING} />

      <main className="app__main">
        {stage === STAGES.IDLE && (
          <UploadZone onFileSelected={handleFileSelected} />
        )}

        {stage === STAGES.ANALYZING && (
          <div className="app__analyzing">
            <span className="app__analyzing-eyebrow">Reading — {fileName}</span>
            <p className="app__analyzing-text">
              Detecting report type, then routing to the matching model…
            </p>
          </div>
        )}

        {stage === STAGES.RESULT && result && (
          <ResultPanel
            result={result}
            fileName={fileName}
            previewUrl={previewUrl}
            fileType={fileType}
            onReset={handleReset}
          />
        )}

        {stage === STAGES.ERROR && (
          <div className="app__error">
            <span className="app__analyzing-eyebrow">Couldn't read that file</span>
            <p className="app__analyzing-text">{errorMessage}</p>
            <button className="result-panel__reset" onClick={handleReset}>Try again</button>
          </div>
        )}
      </main>
        </>
      )}

      <footer className="app__footer">
        <p>Screening assistant only — not a medical diagnosis. Always consult a doctor.</p>
      </footer>
    </div>
  )
}
