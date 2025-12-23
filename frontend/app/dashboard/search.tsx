"use client"

import { useState } from "react"
import { Search } from "lucide-react"

type SearchResult = {
  video: string
  absolute_start_time: string
  absolute_end_time: string
  document: string
  clip_path: string
}

export default function SearchPage() {
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [query, setQuery] = useState("")
  const [datetime, setDatetime] = useState("")

  const handleSearch = async () => {
    const searchQuery = query || datetime
    if (!searchQuery.trim()) return

    setLoading(true)
    setError("")
    setResults([])

    try {
      const res = await fetch(`http://127.0.0.1:8000/search?query=${encodeURIComponent(searchQuery)}`)
      if (!res.ok) throw new Error("Failed to fetch search results")
      const data = await res.json()
      setResults(data.results || [])
    } catch (err: any) {
      setError(err.message || "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative h-full w-full">
      {/* Main container */}
      <div className="absolute top-4 bottom-4 left-0 right-4 bg-white shadow-2xl rounded-xl p-6 flex flex-col overflow-y-auto z-20">
        
        {/* Search bar */}
        <div className="flex gap-4 mb-6">
          <input
            type="text"
            placeholder="Enter query..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="datetime-local"
            value={datetime}
            onChange={(e) => setDatetime(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            className="px-5 py-2 bg-blue-700 text-white rounded-lg hover:bg-blue-900 flex items-center gap-2"
            onClick={handleSearch}
          >
            <Search className="w-5 h-5" /> Search
          </button>
        </div>

        {/* Results */}
        <div className="flex-1 space-y-4">
          {loading && <p className="text-gray-500">Loading results...</p>}
          {error && <p className="text-red-500">{error}</p>}
          {results.length > 0 &&
            results.map((res, idx) => (
              <div key={idx} className="relative border border-gray-200 rounded-lg p-4 bg-gray-50 shadow">
                <p className="font-semibold text-blue-600 text-lg">{res.video}</p>
                <p><strong>Start:</strong> {res.absolute_start_time}</p>
                <p><strong>End:</strong> {res.absolute_end_time}</p>
                <p className="text-gray-700">{res.document}</p>
                <video
                  src={`http://127.0.0.1:8000${res.clip_path}`}
                  controls
                  className="w-full mt-2 rounded-lg"
                />
              </div>
            ))}
        </div>
      </div>
    </div>
  )
}
