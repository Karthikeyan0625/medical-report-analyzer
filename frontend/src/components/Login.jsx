import { useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import AmbientBackground from './AmbientBackground.jsx'
import './Login.css'

export default function Login() {
  const { loginWithGoogle, loginWithEmail, signUpWithEmail, authError } = useAuth()
  const [mode, setMode] = useState('signin') // 'signin' | 'signup'
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const isSignUp = mode === 'signup'

  async function handleSubmit(e) {
    e.preventDefault()
    setSubmitting(true)
    if (isSignUp) {
      await signUpWithEmail(name, email, password)
    } else {
      await loginWithEmail(email, password)
    }
    setSubmitting(false)
  }

  return (
    <div className="login">
      <AmbientBackground />

      <div className="login__card">
        <div className="login__brand">
          <span className="login__brand-mark">VITALS</span>
          <span className="login__brand-sub">Universal Report Reader</span>
        </div>

        <h1 className="login__title">Read any report,<br />in one place.</h1>
        <p className="login__subtitle">
          Blood work, X-rays, CT and MRI scans — upload one, and Vitals
          works out what it is and reads it for you.
        </p>

        <button type="button" className="login__google-btn" onClick={loginWithGoogle}>
          <svg width="18" height="18" viewBox="0 0 18 18" xmlns="http://www.w3.org/2000/svg">
            <path fill="#4285F4" d="M17.64 9.2c0-.64-.06-1.25-.16-1.84H9v3.48h4.84a4.14 4.14 0 0 1-1.8 2.72v2.26h2.9c1.7-1.57 2.7-3.88 2.7-6.62Z"/>
            <path fill="#34A853" d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.9-2.26c-.8.54-1.84.86-3.06.86-2.35 0-4.34-1.59-5.05-3.72H.9v2.33A9 9 0 0 0 9 18Z"/>
            <path fill="#FBBC05" d="M3.95 10.7A5.4 5.4 0 0 1 3.67 9c0-.59.1-1.17.28-1.7V4.97H.9A9 9 0 0 0 0 9c0 1.45.35 2.83.9 4.03l3.05-2.33Z"/>
            <path fill="#EA4335" d="M9 3.58c1.32 0 2.5.46 3.44 1.35l2.58-2.58C13.46.89 11.42 0 9 0A9 9 0 0 0 .9 4.97l3.05 2.33C4.66 5.17 6.65 3.58 9 3.58Z"/>
          </svg>
          Continue with Google
        </button>

        <div className="login__divider"><span>or</span></div>

        <form className="login__form" onSubmit={handleSubmit}>
          {isSignUp && (
            <input
              type="text"
              placeholder="Full name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="login__input"
              required
            />
          )}
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="login__input"
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="login__input"
            required
            minLength={6}
          />
          <button type="submit" className="login__submit-btn" disabled={submitting}>
            {submitting ? 'Please wait…' : isSignUp ? 'Create account' : 'Sign in'}
          </button>
        </form>

        {authError && <p className="login__error">{authError}</p>}

        <p className="login__switch">
          {isSignUp ? 'Already have an account?' : "Don't have an account?"}{' '}
          <button
            type="button"
            className="login__switch-btn"
            onClick={() => setMode(isSignUp ? 'signin' : 'signup')}
          >
            {isSignUp ? 'Sign in' : 'Create one'}
          </button>
        </p>

        <p className="login__disclaimer">
          Screening assistant only — not a medical diagnosis. Always consult a doctor.
        </p>
      </div>
    </div>
  )
}
