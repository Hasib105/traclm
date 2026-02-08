import { get, post, del } from './client'
import type { ApiKey } from '../types'

/** Fetch all API keys */
export async function fetchApiKeys(): Promise<ApiKey[]> {
  return get<ApiKey[]>('/api-keys')
}

/** Create a new API key */
export async function createApiKey(data: { name: string; project_id?: number }): Promise<ApiKey> {
  return post<ApiKey>('/api-keys', data)
}

/** Revoke an API key */
export async function revokeApiKey(id: number): Promise<void> {
  return del(`/api-keys/${id}`)
}
