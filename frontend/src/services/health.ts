/**
 * Health Check API service
 * Handles health status and system monitoring
 */

import { apiClient } from './api'
import { API_CONFIG } from '@/config/api.config'
import { HealthStatus } from '@/types'

/**
 * Get health status of the backend
 */
export const getHealthStatus = async (): Promise<HealthStatus> => {
    try {
        const response = await apiClient.get<HealthStatus>(
            API_CONFIG.ENDPOINTS.HEALTH
        )
        return response.data
    } catch (error) {
        console.error('Health check failed:', error)
        return {
            status: 'unhealthy',
            service: 'webhook-gateway',
            version: 'unknown',
            timestamp: new Date().toISOString(),
        }
    }
}

/**
 * Check if backend is reachable
 */
export const isBackendReachable = async (): Promise<boolean> => {
    try {
        const status = await getHealthStatus()
        return status.status !== 'unhealthy'
    } catch (error) {
        return false
    }
}

/**
 * Get system metrics
 * Note: This endpoint might need to be added to backend
 */
export const getSystemMetrics = async (): Promise<{
    uptime: number
    memory_usage: number
    cpu_usage: number
    request_count: number
    error_count: number
}> => {
    try {
        const response = await apiClient.get(
            '/health/metrics'
        )
        return response.data
    } catch (error) {
        console.warn('System metrics endpoint not available')
        return {
            uptime: 0,
            memory_usage: 0,
            cpu_usage: 0,
            request_count: 0,
            error_count: 0,
        }
    }
}

export default {
    getHealthStatus,
    isBackendReachable,
    getSystemMetrics,
}
