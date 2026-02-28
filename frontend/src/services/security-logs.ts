/**
 * Security Logs API service
 * Handles all security log-related API calls
 */

import { apiClient } from './api'
import { SecurityLog } from '@/types'

/**
 * Get security logs
 * Note: This endpoint might need to be added to backend
 */
export const getSecurityLogs = async (
    filters?: {
        event_type?: string
        provider_name?: string
        date_from?: string
        date_to?: string
    },
    limit: number = 50,
    offset: number = 0
): Promise<SecurityLog[]> => {
    try {
        const params = new URLSearchParams()
        if (filters?.event_type) params.append('event_type', filters.event_type)
        if (filters?.provider_name) params.append('provider_name', filters.provider_name)
        if (filters?.date_from) params.append('date_from', filters.date_from)
        if (filters?.date_to) params.append('date_to', filters.date_to)
        params.append('limit', limit.toString())
        params.append('offset', offset.toString())

        const response = await apiClient.get<SecurityLog[]>(
            `/admin/logs?${params.toString()}`
        )
        return response.data
    } catch (error) {
        console.warn('Security logs endpoint not available')
        return []
    }
}

/**
 * Get security log details
 */
export const getSecurityLog = async (logId: string): Promise<SecurityLog> => {
    const response = await apiClient.get<SecurityLog>(
        `/admin/logs/${logId}`
    )
    return response.data
}

/**
 * Get security statistics
 */
export const getSecurityStats = async (): Promise<{
    total_events: number
    invalid_signatures: number
    rate_limit_events: number
    replay_attempts: number
    timestamp_errors: number
    events_by_type: Record<string, number>
}> => {
    try {
        const response = await apiClient.get(
            '/admin/logs/stats'
        )
        return response.data
    } catch (error) {
        console.warn('Security stats endpoint not available')
        return {
            total_events: 0,
            invalid_signatures: 0,
            rate_limit_events: 0,
            replay_attempts: 0,
            timestamp_errors: 0,
            events_by_type: {},
        }
    }
}

/**
 * Export security logs as CSV
 */
export const exportSecurityLogs = async (
    filters?: {
        event_type?: string
        provider_name?: string
        date_from?: string
        date_to?: string
    }
): Promise<Blob> => {
    const params = new URLSearchParams()
    if (filters?.event_type) params.append('event_type', filters.event_type)
    if (filters?.provider_name) params.append('provider_name', filters.provider_name)
    if (filters?.date_from) params.append('date_from', filters.date_from)
    if (filters?.date_to) params.append('date_to', filters.date_to)

    const response = await apiClient.get(
        `/admin/logs/export?${params.toString()}`,
        {
            responseType: 'blob',
        }
    )
    return response.data
}

export default {
    getSecurityLogs,
    getSecurityLog,
    getSecurityStats,
    exportSecurityLogs,
}
