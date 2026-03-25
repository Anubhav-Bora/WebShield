/**
 * Custom hook for WebSocket real-time event streaming
 */

import { useEffect, useRef, useCallback, useState } from 'react'
import { useNotificationStore } from '@/store/useNotificationStore'
import { useQueryClient } from '@tanstack/react-query'
import { API_CONFIG } from '@/config/api.config'

export interface WebSocketEvent {
    type: 'webhook_event' | 'stats_update' | 'security_event' | 'alert' | 'connection' | 'echo'
    data: any
    timestamp?: string
}

export const useWebSocket = (onEvent?: (event: WebSocketEvent) => void) => {
    const wsRef = useRef<WebSocket | null>(null)
    const { warning, error: showError } = useNotificationStore()
    const queryClient = useQueryClient()
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
    const reconnectAttemptsRef = useRef<number>(0)
    const [isConnected, setIsConnected] = useState(false)
    const maxReconnectAttempts = 5

    const connect = useCallback(() => {
        // Don't reconnect if already connected or max attempts reached
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            return
        }

        if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
            showError('WebSocket Error', 'Max reconnection attempts reached')
            return
        }

        try {
            // Get auth token from localStorage
            const token = localStorage.getItem('auth_token')
            if (!token) {
                console.warn('WebSocket: No auth token found in localStorage')
                showError('WebSocket Error', 'Authentication token not found')
                return
            }

            console.log('WebSocket: Token found, attempting connection')
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
            const baseUrl = API_CONFIG.BASE_URL.replace(/^https?:\/\//, '')
            const wsUrl = `${protocol}//${baseUrl}/ws?token=${encodeURIComponent(token)}`
            
            console.log('WebSocket: Connecting to', wsUrl.replace(token, '[TOKEN]'))

            wsRef.current = new WebSocket(wsUrl)

            // Set a timeout for connection
            const connectionTimeout = setTimeout(() => {
                if (wsRef.current?.readyState === WebSocket.CONNECTING) {
                    wsRef.current?.close()
                }
            }, 5000)

            wsRef.current.onopen = () => {
                clearTimeout(connectionTimeout)
                setIsConnected(true)
                reconnectAttemptsRef.current = 0
                console.log('✓ WebSocket connected')
            }

            wsRef.current.onmessage = (event) => {
                try {
                    const message: WebSocketEvent = JSON.parse(event.data)

                    // Handle different event types
                    switch (message.type) {
                        case 'connection':
                            console.log('WebSocket connection established')
                            break

                        case 'echo':
                            break

                        case 'webhook_event':
                            // Invalidate webhook queries to refresh data
                            queryClient.invalidateQueries({ queryKey: ['webhooks'] })
                            queryClient.invalidateQueries({ queryKey: ['webhookAnalytics'] })
                            console.log('📨 Webhook event received:', message.data)
                            break

                        case 'stats_update':
                            queryClient.invalidateQueries({ queryKey: ['webhooks', 'stats'] })
                            break

                        case 'security_event':
                            showError('Security Alert', `${message.data.event_type}: ${message.data.provider_name}`)
                            queryClient.invalidateQueries({ queryKey: ['security'] })
                            break

                        case 'alert':
                            if (message.data.severity === 'error') {
                                showError(message.data.alert_type, message.data.message)
                            } else if (message.data.severity === 'warning') {
                                warning(message.data.alert_type, message.data.message)
                            }
                            break
                    }

                    if (onEvent) {
                        onEvent(message)
                    }
                } catch (err) {
                    console.error('Error parsing WebSocket message:', err)
                }
            }

            wsRef.current.onerror = (event) => {
                clearTimeout(connectionTimeout)
                setIsConnected(false)
                // Only log on first error, not every retry
                if (reconnectAttemptsRef.current <= 1) {
                    console.warn('WebSocket initial connection error - will retry')
                    console.debug('Error details:', event)
                }
            }

            wsRef.current.onclose = () => {
                clearTimeout(connectionTimeout)
                setIsConnected(false)
                console.log('WebSocket closed')

                // Attempt to reconnect with exponential backoff
                if (reconnectAttemptsRef.current < maxReconnectAttempts) {
                    const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000)
                    reconnectAttemptsRef.current += 1
                    console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current})`)
                    reconnectTimeoutRef.current = setTimeout(() => {
                        connect()
                    }, delay)
                }
            }
        } catch (err) {
            setIsConnected(false)
            console.error('WebSocket connection error:', err)
        }
    }, [queryClient, onEvent, warning, showError])

    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current)
        }
        if (wsRef.current) {
            wsRef.current.close()
            wsRef.current = null
        }
        setIsConnected(false)
        reconnectAttemptsRef.current = 0
    }, [])

    useEffect(() => {
        // Only connect on client side
        if (typeof window !== 'undefined') {
            connect()
        }

        return () => {
            disconnect()
        }
    }, [connect, disconnect])

    return {
        isConnected,
        disconnect,
        reconnect: connect,
    }
}

export default useWebSocket
