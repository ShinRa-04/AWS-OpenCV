"use client"

import { useState, useEffect } from "react"
import { Search } from "lucide-react"

type SearchResult = {
  video_name: string
  segment_id: string
  time_range: string
  threat_level: string
  full_text: string
  parsed_details: {
    location?: string
    activity?: string
    description?: string
  }
}

export default function SearchPage() {
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [query, setQuery] = useState("")
  const [datetime, setDatetime] = useState("")
  const [isIndexed, setIsIndexed] = useState(false)

  // Trigger auto-indexing check on mount
  useEffect(() => {
    const checkIndex = async () => {
      try {
        console.log("Checking search index...")
        // The backend endpoint /videos is not implemented in simple search, 
        // but /index_stats is. Let's use that or just search.
        await fetch("http://127.0.0.1:8001/")
        setIsIndexed(true)
        console.log("Search backend ready")
      } catch (err) {
        console.error("Failed to check search index:", err)
        setError("Search service unreachable. Is backend/search.py running?")
      }
    }
    checkIndex()
  }, [])

  const handleSearch = async () => {
    const searchQuery = query || datetime
    if (!searchQuery.trim()) return

    setLoading(true)
    setError("")
    setResults([])

    try {
      // Use port 8001 for search service
      const res = await fetch(`http://127.0.0.1:8001/search?query=${encodeURIComponent(searchQuery)}`)
      if (!res.ok) throw new Error("Failed to fetch search results")
      const data = await res.json()
      setResults(data.results || [])
    } catch (err: any) {
      setError(err.message || "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  // Helper to parse time range string "0.0s - 10.0s" to start/end numbers
  const parseTimeRange = (rangeStr: string) => {
    try {
      const parts = rangeStr.split('-')
      if (parts.length === 2) {
        const start = parseFloat(parts[0].replace('s', '').trim())
        const end = parseFloat(parts[1].replace('s', '').trim())
        return { start, end }
      }
    } catch (e) {
      console.error("Error parsing time range", e)
    }
    return { start: 0, end: 0 }
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
          {results.length > 0 ? (
            results.map((res, idx) => {
              const { start, end } = parseTimeRange(res.time_range)
              return (
                <div key={idx} className="relative border border-gray-200 rounded-lg p-4 bg-gray-50 shadow">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-semibold text-blue-600 text-lg">{res.video_name}</p>
                      <p className="text-sm text-gray-500">Threat Level: {res.threat_level}</p>
                    </div>
                    <span className="text-xs bg-gray-200 px-2 py-1 rounded">
                      Segment {res.segment_id}
                    </span>
                  </div>

                  <p className="mt-2 text-sm text-gray-700">
                    <strong>Time:</strong> {res.time_range}
                  </p>

                  {res.parsed_details.location && (
                    <p className="text-sm text-gray-600 mt-1"><strong>Location:</strong> {res.parsed_details.location}</p>
                  )}
                  {res.parsed_details.activity && (
                    <p className="text-sm text-gray-600 mt-1"><strong>Activity:</strong> {res.parsed_details.activity}</p>
                  )}

                  <div className="mt-2 p-3 bg-white rounded border border-gray-100 text-sm">
                    <p className="font-medium text-gray-700">Full Text:</p>
                    <pre className="text-xs text-gray-600 whitespace-pre-wrap font-sans mt-1">{res.full_text}</pre>
                  </div>

                  {/* 
                    Video clip display
                  */}
                  <video
                    src={`http://localhost:8000/uploaded_videos/${res.video_name}.mp4#t=${start},${end}`}
                    controls
                    className="w-full mt-3 rounded-lg border border-gray-300 bg-black"
                  />
                </div>
              )
            })
          ) : (
            !loading && results.length === 0 && query && <p className="text-gray-500">No matches found.</p>
          )}
        </div>
      </div>
    </div>
  )
}

