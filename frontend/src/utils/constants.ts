/**
 * Application constants
 */

// Event types
export const EVENT_TYPES = {
    INVALID_SIGNATURE: 'invalid_signature',
    RATE_LIMIT_EXCEEDED: 'rate_limit_exceeded',
    TIMESTAMP_TOO_OLD: 'timestamp_too_old',
    TIMESTAMP_IN_FUTURE: 'timestamp_in_future',
    REPLAY_ATTEMPT: 'replay_attempt',
} as const

export const EVENT_TYPE_LABELS: Record<string, string> = {
    [EVENT_TYPES.INVALID_SIGNATURE]: 'Invalid Signature',
    [EVENT_TYPES.RATE_LIMIT_EXCEEDED]: 'Rate Limit Exceeded',
    [EVENT_TYPES.TIMESTAMP_TOO_OLD]: 'Timestamp Too Old',
    [EVENT_TYPES.TIMESTAMP_IN_FUTURE]: 'Timestamp in Future',
    [EVENT_TYPES.REPLAY_ATTEMPT]: 'Replay Attempt',
}

// Webhook status
export const WEBHOOK_STATUS = {
    SUCCESS: 'success',
    FAILED: 'failed',
    PENDING: 'pending',
} as const

export const WEBHOOK_STATUS_LABELS: Record<string, string> = {
    [WEBHOOK_STATUS.SUCCESS]: 'Success',
    [WEBHOOK_STATUS.FAILED]: 'Failed',
    [WEBHOOK_STATUS.PENDING]: 'Pending',
}

// Health status
export const HEALTH_STATUS = {
    HEALTHY: 'healthy',
    DEGRADED: 'degraded',
    UNHEALTHY: 'unhealthy',
} as const

export const HEALTH_STATUS_LABELS: Record<string, string> = {
    [HEALTH_STATUS.HEALTHY]: 'Healthy',
    [HEALTH_STATUS.DEGRADED]: 'Degraded',
    [HEALTH_STATUS.UNHEALTHY]: 'Unhealthy',
}

// Notification types
export const NOTIFICATION_TYPES = {
    SUCCESS: 'success',
    ERROR: 'error',
    WARNING: 'warning',
    INFO: 'info',
} as const

// Pagination defaults
export const PAGINATION_DEFAULTS = {
    PAGE: 1,
    LIMIT: 50,
    MAX_LIMIT: 100,
} as const

// Sort options
export const SORT_OPTIONS = {
    ASC: 'asc',
    DESC: 'desc',
} as const

// Date formats
export const DATE_FORMATS = {
    DATE: 'MMM dd, yyyy',
    TIME: 'HH:mm:ss',
    DATETIME: 'MMM dd, yyyy HH:mm:ss',
    ISO: "yyyy-MM-dd'T'HH:mm:ss.SSSxxx",
} as const

// Navigation items
export const NAVIGATION_ITEMS = [
    {
        label: 'Dashboard',
        href: '/dashboard',
        icon: 'LayoutDashboard',
    },
    {
        label: 'Providers',
        href: '/providers',
        icon: 'Package',
    },
    {
        label: 'Webhooks',
        href: '/webhooks',
        icon: 'Webhook',
    },
    {
        label: 'Security Logs',
        href: '/security-logs',
        icon: 'Shield',
    },
    {
        label: 'Settings',
        href: '/settings',
        icon: 'Settings',
    },
] as const

// API error messages
export const ERROR_MESSAGES = {
    NETWORK_ERROR: 'Network error. Please check your connection.',
    SERVER_ERROR: 'Server error. Please try again later.',
    VALIDATION_ERROR: 'Validation error. Please check your input.',
    NOT_FOUND: 'Resource not found.',
    UNAUTHORIZED: 'Unauthorized. Please log in.',
    FORBIDDEN: 'Forbidden. You do not have permission.',
    CONFLICT: 'Conflict. Resource already exists.',
    RATE_LIMITED: 'Rate limited. Please try again later.',
    UNKNOWN_ERROR: 'An unknown error occurred.',
} as const

// Success messages
export const SUCCESS_MESSAGES = {
    PROVIDER_CREATED: 'Provider created successfully.',
    PROVIDER_UPDATED: 'Provider updated successfully.',
    PROVIDER_DELETED: 'Provider deleted successfully.',
    WEBHOOK_SENT: 'Test webhook sent successfully.',
    WEBHOOK_RETRIED: 'Webhook retry initiated.',
    LOGS_EXPORTED: 'Logs exported successfully.',
} as const

// Validation rules
export const VALIDATION_RULES = {
    PROVIDER_NAME_MIN: 3,
    PROVIDER_NAME_MAX: 50,
    SECRET_KEY_MIN: 32,
    URL_MIN: 10,
    URL_MAX: 2048,
} as const

// Animation durations (in milliseconds)
export const ANIMATION_DURATIONS = {
    FAST: 200,
    NORMAL: 300,
    SLOW: 500,
    VERY_SLOW: 1000,
} as const

// Debounce delays (in milliseconds)
export const DEBOUNCE_DELAYS = {
    SEARCH: 300,
    RESIZE: 200,
    SCROLL: 100,
} as const

// Polling intervals (in milliseconds)
export const POLLING_INTERVALS = {
    HEALTH: 30000, // 30 seconds
    STATS: 60000, // 1 minute
    LOGS: 10000, // 10 seconds
} as const

export default {
    EVENT_TYPES,
    EVENT_TYPE_LABELS,
    WEBHOOK_STATUS,
    WEBHOOK_STATUS_LABELS,
    HEALTH_STATUS,
    HEALTH_STATUS_LABELS,
    NOTIFICATION_TYPES,
    PAGINATION_DEFAULTS,
    SORT_OPTIONS,
    DATE_FORMATS,
    NAVIGATION_ITEMS,
    ERROR_MESSAGES,
    SUCCESS_MESSAGES,
    VALIDATION_RULES,
    ANIMATION_DURATIONS,
    DEBOUNCE_DELAYS,
    POLLING_INTERVALS,
}
