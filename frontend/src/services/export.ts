/**
 * Export service for downloading reports
 */

import axios from 'axios'
import { API_CONFIG } from '@/config/api.config'

/**
 * Helper function to download file from blob
 */
const downloadFile = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.parentNode?.removeChild(link)
    window.URL.revokeObjectURL(url)
}

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

        const token = localStorage.getItem('auth_token')
        const response = await axios.get(
            `${API_CONFIG.BASE_URL}/admin/logs/export/pdf?${params.toString()}`,
            {
                responseType: 'blob',
                headers: {
                    'Authorization': token ? `Bearer ${token}` : '',
                    ...API_CONFIG.HEADERS
                }
            }
        )

        const blob = new Blob([response.data], { type: 'application/pdf' })
        downloadFile(blob, `security_logs_${new Date().toISOString().split('T')[0]}.pdf`)
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

        const token = localStorage.getItem('auth_token')
        const response = await axios.get(
            `${API_CONFIG.BASE_URL}/admin/logs/export/csv?${params.toString()}`,
            {
                responseType: 'blob',
                headers: {
                    'Authorization': token ? `Bearer ${token}` : '',
                    ...API_CONFIG.HEADERS
                }
            }
        )

        const blob = new Blob([response.data], { type: 'text/csv' })
        downloadFile(blob, `security_logs_${new Date().toISOString().split('T')[0]}.csv`)
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

        const token = localStorage.getItem('auth_token')
        const response = await axios.get(
            `${API_CONFIG.BASE_URL}/admin/webhooks/export/pdf?${params.toString()}`,
            {
                responseType: 'blob',
                headers: {
                    'Authorization': token ? `Bearer ${token}` : '',
                    ...API_CONFIG.HEADERS
                }
            }
        )

        const blob = new Blob([response.data], { type: 'application/pdf' })
        downloadFile(blob, `webhook_events_${new Date().toISOString().split('T')[0]}.pdf`)
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
        const token = localStorage.getItem('auth_token')
        const response = await axios.get(
            `${API_CONFIG.BASE_URL}/admin/dashboard/export/pdf`,
            {
                responseType: 'blob',
                headers: {
                    'Authorization': token ? `Bearer ${token}` : '',
                    ...API_CONFIG.HEADERS
                }
            }
        )

        const blob = new Blob([response.data], { type: 'application/pdf' })
        downloadFile(blob, `dashboard_report_${new Date().toISOString().split('T')[0]}.pdf`)
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
