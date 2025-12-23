"use client" 

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Swiper, SwiperSlide } from "swiper/react"
import { Navigation, Pagination, Autoplay } from "swiper/modules"
import { LoadingScreen } from "@/components/loading-screen"
import "swiper/css"
import "swiper/css/navigation"
import "swiper/css/pagination"

export default function LandingPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)

  const handleLoadingComplete = () => {
    setIsLoading(false)
  }

  const handleGetStarted = () => {
    router.push("/dashboard")
  }

  const handleVision = () => {
    document.getElementById('domain')?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleServices = () => {
    document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleContact = () => {
    document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' })
  }

  // Show loading screen on initial visit
  if (isLoading) {
    return <LoadingScreen onComplete={handleLoadingComplete} />
  }

  return (
    <div className="bg-black relative overflow-x-hidden min-h-screen">
      {/* Animated background spheres */}
      <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-1/4 left-1/4 w-80 h-80 bg-gradient-to-br from-indigo-500/10 to-blue-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>

      {/* Landing Section */}
      <section id="home" className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden px-4">
        {/* Top Navigation */}
        <nav className="fixed top-8 left-8 z-50">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
              <span className="text-black font-bold text-sm">W</span>
            </div>
            <span className="text-white text-xl font-bold tracking-wider">WATCHERAI</span>
          </div>
        </nav>

        {/* Top Right Button */}
        <div className="fixed top-8 right-8 z-50">
          <Button
            onClick={() => router.push("/auth")}
            className="bg-blue-400/80 hover:bg-blue-800/80 text-white rounded-full px-6 py-2 text-sm font-medium transition-all duration-300 shadow-lg shadow-blue-500/30"
          >
            Login / Signup
          </Button>
        </div>

        {/* Main Content */}
        <div className="relative z-10 text-center max-w-6xl mx-auto">
          {/* Hero Title */}
          <h1 className="text-6xl md:text-8xl font-bold mb-8 tracking-tight leading-none">
            <span className="bg-gradient-to-r from-gray-300 via-blue-200 to-blue-400 bg-clip-text text-transparent">
              Unlocking Potential,
              <br />
              Delivering Excellence.
            </span>
          </h1>

          {/* Action Buttons */}
          <div className="flex flex-wrap justify-center gap-6 mb-16">
            <Button
              onClick={handleServices}
              className="bg-transparent border border-gray-600 hover:border-gray-400 text-white rounded-full px-8 py-3 text-sm font-medium transition-all duration-300 hover:bg-gray-800/50"
            >
              SERVICES →
            </Button>
            <Button
              onClick={handleVision}
              className="bg-transparent border border-gray-600 hover:border-gray-400 text-white rounded-full px-8 py-3 text-sm font-medium transition-all duration-300 hover:bg-gray-800/50"
            >
              OUR VISION →
            </Button>
            <Button
              onClick={handleContact}
              className="bg-transparent border border-gray-600 hover:border-gray-400 text-white rounded-full px-8 py-3 text-sm font-medium transition-all duration-300 hover:bg-gray-800/50"
            >
              GET IN TOUCH →
            </Button>
          </div>

          {/* Description */}
          <div className="flex flex-col md:flex-row items-start justify-between max-w-4xl mx-auto">
            <div className="md:w-1/2 text-left">
              <p className="text-gray-300 text-lg leading-relaxed">
                At WatcherAI, we believe in harnessing the power of technology to empower security institutions and businesses alike.
              </p>
            </div>
            <div className="md:w-1/2 flex justify-end mt-8 md:mt-0">
              <div className="text-center">
                <div className="w-12 h-12 mx-auto mb-2 border border-gray-600 rounded-full flex items-center justify-center">
                  <span className="text-gray-400">↓</span>
                </div>
                <span className="text-gray-400 text-sm">SCROLL DOWN</span>
              </div>
            </div>
          </div>

          {/* Central Camera Image */}
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 -z-10">
            <div className="relative">
              {/* Main camera image */}
              <img
                src="/cctv-camera.jpg"
                alt="Security Camera"
                className="w-96 h-96 md:w-[500px] md:h-[500px] object-cover rounded-full opacity-20 blur-sm"
              />
              {/* Glow effect */}
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 to-transparent rounded-full"></div>
              {/* Scanning rings */}
              <div className="absolute inset-0 border border-blue-400/30 rounded-full animate-ping" style={{ animationDuration: "3s" }}></div>
              <div className="absolute inset-4 border border-blue-400/20 rounded-full animate-ping" style={{ animationDuration: "2s", animationDelay: "0.5s" }}></div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section
        id="features"
        className="min-h-screen w-full flex flex-col justify-center items-center bg-transparent md:px-20 snap-start relative z-0"
      >
        <h2 className="text-5xl md:text-6xl font-bold mb-12 text-center bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-blue-500 to-blue-600">
          Features
        </h2>

        <div className="w-full max-w-6xl">
          {/* Top Headings Pagination Container */}
         <div
          id="feature-pagination"
          className="grid grid-cols-4 w-full mb-2 border-b border-gray-600"
        ></div>

        <Swiper
          modules={[Navigation, Pagination, Autoplay]}
          navigation
          pagination={{
            clickable: true,
            el: "#feature-pagination",
            renderBullet: (index, className) => {
              const titles = [
                "Detect events in 24 surveillance footage",
                "Smart Alerts in Real-time",
                "AI-based search",
              ]
              return `<span class="${className} block text-center font-bold px-2 pb-10 cursor-pointer text-gray-400 text-4xl md:text-5xl transition-colors duration-300 hover:text-blue-400 swiper-pagination-bullet-active:text-blue-400">
                        ${titles[index]}
                      </span>`
            },
          }}
          autoplay={{ delay: 5000, disableOnInteraction: false }}
          loop
          className="rounded-3xl">

            {/* Slide 1 */}
            <SwiperSlide>
            <div className="flex flex-col md:flex-row items-center justify-between gap-10 bg-blue-400/5 rounded-3xl p-8 backdrop-blur-md">
              <div className="flex-1 flex flex-col items-start space-y-6">
                
                {/* Heading with emoji inline at the end */}
                <h3 className="flex items-center gap-3 text-3xl md:text-4xl pl-10 font-semibold text-blue-200 -mt-2">
                  Find Events in 3 Clicks
                  <span className="w-12 h-12 flex items-center justify-center rounded-full bg-blue-500/20">
                    🔍
                  </span>
                </h3>

                {/* Paragraph */}
                <p className="text-gray-300 text-lg md:text-xl pl-10 leading-relaxed -mt-1">
                  Quickly search past recordings using AI-powered 
                  <br />
                  filters and object recognition.
                </p>
              </div>

              {/* Right side video placeholder */}
              <div className="flex-1 flex justify-center -ml-10">
                <div className="w-full h-64 md:h-96 bg-blue-500/10 border border-blue-400/20 rounded-2xl flex items-center justify-center text-blue-300 -ml-10">
                  <span className="text-lg">[ Video Placeholder ]</span>
                </div>
              </div>
            </div>
          </SwiperSlide>



            {/* Slide 2 */}
            <SwiperSlide>
            <div className="flex flex-col md:flex-row items-center justify-between gap-10 bg-blue-400/5 rounded-3xl p-8 backdrop-blur-md">
              <div className="flex-1 flex flex-col items-start space-y-6">
                
                {/* Heading with emoji inline at the end */}
                <h3 className="flex items-center gap-3 text-2xl md:text-3xl pl-10 font-semibold text-blue-200 -mt-2">
                  Smart Alerts in Real-time
                  <span className="w-10 h-10 flex items-center justify-center rounded-full bg-blue-500/20">
                    🚨
                  </span>
                </h3>

                {/* Paragraph */}
                <p className="text-gray-300 text-lg md:text-xl pl-10 leading-relaxed -mt-1">
                  Get real-time alerts for anomalies and suspicious activity across all connected cameras.
                </p>
              </div>

              {/* Right side video placeholder */}
              <div className="flex-1 flex justify-center -ml-10">
                <div className="w-full h-64 md:h-96 bg-blue-500/10 border border-blue-400/20 rounded-2xl flex items-center justify-center text-blue-300 -ml-10">
                  <span className="text-lg">[ Video Placeholder ]</span>
                </div>
              </div>
            </div>
          </SwiperSlide>


            {/* Slide 3 */}
            <SwiperSlide>
            <div className="flex flex-col md:flex-row items-center justify-between gap-10 bg-blue-400/5 rounded-3xl p-8 backdrop-blur-md">
              <div className="flex-1 flex flex-col items-start space-y-6 max-w-md">
                
                {/* Heading with emoji inline at the end */}
                <h3 className="flex items-center gap-3 text-2xl md:text-3xl pl-10 font-semibold text-blue-200 -mt-2">
                  Share Clips Instantly
                  <span className="w-12 h-12 flex items-center justify-center rounded-full bg-blue-500/20">
                    📹
                  </span>
                </h3>

                {/* Paragraph */}
                <p className="text-gray-300 text-lg md:text-xl pl-10 leading-relaxed -mt-1">
                  Quick video sharing features take away the frustration of collaborating with witness accounts and sending video to those that need it.
                </p>
              </div>

              {/* Right side video placeholder */}
              <div className="flex-1 flex justify-center -ml-10">
                <div className="w-12/13 h-64 md:h-96 bg-blue-500/10 border border-blue-400/20 rounded-2xl flex items-center justify-center text-blue-300 -ml-5">
                  <span className="text-lg">[ Video Placeholder ]</span>
                </div>
              </div>
            </div>
          </SwiperSlide>


          </Swiper>
        </div>
      </section>

      {/* Domain Section */}
        <section
          id="domain"
          className="w-full flex flex-col justify-start items-center bg-transparent md:px-20 snap-start relative z-0 overflow-hidden pt-32 pb-20"
        >
          <h2 className="text-5xl md:text-6xl font-bold mb-16 text-center bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-blue-500 to-blue-600">
            Domains
          </h2>

          {/* Domain carousel */}
          <div className="w-full overflow-hidden relative mb-16">
            <div className="flex animate-slideLeft gap-6">
              {["AI Security", "Smart Cities", "IoT Monitoring", "Surveillance Analytics"].map((title, index) => (
                <div
                  key={index}
                  className="flex-none w-72 h-64 md:h-80 bg-blue-500/10 backdrop-blur-md rounded-3xl flex flex-col items-center justify-center p-4 relative"
                >
                  <h3 className="text-xl md:text-2xl font-semibold text-blue-300 mb-2 z-10">{title}</h3>
                  <img
                    src={`/domain-${index + 1}.jpg`}
                    className="absolute inset-0 w-full h-full object-cover rounded-3xl opacity-30 -z-10"
                  />
                </div>
              ))}
              {["AI Security", "Smart Cities", "IoT Monitoring", "Surveillance Analytics"].map((title, index) => (
                <div
                  key={`dup-${index}`}
                  className="flex-none w-72 h-64 md:h-80 bg-blue-400/10 backdrop-blur-md rounded-3xl flex flex-col items-center justify-center p-4 relative"
                >
                  <h3 className="text-xl md:text-2xl font-semibold text-blue-300 mb-2 z-10">{title}</h3>
                  <img
                    src={`/domain-${index + 1}.jpg`}
                    className="absolute inset-0 w-full h-full object-cover rounded-3xl opacity-30 -z-10"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Full-width Feature Card */}
          <div className="w-full bg-blue-500/10 backdrop-blur-md rounded-3xl p-8 md:p-16 flex flex-col md:flex-row items-center gap-10">
            
            {/* Left Side Image */}
            <div className="flex-1 flex justify-center">
              <img
                src="/smart-city.png"
                alt="Feature"
                className="w-full md:w-auto h-64 md:h-96 object-cover rounded-2xl shadow-lg"
              />
            </div>

            {/* Right Side Text + Bullets */}
            <div className="flex-1 flex flex-col justify-between items-center h-full max-w-xl mx-auto">
            <ul className="flex flex-col gap-6">
              {/* Bullet 1 */}
              <li className="flex items-start gap-3">
                {/* Icon at start */}
                <img src="/icons/computer.svg" className="w-6 h-6 mt-1" alt="Computer Icon" />
                <span className="text-lg md:text-2xl text-gray-300 pb-5">
                  High Performance Computing
                </span>
              </li>

              {/* Bullet 2 */}
              <li className="flex items-start gap-3">
                <img src="/icons/rocket.svg" className="w-6 h-6 mt-1" alt="Rocket Icon" />
                <span className="text-lg md:text-2xl text-gray-300 pb-5">
                  Fast Deployment
                </span>
              </li>

              {/* Bullet 3 */}
              <li className="flex items-start gap-3">
                <img src="/icons/security.svg" className="w-6 h-6 mt-1" alt="Security Icon" />
                <span className="text-lg md:text-2xl text-gray-300 pb-5">
                  Secure & Reliable
                </span>
              </li>

              {/* Bullet 4 */}
              <li className="flex items-start gap-3">
                <img src="/icons/cloud.svg" className="w-6 h-6 mt-1" alt="Cloud Icon" />
                <span className="text-lg md:text-2xl text-gray-300 pb-5">
                  Cloud Integration
                </span>
              </li>

              {/* Bullet 5 */}
              <li className="flex items-start gap-3">
                <img src="/icons/analytics.svg" className="w-6 h-6 mt-1" alt="Analytics Icon" />
                <span className="text-lg md:text-2xl text-gray-300 pb-5">
                  Advanced Analytics
                </span>
              </li>
            </ul>

          </div>




          </div>
        </section>


      {/* Footer */}
      <footer className="text-center py-6">
        <p className="text-xs text-gray-500">© 2024 SecureVision. Advanced Security Solutions.</p>
      </footer>
    </div>
  )
}