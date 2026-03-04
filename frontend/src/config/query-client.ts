/**
 * React Query configuration - Optimized for performance and UX
 */

import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            // Data becomes stale after 30 seconds - forces more frequent refetches
            staleTime: 30 * 1000,

            // Keep unused data for 5 minutes
            gcTime: 5 * 60 * 1000,

            // Retry failed requests 2 times with backoff
            retry: 2,

            // Exponential backoff: 1s, 2s
            retryDelay: (attemptIndex) => Math.min(1000 * Math.pow(2, attemptIndex), 10000),

            // Always refetch on window focus
            refetchOnWindowFocus: true,

            // Always refetch on mount (even if data exists)
            refetchOnMount: 'always',

            // Refetch on reconnect
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
