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
    const { data: providers = [], isLoading: providersLoading } = useProviders()
    const { data: webhookStats, isLoading: statsLoading } = useWebhookStats()
    const { data: securityStats, isLoading: securityLoading } = useSecurityStats()
    const { data: webhookEvents = [], isLoading: eventsLoading } = useWebhookEvents(undefined, 100, 0)

    // Check if any data is loading - show all skeletons or all cards
    const isAnyLoading = providersLoading || statsLoading || securityLoading || eventsLoading

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
            <div className="dashboard-container max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8 relative z-10">
                    <h1 className="page-title text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400 mb-2">
                        Gateway Overview
                    </h1>
                    <p className="page-subtitle text-slate-400 text-lg">Real-time webhook monitoring and analytics</p>
                </div>

                {/* Stats Grid - Show all skeletons or all cards together */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
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
                                icon={<CheckCircle size={24} className="text-emerald-400" />}
                                trend="Stable"
                                trendUp={true}
                                delay={0.2}
                            />
                            <StatCard
                                title="Security Events"
                                value={securityStats?.total_events || 0}
                                icon={<ShieldAlert size={24} className="text-rose-400" />}
                                trend="-5 threats blocked"
                                trendUp={true}
                                delay={0.3}
                            />
                        </>
                    )}
                </div>

                {/* Main Content Area */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
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
                    <div className="bg-slate-800/80 backdrop-blur-md rounded-xl p-6 border border-slate-700 h-[420px] flex flex-col animate-fadeInUpLg">
                        <h2 className="text-xl font-bold text-white mb-6">Quick Actions</h2>
                        <div className="space-y-4 flex-1">
                            <a href="/providers" className="group flex items-center justify-between p-4 bg-slate-900/50 rounded-lg border border-slate-700 hover:border-indigo-500 hover:bg-slate-800 transition-all cursor-pointer">
                                <div className="flex items-center space-x-3">
                                    <div className="w-10 h-10 rounded-full bg-indigo-500/20 flex items-center justify-center">
                                        <Package className="text-indigo-400" size={20} />
                                    </div>
                                    <div>
                                        <h4 className="text-white font-medium group-hover:text-indigo-400 transition-colors">Manage Providers</h4>
                                        <p className="text-xs text-slate-400">Add or edit endpoints</p>
                                    </div>
                                </div>
                                <ArrowRight size={18} className="text-slate-500 group-hover:text-indigo-400 transition-colors group-hover:translate-x-1" />
                            </a>

                            <a href="/webhooks" className="group flex items-center justify-between p-4 bg-slate-900/50 rounded-lg border border-slate-700 hover:border-cyan-500 hover:bg-slate-800 transition-all cursor-pointer">
                                <div className="flex items-center space-x-3">
                                    <div className="w-10 h-10 rounded-full bg-cyan-500/20 flex items-center justify-center">
                                        <LinkIcon className="text-cyan-400" size={20} />
                                    </div>
                                    <div>
                                        <h4 className="text-white font-medium group-hover:text-cyan-400 transition-colors">View Webhooks</h4>
                                        <p className="text-xs text-slate-400">Check delivery status</p>
                                    </div>
                                </div>
                                <ArrowRight size={18} className="text-slate-500 group-hover:text-cyan-400 transition-colors group-hover:translate-x-1" />
                            </a>

                            <a href="/security-logs" className="group flex items-center justify-between p-4 bg-slate-900/50 rounded-lg border border-slate-700 hover:border-purple-500 hover:bg-slate-800 transition-all cursor-pointer">
                                <div className="flex items-center space-x-3">
                                    <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                                        <ShieldAlert className="text-purple-400" size={20} />
                                    </div>
                                    <div>
                                        <h4 className="text-white font-medium group-hover:text-purple-400 transition-colors">Security Logs</h4>
                                        <p className="text-xs text-slate-400">Review blocked payloads</p>
                                    </div>
                                </div>
                                <ArrowRight size={18} className="text-slate-500 group-hover:text-purple-400 transition-colors group-hover:translate-x-1" />
                            </a>
                        </div>
                    </div>
                </div>

                {/* Providers Table */}
                <div className="mb-10">
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
