/**
 * React Query configuration
 */

import { QueryClient } from '@tanstack/react-query'
import { API_CONFIG } from './api.config'

export const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            // Cache time before data is considered stale
            staleTime: API_CONFIG.CACHE.PROVIDERS,

            // How long to keep unused data in cache
            gcTime: 10 * 60 * 1000, // 10 minutes

            // Retry failed requests
            retry: API_CONFIG.RETRY.MAX_ATTEMPTS,

            // Retry delay with exponential backoff
            retryDelay: (attemptIndex) =>
                Math.min(
                    1000 * Math.pow(API_CONFIG.RETRY.BACKOFF_MULTIPLIER, attemptIndex),
                    30000
                ),

            // Don't refetch on window focus
            refetchOnWindowFocus: false,

            // Don't refetch on mount if data is fresh
            refetchOnMount: false,

            // Don't refetch on reconnect
            refetchOnReconnect: false,
        },

        mutations: {
            // Retry failed mutations
            retry: 1,

            // Retry delay
            retryDelay: 1000,
        },
    },
})

export default queryClient
