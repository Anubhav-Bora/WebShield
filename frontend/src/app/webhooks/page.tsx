'use client'

import React from 'react'
import { useWebhookEvents } from '@/hooks/useWebhooks'
import { formatDateTime } from '@/utils/formatters'
import { DataTable } from '@/components/ui/DataTable'
import DashboardLayout from '@/components/layout/DashboardLayout'
import gsap from 'gsap'

export default function WebhooksPage() {
    const { data: webhooks, isLoading, error } = useWebhookEvents()

    React.useEffect(() => {
        gsap.from('.page-header', { opacity: 0, x: -20, duration: 0.5, ease: 'power2.out' })
    }, [])

    const columns = [
        { key: 'request_id', title: 'Request ID', render: (w: any) => <span className="font-mono text-white text-xs truncate max-w-[150px] inline-block">{w.request_id}</span> },
        { key: 'received_at', title: 'Received At', render: (w: any) => <span className="text-slate-300">{formatDateTime(w.received_at)}</span> },
        {
            key: 'signature_valid', title: 'Signature', render: (w: any) => (
                <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${w.signature_valid ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'}`}>
                    {w.signature_valid ? 'Valid' : 'Invalid'}
                </span>
            )
        },
        {
            key: 'forwarded', title: 'Forwarded', render: (w: any) => (
                <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${w.forwarded ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20' : 'bg-slate-500/10 text-slate-400 border border-slate-500/20'}`}>
                    {w.forwarded ? 'Yes' : 'No'}
                </span>
            )
        },
        {
            key: 'status', title: 'Status', render: (w: any) => (
                <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${w.response_status === 200 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'}`}>
                    {w.response_status || 'Pending'}
                </span>
            )
        }
    ]

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto">
                <div className="mb-8 page-header">
                    <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400 mb-2">Webhooks</h1>
                    <p className="text-slate-400 text-lg">View and manage webhook events</p>
                </div>

                {isLoading ? (
                    <div className="p-8 text-center text-slate-400 animate-pulse">Loading webhooks...</div>
                ) : error ? (
                    <div className="p-8 text-center text-rose-400">Error loading webhooks</div>
                ) : (
                    <DataTable
                        columns={columns}
                        data={webhooks || []}
                        delay={0.2}
                    />
                )}
            </div>
        </DashboardLayout>
    )
}

