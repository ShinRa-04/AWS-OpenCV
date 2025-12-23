"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Alerts from "./alerts"
import Cameras from "./cameras"
import SearchPage from "./search" // <-- Added import
import {
  User,
  Clock,
  Eye,
  AlertTriangle,
  Search,
  Archive,
  Bell,
  Settings,
  Target,
  Camera,
} from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useAuth } from "@/lib/auth-context"
import { cn } from "@/lib/utils"

const menuItems = [
  { name: "Dashboard", icon: Target },
  { name: "Cameras", icon: Camera },
  { name: "Alerts", icon: AlertTriangle },
  { name: "Search", icon: Search }, // <-- Search menu item
  { name: "Archives", icon: Archive },
  { name: "Settings", icon: Settings },
]

export default function DashboardPage() {
  const router = useRouter()
  const { user } = useAuth()
  const [activeMenu, setActiveMenu] = useState("Dashboard")
  const [dateTime, setDateTime] = useState("")

  useEffect(() => {
    if (!user) {
      router.push("/auth")
    }
  }, [user, router])

  useEffect(() => {
    const interval = setInterval(() => {
      setDateTime(new Date().toLocaleString())
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-950 text-white">
        Loading dashboard...
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-800 px-6 py-4 flex justify-between items-center fixed top-0 left-0 w-full z-50 text-white">
        <div className="flex items-center gap-3">
          <Eye className="h-8 w-8 text-blue-700" />
          <span className="text-2xl font-bold">WatcherAI</span>
        </div>
        <div className="flex items-center gap-6">
          <span className="text-gray-400">{dateTime}</span>
          <div className="flex items-center gap-2 cursor-pointer">
            <User className="h-6 w-6 text-gray-400" />
            <span>{user.name || "User"}</span>
          </div>
        </div>
      </header>

      {/* Body with Sidebar + Content */}
      <div className="flex flex-1 pt-16">
        {/* Sidebar */}
        <aside className="w-1/5 bg-gray-900 border-r border-gray-800 py-6 h-[calc(100vh-4rem)] sticky top-16 text-white">
          <nav className="flex flex-col">
            {menuItems.map(({ name, icon: Icon }) => (
              <button
                key={name}
                onClick={() => setActiveMenu(name)}
                className={cn(
                  "flex items-center gap-3 px-6 py-3 text-gray-300 text-lg transition-all relative",
                  activeMenu === name
                    ? "bg-gradient-to-r from-blue-900/50 to-blue-700/30 text-white"
                    : "hover:bg-gradient-to-r hover:from-blue-900/40 hover:to-blue-700/20"
                )}
              >
                {activeMenu === name && (
                  <span className="absolute left-0 top-0 h-full w-1 bg-blue-700 rounded-r"></span>
                )}
                <Icon className="h-5 w-5" />
                {name}
              </button>
            ))}
          </nav>
        </aside>

        {/* Main Dashboard Content */}
        <main className="flex-1 p-6 overflow-y-auto bg-gray-50 text-gray-900">
          {activeMenu === "Dashboard" && (
            <>
              {/* System Overview Cards */}
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                <Card className="bg-white shadow-md border border-blue-100">
                  <CardHeader>
                    <CardTitle className="text-blue-600">Active Cameras</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-3xl font-bold text-gray-900">24</p>
                    <p className="text-green-600 font-bold">96% Operational</p>
                  </CardContent>
                </Card>

                <Card className="bg-white shadow-md border border-blue-100">
                  <CardHeader>
                    <CardTitle className="text-blue-600">Active Alerts</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-3xl font-bold text-gray-900">3</p>
                    <p className="text-red-600 font-bold">Needs attention</p>
                  </CardContent>
                </Card>

                <Card className="bg-white shadow-md border border-blue-100">
                  <CardHeader>
                    <CardTitle className="text-blue-600">System Uptime</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-3xl font-bold text-gray-900">99.8%</p>
                    <p className="text-gray-500 font-bold">This month</p>
                  </CardContent>
                </Card>

                <Card className="bg-white shadow-md border border-blue-100">
                  <CardHeader>
                    <CardTitle className="text-blue-600">Storage Used</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-3xl font-bold text-gray-900">72%</p>
                    <div className="h-2 bg-gray-200 rounded mt-2">
                      <div
                        className="h-2 bg-blue-700 rounded"
                        style={{ width: "72%" }}
                      ></div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Camera Status + Alerts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
                <Card className="bg-white shadow-md border border-blue-100">
                  <CardHeader>
                    <CardTitle className="text-blue-600">Camera Status</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {[{ name: "Main Entrance", status: "active" },
                      { name: "Parking Lot", status: "active" },
                      { name: "Server Room", status: "maintenance" },
                      { name: "Reception", status: "active" },
                      { name: "Back Gate", status: "active" },
                      { name: "Hallway 2F", status: "active" },
                      { name: "Warehouse", status: "active" },
                      { name: "Lobby", status: "active" },
                    ].map((cam) => (
                      <div
                        key={cam.name}
                        className="flex items-center justify-between p-2 bg-gray-100 rounded"
                      >
                        <div className="flex items-center gap-2">
                          <div
                            className={`w-3 h-3 rounded-full ${
                              cam.status === "active"
                                ? "bg-blue-700"
                                : cam.status === "maintenance"
                                ? "bg-yellow-500"
                                : "bg-gray-400"
                            }`}
                          />
                          <span className="text-gray-900">{cam.name}</span>
                        </div>

                        {/* Status Badge */}
                        <span
                          className={cn(
                            "text-sm font-medium px-2 py-1 rounded-md capitalize",
                            cam.status === "active" &&
                              "bg-blue-100 text-blue-600",
                            cam.status === "maintenance" &&
                              "bg-yellow-300/40 text-yellow-600",
                            cam.status !== "active" &&
                              cam.status !== "maintenance" &&
                              "bg-gray-100 text-gray-600"
                          )}
                        >
                          {cam.status}
                        </span>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                <Card className="bg-white shadow-md border border-blue-100">
                  <CardHeader>
                    <CardTitle className="text-blue-600">Recent Alerts</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Video Placeholder */}
                    <div className="w-full h-48 bg-gray-200 rounded flex items-center justify-center text-gray-500">
                      <Camera className="w-10 h-10 mr-2 text-blue-700" />
                      Video Feed Placeholder
                    </div>

                    {[{
                      msg: "Unauthorized access detected - Main Entrance",
                      time: "10:45 AM",
                    }, { msg: "Camera 3 offline - Server Room", time: "09:30 AM" },
                    { msg: "After hours movement - Parking Lot", time: "08:15 AM" }
                    ].map((alert, i) => (
                      <div
                        key={i}
                        className="p-2 bg-blue-50 border border-blue-100 rounded"
                      >
                        <p className="text-gray-900">{alert.msg}</p>
                        <p className="text-sm text-gray-500 flex items-center gap-1">
                          <Clock className="w-3 h-3 text-blue-700" /> {alert.time}
                        </p>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>
            </>
          )}

          {/* Render Alerts, Cameras, or Search based on active menu */}
          {activeMenu === "Alerts" && <Alerts />}
          {activeMenu === "Cameras" && <Cameras />}
          {activeMenu === "Search" && <SearchPage />} {/* <-- Added SearchPage */}
        </main>
      </div>
    </div>
  )
}