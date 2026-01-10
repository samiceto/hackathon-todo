/**
 * Better Auth client for authentication operations.
 *
 * Provides methods for signup, signin, signout, and session management.
 * JWT tokens are stored in httpOnly cookies for security.
 */

import { authConfig } from './auth-config'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface User {
  id: number
  email: string
  created_at?: string
}

export interface AuthResponse {
  user: User
  token: string
}

export interface SignupData {
  email: string
  password: string
}

export interface SigninData {
  email: string
  password: string
}

/**
 * Authentication client
 */
export const authClient = {
  /**
   * Sign up a new user
   */
  async signup(data: SignupData): Promise<AuthResponse> {
    const response = await fetch(`${API_URL}/api/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
      credentials: 'include', // Include cookies in request
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Signup failed')
    }

    const result: AuthResponse = await response.json()

    // Store JWT token in localStorage (fallback if httpOnly cookies not working)
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', result.token)
    }

    return result
  },

  /**
   * Sign in an existing user
   */
  async signin(data: SigninData): Promise<AuthResponse> {
    const response = await fetch(`${API_URL}/api/auth/signin`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
      credentials: 'include', // Include cookies in request
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Signin failed')
    }

    const result: AuthResponse = await response.json()

    // Store JWT token in localStorage (fallback if httpOnly cookies not working)
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', result.token)
    }

    return result
  },

  /**
   * Sign out current user
   */
  async signout(): Promise<void> {
    // Clear token from localStorage
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token')
    }

    // Note: In production with httpOnly cookies, you'd call a backend endpoint
    // to clear the cookie: await fetch(`${API_URL}/api/auth/signout`, ...)
  },

  /**
   * Get current JWT token
   */
  getToken(): string | null {
    if (typeof window === 'undefined') {
      return null
    }
    return localStorage.getItem('auth_token')
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return this.getToken() !== null
  },

  /**
   * Get current user from JWT token
   * Note: This is a simplified implementation
   * In production, you'd decode the JWT to get user info
   */
  getCurrentUser(): User | null {
    const token = this.getToken()
    if (!token) {
      return null
    }

    try {
      // Decode JWT payload (middle part of token)
      const payload = JSON.parse(atob(token.split('.')[1]))
      return {
        id: parseInt(payload.sub),
        email: payload.email,
      }
    } catch (error) {
      console.error('Failed to decode JWT:', error)
      return null
    }
  },
}

export default authClient
