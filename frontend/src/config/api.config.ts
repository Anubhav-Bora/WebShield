/**
 * API configuration
 */

export const API_CONFIG = {
    // Base URL for API requests
    BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',

    // API endpoints
    ENDPOINTS: {
        // Health
        HEALTH: '/health',

        // Webhooks
        WEBHOOKS: '/webhooks',
        WEBHOOK_RECEIVE: (provider: string) => `/webhooks/${provider}`,

        // Admin - Providers
        PROVIDERS: '/admin/providers',
        PROVIDER_DETAIL: (name: string) => `/admin/providers/${name}`,

        // Admin - Webhooks (if we add them later)
        ADMIN_WEBHOOKS: '/admin/webhooks',
        ADMIN_WEBHOOK_DETAIL: (id: string) => `/admin/webhooks/${id}`,

        // Admin - Security Logs (if we add them later)
        ADMIN_LOGS: '/admin/logs',
    },

    // Request timeout in milliseconds
    TIMEOUT: 30000,

    // Retry configuration
    RETRY: {
        MAX_ATTEMPTS: 3,
        DELAY: 1000, // milliseconds
        BACKOFF_MULTIPLIER: 2,
    },

    // Cache configuration
    CACHE: {
        PROVIDERS: 5 * 60 * 1000, // 5 minutes
        WEBHOOKS: 2 * 60 * 1000, // 2 minutes
        LOGS: 1 * 60 * 1000, // 1 minute
        HEALTH: 30 * 1000, // 30 seconds
    },

    // Headers
    HEADERS: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
}

export default API_CONFIG
