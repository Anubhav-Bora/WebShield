/**
 * Custom hook for webhook data fetching with React Query
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { WebhookEvent, WebhookResponse } from '@/types'
import * as webhookService from '@/services/webhooks'
import { useNotificationStore } from '@/store/useNotificationStore'

// Query keys
export const webhookKeys = {
    all: ['webhooks'] as const,
    lists: () => [...webhookKeys.all, 'list'] as const,
    list: (filters?: any) => [...webhookKeys.lists(), { filters }] as const,
    details: () => [...webhookKeys.all, 'detail'] as const,
    detail: (id: string) => [...webhookKeys.details(), id] as const,
    stats: () => [...webhookKeys.all, 'stats'] as const,
}

/**
 * Hook to fetch webhook events
 */
export const useWebhookEvents = (
    providerName?: string,
    limit: number = 50,
    offset: number = 0
) => {
    return useQuery({
        queryKey: webhookKeys.list({ providerName, limit, offset }),
        queryFn: () => webhookService.getWebhookEvents(providerName, limit, offset),
    })
}

/**
 * Hook to fetch a single webhook event
 */
export const useWebhookEvent = (webhookId: string) => {
    return useQuery({
        queryKey: webhookKeys.detail(webhookId),
        queryFn: () => webhookService.getWebhookEvent(webhookId),
        enabled: !!webhookId,
    })
}

/**
 * Hook to fetch webhook statistics
 */
export const useWebhookStats = (providerName?: string) => {
    return useQuery({
        queryKey: webhookKeys.stats(),
        queryFn: () => webhookService.getWebhookStats(providerName),
    })
}

/**
 * Hook to send a test webhook
 */
export const useSendTestWebhook = () => {
    const queryClient = useQueryClient()
    const { success, error } = useNotificationStore()

    return useMutation({
        mutationFn: ({
            providerName,
            payload,
            headers,
        }: {
            providerName: string
            payload: Record<string, any>
            headers?: Record<string, string>
        }) => webhookService.sendTestWebhook(providerName, payload, headers),
        onSuccess: (data: WebhookResponse) => {
            queryClient.invalidateQueries({ queryKey: webhookKeys.lists() })
            success('Success', `Test webhook sent successfully (ID: ${data.webhook_id})`)
        },
        onError: (err: any) => {
            error('Error', err.detail || 'Failed to send test webhook')
        },
    })
}

/**
 * Hook to retry a failed webhook
 */
export const useRetryWebhook = (webhookId: string) => {
    const queryClient = useQueryClient()
    const { success, error } = useNotificationStore()

    return useMutation({
        mutationFn: () => webhookService.retryWebhook(webhookId),
        onSuccess: (data: WebhookResponse) => {
            queryClient.invalidateQueries({ queryKey: webhookKeys.detail(webhookId) })
            queryClient.invalidateQueries({ queryKey: webhookKeys.lists() })
            success('Success', `Webhook retry initiated (ID: ${data.webhook_id})`)
        },
        onError: (err: any) => {
            error('Error', err.detail || 'Failed to retry webhook')
        },
    })
}

export default {
    useWebhookEvents,
    useWebhookEvent,
    useWebhookStats,
    useSendTestWebhook,
    useRetryWebhook,
}
