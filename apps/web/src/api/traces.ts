import { get, post, del } from './client'
import type { Trace, TraceListResponse } from '../types'

export interface TraceFilters {
  project_id?: number
  status?: string
  model_name?: string
  session_id?: string
  user_id?: string
  page?: number
  page_size?: number
}

/** Fetch traces with filters */
export async function fetchTraces(filters: TraceFilters = {}): Promise<TraceListResponse> {
  const params = new URLSearchParams()
  
  if (filters.project_id) params.set('project_id', String(filters.project_id))
  if (filters.status) params.set('status', filters.status)
  if (filters.model_name) params.set('model_name', filters.model_name)
  if (filters.session_id) params.set('session_id', filters.session_id)
  if (filters.user_id) params.set('user_id', filters.user_id)
  if (filters.page) params.set('page', String(filters.page))
  if (filters.page_size) params.set('page_size', String(filters.page_size))
  
  const query = params.toString()
  return get<TraceListResponse>(`/traces${query ? `?${query}` : ''}`)
}

/** Fetch a single trace by ID */
export async function fetchTrace(traceId: string): Promise<Trace> {
  return get<Trace>(`/traces/${traceId}`)
}

/** Fetch recent traces for dashboard */
export async function fetchRecentTraces(limit = 5): Promise<Trace[]> {
  return get<Trace[]>(`/traces/recent?limit=${limit}`)
}

/** Fetch trace statistics */
export async function fetchTraceStats(projectId?: number, days = 7) {
  const params = new URLSearchParams()
  if (projectId) params.set('project_id', String(projectId))
  params.set('days', String(days))
  return get(`/traces/stats?${params.toString()}`)
}

/** Delete a trace */
export async function deleteTrace(traceId: string): Promise<void> {
  return del(`/traces/${traceId}`)
}
