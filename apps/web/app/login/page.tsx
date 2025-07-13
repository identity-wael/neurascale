'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '../../components/AuthProvider'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const { login } = useAuth()
  const router = useRouter()

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (!username) return
    login(username)
    router.push('/profile')
  }

  return (
    <div className="flex items-center justify-center min-h-screen">
      <form onSubmit={handleSubmit} className="space-y-4 p-6 border rounded bg-white text-black">
        <h1 className="text-xl font-bold">Login</h1>
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
          className="border p-2 rounded w-full"
        />
        <button type="submit" className="rounded px-4 py-2 bg-blue-500 text-white w-full">
          Login
        </button>
      </form>
    </div>
  )
}
