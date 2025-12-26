"use client"

import { useState } from "react"
import { Search, Expand, Download, X, Upload } from "lucide-react"

type Alert = {
  id: number
  emoji: string
  title: string
  location: string
  camera: string
  time: string
}

const sampleAlerts: Alert[] = [
  {
    id: 1,
    emoji: "🚨",
    title: "Unauthorized Access",
    location: "Main Entrance",
    camera: "CameraID: 001",
    time: "10:45 AM",
  },
  {
    id: 2,
    emoji: "⚠️",
    title: "Camera Offline",
    location: "Server Room",
    camera: "CameraID: 322",
    time: "09:30 AM",
  },
  {
    id: 3,
    emoji: "🔔",
    title: "After Hours Movement",
    location: "Parking Lot",
    camera: "CameraID: 127",
    time: "08:15 AM",
  },
]

export default function Alerts() {
  const [expandedAlert, setExpandedAlert] = useState<Alert | null>(null)

  // State for uploaded file + analysis result
  const [uploadedVideo, setUploadedVideo] = useState<File | null>(null)
  const [processing, setProcessing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<string | null>(null)

  const handleVideoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploadedVideo(file)
    setProcessing(true)
    setAnalysisResult(null)

    try {
      const formData = new FormData()
      formData.append("file", file) // Fixed field name to match backend

      console.log("Submitting video to backend...")
      const uploadRes = await fetch("http://localhost:8000/process_video", {
        method: "POST",
        body: formData,
      })

      if (!uploadRes.ok) throw new Error(`Upload failed: ${uploadRes.statusText}`)
      const uploadData = await uploadRes.json()
      const videoName = uploadData.filename.split('.')[0]
      await new Promise(resolve => setTimeout(resolve, 5000));
      // Polling for analysis
      let attempts = 0
      const maxAttempts = 30 // 30 * 2s = 60s

      const poll = async () => {
        if (attempts >= maxAttempts) {
          setAnalysisResult("Parsing timed out. Please check again later.")
          setProcessing(false)
          return
        }

        try {
          const res = await fetch(`http://localhost:8000/analysis/${videoName}`)
          const data = await res.json()

          if (data.status === "complete") {
            setAnalysisResult(data.summary)
            setProcessing(false)
          } else if (data.status === "processing") {
            attempts++
            setTimeout(poll, 2000)
          } else {
            setAnalysisResult("Error or file not found in anomaly detection.")
            setProcessing(false)
          }
        } catch (err) {
          console.error("Polling error:", err)
          setTimeout(poll, 2000)
        }
      }

      poll()

    } catch (err) {
      console.error(err)
      setAnalysisResult("Error processing video")
      setProcessing(false)
    }
  }


  return (
    <div className="space-y-6">
      {/* Header */}
      <h2 className="text-2xl font-bold text-blue-600">Alerts</h2>

      {/* Upload Section */}
      <div className="bg-white shadow-md border border-blue-200 rounded-lg p-8 flex flex-col items-center justify-center min-h-[250px]">
        {!uploadedVideo && !analysisResult && !processing && (
          <>
            <Upload className="w-10 h-10 text-gray-500 mb-4" />
            <label className="cursor-pointer px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition">
              Upload Video
              <input
                type="file"
                accept="video/*"
                className="hidden"
                onChange={handleVideoUpload}
              />
            </label>
          </>
        )}

        {processing && (
          <p className="text-gray-600 font-medium">Processing video, please wait...</p>
        )}

        {analysisResult && (
          <div className="w-full">
            <h3 className="font-bold text-gray-900 mb-2">Analysis Result</h3>
            <p className="text-gray-700 whitespace-pre-line">{analysisResult}</p>
          </div>
        )}
      </div>



      {/* Expanded Video Overlay */}
      {expandedAlert && (
        <div className="fixed inset-0 bg-black/60 flex justify-end z-50">
          <div className="bg-white h-full w-full md:w-2/3 p-6 relative shadow-lg">
            {/* Close Button */}
            <button
              onClick={() => setExpandedAlert(null)}
              className="absolute top-4 right-4 p-2 bg-gray-100 rounded hover:bg-gray-200"
            >
              <X className="w-5 h-5 text-gray-600" />
            </button>

            <h2 className="text-xl font-bold text-blue-600 mb-4">
              {expandedAlert.emoji} {expandedAlert.title} – {expandedAlert.location}
            </h2>

            {/* Big Video Placeholder */}
            <div className="w-full h-[70%] bg-gray-300 rounded flex items-center justify-center text-gray-600">
              Expanded Video Placeholder
            </div>

            <p className="mt-4 text-gray-700">
              Reviewing footage from <strong>{expandedAlert.camera}</strong> at{" "}
              {expandedAlert.time}.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
