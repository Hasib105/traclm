/** Trace data from the API */
export interface Trace {
  id: number
  trace_id: string
  parent_trace_id: string | null
  project_id: number | null
  model_name: string
  model_provider: string | null
  status: 'running' | 'success' | 'error'
  error_message: string | null
  input_data: Record<string, unknown>
  output_data: Record<string, unknown>
  tool_calls: ToolCall[]
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
  cost_cents: number
  start_time: string
  end_time: string | null
  latency_ms: number
  metadata: Record<string, unknown>
  tags: string[]
  session_id: string | null
  user_id: string | null
}

export interface ToolCall {
  name: string
  input: string
  output?: string
  error?: string
  start_time: string
  end_time?: string
  status: 'success' | 'error'
}

export interface TraceListResponse {
  traces: Trace[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

/** Project data */
export interface Project {
  id: number
  name: string
  description: string | null
  created_at: string
  updated_at: string
}

/** API Key data */
export interface ApiKey {
  id: number
  name: string
  key?: string
  key_prefix: string
  project_id: number | null
  is_active: boolean
  created_at: string
  last_used_at: string | null
}

/** User data */
export interface User {
  id: number
  username: string
  email: string
  is_admin: boolean
}

/** Dashboard stats */
export interface DashboardStats {
  trace_count: number
  project_count: number
  api_key_count: number
}

/** Auth response */
export interface AuthResponse {
  user: User
}
