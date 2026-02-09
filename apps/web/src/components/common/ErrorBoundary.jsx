import { Component } from 'react'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, info) {
    // Surface details in console for debugging in dev.
    // Avoids a blank screen if a runtime error occurs.
    // eslint-disable-next-line no-console
    console.error('App crashed:', error, info)
  }

  render() {
    const { hasError, error } = this.state
    if (!hasError) return this.props.children

    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 p-6">
        <div className="max-w-lg w-full bg-white rounded-2xl shadow-lg border border-slate-200 p-6">
          <h1 className="text-xl font-semibold text-slate-900">Something went wrong</h1>
          <p className="text-slate-600 mt-2">
            The app hit a runtime error and couldn&apos;t render this page.
          </p>
          {error?.message && (
            <div className="mt-4 text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg p-3">
              {error.message}
            </div>
          )}
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="mt-6 inline-flex items-center justify-center px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 transition-colors"
          >
            Reload
          </button>
        </div>
      </div>
    )
  }
}
