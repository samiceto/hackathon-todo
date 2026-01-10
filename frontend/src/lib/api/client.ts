/**
 * API client with JWT authentication support.
 *
 * Automatically includes JWT token in Authorization header for all requests.
 * Handles token refresh and error responses.
 */

import authClient from '../auth/auth-client'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ApiError {
  detail: string
  status?: number
}

export class ApiClientError extends Error {
  status: number
  detail: string

  constructor(message: string, status: number, detail: string) {
    super(message)
    this.name = 'ApiClientError'
    this.status = status
    this.detail = detail
  }
}

/**
 * Make an authenticated API request
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  // Get JWT token
  const token = authClient.getToken()

  if (!token) {
    throw new ApiClientError(
      'Not authenticated',
      401,
      'No authentication token found'
    )
  }

  // Build request URL
  const url = endpoint.startsWith('http')
    ? endpoint
    : `${API_URL}${endpoint}`

  // Add Authorization header
  const headers = new Headers(options.headers)
  headers.set('Authorization', `Bearer ${token}`)
  headers.set('Content-Type', 'application/json')

  // Make request
  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include', // Include cookies
  })

  // Handle non-OK responses
  if (!response.ok) {
    let errorDetail = 'Request failed'

    try {
      const errorData = await response.json()
      errorDetail = errorData.detail || errorDetail
    } catch {
      // Response body is not JSON
      errorDetail = response.statusText || errorDetail
    }

    // Handle 401 Unauthorized (token expired or invalid)
    if (response.status === 401) {
      // Clear token and redirect to signin
      await authClient.signout()
      if (typeof window !== 'undefined') {
        window.location.href = '/signin'
      }
    }

    throw new ApiClientError(
      `API Error: ${errorDetail}`,
      response.status,
      errorDetail
    )
  }

  // Handle 204 No Content (successful deletion)
  if (response.status === 204) {
    return undefined as T
  }

  // Parse JSON response
  try {
    return await response.json()
  } catch {
    // Response has no body
    return undefined as T
  }
}

/**
 * API client with convenience methods
 */
export const apiClient = {
  /**
   * GET request
   */
  async get<T>(endpoint: string): Promise<T> {
    return apiRequest<T>(endpoint, {
      method: 'GET',
    })
  },

  /**
   * POST request
   */
  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    return apiRequest<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  },

  /**
   * PUT request
   */
  async put<T>(endpoint: string, data: unknown): Promise<T> {
    return apiRequest<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  /**
   * PATCH request
   */
  async patch<T>(endpoint: string, data?: unknown): Promise<T> {
    return apiRequest<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    })
  },

  /**
   * DELETE request
   */
  async delete<T>(endpoint: string): Promise<T> {
    return apiRequest<T>(endpoint, {
      method: 'DELETE',
    })
  },
}

export default apiClient
