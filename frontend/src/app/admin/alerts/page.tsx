'use client'

import React from 'react'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { DataTable } from '@/components/ui/DataTable'
import gsap from 'gsap'
import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '@/store/useAuthStore'

interface AlertRule {
    id: string
    name: string
    condition: string
    threshold: number
    window_minutes: number
    is_active: boolean
    last_triggered_at: string
    created_at: string
}

interface AlertHistory {
    id: string
    alert_rule_id: string
    metric_value: number
    threshold: number
    message: string
    created_at: string
}

export default function AlertsPage() {
    const token = useAuthStore((state) => state.token)
    const [isHydrated, setIsHydrated] = React.useState(false)
    const [activeTab, setActiveTab] = React.useState<'rules' | 'history'>('rules')

    React.useEffect(() => {
        setIsHydrated(true)
        gsap.from('.page-header', { opacity: 0, x: -20, duration: 0.5, ease: 'power2.out' })
    }, [])

    const { data: alertRules = [], isLoading: rulesLoading } = useQuery({
        queryKey: ['alertRules'],
        queryFn: async () => {
            const response = await fetch('http://localhost:8000/admin/alert-rules', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            if (!response.ok) throw new Error('Failed to fetch alert rules')
            return response.json()
        },
        enabled: !!token && isHydrated,
        staleTime: 30000,
        refetchOnMount: 'always'
    })

    const { data: alertHistory = [], isLoading: historyLoading } = useQuery({
        queryKey: ['alertHistory'],
        queryFn: async () => {
            const response = await fetch('http://localhost:8000/admin/alert-history?limit=100&days=7', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            if (!response.ok) throw new Error('Failed to fetch alert history')
            return response.json()
        },
        enabled: !!token && isHydrated,
        staleTime: 30000,
        refetchOnMount: 'always'
    })

    const rulesColumns = [
        {
            key: 'name',
            title: 'Alert Name',
            render: (rule: AlertRule) => (
                <span className="text-white font-semibold">{rule.name}</span>
            )
        },
        {
            key: 'condition',
            title: 'Condition',
            render: (rule: AlertRule) => (
                <span className="text-slate-300 capitalize">{rule.condition.replace(/_/g, ' ')}</span>
            )
        },
        {
            key: 'threshold',
            title: 'Threshold',
            render: (rule: AlertRule) => (
                <span className="text-slate-300">{rule.threshold}</span>
            )
        },
        {
            key: 'window_minutes',
            title: 'Window',
            render: (rule: AlertRule) => (
                <span className="text-slate-300">{rule.window_minutes} min</span>
            )
        },
        {
            key: 'is_active',
            title: 'Status',
            render: (rule: AlertRule) => (
                <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${rule.is_active
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : 'bg-slate-500/10 text-slate-400 border border-slate-500/20'
                    }`}>
                    {rule.is_active ? 'Active' : 'Inactive'}
                </span>
            )
        },
        {
            key: 'last_triggered_at',
            title: 'Last Triggered',
            render: (rule: AlertRule) => (
                <span className="text-slate-400 text-sm">
                    {rule.last_triggered_at ? new Date(rule.last_triggered_at).toLocaleString() : 'Never'}
                </span>
            )
        }
    ]

    const historyColumns = [
        {
            key: 'message',
            title: 'Alert Message',
            render: (history: AlertHistory) => (
                <span className="text-white">{history.message}</span>
            )
        },
        {
            key: 'metric_value',
            title: 'Metric Value',
            render: (history: AlertHistory) => (
                <span className="text-slate-300 font-mono">{history.metric_value.toFixed(2)}</span>
            )
        },
        {
            key: 'threshold',
            title: 'Threshold',
            render: (history: AlertHistory) => (
                <span className="text-slate-300 font-mono">{history.threshold.toFixed(2)}</span>
            )
        },
        {
            key: 'created_at',
            title: 'Triggered At',
            render: (history: AlertHistory) => (
                <span className="text-slate-400 text-sm">
                    {new Date(history.created_at).toLocaleString()}
                </span>
            )
        }
    ]

    if (!isHydrated) {
        return (
            <DashboardLayout>
                <div className="max-w-7xl mx-auto">
                    <div className="mb-8 page-header">
                        <div>
                            <h1 className="text-4xl font-extrabold text-white mb-2">Alert Rules</h1>
                            <p className="text-slate-300 text-lg">Monitor and manage alert rules</p>
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
                        <h1 className="text-4xl font-extrabold text-white mb-2">Alert Rules</h1>
                        <p className="text-slate-300 text-lg">Monitor and manage alert rules</p>
                    </div>
                </div>

                {/* Tab Navigation */}
                <div className="flex gap-4 mb-8 border-b border-slate-700">
                    <button
                        onClick={() => setActiveTab('rules')}
                        className={`px-4 py-3 font-semibold transition-colors ${activeTab === 'rules'
                            ? 'text-white border-b-2 border-indigo-500'
                            : 'text-slate-400 hover:text-white'
                            }`}
                    >
                        Alert Rules ({alertRules.length})
                    </button>
                    <button
                        onClick={() => setActiveTab('history')}
                        className={`px-4 py-3 font-semibold transition-colors ${activeTab === 'history'
                            ? 'text-white border-b-2 border-indigo-500'
                            : 'text-slate-400 hover:text-white'
                            }`}
                    >
                        Alert History ({alertHistory.length})
                    </button>
                </div>

                {/* Rules Tab */}
                {activeTab === 'rules' && (
                    <>
                        {rulesLoading ? (
                            <div className="p-8 text-center text-slate-400 animate-pulse">Loading alert rules...</div>
                        ) : alertRules.length > 0 ? (
                            <DataTable columns={rulesColumns} data={alertRules} delay={0.2} />
                        ) : (
                            <div className="bg-slate-800/80 backdrop-blur-sm rounded-xl border border-slate-700 p-12 text-center">
                                <p className="text-slate-400 mb-6 text-lg">No alert rules configured</p>
                            </div>
                        )}
                    </>
                )}

                {/* History Tab */}
                {activeTab === 'history' && (
                    <>
                        {historyLoading ? (
                            <div className="p-8 text-center text-slate-400 animate-pulse">Loading alert history...</div>
                        ) : alertHistory.length > 0 ? (
                            <DataTable columns={historyColumns} data={alertHistory} delay={0.2} />
                        ) : (
                            <div className="bg-slate-800/80 backdrop-blur-sm rounded-xl border border-slate-700 p-12 text-center">
                                <p className="text-slate-400 mb-6 text-lg">No alerts triggered in the last 7 days</p>
                            </div>
                        )}
                    </>
                )}
            </div>
        </DashboardLayout>
    )
}
