import type { User, AuthResponse } from '../types'

/** Check current authentication status */
export async function checkAuth(): Promise<User | null> {
  try {
    const res = await fetch('/api/v1/auth/me')
    if (res.ok) {
      return res.json()
    }
    return null
  } catch {
    return null
  }
}

/** Login with username and password */
export async function login(username: string, password: string): Promise<{ success: true; user: User } | { success: false; error: string }> {
  try {
    const res = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
    
    if (res.ok) {
      const data: AuthResponse = await res.json()
      return { success: true, user: data.user }
    }
    
    const err = await res.json()
    return { success: false, error: err.detail || 'Login failed' }
  } catch (e) {
    return { success: false, error: 'Network error' }
  }
}

/** Register a new account */
export async function register(
  username: string,
  email: string,
  password: string
): Promise<{ success: true; user: User } | { success: false; error: string }> {
  try {
    const res = await fetch('/api/v1/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password }),
    })
    
    if (res.ok) {
      const data: AuthResponse = await res.json()
      return { success: true, user: data.user }
    }
    
    const err = await res.json()
    return { success: false, error: err.detail || 'Registration failed' }
  } catch (e) {
    return { success: false, error: 'Network error' }
  }
}

/** Logout */
export async function logout(): Promise<void> {
  await fetch('/api/v1/auth/logout', { method: 'POST' })
}
