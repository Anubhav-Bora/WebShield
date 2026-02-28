/**
 * Formatting utilities for dates, numbers, and other data
 */

import { format, formatDistanceToNow, parseISO } from 'date-fns'

/**
 * Format date to readable string
 */
export const formatDate = (date: string | Date, formatStr: string = 'MMM dd, yyyy'): string => {
    try {
        const dateObj = typeof date === 'string' ? parseISO(date) : date
        return format(dateObj, formatStr)
    } catch (error) {
        return 'Invalid date'
    }
}

/**
 * Format date to time string
 */
export const formatTime = (date: string | Date, formatStr: string = 'HH:mm:ss'): string => {
    try {
        const dateObj = typeof date === 'string' ? parseISO(date) : date
        return format(dateObj, formatStr)
    } catch (error) {
        return 'Invalid time'
    }
}

/**
 * Format date to datetime string
 */
export const formatDateTime = (date: string | Date, formatStr: string = 'MMM dd, yyyy HH:mm:ss'): string => {
    try {
        const dateObj = typeof date === 'string' ? parseISO(date) : date
        return format(dateObj, formatStr)
    } catch (error) {
        return 'Invalid datetime'
    }
}

/**
 * Format date as relative time (e.g., "2 hours ago")
 */
export const formatRelativeTime = (date: string | Date): string => {
    try {
        const dateObj = typeof date === 'string' ? parseISO(date) : date
        return formatDistanceToNow(dateObj, { addSuffix: true })
    } catch (error) {
        return 'Unknown time'
    }
}

/**
 * Format number with thousand separators
 */
export const formatNumber = (num: number, decimals: number = 0): string => {
    return num.toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
    })
}

/**
 * Format bytes to human readable size
 */
export const formatBytes = (bytes: number, decimals: number = 2): string => {
    if (bytes === 0) return '0 Bytes'

    const k = 1024
    const dm = decimals < 0 ? 0 : decimals
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

/**
 * Format milliseconds to human readable duration
 */
export const formatDuration = (ms: number): string => {
    if (ms < 1000) return `${ms}ms`
    if (ms < 60000) return `${(ms / 1000).toFixed(2)}s`
    if (ms < 3600000) return `${(ms / 60000).toFixed(2)}m`
    return `${(ms / 3600000).toFixed(2)}h`
}

/**
 * Format percentage
 */
export const formatPercentage = (value: number, decimals: number = 1): string => {
    return `${(value * 100).toFixed(decimals)}%`
}

/**
 * Format status badge text
 */
export const formatStatus = (status: string): string => {
    return status
        .split('_')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')
}

/**
 * Format event type for display
 */
export const formatEventType = (eventType: string): string => {
    const eventMap: Record<string, string> = {
        invalid_signature: 'Invalid Signature',
        rate_limit_exceeded: 'Rate Limit Exceeded',
        timestamp_too_old: 'Timestamp Too Old',
        timestamp_in_future: 'Timestamp in Future',
        replay_attempt: 'Replay Attempt',
    }
    return eventMap[eventType] || formatStatus(eventType)
}

/**
 * Format IP address (mask last octet for privacy)
 */
export const formatIPAddress = (ip: string, mask: boolean = false): string => {
    if (!mask) return ip
    const parts = ip.split('.')
    if (parts.length === 4) {
        parts[3] = 'xxx'
        return parts.join('.')
    }
    return ip
}

/**
 * Truncate string with ellipsis
 */
export const truncateString = (str: string, length: number = 50): string => {
    if (str.length <= length) return str
    return str.substring(0, length) + '...'
}

/**
 * Format JSON for display
 */
export const formatJSON = (obj: any, indent: number = 2): string => {
    try {
        return JSON.stringify(obj, null, indent)
    } catch (error) {
        return 'Invalid JSON'
    }
}

export default {
    formatDate,
    formatTime,
    formatDateTime,
    formatRelativeTime,
    formatNumber,
    formatBytes,
    formatDuration,
    formatPercentage,
    formatStatus,
    formatEventType,
    formatIPAddress,
    truncateString,
    formatJSON,
}
