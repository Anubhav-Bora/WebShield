'use client'

import React from 'react'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { DataTable } from '@/components/ui/DataTable'
import gsap from 'gsap'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '@/store/useAuthStore'
import { useNotificationStore } from '@/store/useNotificationStore'

interface WebhookRetry {
    id: string
    webhook_event_id: string
    attempt_number: number
    status: string
    error_message: string
    next_retry_at: string
    created_at: string
}

export default function WebhookRetriesPage() {
    const token = useAuthStore((state) => state.token)
    const { success: showSuccess, error: showError } = useNotificationStore()
    const queryClient = useQueryClient()
    const [isHydrated, setIsHydrated] = React.useState(false)
    const [retryingId, setRetryingId] = React.useState<string | null>(null)

    React.useEffect(() => {
        setIsHydrated(true)
        gsap.from('.page-header', { opacity: 0, x: -20, duration: 0.5, ease: 'power2.out' })
    }, [])

    const { data: retries = [], isLoading } = useQuery({
        queryKey: ['deadLetterQueue'],
        queryFn: async () => {
            const response = await fetch('http://localhost:8000/admin/dead-letter-queue?limit=100', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            if (!response.ok) throw new Error('Failed to fetch dead letter queue')
            return response.json()
        },
        enabled: !!token && isHydrated,
        staleTime: 30000,
        refetchOnMount: 'always'
    })

    const handleRetry = async (retryId: string) => {
        try {
            setRetryingId(retryId)
            const response = await fetch(`http://localhost:8000/admin/dead-letter-queue/${retryId}/retry`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })

            if (!response.ok) throw new Error('Failed to retry webhook')

            showSuccess('Success', 'Webhook queued for retry')
            queryClient.invalidateQueries({ queryKey: ['deadLetterQueue'] })
        } catch (error) {
            showError('Error', 'Failed to retry webhook')
        } finally {
            setRetryingId(null)
        }
    }

    const columns = [
        {
            key: 'webhook_event_id',
            title: 'Webhook ID',
            render: (r: WebhookRetry) => (
                <span className="text-white font-mono text-sm">{String(r.webhook_event_id).slice(0, 8)}...</span>
            )
        },
        {
            key: 'attempt_number',
            title: 'Attempts',
            render: (r: WebhookRetry) => (
                <span className="text-slate-300">{r.attempt_number}</span>
            )
        },
        {
            key: 'status',
            title: 'Status',
            render: (r: WebhookRetry) => (
                <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                    {r.status}
                </span>
            )
        },
        {
            key: 'error_message',
            title: 'Error',
            render: (r: WebhookRetry) => (
                <span className="text-slate-400 text-sm truncate max-w-[300px]">{r.error_message || 'N/A'}</span>
            )
        },
        {
            key: 'created_at',
            title: 'Failed At',
            render: (r: WebhookRetry) => (
                <span className="text-slate-400 text-sm">
                    {new Date(r.created_at).toLocaleString()}
                </span>
            )
        },
        {
            key: 'actions',
            title: 'Actions',
            render: (r: WebhookRetry) => (
                <button
                    onClick={() => handleRetry(r.id)}
                    disabled={retryingId === r.id}
                    className="px-3 py-1 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded text-sm hover:bg-indigo-500/20 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {retryingId === r.id ? 'Retrying...' : 'Retry'}
                </button>
            )
        }
    ]

    if (!isHydrated) {
        return (
            <DashboardLayout>
                <div className="max-w-7xl mx-auto">
                    <div className="mb-8 page-header">
                        <div>
                            <h1 className="text-4xl font-extrabold text-white mb-2">Dead Letter Queue</h1>
                            <p className="text-slate-300 text-lg">Permanently failed webhooks</p>
                        </div>
                    </div>
                    <div className="p-8 text-center text-slate-400 animate-pulse">Loading...</div>
                </div>
            </DashboardLayout>
        )
    }

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto">
                <div className="mb-8 page-header">
                    <div>
                        <h1 className="text-4xl font-extrabold text-white mb-2">Dead Letter Queue</h1>
                        <p className="text-slate-300 text-lg">Permanently failed webhooks that need manual intervention</p>
                    </div>
                </div>

                {isLoading ? (
                    <div className="p-8 text-center text-slate-400 animate-pulse">Loading dead letter queue...</div>
                ) : retries.length > 0 ? (
                    <DataTable columns={columns} data={retries} delay={0.2} />
                ) : (
                    <div className="bg-slate-800/80 backdrop-blur-sm rounded-xl border border-slate-700 p-12 text-center">
                        <p className="text-slate-400 mb-6 text-lg">No dead-lettered webhooks</p>
                        <p className="text-slate-500 text-sm">All webhooks are being delivered successfully</p>
                    </div>
                )}
            </div>
        </DashboardLayout>
    )
}
