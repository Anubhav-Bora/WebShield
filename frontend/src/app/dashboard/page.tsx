'use client'

import React, { useEffect } from 'react'
import { useProviders } from '@/hooks/useProviders'
import { useWebhookStats } from '@/hooks/useWebhooks'
import { useSecurityStats } from '@/hooks/useSecurityLogs'
import { useNotificationStore } from '@/store/useNotificationStore'

export default function DashboardPage() {
    const { data: providers, isLoading: providersLoading, error: providersError } = useProviders()
    const { data: webhookStats, isLoading: statsLoading } = useWebhookStats()
    const { data: securityStats, isLoading: securityLoading } = useSecurityStats()
    const { error: notificationError } = useNotificationStore()

    // Show error notification if there's an error
    useEffect(() => {
        if (providersError) {
            console.error('Error loading providers:', providersError)
        }
    }, [providersError])

    return (
        <main className="min-h-screen bg-slate-900 p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold text-white mb-2">Dashboard</h1>
                    <p className="text-slate-400">Welcome to your webhook gateway dashboard</p>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    {/* Total Providers */}
                    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-slate-400 text-sm mb-2">Total Providers</p>
                                <p className="text-3xl font-bold text-white">
                                    {providersLoading ? '...' : providers?.length || 0}
                                </p>
                            </div>
                            <div className="text-2xl">📦</div>
                        </div>
                    </div>

                    {/* Total Webhooks */}
                    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-slate-400 text-sm mb-2">Total Webhooks</p>
                                <p className="text-3xl font-bold text-white">
                                    {statsLoading ? '...' : webhookStats?.total || 0}
                                </p>
                            </div>
                            <div className="text-2xl">🔗</div>
                        </div>
                    </div>

                    {/* Success Rate */}
                    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-slate-400 text-sm mb-2">Success Rate</p>
                                <p className="text-3xl font-bold text-green-400">
                                    {statsLoading ? '...' : `${Math.round((webhookStats?.successful || 0) / (webhookStats?.total || 1) * 100)}%`}
                                </p>
                            </div>
                            <div className="text-2xl">✅</div>
                        </div>
                    </div>

                    {/* Security Events */}
                    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                        <div className="flex justify-between items-start">
                            <div>
                                <p className="text-slate-400 text-sm mb-2">Security Events</p>
                                <p className="text-3xl font-bold text-red-400">
                                    {securityLoading ? '...' : securityStats?.total_events || 0}
                                </p>
                            </div>
                            <div className="text-2xl">🛡️</div>
                        </div>
                    </div>
                </div>

                {/* Content Sections */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Providers Section */}
                    <div className="lg:col-span-2 bg-slate-800 rounded-lg p-6 border border-slate-700">
                        <h2 className="text-xl font-bold text-white mb-4">Recent Providers</h2>
                        {providersLoading ? (
                            <p className="text-slate-400">Loading providers...</p>
                        ) : providers && providers.length > 0 ? (
                            <div className="space-y-3">
                                {providers.slice(0, 5).map((provider: any) => (
                                    <div key={provider.id} className="flex justify-between items-center p-3 bg-slate-700 rounded">
                                        <div>
                                            <p className="text-white font-semibold">{provider.name}</p>
                                            <p className="text-slate-400 text-sm">{provider.forwarding_url}</p>
                                        </div>
                                        <span className={`px-3 py-1 rounded text-sm ${provider.is_active ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'}`}>
                                            {provider.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-slate-400">No providers found</p>
                        )}
                    </div>

                    {/* Quick Actions */}
                    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                        <h2 className="text-xl font-bold text-white mb-4">Quick Actions</h2>
                        <div className="space-y-3">
                            <a href="/providers/create" className="block w-full px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 transition text-center">
                                Create Provider
                            </a>
                            <a href="/webhooks" className="block w-full px-4 py-2 bg-slate-700 text-white rounded hover:bg-slate-600 transition text-center">
                                View Webhooks
                            </a>
                            <a href="/security-logs" className="block w-full px-4 py-2 bg-slate-700 text-white rounded hover:bg-slate-600 transition text-center">
                                Security Logs
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    )
}
