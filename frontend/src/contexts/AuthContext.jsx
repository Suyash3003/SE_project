import { createContext, useContext, useMemo, useState } from 'react'
import { Navigate } from 'react-router-dom'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [session, setSession] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('paintflow_session')) || null
    } catch {
      return null
    }
  })

  const saveSession = (data) => {
    const next = { token: data.access_token, role: data.role, dealerId: data.dealer_id }
    localStorage.setItem('paintflow_session', JSON.stringify(next))
    setSession(next)
  }

  const logout = () => {
    localStorage.removeItem('paintflow_session')
    setSession(null)
  }

  const value = useMemo(() => ({
    session,
    isAuthenticated: Boolean(session?.token),
    saveSession,
    logout,
  }), [session])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  return useContext(AuthContext)
}

export function ProtectedRoute({ role, children }) {
  const { session } = useAuth()
  if (!session?.token) return <Navigate to="/login" replace />
  if (role && session.role !== role) return <Navigate to={`/${session.role}`} replace />
  return children
}
