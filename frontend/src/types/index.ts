/**
 * Main type definitions for the webhook gateway dashboard
 */

// Provider types
export interface Provider {
    id: string
    name: string
    secret_key: string
    forwarding_url: string
    is_active: boolean
    created_at?: string
    updated_at?: string
}

export interface ProviderCreate {
    name: string
    secret_key: string
    forwarding_url: string
}

export interface ProviderUpdate {
    secret_key?: string
    forwarding_url?: string
    is_active?: boolean
}

// Webhook event types
export interface WebhookEvent {
    id: string
    provider_id: string
    request_id: string
    payload: Record<string, any>
    headers: Record<string, string>
    signature_valid: boolean
    forwarded: boolean
    received_at: string
    forwarded_at?: string
    response_status?: number
    response_body?: string
}

export interface WebhookResponse {
    status: 'accepted' | 'rejected'
    message: string
    webhook_id: string
}

// Security log types
export interface SecurityLog {
    id: string
    provider_name: string
    event_type: 'invalid_signature' | 'rate_limit_exceeded' | 'timestamp_too_old' | 'timestamp_in_future' | 'replay_attempt'
    ip_address: string
    request_id?: string
    details: Record<string, any>
    created_at: string
}

// API response wrapper
export interface ApiResponse<T> {
    data: T
    status: number
    message?: string
}

export interface ApiError {
    status: number
    detail: string
    timestamp?: string
}

// Pagination types
export interface PaginationParams {
    page: number
    limit: number
    sort?: string
    order?: 'asc' | 'desc'
}

export interface PaginatedResponse<T> {
    items: T[]
    total: number
    page: number
    limit: number
    pages: number
}

// Filter types
export interface ProviderFilters {
    search?: string
    is_active?: boolean
    sort?: 'name' | 'created_at'
    order?: 'asc' | 'desc'
}

export interface WebhookFilters {
    provider_id?: string
    status?: 'success' | 'failed' | 'pending'
    date_from?: string
    date_to?: string
    sort?: 'received_at' | 'forwarded_at'
    order?: 'asc' | 'desc'
}

export interface SecurityLogFilters {
    event_type?: string
    provider_name?: string
    date_from?: string
    date_to?: string
    sort?: 'created_at'
    order?: 'asc' | 'desc'
}

// Dashboard stats types
export interface DashboardStats {
    total_providers: number
    active_providers: number
    total_webhooks: number
    successful_webhooks: number
    failed_webhooks: number
    security_events: number
    rate_limit_events: number
    replay_attempts: number
}

export interface DashboardMetrics {
    webhooks_per_hour: Array<{ hour: string; count: number }>
    success_rate: number
    avg_response_time: number
    top_providers: Array<{ name: string; count: number }>
    recent_events: SecurityLog[]
}

// Health check types
export interface HealthStatus {
    status: 'healthy' | 'degraded' | 'unhealthy'
    service: string
    version: string
    database?: 'connected' | 'disconnected'
    redis?: 'connected' | 'disconnected'
    timestamp: string
}

// Form types
export interface ProviderFormData {
    name: string
    secret_key: string
    forwarding_url: string
}

export interface WebhookTestData {
    provider_name: string
    payload: Record<string, any>
    headers?: Record<string, string>
}

// Notification types
export interface Notification {
    id: string
    type: 'success' | 'error' | 'warning' | 'info'
    title: string
    message: string
    duration?: number
}

// UI state types
export interface UIState {
    isLoading: boolean
    error: string | null
    selectedProvider?: string
    selectedWebhook?: string
    filters: Record<string, any>
}

// Request/Response logging
export interface RequestLog {
    method: string
    url: string
    status: number
    duration: number
    timestamp: string
}

export type { }
