/**
 * Zod validation schemas for forms and API responses
 */

import { z } from 'zod'

// Provider schemas
export const ProviderCreateSchema = z.object({
    name: z
        .string()
        .min(1, 'Provider name is required')
        .min(3, 'Provider name must be at least 3 characters')
        .max(50, 'Provider name must be less than 50 characters')
        .regex(/^[a-zA-Z0-9_-]+$/, 'Provider name can only contain letters, numbers, hyphens, and underscores'),
    secret_key: z
        .string()
        .min(1, 'Secret key is required')
        .min(32, 'Secret key must be at least 32 characters'),
    forwarding_url: z
        .string()
        .min(1, 'Forwarding URL is required')
        .url('Forwarding URL must be a valid URL')
})

export const ProviderUpdateSchema = z.object({
    secret_key: z
        .string()
        .min(32, 'Secret key must be at least 32 characters')
        .optional(),
    forwarding_url: z
        .string()
        .url('Forwarding URL must be a valid URL')
        .optional(),
    is_active: z.boolean().optional()
})

// Webhook test schema
export const WebhookTestSchema = z.object({
    provider_name: z
        .string()
        .min(1, 'Provider name is required'),
    payload: z
        .record(z.any())
        .refine((obj) => Object.keys(obj).length > 0, 'Payload cannot be empty'),
    headers: z
        .record(z.string())
        .optional()
})

// Filter schemas
export const ProviderFiltersSchema = z.object({
    search: z.string().optional(),
    is_active: z.boolean().optional(),
    sort: z.enum(['name', 'created_at']).optional(),
    order: z.enum(['asc', 'desc']).optional()
})

export const WebhookFiltersSchema = z.object({
    provider_id: z.string().optional(),
    status: z.enum(['success', 'failed', 'pending']).optional(),
    date_from: z.string().datetime().optional(),
    date_to: z.string().datetime().optional(),
    sort: z.enum(['received_at', 'forwarded_at']).optional(),
    order: z.enum(['asc', 'desc']).optional()
})

export const SecurityLogFiltersSchema = z.object({
    event_type: z.string().optional(),
    provider_name: z.string().optional(),
    date_from: z.string().datetime().optional(),
    date_to: z.string().datetime().optional(),
    sort: z.enum(['created_at']).optional(),
    order: z.enum(['asc', 'desc']).optional()
})

// Pagination schema
export const PaginationSchema = z.object({
    page: z.number().int().min(1, 'Page must be at least 1'),
    limit: z.number().int().min(1, 'Limit must be at least 1').max(100, 'Limit cannot exceed 100')
})

// API response schemas
export const ApiResponseSchema = z.object({
    status: z.string(),
    message: z.string().optional(),
    webhook_id: z.string().optional()
})

export const ProviderResponseSchema = z.object({
    id: z.string().uuid(),
    name: z.string(),
    secret_key: z.string(),
    forwarding_url: z.string().url(),
    is_active: z.boolean(),
    created_at: z.string().datetime().optional(),
    updated_at: z.string().datetime().optional()
})

export const WebhookEventSchema = z.object({
    id: z.string().uuid(),
    provider_id: z.string().uuid(),
    request_id: z.string(),
    payload: z.record(z.any()),
    headers: z.record(z.string()),
    signature_valid: z.boolean(),
    forwarded: z.boolean(),
    received_at: z.string().datetime(),
    forwarded_at: z.string().datetime().optional(),
    response_status: z.number().optional(),
    response_body: z.string().optional()
})

export const SecurityLogSchema = z.object({
    id: z.string().uuid(),
    provider_name: z.string(),
    event_type: z.enum([
        'invalid_signature',
        'rate_limit_exceeded',
        'timestamp_too_old',
        'timestamp_in_future',
        'replay_attempt'
    ]),
    client_ip: z.string().ip(),
    request_id: z.string().optional(),
    details: z.record(z.any()),
    created_at: z.string().datetime()
})

export const HealthStatusSchema = z.object({
    status: z.enum(['healthy', 'degraded', 'unhealthy']),
    service: z.string(),
    version: z.string(),
    database: z.enum(['connected', 'disconnected']).optional(),
    redis: z.enum(['connected', 'disconnected']).optional(),
    timestamp: z.string().datetime()
})

// Type inference from schemas
export type ProviderCreateInput = z.infer<typeof ProviderCreateSchema>
export type ProviderUpdateInput = z.infer<typeof ProviderUpdateSchema>
export type WebhookTestInput = z.infer<typeof WebhookTestSchema>
export type ProviderFiltersInput = z.infer<typeof ProviderFiltersSchema>
export type WebhookFiltersInput = z.infer<typeof WebhookFiltersSchema>
export type SecurityLogFiltersInput = z.infer<typeof SecurityLogFiltersSchema>
export type PaginationInput = z.infer<typeof PaginationSchema>
