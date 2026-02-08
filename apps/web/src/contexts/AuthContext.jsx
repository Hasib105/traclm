import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import * as authApi from '../api/auth'

const AuthContext = createContext(null)

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is logged in on mount
    authApi.checkAuth()
      .then(userData => {
        setUser(userData)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  const login = useCallback(async (username, password) => {
    const result = await authApi.login(username, password)
    if (result.success) {
      setUser(result.user)
    }
    return result
  }, [])

  const register = useCallback(async (username, email, password) => {
    const result = await authApi.register(username, email, password)
    if (result.success) {
      setUser(result.user)
    }
    return result
  }, [])

  const logout = useCallback(async () => {
    await authApi.logout()
    setUser(null)
  }, [])

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export default AuthContext
