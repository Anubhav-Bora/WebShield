/**
 * Axios instance with interceptors for API communication
 */

import axios, { AxiosInstance, AxiosError } from 'axios'
import { API_CONFIG } from '@/config/api.config'
import { ApiError } from '@/types'

// Create axios instance
export const apiClient: AxiosInstance = axios.create({
    baseURL: API_CONFIG.BASE_URL,
    timeout: API_CONFIG.TIMEOUT,
    headers: API_CONFIG.HEADERS,
})

// Request interceptor
apiClient.interceptors.request.use(
    (config) => {
        // Log request (development only)
        if (process.env.NODE_ENV === 'development') {
            console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`)
            console.log(`[API] BaseURL: ${config.baseURL}`)
            console.log(`[API] Full URL: ${config.baseURL}${config.url}`)
            
            // Log request body for login requests
            if (config.url?.includes('/login') && config.data) {
                console.log(`[API] Request payload:`, config.data)
            }
        }

        // Add auth token if available (client-side only)
        if (typeof window !== 'undefined') {
            const token = localStorage.getItem('auth_token')
            if (token) {
                config.headers.Authorization = `Bearer ${token}`
            }
        }

        return config
    },
    (error) => {
        console.error('[API] Request error:', error)
        return Promise.reject(error)
    }
)

// Response interceptor
apiClient.interceptors.response.use(
    (response) => {
        // Log response (development only)
        if (process.env.NODE_ENV === 'development') {
            console.log(`[API] Response ${response.status} from ${response.config.url}`)
        }
        return response
    },
    (error: AxiosError) => {
        // Handle different error types
        if (error.response) {
            // Server responded with error status
            const status = error.response.status
            const data = error.response.data as any

            // Handle 401 Unauthorized - redirect to login
            if (status === 401) {
                localStorage.removeItem('auth_token')
                // Don't log 401 errors as they're expected when not authenticated
                const apiError: ApiError = {
                    status,
                    detail: data?.detail || 'Unauthorized - please log in',
                    timestamp: new Date().toISOString(),
                }
                return Promise.reject(apiError)
            }

            // Handle 403 Forbidden
            if (status === 403) {
                console.error('[API] Access denied')
            }

            const apiError: ApiError = {
                status,
                detail: data?.detail || data?.message || error.message || 'Server error',
                timestamp: new Date().toISOString(),
            }
            console.error(`[API] Response error: [${status}] ${apiError.detail}`)
            return Promise.reject(apiError)
        } else if (error.request) {
            // Request made but no response (network error or timeout)
            const apiError: ApiError = {
                status: 0,
                detail: error.code === 'ECONNABORTED'
                    ? 'Request timeout - server not responding'
                    : 'Network error - unable to reach server',
                timestamp: new Date().toISOString(),
            }
            console.error('[API] No response:', apiError.detail)
            return Promise.reject(apiError)
        } else {
            // Error in request setup
            const apiError: ApiError = {
                status: 0,
                detail: error.message || 'Unknown error',
                timestamp: new Date().toISOString(),
            }
            console.error('[API] Request setup error:', apiError.detail)
            return Promise.reject(apiError)
        }
    }
)

export default apiClient
