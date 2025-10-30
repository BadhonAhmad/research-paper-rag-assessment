'use client'

import { useState } from 'react'

interface Citation {
  paper_title: string
  section: string | null
  page: number
  relevance_score: number
  chunk_text?: string
}

interface QueryResponse {
  answer: string
  citations: Citation[]
  sources_used: string[]
  confidence: number
  response_time: number
}

export default function QueryPage() {
  const [question, setQuestion] = useState('')
  const [topK, setTopK] = useState(5)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<QueryResponse | null>(null)
  const [error, setError] = useState('')

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim()) return

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question.trim(),
          top_k: topK,
        }),
      })

      const data = await response.json()

      if (response.ok) {
        setResult(data)
      } else {
        setError(data.detail || 'Query failed')
      }
    } catch (err) {
      setError('Network error - is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Query Papers</h1>

      <form onSubmit={handleQuery} className="bg-white border border-gray-300 rounded-lg p-6 mb-6">
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Your Question
          </label>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="E.g., What methodology was used in the transformer paper?"
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Top K Results: {topK}
          </label>
          <input
            type="range"
            min="1"
            max="20"
            value={topK}
            onChange={(e) => setTopK(parseInt(e.target.value))}
            className="w-full"
            disabled={loading}
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>1</span>
            <span>20</span>
          </div>
        </div>

        <button
          type="submit"
          disabled={!question.trim() || loading}
          className="w-full bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {loading ? 'Searching...' : 'Ask Question'}
        </button>
      </form>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg mb-4">
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div className="space-y-6">
          {/* Answer */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-blue-900 mb-3">Answer</h2>
            <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
              {result.answer}
            </p>
            <div className="mt-4 flex gap-4 text-sm text-gray-600">
              <span>
                <strong>Confidence:</strong> {(result.confidence * 100).toFixed(1)}%
              </span>
              <span>
                <strong>Response Time:</strong> {result.response_time.toFixed(2)}s
              </span>
            </div>
          </div>

          {/* Sources */}
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-purple-900 mb-3">
              Sources ({result.sources_used.length})
            </h2>
            <ul className="list-disc list-inside space-y-1">
              {result.sources_used.map((source, idx) => (
                <li key={idx} className="text-gray-700">
                  {source}
                </li>
              ))}
            </ul>
          </div>

          {/* Citations */}
          <div className="bg-white border border-gray-300 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Citations ({result.citations.length})
            </h2>
            <div className="space-y-4">
              {result.citations.map((citation, idx) => (
                <div
                  key={idx}
                  className="border-l-4 border-green-500 pl-4 py-2 bg-gray-50"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-semibold text-gray-900">
                      {citation.paper_title}
                    </h3>
                    <span className="text-sm bg-green-100 text-green-800 px-2 py-1 rounded">
                      {(citation.relevance_score * 100).toFixed(0)}% relevant
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 mb-2">
                    <strong>Section:</strong> {citation.section || 'N/A'} •{' '}
                    <strong>Page:</strong> {citation.page}
                  </div>
                  {citation.chunk_text && (
                    <p className="text-sm text-gray-700 italic">
                      "{citation.chunk_text}"
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="mt-6 bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h3 className="font-semibold mb-2">💡 Example Questions</h3>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>• What methodology was used in the transformer paper?</li>
          <li>• Which activation functions are commonly used in neural networks?</li>
          <li>• Compare the performance of CNNs and Transformers.</li>
          <li>• What datasets are used to evaluate computer vision models?</li>
        </ul>
      </div>
    </div>
  )
}
