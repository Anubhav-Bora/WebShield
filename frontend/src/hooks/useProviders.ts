/**
 * Custom hook for provider data fetching with React Query
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Provider, ProviderCreate, ProviderUpdate } from '@/types'
import * as providerService from '@/services/providers'
import { useNotificationStore } from '@/store/useNotificationStore'

// Query keys
export const providerKeys = {
    all: ['providers'] as const,
    lists: () => [...providerKeys.all, 'list'] as const,
    list: (filters?: any) => [...providerKeys.lists(), { filters }] as const,
    details: () => [...providerKeys.all, 'detail'] as const,
    detail: (name: string) => [...providerKeys.details(), name] as const,
    stats: () => [...providerKeys.all, 'stats'] as const,
    stat: (name: string) => [...providerKeys.stats(), name] as const,
}

/**
 * Hook to fetch all providers
 */
export const useProviders = () => {
    return useQuery({
        queryKey: providerKeys.lists(),
        queryFn: () => providerService.getProviders(),
    })
}

/**
 * Hook to fetch a single provider
 */
export const useProvider = (name: string) => {
    return useQuery({
        queryKey: providerKeys.detail(name),
        queryFn: () => providerService.getProvider(name),
        enabled: !!name,
    })
}

/**
 * Hook to fetch provider statistics
 */
export const useProviderStats = (name: string) => {
    return useQuery({
        queryKey: providerKeys.stat(name),
        queryFn: () => providerService.getProviderStats(name),
        enabled: !!name,
    })
}

/**
 * Hook to create a provider
 */
export const useCreateProvider = () => {
    const queryClient = useQueryClient()
    const { success, error } = useNotificationStore()

    return useMutation({
        mutationFn: (data: ProviderCreate) => providerService.createProvider(data),
        onSuccess: (data: Provider) => {
            queryClient.invalidateQueries({ queryKey: providerKeys.lists() })
            success('Success', `Provider "${data.name}" created successfully`)
        },
        onError: (err: any) => {
            error('Error', err.detail || 'Failed to create provider')
        },
    })
}

/**
 * Hook to update a provider
 */
export const useUpdateProvider = (name: string) => {
    const queryClient = useQueryClient()
    const { success, error } = useNotificationStore()

    return useMutation({
        mutationFn: (data: ProviderUpdate) =>
            providerService.updateProvider(name, data),
        onSuccess: (data: Provider) => {
            queryClient.invalidateQueries({ queryKey: providerKeys.detail(name) })
            queryClient.invalidateQueries({ queryKey: providerKeys.lists() })
            success('Success', `Provider "${data.name}" updated successfully`)
        },
        onError: (err: any) => {
            error('Error', err.detail || 'Failed to update provider')
        },
    })
}

/**
 * Hook to delete a provider
 */
export const useDeleteProvider = (name: string) => {
    const queryClient = useQueryClient()
    const { success, error } = useNotificationStore()

    return useMutation({
        mutationFn: () => providerService.deleteProvider(name),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: providerKeys.lists() })
            queryClient.removeQueries({ queryKey: providerKeys.detail(name) })
            success('Success', `Provider "${name}" deleted successfully`)
        },
        onError: (err: any) => {
            error('Error', err.detail || 'Failed to delete provider')
        },
    })
}

export default {
    useProviders,
    useProvider,
    useProviderStats,
    useCreateProvider,
    useUpdateProvider,
    useDeleteProvider,
}
