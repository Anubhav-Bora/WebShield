/**
 * Webhook Zustand store
 * Manages webhook-related client state
 */

import { create } from 'zustand'
import { WebhookEvent, WebhookFilters } from '@/types'

interface WebhookStoreState {
    // State
    webhooks: WebhookEvent[]
    selectedWebhook: WebhookEvent | null
    filters: WebhookFilters
    isLoading: boolean
    error: string | null
    pagination: {
        page: number
        limit: number
        total: number
    }

    // Actions
    setWebhooks: (webhooks: WebhookEvent[]) => void
    addWebhook: (webhook: WebhookEvent) => void
    updateWebhook: (webhook: WebhookEvent) => void
    removeWebhook: (webhookId: string) => void
    setSelectedWebhook: (webhook: WebhookEvent | null) => void
    setFilters: (filters: WebhookFilters) => void
    setLoading: (isLoading: boolean) => void
    setError: (error: string | null) => void
    clearError: () => void
    setPagination: (pagination: { page?: number; limit?: number; total?: number }) => void
    reset: () => void
}

const initialState = {
    webhooks: [],
    selectedWebhook: null,
    filters: {},
    isLoading: false,
    error: null,
    pagination: {
        page: 1,
        limit: 50,
        total: 0,
    },
}

export const useWebhookStore = create<WebhookStoreState>((set: any) => ({
    ...initialState,

    setWebhooks: (webhooks: WebhookEvent[]) => set({ webhooks }),

    addWebhook: (webhook: WebhookEvent) =>
        set((state: WebhookStoreState) => ({
            webhooks: [webhook, ...state.webhooks],
        })),

    updateWebhook: (webhook: WebhookEvent) =>
        set((state: WebhookStoreState) => ({
            webhooks: state.webhooks.map((w: WebhookEvent) =>
                w.id === webhook.id ? webhook : w
            ),
            selectedWebhook:
                state.selectedWebhook?.id === webhook.id ? webhook : state.selectedWebhook,
        })),

    removeWebhook: (webhookId: string) =>
        set((state: WebhookStoreState) => ({
            webhooks: state.webhooks.filter((w: WebhookEvent) => w.id !== webhookId),
            selectedWebhook:
                state.selectedWebhook?.id === webhookId ? null : state.selectedWebhook,
        })),

    setSelectedWebhook: (webhook: WebhookEvent | null) => set({ selectedWebhook: webhook }),

    setFilters: (filters: WebhookFilters) => set({ filters }),

    setLoading: (isLoading: boolean) => set({ isLoading }),

    setError: (error: string | null) => set({ error }),

    clearError: () => set({ error: null }),

    setPagination: (pagination: { page?: number; limit?: number; total?: number }) =>
        set((state: WebhookStoreState) => ({
            pagination: {
                ...state.pagination,
                ...pagination,
            },
        })),

    reset: () => set(initialState),
}))

export default useWebhookStore
