'use client'

import React from 'react'
import Link from 'next/link'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { DataTable } from '@/components/ui/DataTable'
import gsap from 'gsap'
import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '@/store/useAuthStore'

interface AuditLog {
    id: string
    user_id: string
    action: string
    resource_type: string
    resource_id: string
    ip_address: string
    user_agent: string
    changes: Record<string, any>
    status: string
    error_message: string
    created_at: string
}

export default function AuditLogsPage() {
    const token = useAuthStore((state) => state.token)
    const [isHydrated, setIsHydrated] = React.useState(false)

    React.useEffect(() => {
        setIsHydrated(true)
        gsap.from('.page-header', { opacity: 0, x: -20, duration: 0.5, ease: 'power2.out' })
    }, [])

    const { data: auditLogs = [], isLoading } = useQuery({
        queryKey: ['auditLogs'],
        queryFn: async () => {
            const response = await fetch('http://localhost:8000/admin/audit-logs?limit=100', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
            if (!response.ok) throw new Error('Failed to fetch audit logs')
            return response.json()
        },
        enabled: !!token && isHydrated,
        staleTime: 30000,
        refetchOnMount: 'always'
    })

    const columns = [
        {
            key: 'action',
            title: 'Action',
            render: (log: AuditLog) => (
                <span className="text-white font-semibold capitalize">{log.action.replace(/_/g, ' ')}</span>
            )
        },
        {
            key: 'resource_type',
            title: 'Resource',
            render: (log: AuditLog) => (
                <span className="text-slate-300 capitalize">{log.resource_type}</span>
            )
        },
        {
            key: 'status',
            title: 'Status',
            render: (log: AuditLog) => (
                <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${log.status === 'success'
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                    }`}>
                    {log.status}
                </span>
            )
        },
        {
            key: 'ip_address',
            title: 'IP Address',
            render: (log: AuditLog) => (
                <span className="text-slate-400 text-sm font-mono">{log.ip_address}</span>
            )
        },
        {
            key: 'created_at',
            title: 'Timestamp',
            render: (log: AuditLog) => (
                <span className="text-slate-400 text-sm">
                    {new Date(log.created_at).toLocaleString()}
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
                            <h1 className="text-4xl font-extrabold text-white mb-2">Audit Logs</h1>
                            <p className="text-slate-300 text-lg">Track all admin actions and changes</p>
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
                        <h1 className="text-4xl font-extrabold text-white mb-2">Audit Logs</h1>
                        <p className="text-slate-300 text-lg">Track all admin actions and changes</p>
                    </div>
                </div>

                {isLoading ? (
                    <div className="p-8 text-center text-slate-400 animate-pulse">Loading audit logs...</div>
                ) : auditLogs.length > 0 ? (
                    <DataTable columns={columns} data={auditLogs} delay={0.2} />
                ) : (
                    <div className="bg-slate-800/80 backdrop-blur-sm rounded-xl border border-slate-700 p-12 text-center">
                        <p className="text-slate-400 mb-6 text-lg">No audit logs found</p>
                    </div>
                )}
            </div>
        </DashboardLayout>
    )
}
