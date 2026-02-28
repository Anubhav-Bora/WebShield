/**
 * Provider Zustand store
 * Manages provider-related client state
 */

import { create } from 'zustand'
import { Provider, ProviderFilters } from '@/types'

interface ProviderStoreState {
    // State
    providers: Provider[]
    selectedProvider: Provider | null
    filters: ProviderFilters
    isLoading: boolean
    error: string | null

    // Actions
    setProviders: (providers: Provider[]) => void
    addProvider: (provider: Provider) => void
    updateProvider: (provider: Provider) => void
    removeProvider: (providerId: string) => void
    setSelectedProvider: (provider: Provider | null) => void
    setFilters: (filters: ProviderFilters) => void
    setLoading: (isLoading: boolean) => void
    setError: (error: string | null) => void
    clearError: () => void
    reset: () => void
}

const initialState = {
    providers: [],
    selectedProvider: null,
    filters: {},
    isLoading: false,
    error: null,
}

export const useProviderStore = create<ProviderStoreState>((set: any) => ({
    ...initialState,

    setProviders: (providers: Provider[]) =>
        set({ providers }),

    addProvider: (provider: Provider) =>
        set((state: ProviderStoreState) => ({
            providers: [...state.providers, provider],
        })),

    updateProvider: (provider: Provider) =>
        set((state: ProviderStoreState) => ({
            providers: state.providers.map((p: Provider) =>
                p.id === provider.id ? provider : p
            ),
            selectedProvider:
                state.selectedProvider?.id === provider.id ? provider : state.selectedProvider,
        })),

    removeProvider: (providerId: string) =>
        set((state: ProviderStoreState) => ({
            providers: state.providers.filter((p: Provider) => p.id !== providerId),
            selectedProvider:
                state.selectedProvider?.id === providerId ? null : state.selectedProvider,
        })),

    setSelectedProvider: (provider: Provider | null) => set({ selectedProvider: provider }),

    setFilters: (filters: ProviderFilters) => set({ filters }),

    setLoading: (isLoading: boolean) => set({ isLoading }),

    setError: (error: string | null) => set({ error }),

    clearError: () => set({ error: null }),

    reset: () => set(initialState),
}))

export default useProviderStore
