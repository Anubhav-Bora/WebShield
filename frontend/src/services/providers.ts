/**
 * Provider API service
 * Handles all provider-related API calls
 */

import { apiClient } from './api'
import { API_CONFIG } from '@/config/api.config'
import { Provider, ProviderCreate, ProviderUpdate } from '@/types'

/**
 * Create a new provider
 */
export const createProvider = async (data: ProviderCreate): Promise<Provider> => {
    const response = await apiClient.post<Provider>(
        API_CONFIG.ENDPOINTS.PROVIDERS,
        data
    )
    return response.data
}

/**
 * Get provider by name
 */
export const getProvider = async (name: string): Promise<Provider> => {
    const response = await apiClient.get<Provider>(
        API_CONFIG.ENDPOINTS.PROVIDER_DETAIL(name)
    )
    return response.data
}

/**
 * Get all providers
 */
export const getProviders = async (): Promise<Provider[]> => {
    // Note: Backend doesn't have a list endpoint yet, so we'll need to add it
    // For now, this is a placeholder
    try {
        const response = await apiClient.get<Provider[]>(
            API_CONFIG.ENDPOINTS.PROVIDERS
        )
        return response.data
    } catch (error) {
        // If endpoint doesn't exist, return empty array
        console.warn('Providers list endpoint not available')
        return []
    }
}

/**
 * Update provider
 */
export const updateProvider = async (
    name: string,
    data: ProviderUpdate
): Promise<Provider> => {
    const response = await apiClient.put<Provider>(
        API_CONFIG.ENDPOINTS.PROVIDER_DETAIL(name),
        data
    )
    return response.data
}

/**
 * Delete provider
 */
export const deleteProvider = async (name: string): Promise<void> => {
    await apiClient.delete(
        API_CONFIG.ENDPOINTS.PROVIDER_DETAIL(name)
    )
}

/**
 * Get provider statistics
 */
export const getProviderStats = async (name: string): Promise<{
    total_webhooks: number
    successful_webhooks: number
    failed_webhooks: number
    last_webhook_at: string | null
}> => {
    // This endpoint might need to be added to backend
    try {
        const response = await apiClient.get(
            `${API_CONFIG.ENDPOINTS.PROVIDER_DETAIL(name)}/stats`
        )
        return response.data
    } catch (error) {
        console.warn('Provider stats endpoint not available')
        return {
            total_webhooks: 0,
            successful_webhooks: 0,
            failed_webhooks: 0,
            last_webhook_at: null,
        }
    }
}

export default {
    createProvider,
    getProvider,
    getProviders,
    updateProvider,
    deleteProvider,
    getProviderStats,
}
