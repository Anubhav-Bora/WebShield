'use client'

import React from 'react'
import { useSecurityLogs } from '@/hooks/useSecurityLogs'
import { formatDateTime, formatEventType, formatIPAddress } from '@/utils/formatters'
import { DataTable } from '@/components/ui/DataTable'
import DashboardLayout from '@/components/layout/DashboardLayout'
import gsap from 'gsap'
import { Download, FileText } from 'lucide-react'
import { exportSecurityLogsPDF, exportSecurityLogsCSV } from '@/services/export'
import { useNotificationStore } from '@/store/useNotificationStore'

export default function SecurityLogsPage() {
    const { data: logs, isLoading, error } = useSecurityLogs()
    const { success, error: showError } = useNotificationStore()

    React.useEffect(() => {
        gsap.from('.page-header', { opacity: 0, x: -20, duration: 0.5, ease: 'power2.out' })
    }, [])

    const handleExportPDF = async () => {
        try {
            await exportSecurityLogsPDF()
            success('Export successful', 'Security logs exported as PDF')
        } catch (err) {
            showError('Export failed', 'Failed to export security logs as PDF')
        }
    }

    const handleExportCSV = async () => {
        try {
            await exportSecurityLogsCSV()
            success('Export successful', 'Security logs exported as CSV')
        } catch (err) {
            showError('Export failed', 'Failed to export security logs as CSV')
        }
    }

    const columns = [
        {
            key: 'event_type', title: 'Event Type', render: (l: any) => (
                <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                    {formatEventType(l.event_type)}
                </span>
            )
        },
        { key: 'provider_name', title: 'Provider', render: (l: any) => <span className="text-white font-medium">{l.provider_name}</span> },
        { key: 'ip_address', title: 'Client IP', render: (l: any) => <span className="font-mono text-cyan-400 text-sm">{formatIPAddress(l.ip_address, true)}</span> },
        { key: 'request_id', title: 'Request ID', render: (l: any) => <span className="font-mono text-slate-400 text-xs truncate max-w-[150px] inline-block">{l.request_id || 'N/A'}</span> },
        { key: 'created_at', title: 'Created At', render: (l: any) => <span className="text-slate-300">{formatDateTime(l.created_at)}</span> }
    ]

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto">
                <div className="mb-8 page-header">
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <h1 className="text-4xl font-extrabold text-white mb-2">Security Logs</h1>
                            <p className="text-slate-300 text-lg">Monitor security events and threats</p>
                        </div>
                        <div className="flex gap-3">
                            <button
                                onClick={handleExportPDF}
                                className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold transition whitespace-nowrap"
                            >
                                <FileText size={18} />
                                PDF
                            </button>
                            <button
                                onClick={handleExportCSV}
                                className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-semibold transition whitespace-nowrap"
                            >
                                <Download size={18} />
                                CSV
                            </button>
                        </div>
                    </div>
                </div>

                {isLoading ? (
                    <div className="p-8 text-center text-slate-400 animate-pulse">Loading security logs...</div>
                ) : error ? (
                    <div className="p-8 text-center text-rose-400">Error loading security logs</div>
                ) : (
                    <DataTable
                        columns={columns}
                        data={logs || []}
                        delay={0.2}
                    />
                )}
            </div>
        </DashboardLayout>
    )
}

