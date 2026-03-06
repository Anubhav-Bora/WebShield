'use client'

import React from 'react'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { AnimatedChart } from '@/components/ui/AnimatedChart'
import { StatCard } from '@/components/ui/StatCard'
import gsap from 'gsap'
import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '@/store/useAuthStore'

interface WebhookAnalytics {
    hour: string
    total_webhooks: number
    successful_webhooks: number
    failed_webhooks: number
    success_rate: number
    avg_latency_ms: number
    p95_latency_ms: number
    p99_latency_ms: number
}

export default function AnalyticsPage() {
    const token = useAuthStore((state) => state.token)
    const [isHydrated, setIsHydrated] = React.useState(false)

    React.useEffect(() => {
        setIsHydrated(true)
        gsap.from('.page-header', { opacity: 0, x: -20, duration: 0.5, ease: 'power2.out' })
        gsap.from('.stat-cards', { opacity: 0, y: 20, duration: 0.6, ease: 'power2.out', delay: 0.1 })
        gsap.from('.chart-container', { opacity: 0, y: 20, duration: 0.6, ease: 'power2.out', delay: 0.2 })
    }, [])

    const { data: summary = null, isLoading: summaryLoading } = useQuery({
        queryKey: ['analyticsSummary'],
        queryFn: async () => {
            const response = await fetch('http://localhost:8000/admin/analytics/summary?days=7', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            if (!response.ok) throw new Error('Failed to fetch analytics summary')
            return response.json()
        },
        enabled: !!token && isHydrated,
        staleTime: 30000,
        refetchOnMount: 'always'
    })

    const { data: webhookAnalytics = [], isLoading: analyticsLoading } = useQuery({
        queryKey: ['webhookAnalytics'],
        queryFn: async () => {
            const response = await fetch('http://localhost:8000/admin/analytics/webhooks?days=7', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            if (!response.ok) throw new Error('Failed to fetch webhook analytics')
            return response.json()
        },
        enabled: !!token && isHydrated,
        staleTime: 30000,
        refetchOnMount: 'always'
    })

    const chartData = React.useMemo(() => {
        if (!webhookAnalytics || webhookAnalytics.length === 0) return []

        return webhookAnalytics
            .sort((a: WebhookAnalytics, b: WebhookAnalytics) =>
                new Date(a.hour).getTime() - new Date(b.hour).getTime()
            )
            .map((item: WebhookAnalytics) => ({
                time: new Date(item.hour).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
                successful: item.successful_webhooks,
                failed: item.failed_webhooks,
                latency: Math.round(item.avg_latency_ms)
            }))
    }, [webhookAnalytics])

    if (!isHydrated) {
        return (
            <DashboardLayout>
                <div className="max-w-7xl mx-auto">
                    <div className="mb-8 page-header">
                        <div>
                            <h1 className="text-4xl font-extrabold text-white mb-2">Analytics</h1>
                            <p className="text-slate-300 text-lg">Webhook performance and metrics</p>
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
                        <h1 className="text-4xl font-extrabold text-white mb-2">Analytics</h1>
                        <p className="text-slate-300 text-lg">Webhook performance and metrics (Last 7 days)</p>
                    </div>
                </div>

                {/* Summary Stats */}
                {summaryLoading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8 stat-cards">
                        {[1, 2, 3, 4].map((i) => (
                            <div key={i} className="h-32 bg-slate-800/50 rounded-xl animate-pulse" />
                        ))}
                    </div>
                ) : summary ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8 stat-cards">
                        <StatCard
                            title="Total Webhooks"
                            value={String(summary.total_webhooks)}
                            trend="+0%"
                            icon="📊"
                        />
                        <StatCard
                            title="Success Rate"
                            value={`${summary.avg_success_rate.toFixed(1)}%`}
                            trend="+0%"
                            icon="✓"
                        />
                        <StatCard
                            title="Avg Latency"
                            value={`${summary.avg_latency_ms.toFixed(0)}ms`}
                            trend="+0%"
                            icon="⚡"
                        />
                        <StatCard
                            title="P99 Latency"
                            value={`${summary.p99_latency_ms.toFixed(0)}ms`}
                            trend="+0%"
                            icon="📈"
                        />
                    </div>
                ) : null}

                {/* Charts */}
                {analyticsLoading ? (
                    <div className="bg-slate-800/80 backdrop-blur-sm rounded-xl border border-slate-700 p-8 chart-container">
                        <div className="h-96 flex items-center justify-center text-slate-400 animate-pulse">
                            Loading analytics data...
                        </div>
                    </div>
                ) : chartData.length > 0 ? (
                    <div className="bg-slate-800/80 backdrop-blur-sm rounded-xl border border-slate-700 p-8 chart-container">
                        <h2 className="text-xl font-bold text-white mb-6">Webhook Success/Failure Trend</h2>
                        <AnimatedChart
                            title="Webhook Metrics"
                            data={chartData}
                            dataKey="successful"
                            xAxisKey="time"
                        />
                    </div>
                ) : (
                    <div className="bg-slate-800/80 backdrop-blur-sm rounded-xl border border-slate-700 p-12 text-center chart-container">
                        <p className="text-slate-400 mb-6 text-lg">No analytics data available</p>
                    </div>
                )}

                {/* Detailed Metrics */}
                {summary && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
                        <div className="bg-slate-800/80 backdrop-blur-sm rounded-xl border border-slate-700 p-6">
                            <h3 className="text-lg font-bold text-white mb-4">Success Metrics</h3>
                            <div className="space-y-3">
                                <div className="flex justify-between items-center">
                                    <span className="text-slate-300">Total Successful</span>
                                    <span className="text-white font-semibold">{summary.total_successful}</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-slate-300">Total Failed</span>
                                    <span className="text-rose-400 font-semibold">{summary.total_failed}</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-slate-300">Success Rate</span>
                                    <span className="text-emerald-400 font-semibold">{summary.avg_success_rate.toFixed(2)}%</span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-slate-800/80 backdrop-blur-sm rounded-xl border border-slate-700 p-6">
                            <h3 className="text-lg font-bold text-white mb-4">Latency Metrics</h3>
                            <div className="space-y-3">
                                <div className="flex justify-between items-center">
                                    <span className="text-slate-300">Average Latency</span>
                                    <span className="text-white font-semibold">{summary.avg_latency_ms.toFixed(2)}ms</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-slate-300">P95 Latency</span>
                                    <span className="text-white font-semibold">{summary.p95_latency_ms.toFixed(2)}ms</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-slate-300">P99 Latency</span>
                                    <span className="text-white font-semibold">{summary.p99_latency_ms.toFixed(2)}ms</span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </DashboardLayout>
    )
}
