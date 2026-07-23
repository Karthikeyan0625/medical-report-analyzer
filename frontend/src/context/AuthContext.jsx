import { createContext, useContext, useEffect, useState } from 'react'
import {
  onAuthStateChanged,
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  updateProfile,
  signOut,
} from 'firebase/auth'
import { auth, googleProvider } from '../firebase.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [checkingAuth, setCheckingAuth] = useState(true)
  const [authError, setAuthError] = useState('')

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      setUser(firebaseUser)
      setCheckingAuth(false)
    })
    return unsubscribe
  }, [])

  async function loginWithGoogle() {
    setAuthError('')
    try {
      await signInWithPopup(auth, googleProvider)
    } catch (err) {
      setAuthError(err.message || 'Could not sign in. Please try again.')
    }
  }

  async function loginWithEmail(email, password) {
    setAuthError('')
    try {
      await signInWithEmailAndPassword(auth, email, password)
    } catch (err) {
      setAuthError(friendlyAuthError(err))
    }
  }

  async function signUpWithEmail(name, email, password) {
    setAuthError('')
    try {
      const credential = await createUserWithEmailAndPassword(auth, email, password)
      if (name) {
        await updateProfile(credential.user, { displayName: name })
        // updateProfile doesn't trigger onAuthStateChanged, so refresh our copy
        setUser({ ...credential.user, displayName: name })
      }
    } catch (err) {
      setAuthError(friendlyAuthError(err))
    }
  }

  async function logout() {
    await signOut(auth)
  }

  return (
    <AuthContext.Provider value={{
      user, checkingAuth, authError,
      loginWithGoogle, loginWithEmail, signUpWithEmail, logout,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

function friendlyAuthError(err) {
  const code = err.code || ''
  if (code.includes('email-already-in-use')) return 'An account already exists with this email. Try signing in instead.'
  if (code.includes('weak-password')) return 'Password should be at least 6 characters.'
  if (code.includes('invalid-email')) return 'Please enter a valid email address.'
  if (code.includes('invalid-credential') || code.includes('wrong-password') || code.includes('user-not-found')) {
    return 'Incorrect email or password.'
  }
  return err.message || 'Something went wrong. Please try again.'
}

export function useAuth() {
  return useContext(AuthContext)
}
