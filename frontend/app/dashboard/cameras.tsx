
"use client"

import { useState } from "react"
import { Expand, Download } from "lucide-react"

type Camera = {
  id: string
  location: string
  info: string
}

const sampleCameras: Camera[] = [
  { id: "CAM001", location: "Main Entrance", info: "Covers main door" },
  { id: "CAM002", location: "Parking Lot", info: "Covers parking area" },
  { id: "CAM003", location: "Server Room", info: "Sensitive area" },
  { id: "CAM004", location: "Hallway 1F", info: "North corridor" },
  { id: "CAM005", location: "Lobby", info: "Reception area" },
  { id: "CAM006", location: "Back Gate", info: "Rear exit" },
]

export default function Cameras() {
  const [expandedCamera, setExpandedCamera] = useState<Camera | null>(null)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-blue-600">Cameras</h2>
      </div>

      {/* Cameras Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {sampleCameras.map((cam) => (
          <div
            key={cam.id}
            className="bg-white shadow-md border border-blue-100 rounded-lg p-4 flex flex-col"
          >
            {/* Video Placeholder */}
            <div className="relative w-full h-48 bg-gray-200 rounded flex items-center justify-center text-gray-500 mb-4">
              Video Placeholder
              <div className="absolute top-2 right-2 flex gap-2">
                <button
                  onClick={() => setExpandedCamera(cam)}
                  className="p-2 bg-white shadow rounded hover:bg-gray-100"
                >
                  <Expand className="w-4 h-4 text-gray-600" />
                </button>
                <button className="p-2 bg-white shadow rounded hover:bg-gray-100">
                  <Download className="w-4 h-4 text-gray-600" />
                </button>
              </div>
            </div>

            {/* Camera Info */}
            <div className="flex flex-col gap-1">
              <p className="text-gray-900 font-semibold">Camera ID: {cam.id}</p>
              <p className="text-gray-700">Location: {cam.location}</p>
              <p className="text-gray-500 text-sm">{cam.info}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Expanded Video Overlay */}
      {expandedCamera && (
        <div className="fixed inset-0 bg-black/60 flex justify-end z-50">
          <div className="bg-white h-full w-full md:w-2/3 p-6 relative shadow-lg">
            {/* Close Button */}
            <button
              onClick={() => setExpandedCamera(null)}
              className="absolute top-4 right-4 p-2 bg-gray-100 rounded hover:bg-gray-200"
            >
              X
            </button>

            <h2 className="text-xl font-bold text-blue-600 mb-4">
              Camera ID: {expandedCamera.id} – {expandedCamera.location}
            </h2>

            {/* Big Video Placeholder */}
            <div className="w-full h-[70%] bg-gray-300 rounded flex items-center justify-center text-gray-600">
              Expanded Video Placeholder
            </div>

            <p className="mt-4 text-gray-700">{expandedCamera.info}</p>
          </div>
        </div>
      )}
    </div>
  )
}
