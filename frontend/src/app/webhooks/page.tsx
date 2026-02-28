'use client'

import React from 'react'
import { useWebhookEvents } from '@/hooks/useWebhooks'
import { formatDateTime, formatStatus } from '@/utils/formatters'

export default function WebhooksPage() {
    const { data: webhooks, isLoading, error } = useWebhookEvents()

    return (
        <main className="min-h-screen bg-slate-900 p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold text-white mb-2">Webhooks</h1>
                    <p className="text-slate-400">View and manage webhook events</p>
                </div>

                {/* Webhooks Table */}
                <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
                    {isLoading ? (
                        <div className="p-8 text-center text-slate-400">Loading webhooks...</div>
                    ) : error ? (
                        <div className="p-8 text-center text-red-400">Error loading webhooks</div>
                    ) : webhooks && webhooks.length > 0 ? (
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-slate-700 border-b border-slate-600">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-sm font-semibold text-white">Request ID</th>
                                        <th className="px-6 py-3 text-left text-sm font-semibold text-white">Received At</th>
                                        <th className="px-6 py-3 text-left text-sm font-semibold text-white">Signature Valid</th>
                                        <th className="px-6 py-3 text-left text-sm font-semibold text-white">Forwarded</th>
                                        <th className="px-6 py-3 text-left text-sm font-semibold text-white">Status</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-700">
                                    {webhooks.map((webhook: any) => (
                                        <tr key={webhook.id} className="hover:bg-slate-700 transition">
                                            <td className="px-6 py-4 text-white font-mono text-sm truncate">{webhook.request_id}</td>
                                            <td className="px-6 py-4 text-slate-300 text-sm">{formatDateTime(webhook.received_at)}</td>
                                            <td className="px-6 py-4">
                                                <span className={`px-3 py-1 rounded text-sm font-semibold ${webhook.signature_valid ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'}`}>
                                                    {webhook.signature_valid ? 'Valid' : 'Invalid'}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className={`px-3 py-1 rounded text-sm font-semibold ${webhook.forwarded ? 'bg-blue-900 text-blue-200' : 'bg-slate-700 text-slate-300'}`}>
                                                    {webhook.forwarded ? 'Yes' : 'No'}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className={`px-3 py-1 rounded text-sm font-semibold ${webhook.response_status === 200 ? 'bg-green-900 text-green-200' : 'bg-yellow-900 text-yellow-200'}`}>
                                                    {webhook.response_status || 'Pending'}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <div className="p-8 text-center text-slate-400">
                            <p>No webhooks found</p>
                        </div>
                    )}
                </div>
            </div>
        </main>
    )
}
