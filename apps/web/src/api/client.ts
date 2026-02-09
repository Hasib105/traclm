/** API base URL - uses relative paths that proxy to the backend */
const API_BASE = '/api/v1'

/** Generic API error */
export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

/** Make an API request */
async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`
  
  const res = await fetch(url, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new ApiError(res.status, data.detail || 'An error occurred')
  }

  // Handle 204 No Content
  if (res.status === 204) {
    return undefined as T
  }

  return res.json()
}

/** GET request */
export function get<T>(endpoint: string): Promise<T> {
  return request<T>(endpoint)
}

/** POST request */
export function post<T>(endpoint: string, data?: unknown): Promise<T> {
  return request<T>(endpoint, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  })
}

/** PATCH request */
export function patch<T>(endpoint: string, data: unknown): Promise<T> {
  return request<T>(endpoint, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

/** DELETE request */
export function del<T>(endpoint: string): Promise<T> {
  return request<T>(endpoint, {
    method: 'DELETE',
  })
}
