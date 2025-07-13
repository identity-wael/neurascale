'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'

interface User {
  username: string
}

interface AuthContextType {
  user: User | null
  login: (username: string) => void
  signup: (username: string) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    const stored = localStorage.getItem('user')
    if (stored) setUser(JSON.parse(stored))
  }, [])

  const saveUser = (u: User | null) => {
    setUser(u)
    if (u) {
      localStorage.setItem('user', JSON.stringify(u))
    } else {
      localStorage.removeItem('user')
    }
  }

  const login = (username: string) => saveUser({ username })
  const signup = (username: string) => saveUser({ username })
  const logout = () => saveUser(null)

  return (
    <AuthContext.Provider value={{ user, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (ctx === undefined) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return ctx
}
