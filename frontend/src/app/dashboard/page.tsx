'use client'

import React, { useEffect } from 'react'
import gsap from 'gsap'
import { useProviders } from '@/hooks/useProviders'
import { useWebhookStats, useWebhookEvents } from '@/hooks/useWebhooks'
import { useSecurityStats } from '@/hooks/useSecurityLogs'
import { StatCard } from '@/components/ui/StatCard'
import { StatCardSkeleton } from '@/components/ui/StatCardSkeleton'
import { AnimatedChart } from '@/components/ui/AnimatedChart'
import { DataTable } from '@/components/ui/DataTable'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { User, Download } from 'lucide-react'
import { exportDashboardPDF } from '@/services/export'
import { useNotificationStore } from '@/store/useNotificationStore'

export default function DashboardPage() {
    const { success, error: showError } = useNotificationStore()

    // Fetch data - React Query handles caching automatically
    // Use isFetching to show loading during background refetches
    const { data: providers = [], isLoading: providersLoading, isFetching: providersFetching } = useProviders()
    const { data: webhookStats, isLoading: statsLoading, isFetching: statsFetching } = useWebhookStats()
    const { data: securityStats, isLoading: securityLoading, isFetching: securityFetching } = useSecurityStats()

    const handleExportDashboard = async () => {
        try {
            await exportDashboardPDF()
            success('Export successful', 'Dashboard exported as PDF')
        } catch (err) {
            showError('Export failed', 'Failed to export dashboard as PDF')
        }
    }
    const { data: webhookEvents = [], isLoading: eventsLoading, isFetching: eventsFetching } = useWebhookEvents(undefined, 100, 0)

    // Show loading state if initial load OR if all queries are fetching
    const isInitialLoading = providersLoading || statsLoading || securityLoading || eventsLoading
    const isRefetching = providersFetching && statsFetching && securityFetching && eventsFetching
    const isAnyLoading = isInitialLoading || isRefetching

    // Calculate success rate
    const successRate = Math.round(((webhookStats?.successful || 0) / (webhookStats?.total || 1)) * 100)

    // Calculate traffic sources from webhook events
    const trafficSources = React.useMemo(() => {
        if (!webhookEvents || webhookEvents.length === 0) {
            return []
        }

        const sourceMap: Record<string, number> = {}
        webhookEvents.forEach((event: any) => {
            const source = event.source || 'Unknown'
            sourceMap[source] = (sourceMap[source] || 0) + 1
        })

        const total = Object.values(sourceMap).reduce((a, b) => a + b, 0)
        return Object.entries(sourceMap)
            .map(([source, count]) => ({
                source,
                count,
                percentage: total > 0 ? (count / total) * 100 : 0
            }))
            .sort((a, b) => b.count - a.count)
    }, [webhookEvents])

    // Transform webhook events into chart data
    const chartData = React.useMemo(() => {
        if (!webhookEvents || webhookEvents.length === 0) {
            return []
        }

        const timeGroups: Record<string, number> = {}

        webhookEvents.forEach((event: any) => {
            const date = new Date(event.received_at)
            const minutes = Math.floor(date.getMinutes() / 5) * 5
            const timeKey = `${date.getHours()}:${String(minutes).padStart(2, '0')}`
            timeGroups[timeKey] = (timeGroups[timeKey] || 0) + 1
        })

        return Object.entries(timeGroups)
            .map(([time, count]) => ({ time, requests: count }))
            .slice(-20)
    }, [webhookEvents])

    // Animate page entrance
    useEffect(() => {
        const tl = gsap.timeline()
        tl.from('.page-title', { opacity: 0, x: -30, duration: 0.5, ease: 'power2.out' })
            .from('.page-subtitle', { opacity: 0, x: -30, duration: 0.5, ease: 'power2.out' }, '-=0.3')
    }, [])

    const providerColumns = [
        { key: 'name', title: 'Provider Name', render: (p: any) => <span className="text-white font-medium">{p.name}</span> },
        { key: 'forwarding_url', title: 'Target URL', render: (p: any) => <span className="truncate max-w-[200px] inline-block">{p.forwarding_url}</span> },
        {
            key: 'status', title: 'Status', render: (p: any) => (
                <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${p.is_active ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'}`}>
                    {p.is_active ? 'Active' : 'Inactive'}
                </span>
            )
        }
    ]

    return (
        <DashboardLayout>
            <div className="dashboard-container max-w-7xl mx-auto relative">
                {/* Floating orbs background effect */}
                <div className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDuration: '4s' }} />
                <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDuration: '6s', animationDelay: '1s' }} />

                {/* Header */}
                <div className="mb-10 relative z-10 flex items-end justify-between">
                    <div>
                        <h1 className="page-title text-white text-3xl font-bold mb-2">
                            Dashboard
                        </h1>
                        <p className="page-subtitle text-slate-400 text-sm flex items-center gap-2">
                            Hey Admin— Here's what's happening with your gateway today
                        </p>
                    </div>
                    <button
                        onClick={handleExportDashboard}
                        className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold transition"
                    >
                        <Download size={18} />
                        Export PDF
                    </button>
                </div>

                {/* Stats Grid - Show all skeletons or all cards together */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8 relative z-10">
                    {isAnyLoading ? (
                        <>
                            <StatCardSkeleton />
                            <StatCardSkeleton />
                            <StatCardSkeleton />
                            <StatCardSkeleton />
                        </>
                    ) : (
                        <>
                            <StatCard
                                title="Total Providers"
                                value={providers?.length || 0}
                                delay={0}
                                colorTheme="emerald"
                            />
                            <StatCard
                                title="Total Webhooks"
                                value={webhookStats?.total || 0}
                                delay={0.1}
                                colorTheme="blue"
                            />
                            <StatCard
                                title="Delivery Success"
                                value={`${successRate}%`}
                                delay={0.2}
                                colorTheme="dark"
                            />
                            <StatCard
                                title="Security Events"
                                value={securityStats?.total_events || 0}
                                delay={0.3}
                                colorTheme="dark"
                            />
                        </>
                    )}
                </div>

                {/* Main Content Area */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-10 relative z-10 flex-col-reverse lg:flex-row">
                    {/* Animated Traffic Chart */}
                    <div className="lg:col-span-2 relative h-[420px]">
                        <AnimatedChart
                            title="Webhook Traffic"
                            data={chartData}
                            dataKey="requests"
                            xAxisKey="time"
                            delay={0.4}
                        />
                        {/* Providers Table moved here to match layout */}
                        <div className="mt-8 relative z-10">
                            <DataTable
                                title="Transactions"
                                columns={providerColumns}
                                data={providers?.slice(0, 5) || []}
                                delay={0.6}
                            />
                        </div>
                    </div>

                    {/* Right Column: Traffic Sources List */}
                    <div className="glass flex flex-col gap-6 relative overflow-hidden group">

                        {/* Traffic Sources */}
                        <div className="bg-[#141419]/90 rounded-2xl p-6 border border-white/5 h-auto">
                            <h2 className="text-xl font-bold text-white mb-6">
                                Traffic Sources
                            </h2>
                            {trafficSources.length === 0 ? (
                                <p className="text-slate-400 text-sm">No traffic data available</p>
                            ) : (
                                <div className="space-y-4">
                                    {trafficSources.map((source) => (
                                        <div key={source.source} className="flex flex-col gap-2 py-2 border-b border-white/5 last:border-0 hover:bg-white/5 px-2 rounded-lg transition-colors cursor-pointer">
                                            <div className="flex justify-between items-center">
                                                <p className="text-slate-300 font-medium text-sm">{source.source}</p>
                                                <p className="text-xs text-slate-500">{source.count}</p>
                                            </div>
                                            <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                                                <div className="h-full bg-slate-500 rounded-full" style={{ width: `${source.percentage}%` }}></div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Recent Customers (formerly Quick Actions) */}
                        <div className="bg-[#141419]/90 rounded-2xl p-6 border border-white/5 flex-1 min-h-[300px]">
                            <h2 className="text-xl font-bold text-white mb-6">
                                Recent Customers
                            </h2>
                            <div className="space-y-4">
                                {providers?.slice(0, 4).map((p: any, i) => (
                                    <div key={i} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0 hover:bg-white/5 px-2 rounded-lg transition-colors cursor-pointer">
                                        <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 rounded-full bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center overflow-hidden">
                                                {/* Fallback to user icon if fake face image URL doesn't exist */}
                                                <User size={14} className="text-indigo-400" />
                                            </div>
                                            <div>
                                                <h4 className="text-white text-sm font-semibold">{p.name}</h4>
                                                <p className="text-xs text-slate-500">customer@email.com</p>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    )
}
