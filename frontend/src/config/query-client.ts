/**
 * React Query configuration - Optimized for performance and UX
 */

import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            // Keep data fresh for 5 minutes
            staleTime: 5 * 60 * 1000,

            // Keep unused data for 10 minutes
            gcTime: 10 * 60 * 1000,

            // Retry failed requests 2 times with backoff
            retry: 2,

            // Exponential backoff: 1s, 2s
            retryDelay: (attemptIndex) => Math.min(1000 * Math.pow(2, attemptIndex), 10000),

            // Refetch on window focus if data is stale
            refetchOnWindowFocus: true,

            // Refetch on mount if data is stale
            refetchOnMount: true,

            // Refetch on reconnect if data is stale
            refetchOnReconnect: true,
        },

        mutations: {
            // Retry failed mutations once
            retry: 1,

            // 500ms delay before retry
            retryDelay: 500,
        },
    },
})

export default queryClient
