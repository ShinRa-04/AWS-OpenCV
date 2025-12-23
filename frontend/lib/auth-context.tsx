"use client"

import { createContext, useContext, useEffect, useState, type ReactNode } from "react"

interface User {
  id: string
  name: string
  employeeId: string
  email: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  signIn: (employeeId: string, password: string) => Promise<void>
  signUp: (name: string, employeeId: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const DEMO_USERS = [
  {
    id: "1",
    name: "Riddhi Sharma",
    employeeId: "SEC001",
    email: "john.smith@securevision.com",
    password: "admin123",
  },
  {
    id: "2",
    name: "Hemang Jain",
    employeeId: "SEC002",
    email: "sarah.johnson@securevision.com",
    password: "security456",
  },
  {
    id: "3",
    name: "Siddhart Bansal",
    employeeId: "SEC003",
    email: "mike.wilson@securevision.com",
    password: "guard789",
  },
]

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const storedUser = localStorage.getItem("securevision_user")
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser))
      } catch (error) {
        localStorage.removeItem("securevision_user")
      }
    }
    setLoading(false)
  }, [])

  const signIn = async (employeeId: string, password: string) => {
    return new Promise<void>((resolve, reject) => {
      setTimeout(() => {
        const foundUser = DEMO_USERS.find((u) => u.employeeId === employeeId && u.password === password)

        if (foundUser) {
          const { password: _, ...userWithoutPassword } = foundUser
          setUser(userWithoutPassword)
          localStorage.setItem("securevision_user", JSON.stringify(userWithoutPassword))
          resolve()
        } else {
          reject(new Error("Invalid employee ID or password"))
        }
      }, 1000) // Simulate network delay
    })
  }

  const signUp = async (name: string, employeeId: string, password: string) => {
    return new Promise<void>((resolve, reject) => {
      setTimeout(() => {
        const existingUser = DEMO_USERS.find((u) => u.employeeId === employeeId)
        if (existingUser) {
          reject(new Error("Employee ID already exists"))
          return
        }

        const newUser = {
          id: Date.now().toString(),
          name,
          employeeId,
          email: `${employeeId.toLowerCase()}@securevision.com`,
          password,
        }

        DEMO_USERS.push(newUser)
        const { password: _, ...userWithoutPassword } = newUser
        setUser(userWithoutPassword)
        localStorage.setItem("securevision_user", JSON.stringify(userWithoutPassword))
        resolve()
      }, 1000)
    })
  }

  const logout = async () => {
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        setUser(null)
        localStorage.removeItem("securevision_user")
        resolve()
      }, 500)
    })
  }

  const value = {
    user,
    loading,
    signIn,
    signUp,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
