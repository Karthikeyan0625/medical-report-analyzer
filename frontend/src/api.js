import { auth } from './firebase.js'

const API_BASE =import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function authHeaders() {
  const token = await auth.currentUser?.getIdToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function analyzeReport(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE}/api/analyze-report`, {
    method: 'POST',
    headers: await authHeaders(),
    body: formData,
  })

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}))
    throw new Error(errorBody.detail || `Request failed (${response.status})`)
  }

  return response.json()
}

export async function fetchHistory() {
  const response = await fetch(`${API_BASE}/api/history`, {
    headers: await authHeaders(),
  })

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}))
    throw new Error(errorBody.detail || `Request failed (${response.status})`)
  }

  const data = await response.json()
  return data.reports || []
}
