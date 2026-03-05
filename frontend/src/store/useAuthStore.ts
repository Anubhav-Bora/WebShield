import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
    id: string
    email: string
    username: string
    full_name: string
    is_active: boolean
}

interface AuthStore {
    user: User | null
    token: string | null
    isAuthenticated: boolean
    setAuth: (user: User, token: string) => void
    clearAuth: () => void
}

export const useAuthStore = create<AuthStore>()(
    persist(
        (set) => ({
            user: null,
            token: null,
            isAuthenticated: false,

            setAuth: (user, token) => {
                localStorage.setItem('auth_token', token)
                // Set cookie for middleware
                document.cookie = `auth_token=${token}; path=/; max-age=${60 * 60 * 24 * 7}` // 7 days
                set({ user, token, isAuthenticated: true })
            },

            clearAuth: () => {
                localStorage.removeItem('auth_token')
                // Clear cookie
                document.cookie = 'auth_token=; path=/; max-age=0'
                set({ user: null, token: null, isAuthenticated: false })
            }
        }),
        {
            name: 'auth-storage'
        }
    )
)
