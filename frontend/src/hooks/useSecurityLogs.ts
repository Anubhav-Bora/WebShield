/**
 * Custom hook for security logs data fetching with React Query
 */

import { useQuery, useMutation } from '@tanstack/react-query'
import { SecurityLogFilters } from '@/types'
import * as securityLogService from '@/services/security-logs'
import { useNotificationStore } from '@/store/useNotificationStore'

// Query keys
export const securityLogKeys = {
    all: ['security-logs'] as const,
    lists: () => [...securityLogKeys.all, 'list'] as const,
    list: (filters?: any) => [...securityLogKeys.lists(), { filters }] as const,
    details: () => [...securityLogKeys.all, 'detail'] as const,
    detail: (id: string) => [...securityLogKeys.details(), id] as const,
    stats: () => [...securityLogKeys.all, 'stats'] as const,
}

/**
 * Hook to fetch security logs
 */
export const useSecurityLogs = (
    filters?: SecurityLogFilters,
    limit: number = 50,
    offset: number = 0
) => {
    return useQuery({
        queryKey: securityLogKeys.list({ filters, limit, offset }),
        queryFn: () => securityLogService.getSecurityLogs(filters, limit, offset),
    })
}

/**
 * Hook to fetch a single security log
 */
export const useSecurityLog = (logId: string) => {
    return useQuery({
        queryKey: securityLogKeys.detail(logId),
        queryFn: () => securityLogService.getSecurityLog(logId),
        enabled: !!logId,
    })
}

/**
 * Hook to fetch security statistics
 */
export const useSecurityStats = () => {
    return useQuery({
        queryKey: securityLogKeys.stats(),
        queryFn: () => securityLogService.getSecurityStats(),
    })
}

/**
 * Hook to export security logs
 */
export const useExportSecurityLogs = () => {
    const { success, error } = useNotificationStore()

    return useMutation({
        mutationFn: (filters?: SecurityLogFilters) =>
            securityLogService.exportSecurityLogs(filters),
        onSuccess: (blob) => {
            // Create download link
            const url = window.URL.createObjectURL(blob)
            const link = document.createElement('a')
            link.href = url
            link.download = `security-logs-${new Date().toISOString()}.csv`
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
            window.URL.revokeObjectURL(url)

            success('Success', 'Security logs exported successfully')
        },
        onError: (err: any) => {
            error('Error', err.detail || 'Failed to export security logs')
        },
    })
}

export default {
    useSecurityLogs,
    useSecurityLog,
    useSecurityStats,
    useExportSecurityLogs,
}
