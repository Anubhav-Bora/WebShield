/**
 * Webhooks API service
 * Handles all webhook-related API calls
 */

import { apiClient } from './api'
import { API_CONFIG } from '@/config/api.config'
import { WebhookEvent, WebhookResponse } from '@/types'

/**
 * Send a test webhook to a provider
 */
export const sendTestWebhook = async (
    providerName: string,
    payload: Record<string, any>,
    headers?: Record<string, string>
): Promise<WebhookResponse> => {
    const response = await apiClient.post<WebhookResponse>(
        API_CONFIG.ENDPOINTS.WEBHOOK_RECEIVE(providerName),
        payload,
        {
            headers: {
                'X-Signature': headers?.['X-Signature'] || 'test-signature',
                'X-Timestamp': headers?.['X-Timestamp'] || new Date().toISOString(),
                'X-Request-ID': headers?.['X-Request-ID'] || `test-${Date.now()}`,
                ...headers,
            },
        }
    )
    return response.data
}

/**
 * Get webhook events for a provider
 */
export const getWebhookEvents = async (
    providerName?: string,
    limit: number = 50,
    offset: number = 0
): Promise<WebhookEvent[]> => {
    try {
        const params = new URLSearchParams()
        if (providerName) params.append('provider_name', providerName)
        params.append('limit', limit.toString())
        params.append('offset', offset.toString())

        const response = await apiClient.get<WebhookEvent[]>(
            `${API_CONFIG.ENDPOINTS.ADMIN_WEBHOOKS}?${params.toString()}`
        )
        return response.data
    } catch (error) {
        console.warn('Webhooks list endpoint not available')
        return []
    }
}

/**
 * Get webhook event details
 */
export const getWebhookEvent = async (webhookId: string): Promise<WebhookEvent> => {
    const response = await apiClient.get<WebhookEvent>(
        `${API_CONFIG.ENDPOINTS.ADMIN_WEBHOOK_DETAIL(webhookId)}`
    )
    return response.data
}

/**
 * Retry a failed webhook
 */
export const retryWebhook = async (webhookId: string): Promise<WebhookResponse> => {
    const response = await apiClient.post<WebhookResponse>(
        `${API_CONFIG.ENDPOINTS.ADMIN_WEBHOOK_DETAIL(webhookId)}/retry`
    )
    return response.data
}

/**
 * Get webhook statistics
 */
export const getWebhookStats = async (providerName?: string): Promise<{
    total: number
    successful: number
    failed: number
    pending: number
    avg_response_time: number
}> => {
    try {
        const params = new URLSearchParams()
        if (providerName) params.append('provider_name', providerName)

        const response = await apiClient.get(
            `${API_CONFIG.ENDPOINTS.ADMIN_WEBHOOKS}/stats?${params.toString()}`
        )
        return response.data
    } catch (error) {
        console.warn('Webhooks stats endpoint not available')
        return {
            total: 0,
            successful: 0,
            failed: 0,
            pending: 0,
            avg_response_time: 0,
        }
    }
}

export default {
    sendTestWebhook,
    getWebhookEvents,
    getWebhookEvent,
    retryWebhook,
    getWebhookStats,
}
