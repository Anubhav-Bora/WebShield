/**
 * Error handling utilities
 */

import { ApiError } from '@/types'
import { ERROR_MESSAGES } from './constants'

/**
 * Get user-friendly error message
 */
export const getErrorMessage = (error: any): string => {
    if (!error) return ERROR_MESSAGES.UNKNOWN_ERROR

    // Handle ApiError
    if (error.status !== undefined && error.detail) {
        return error.detail
    }

    // Handle Axios error
    if (error.response?.data?.detail) {
        return error.response.data.detail
    }

    // Handle standard Error
    if (error.message) {
        return error.message
    }

    // Handle string error
    if (typeof error === 'string') {
        return error
    }

    return ERROR_MESSAGES.UNKNOWN_ERROR
}

/**
 * Get error title based on status code
 */
export const getErrorTitle = (status: number): string => {
    switch (status) {
        case 400:
            return 'Bad Request'
        case 401:
            return 'Unauthorized'
        case 403:
            return 'Forbidden'
        case 404:
            return 'Not Found'
        case 409:
            return 'Conflict'
        case 429:
            return 'Rate Limited'
        case 500:
            return 'Server Error'
        case 502:
            return 'Bad Gateway'
        case 503:
            return 'Service Unavailable'
        default:
            return 'Error'
    }
}

/**
 * Check if error is retryable
 */
export const isRetryableError = (error: any): boolean => {
    const status = error.status || error.response?.status
    // Retry on 5xx errors and network errors
    return !status || status >= 500 || status === 429
}

/**
 * Check if error is authentication error
 */
export const isAuthError = (error: any): boolean => {
    const status = error.status || error.response?.status
    return status === 401 || status === 403
}

/**
 * Check if error is validation error
 */
export const isValidationError = (error: any): boolean => {
    const status = error.status || error.response?.status
    return status === 400 || status === 422
}

/**
 * Check if error is not found error
 */
export const isNotFoundError = (error: any): boolean => {
    const status = error.status || error.response?.status
    return status === 404
}

/**
 * Check if error is conflict error
 */
export const isConflictError = (error: any): boolean => {
    const status = error.status || error.response?.status
    return status === 409
}

/**
 * Check if error is rate limit error
 */
export const isRateLimitError = (error: any): boolean => {
    const status = error.status || error.response?.status
    return status === 429
}

/**
 * Check if error is network error
 */
export const isNetworkError = (error: any): boolean => {
    return !error.status && !error.response
}

/**
 * Format error for logging
 */
export const formatErrorForLogging = (error: any): string => {
    const title = getErrorTitle(error.status || 0)
    const message = getErrorMessage(error)
    return `[${title}] ${message}`
}

/**
 * Handle API error and return user-friendly message
 */
export const handleApiError = (error: any): { title: string; message: string } => {
    const status = error.status || error.response?.status || 0
    const title = getErrorTitle(status)
    const message = getErrorMessage(error)

    return { title, message }
}

export default {
    getErrorMessage,
    getErrorTitle,
    isRetryableError,
    isAuthError,
    isValidationError,
    isNotFoundError,
    isConflictError,
    isRateLimitError,
    isNetworkError,
    formatErrorForLogging,
    handleApiError,
}
