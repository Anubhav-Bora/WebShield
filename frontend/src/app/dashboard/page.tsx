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
import { Package, Link as LinkIcon, CheckCircle, ShieldAlert, ArrowRight } from 'lucide-react'

export default function DashboardPage() {
    // Fetch data - React Query handles caching automatically
    // Use isFetching to show loading during background refetches
    const { data: providers = [], isLoading: providersLoading, isFetching: providersFetching } = useProviders()
    const { data: webhookStats, isLoading: statsLoading, isFetching: statsFetching } = useWebhookStats()
    const { data: securityStats, isLoading: securityLoading, isFetching: securityFetching } = useSecurityStats()
    const { data: webhookEvents = [], isLoading: eventsLoading, isFetching: eventsFetching } = useWebhookEvents(undefined, 100, 0)

    // Show loading state if initial load OR if all queries are fetching
    const isInitialLoading = providersLoading || statsLoading || securityLoading || eventsLoading
    const isRefetching = providersFetching && statsFetching && securityFetching && eventsFetching
    const isAnyLoading = isInitialLoading || isRefetching

    // Calculate success rate
    const successRate = Math.round(((webhookStats?.successful || 0) / (webhookStats?.total || 1)) * 100)

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
                <div className="mb-12 relative z-10">
                    <h1 className="page-title text-5xl font-extrabold mb-3 gradient-text">
                        Gateway Overview
                    </h1>
                    <p className="page-subtitle text-slate-400 text-lg flex items-center gap-2">
                        <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
                        Real-time webhook monitoring and analytics
                    </p>
                </div>

                {/* Stats Grid - Show all skeletons or all cards together */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10 relative z-10">
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
                                icon={<Package size={24} />}
                                trend="+2 this week"
                                trendUp={true}
                                delay={0}
                            />
                            <StatCard
                                title="Total Webhooks"
                                value={webhookStats?.total || 0}
                                icon={<LinkIcon size={24} />}
                                trend="+15% vs yesterday"
                                trendUp={true}
                                delay={0.1}
                            />
                            <StatCard
                                title="Delivery Success"
                                value={`${successRate}%`}
                                icon={<CheckCircle size={24} />}
                                trend="Stable"
                                trendUp={true}
                                delay={0.2}
                            />
                            <StatCard
                                title="Security Events"
                                value={securityStats?.total_events || 0}
                                icon={<ShieldAlert size={24} />}
                                trend="-5 threats blocked"
                                trendUp={true}
                                delay={0.3}
                            />
                        </>
                    )}
                </div>

                {/* Main Content Area */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-10 relative z-10">
                    {/* Animated Traffic Chart */}
                    <div className="lg:col-span-2 relative h-[420px]">
                        <AnimatedChart
                            title="Real-time Webhook Traffic"
                            data={chartData}
                            dataKey="requests"
                            xAxisKey="time"
                            delay={0.4}
                        />
                    </div>

                    {/* Quick Actions Panel */}
                    <div className="glass rounded-2xl p-6 border border-slate-700/50 h-[420px] flex flex-col relative overflow-hidden group">
                        {/* Gradient overlay */}
                        <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/0 via-blue-500/0 to-transparent group-hover:from-cyan-500/5 group-hover:via-blue-500/5 transition-all duration-700 rounded-2xl" />

                        <div className="relative z-10">
                            <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-3">
                                <span className="w-1 h-6 bg-gradient-to-b from-cyan-500 to-blue-500 rounded-full"></span>
                                Quick Actions
                            </h2>
                            <div className="space-y-4 flex-1">
                                <a href="/providers" className="group/item flex items-center justify-between p-4 glass rounded-xl border border-slate-700/50 hover:border-indigo-500/50 transition-all duration-300 cursor-pointer relative overflow-hidden">
                                    <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/0 to-indigo-500/0 group-hover/item:from-indigo-500/10 group-hover/item:to-transparent transition-all duration-300" />
                                    <div className="flex items-center space-x-3 relative z-10">
                                        <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border border-indigo-500/30 flex items-center justify-center group-hover/item:scale-110 transition-transform duration-300">
                                            <Package className="text-indigo-400" size={20} />
                                        </div>
                                        <div>
                                            <h4 className="text-white font-semibold group-hover/item:text-indigo-400 transition-colors">Manage Providers</h4>
                                            <p className="text-xs text-slate-400">Add or edit endpoints</p>
                                        </div>
                                    </div>
                                    <ArrowRight size={18} className="text-slate-500 group-hover/item:text-indigo-400 group-hover/item:translate-x-1 transition-all relative z-10" />
                                </a>

                                <a href="/webhooks" className="group/item flex items-center justify-between p-4 glass rounded-xl border border-slate-700/50 hover:border-cyan-500/50 transition-all duration-300 cursor-pointer relative overflow-hidden">
                                    <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/0 to-cyan-500/0 group-hover/item:from-cyan-500/10 group-hover/item:to-transparent transition-all duration-300" />
                                    <div className="flex items-center space-x-3 relative z-10">
                                        <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 flex items-center justify-center group-hover/item:scale-110 transition-transform duration-300">
                                            <LinkIcon className="text-cyan-400" size={20} />
                                        </div>
                                        <div>
                                            <h4 className="text-white font-semibold group-hover/item:text-cyan-400 transition-colors">View Webhooks</h4>
                                            <p className="text-xs text-slate-400">Check delivery status</p>
                                        </div>
                                    </div>
                                    <ArrowRight size={18} className="text-slate-500 group-hover/item:text-cyan-400 group-hover/item:translate-x-1 transition-all relative z-10" />
                                </a>

                                <a href="/security-logs" className="group/item flex items-center justify-between p-4 glass rounded-xl border border-slate-700/50 hover:border-purple-500/50 transition-all duration-300 cursor-pointer relative overflow-hidden">
                                    <div className="absolute inset-0 bg-gradient-to-r from-purple-500/0 to-purple-500/0 group-hover/item:from-purple-500/10 group-hover/item:to-transparent transition-all duration-300" />
                                    <div className="flex items-center space-x-3 relative z-10">
                                        <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30 flex items-center justify-center group-hover/item:scale-110 transition-transform duration-300">
                                            <ShieldAlert className="text-purple-400" size={20} />
                                        </div>
                                        <div>
                                            <h4 className="text-white font-semibold group-hover/item:text-purple-400 transition-colors">Security Logs</h4>
                                            <p className="text-xs text-slate-400">Review blocked payloads</p>
                                        </div>
                                    </div>
                                    <ArrowRight size={18} className="text-slate-500 group-hover/item:text-purple-400 group-hover/item:translate-x-1 transition-all relative z-10" />
                                </a>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Providers Table */}
                <div className="mb-10 relative z-10">
                    <DataTable
                        title="Current Providers Activity"
                        columns={providerColumns}
                        data={providers?.slice(0, 5) || []}
                        delay={0.6}
                    />
                </div>
            </div>
        </DashboardLayout>
    )
}
