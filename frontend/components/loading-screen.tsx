"use client"

import { useEffect, useState } from "react"

interface LoadingScreenProps {
  onComplete?: () => void
}

export function LoadingScreen({ onComplete }: LoadingScreenProps) {
  const [progress, setProgress] = useState(0)
  const [isVideoLoaded, setIsVideoLoaded] = useState(false)

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(timer)
          setTimeout(() => onComplete?.(), 800) // Slightly longer delay for smoother transition
          return 100
        }
        // Slower progress initially if video isn't loaded
        const increment = !isVideoLoaded && prev < 30 ? 
          Math.random() * 1.5 + 0.3 : // Slower for video loading
          Math.random() * 3 + 0.8 // Normal speed after video loads
        return prev + increment
      })
    }, 120) // Slightly slower interval for smoother animation

    return () => clearInterval(timer)
  }, [onComplete, isVideoLoaded])

  return (
    <div className="fixed inset-0 bg-black z-50 flex flex-col items-center justify-center overflow-hidden">
      {/* Animated background spheres */}
      <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-1/4 left-1/4 w-80 h-80 bg-gradient-to-br from-indigo-500/20 to-blue-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>

      {/* Main loading content */}
      <div className="relative z-10 flex flex-col items-center">
        {/* Video container */}
        <div className="relative mb-8">
          <video
            autoPlay
            loop
            muted
            playsInline
            preload="auto"
            className="w-40 h-40 md:w-56 md:h-56 object-cover rounded-full shadow-2xl shadow-blue-500/50"
            onLoadedData={() => setIsVideoLoaded(true)}
            onError={() => setIsVideoLoaded(false)}
            style={{ filter: 'brightness(1.2) contrast(1.1)' }}
          >
            <source src="/logo-video.mp4" type="video/mp4" />
            Your browser does not support the video tag.
          </video>
          
          {/* Fallback if video doesn't load */}
          {!isVideoLoaded && (
            <div className="absolute inset-0 w-40 h-40 md:w-56 md:h-56 bg-gradient-to-br from-blue-500/30 to-purple-500/30 rounded-full flex items-center justify-center backdrop-blur-sm">
              <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center animate-pulse">
                <span className="text-black font-bold text-lg">W</span>
              </div>
            </div>
          )}
          
          {/* Enhanced glow effect around video */}
          <div className="absolute inset-0 bg-gradient-to-br from-blue-400/40 via-blue-500/30 to-purple-500/40 rounded-full blur-sm"></div>
          <div className="absolute inset-2 bg-gradient-to-br from-blue-500/20 to-transparent rounded-full"></div>
          
          {/* Enhanced scanning rings */}
          <div className="absolute inset-0 border-2 border-blue-400/50 rounded-full animate-ping" style={{ animationDuration: "3s" }}></div>
          <div className="absolute inset-4 border border-blue-400/40 rounded-full animate-ping" style={{ animationDuration: "2s", animationDelay: "0.5s" }}></div>
          <div className="absolute inset-8 border border-blue-300/30 rounded-full animate-ping" style={{ animationDuration: "4s", animationDelay: "1s" }}></div>
        </div>

        {/* Brand name */}
        <div className="mb-8 text-center">
          <h1 className="text-white text-3xl md:text-4xl font-bold tracking-wider mb-2">
            WATCHERAI
          </h1>
          {/* Video status indicator */}
          <div className="flex items-center justify-center space-x-2 text-xs text-gray-400">
            <div className={`w-2 h-2 rounded-full ${isVideoLoaded ? 'bg-green-400' : 'bg-yellow-400'} animate-pulse`}></div>
            <span>{isVideoLoaded ? 'Video Loaded' : 'Loading Video...'}</span>
          </div>
        </div>

        {/* Loading progress */}
        <div className="w-80 md:w-96">
          {/* Progress bar */}
          <div className="relative mb-4">
            <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-blue-500 to-blue-400 rounded-full transition-all duration-300 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>
            {/* Progress glow effect */}
            <div 
              className="absolute top-0 h-2 bg-gradient-to-r from-blue-500/50 to-blue-400/50 rounded-full blur-sm transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* Percentage and loading text */}
          <div className="flex justify-between items-center text-gray-300">
            <span className="text-sm font-medium">
              {!isVideoLoaded && progress < 30 ? 'Loading Video Assets...' : 
               progress < 50 ? 'Initializing Security Systems...' : 
               progress < 80 ? 'Connecting to Network...' : 
               progress < 100 ? 'Finalizing Setup...' : 'Ready!'}
            </span>
            <span className="text-xl font-bold text-blue-400 tabular-nums">
              {Math.floor(progress)}%
            </span>
          </div>
        </div>

        {/* Loading dots animation */}
        <div className="mt-6 flex space-x-1">
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
        </div>
      </div>

      {/* Bottom tagline */}
      <div className="absolute bottom-8 text-center">
        <p className="text-gray-400 text-sm">
          Advanced Security Solutions
        </p>
      </div>
    </div>
  )
}