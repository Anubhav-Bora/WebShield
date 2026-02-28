/**
 * Application configuration
 */

export const APP_CONFIG = {
    // App metadata
    name: 'Webhook Gateway Dashboard',
    description: 'Professional webhook gateway management dashboard',
    version: '1.0.0',

    // Environment
    environment: process.env.NODE_ENV || 'development',
    isDevelopment: process.env.NODE_ENV === 'development',
    isProduction: process.env.NODE_ENV === 'production',

    // Feature flags
    features: {
        enableAnalytics: process.env.NEXT_PUBLIC_ENABLE_ANALYTICS === 'true',
        enableErrorTracking: process.env.NEXT_PUBLIC_ENABLE_ERROR_TRACKING === 'true',
        enableDebugMode: process.env.NEXT_PUBLIC_DEBUG_MODE === 'true',
    },

    // Logging
    logging: {
        enabled: true,
        level: process.env.NEXT_PUBLIC_LOG_LEVEL || 'info',
        logToConsole: true,
        logToServer: false,
    },

    // Performance
    performance: {
        enableMetrics: true,
        enableProfiling: process.env.NODE_ENV === 'development',
    },

    // Security
    security: {
        enableCSP: true,
        enableXSSProtection: true,
        enableFrameProtection: true,
    },

    // Timeouts
    timeouts: {
        apiRequest: 30000, // 30 seconds
        debounce: 300, // 300ms
        animation: 300, // 300ms
    },

    // Limits
    limits: {
        maxNotifications: 5,
        maxRetries: 3,
        maxPayloadSize: 1000000, // 1MB
    },
}

export default APP_CONFIG
