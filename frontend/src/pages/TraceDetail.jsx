import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'

export default function TraceDetail() {
  const { traceId } = useParams()
  const [trace, setTrace] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('input')

  useEffect(() => {
    fetch(`/api/traces/${traceId}`)
      .then(r => {
        if (!r.ok) throw new Error('Trace not found')
        return r.json()
      })
      .then(data => setTrace(data))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [traceId])

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A'
    return new Date(dateStr).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  const formatJson = (data) => {
    if (!data) return 'No data'
    return JSON.stringify(data, null, 2)
  }

  const getStatusConfig = (status) => {
    const configs = {
      success: { bg: 'bg-emerald-500/10', text: 'text-emerald-600', border: 'border-emerald-500/20', icon: '✓' },
      error: { bg: 'bg-red-500/10', text: 'text-red-600', border: 'border-red-500/20', icon: '✕' },
      running: { bg: 'bg-amber-500/10', text: 'text-amber-600', border: 'border-amber-500/20', icon: '◷' }
    }
    return configs[status] || configs.running
  }

  const calculateDuration = () => {
    if (!trace?.start_time || !trace?.end_time) return 'N/A'
    const start = new Date(trace.start_time)
    const end = new Date(trace.end_time)
    const diff = end - start
    if (diff < 1000) return `${diff}ms`
    return `${(diff / 1000).toFixed(2)}s`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <div className="w-16 h-16 bg-red-100 rounded-2xl flex items-center justify-center mb-4">
          <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p className="text-red-600 font-medium mb-4">{error}</p>
        <Link 
          to="/traces" 
          className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-700 font-medium"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to traces
        </Link>
      </div>
    )
  }

  const statusConfig = getStatusConfig(trace?.status)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link 
          to="/traces" 
          className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-slate-800">{trace?.name || 'LLM Trace'}</h1>
          <p className="text-slate-500 text-sm font-mono mt-1">{trace?.trace_id}</p>
        </div>
        <span className={`inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-xl ${statusConfig.bg} ${statusConfig.text} border ${statusConfig.border}`}>
          <span>{statusConfig.icon}</span>
          {trace?.status || 'running'}
        </span>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-200/60">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <span className="text-sm text-slate-500">Model</span>
          </div>
          <p className="text-lg font-semibold text-slate-800">{trace?.model || 'Unknown'}</p>
        </div>
        
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-200/60">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
              </svg>
            </div>
            <span className="text-sm text-slate-500">Tokens</span>
          </div>
          <p className="text-lg font-semibold text-slate-800">{trace?.total_tokens?.toLocaleString() || '0'}</p>
        </div>
        
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-200/60">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <span className="text-sm text-slate-500">Duration</span>
          </div>
          <p className="text-lg font-semibold text-slate-800">{calculateDuration()}</p>
        </div>
        
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-slate-200/60">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-gradient-to-br from-amber-500 to-orange-600 rounded-xl flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <span className="text-sm text-slate-500">Started</span>
          </div>
          <p className="text-sm font-semibold text-slate-800">{formatDate(trace?.start_time)}</p>
        </div>
      </div>

      {/* Content Tabs */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200/60 overflow-hidden">
        <div className="flex border-b border-slate-200">
          {['input', 'output', 'metadata'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-4 text-sm font-medium transition-colors relative ${
                activeTab === tab 
                  ? 'text-indigo-600' 
                  : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
              {activeTab === tab && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600"></div>
              )}
            </button>
          ))}
          {trace?.error && (
            <button
              onClick={() => setActiveTab('error')}
              className={`px-6 py-4 text-sm font-medium transition-colors relative ${
                activeTab === 'error' 
                  ? 'text-red-600' 
                  : 'text-red-400 hover:text-red-500'
              }`}
            >
              Error
              {activeTab === 'error' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-red-600"></div>
              )}
            </button>
          )}
        </div>

        <div className="p-6">
          {activeTab === 'input' && (
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-slate-700">Input Data</h3>
                <button 
                  onClick={() => navigator.clipboard.writeText(formatJson(trace?.input_data))}
                  className="text-xs text-slate-500 hover:text-indigo-600 flex items-center gap-1"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  Copy
                </button>
              </div>
              <pre className="bg-slate-900 text-slate-100 p-5 rounded-xl overflow-auto text-sm max-h-96 font-mono">
                {formatJson(trace?.input_data)}
              </pre>
            </div>
          )}

          {activeTab === 'output' && (
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-slate-700">Output Data</h3>
                <button 
                  onClick={() => navigator.clipboard.writeText(formatJson(trace?.output_data))}
                  className="text-xs text-slate-500 hover:text-indigo-600 flex items-center gap-1"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  Copy
                </button>
              </div>
              <pre className="bg-slate-900 text-slate-100 p-5 rounded-xl overflow-auto text-sm max-h-96 font-mono">
                {formatJson(trace?.output_data)}
              </pre>
            </div>
          )}

          {activeTab === 'metadata' && (
            <div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-slate-700">Metadata</h3>
              </div>
              {trace?.metadata && Object.keys(trace.metadata).length > 0 ? (
                <pre className="bg-slate-100 text-slate-700 p-5 rounded-xl overflow-auto text-sm max-h-96 font-mono">
                  {formatJson(trace.metadata)}
                </pre>
              ) : (
                <div className="text-center py-8 text-slate-400">
                  <p>No metadata available</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'error' && trace?.error && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 className="text-sm font-semibold text-red-700">Error Details</h3>
              </div>
              <pre className="bg-red-50 text-red-800 p-5 rounded-xl overflow-auto text-sm max-h-96 font-mono border border-red-200">
                {trace.error}
              </pre>
            </div>
          )}
        </div>
      </div>

      {/* Timeline */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200/60 p-6">
        <h3 className="text-sm font-semibold text-slate-700 mb-4">Timeline</h3>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-emerald-500 rounded-full"></div>
            <span className="text-sm text-slate-600">Start: {formatDate(trace?.start_time)}</span>
          </div>
          <div className="flex-1 h-1 bg-gradient-to-r from-emerald-500 to-indigo-500 rounded-full"></div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-indigo-500 rounded-full"></div>
            <span className="text-sm text-slate-600">End: {formatDate(trace?.end_time)}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
