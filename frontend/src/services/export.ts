/**
 * Export service for downloading reports
 */

import { apiClient } from './api'

/**
 * Export security logs as PDF
 */
export const exportSecurityLogsPDF = async (
    eventType?: string,
    providerName?: string,
    dateFrom?: string,
    dateTo?: string
): Promise<void> => {
    try {
        const params = new URLSearchParams()
        if (eventType) params.append('event_type', eventType)
        if (providerName) params.append('provider_name', providerName)
        if (dateFrom) params.append('date_from', dateFrom)
        if (dateTo) params.append('date_to', dateTo)

        const response = await apiClient.get(
            `/admin/logs/export/pdf?${params.toString()}`,
            { responseType: 'blob' }
        )

        // Create blob and download
        const blob = new Blob([response.data], { type: 'application/pdf' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `security_logs_${new Date().toISOString().split('T')[0]}.pdf`)
        document.body.appendChild(link)
        link.click()
        link.parentNode?.removeChild(link)
        window.URL.revokeObjectURL(url)
    } catch (error) {
        console.error('Failed to export security logs as PDF:', error)
        throw error
    }
}

/**
 * Export security logs as CSV
 */
export const exportSecurityLogsCSV = async (
    eventType?: string,
    providerName?: string,
    dateFrom?: string,
    dateTo?: string
): Promise<void> => {
    try {
        const params = new URLSearchParams()
        if (eventType) params.append('event_type', eventType)
        if (providerName) params.append('provider_name', providerName)
        if (dateFrom) params.append('date_from', dateFrom)
        if (dateTo) params.append('date_to', dateTo)

        const response = await apiClient.get(
            `/admin/logs/export/csv?${params.toString()}`,
            { responseType: 'blob' }
        )

        // Create blob and download
        const blob = new Blob([response.data], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `security_logs_${new Date().toISOString().split('T')[0]}.csv`)
        document.body.appendChild(link)
        link.click()
        link.parentNode?.removeChild(link)
        window.URL.revokeObjectURL(url)
    } catch (error) {
        console.error('Failed to export security logs as CSV:', error)
        throw error
    }
}

/**
 * Export webhook events as PDF
 */
export const exportWebhookEventsPDF = async (providerName?: string): Promise<void> => {
    try {
        const params = new URLSearchParams()
        if (providerName) params.append('provider_name', providerName)

        const response = await apiClient.get(
            `/admin/webhooks/export/pdf?${params.toString()}`,
            { responseType: 'blob' }
        )

        // Create blob and download
        const blob = new Blob([response.data], { type: 'application/pdf' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `webhook_events_${new Date().toISOString().split('T')[0]}.pdf`)
        document.body.appendChild(link)
        link.click()
        link.parentNode?.removeChild(link)
        window.URL.revokeObjectURL(url)
    } catch (error) {
        console.error('Failed to export webhook events as PDF:', error)
        throw error
    }
}

/**
 * Export complete dashboard as PDF
 */
export const exportDashboardPDF = async (): Promise<void> => {
    try {
        const response = await apiClient.get(
            `/admin/dashboard/export/pdf`,
            { responseType: 'blob' }
        )

        // Create blob and download
        const blob = new Blob([response.data], { type: 'application/pdf' })
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `dashboard_report_${new Date().toISOString().split('T')[0]}.pdf`)
        document.body.appendChild(link)
        link.click()
        link.parentNode?.removeChild(link)
        window.URL.revokeObjectURL(url)
    } catch (error) {
        console.error('Failed to export dashboard as PDF:', error)
        throw error
    }
}

export default {
    exportSecurityLogsPDF,
    exportSecurityLogsCSV,
    exportWebhookEventsPDF,
    exportDashboardPDF,
}
