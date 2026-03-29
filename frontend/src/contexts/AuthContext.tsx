import React, { createContext, useContext, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { authApi } from '@/lib/api'
import type { User, LoginCredentials, AuthResponse } from '@/types'

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => void
  updateUser: (user: User) => void
  hasPermission: (role: string | string[]) => boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('token')
      const savedUser = localStorage.getItem('user')

      if (token && savedUser) {
        try {
          setUser(JSON.parse(savedUser))
          // Verify token is still valid
          const profile = await authApi.getProfile()
          setUser(profile as User)
          localStorage.setItem('user', JSON.stringify(profile))
        } catch (error) {
          localStorage.removeItem('token')
          localStorage.removeItem('user')
        }
      }

      setIsLoading(false)
    }

    initAuth()
  }, [])

  const login = async (credentials: LoginCredentials) => {
    try {
      setIsLoading(true)
      const response = await authApi.login(credentials) as AuthResponse

      localStorage.setItem('token', response.token)
      localStorage.setItem('user', JSON.stringify(response.user))
      setUser(response.user as User)

      toast.success('Login successful!')
      navigate('/')
    } catch (error: unknown) {
      const err = error as { response?: { data?: { error?: string } } }
      toast.error(err.response?.data?.error || 'Login failed')
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
    toast.info('Logged out successfully')
    navigate('/login')
  }

  const updateUser = (updatedUser: User) => {
    setUser(updatedUser)
    localStorage.setItem('user', JSON.stringify(updatedUser))
  }

  const hasPermission = (role: string | string[]) => {
    if (!user) return false

    const roles = Array.isArray(role) ? role : [role]

    if (roles.includes('admin') && user.role === 'admin') return true
    if (roles.includes('manager') && (user.role === 'admin' || user.role === 'manager')) return true
    if (roles.includes('staff') && (user.role === 'admin' || user.role === 'manager' || user.role === 'staff')) return true

    return false
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        updateUser,
        hasPermission,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
