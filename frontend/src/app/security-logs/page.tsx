'use client'

import React, { useState } from 'react'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { formatDateTime, formatEventType, formatIPAddress } from '@/utils/formatters'
import { useSecurityLogs } from '@/hooks/useSecurityLogs'
import useWebSocket from '@/hooks/useWebSocket'
import gsap from 'gsap'
import { Download, FileText, ChevronDown, ChevronUp, AlertTriangle, Globe, Clock } from 'lucide-react'
import { exportSecurityLogsPDF, exportSecurityLogsCSV } from '@/services/export'
import { useNotificationStore } from '@/store/useNotificationStore'

export default function SecurityLogsPage() {
    const { data: logs, isLoading, error } = useSecurityLogs()
    const { isConnected } = useWebSocket()
    const { success, error: showError } = useNotificationStore()
    const [expandedId, setExpandedId] = useState<string | null>(null)

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

    const getEventColor = (eventType: string) => {
        const colors: Record<string, string> = {
            'invalid_signature': 'rose',
            'rate_limit_exceeded': 'amber',
            'replay_attempt': 'orange',
            'timestamp_too_old': 'yellow',
            'payload_too_large': 'red',
            'payload_tampering_detected': 'rose'
        }
        return colors[eventType] || 'slate'
    }

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto">
                <div className="mb-12 page-header">
                    <div className="flex justify-between items-start gap-6">
                        <div>
                            <h1 className="text-5xl font-black text-white mb-3">Security Logs</h1>
                            <p className="text-slate-400 text-lg flex items-center gap-2">
                                Monitor and analyze security events in real-time
                                {isConnected && (
                                    <span className="ml-2 inline-flex items-center gap-1 px-2 py-1 bg-emerald-500/10 text-emerald-400 text-xs rounded-full border border-emerald-500/20">
                                        <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
                                        Live
                                    </span>
                                )}
                            </p>
                        </div>
                        <div className="flex gap-3 flex-shrink-0">
                            <button
                                onClick={handleExportPDF}
                                className="flex items-center gap-2 px-4 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold transition-all duration-200 hover:shadow-lg hover:shadow-indigo-500/30"
                            >
                                <FileText size={18} />
                                <span className="hidden sm:inline">PDF</span>
                            </button>
                            <button
                                onClick={handleExportCSV}
                                className="flex items-center gap-2 px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-semibold transition-all duration-200 hover:shadow-lg hover:shadow-slate-500/20"
                            >
                                <Download size={18} />
                                <span className="hidden sm:inline">CSV</span>
                            </button>
                        </div>
                    </div>
                </div>

                {isLoading ? (
                    <div className="flex items-center justify-center py-20">
                        <div className="text-center">
                            <div className="w-12 h-12 rounded-full border-4 border-slate-700 border-t-indigo-500 animate-spin mx-auto mb-4"></div>
                            <p className="text-slate-400">Loading security logs...</p>
                        </div>
                    </div>
                ) : error ? (
                    <div className="bg-rose-500/10 border border-rose-500/20 rounded-xl p-6 text-center">
                        <p className="text-rose-400 font-semibold">Error loading security logs</p>
                    </div>
                ) : logs && logs.length > 0 ? (
                    <div className="space-y-4">
                        {logs.map((log: any, idx: number) => {
                            const color = getEventColor(log.event_type)
                            const colorMap: Record<string, { bg: string; border: string; text: string; icon: string }> = {
                                'rose': { bg: 'bg-rose-500/10', border: 'border-rose-500/20', text: 'text-rose-400', icon: 'text-rose-400' },
                                'amber': { bg: 'bg-amber-500/10', border: 'border-amber-500/20', text: 'text-amber-400', icon: 'text-amber-400' },
                                'orange': { bg: 'bg-orange-500/10', border: 'border-orange-500/20', text: 'text-orange-400', icon: 'text-orange-400' },
                                'yellow': { bg: 'bg-yellow-500/10', border: 'border-yellow-500/20', text: 'text-yellow-400', icon: 'text-yellow-400' },
                                'red': { bg: 'bg-red-500/10', border: 'border-red-500/20', text: 'text-red-400', icon: 'text-red-400' },
                                'slate': { bg: 'bg-slate-500/10', border: 'border-slate-500/20', text: 'text-slate-400', icon: 'text-slate-400' }
                            }
                            const colors = colorMap[color]

                            return (
                                <div
                                    key={log.id}
                                    className="group rounded-xl border border-slate-700/50 bg-gradient-to-br from-slate-800/50 to-slate-900/30 backdrop-blur-sm overflow-hidden hover:border-slate-600/50 transition-all duration-300 hover:shadow-lg hover:shadow-slate-500/5"
                                    style={{
                                        animation: `slideIn 0.5s ease-out ${idx * 0.05}s both`
                                    }}
                                >
                                    {/* Header Row */}
                                    <button
                                        onClick={() => setExpandedId(expandedId === log.id ? null : log.id)}
                                        className="w-full px-6 py-5 flex items-center justify-between hover:bg-slate-700/20 transition-colors"
                                    >
                                        <div className="flex items-center gap-4 flex-1 text-left min-w-0">
                                            {/* Event Icon */}
                                            <div className={`flex-shrink-0 w-10 h-10 rounded-lg ${colors.bg} border ${colors.border} flex items-center justify-center`}>
                                                <AlertTriangle className={`w-5 h-5 ${colors.icon}`} />
                                            </div>

                                            {/* Event Type Badge */}
                                            <div className="flex-shrink-0">
                                                <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-bold ${colors.bg} ${colors.text} border ${colors.border}`}>
                                                    {formatEventType(log.event_type)}
                                                </span>
                                            </div>

                                            {/* Provider */}
                                            <div className="flex-shrink-0 hidden sm:block">
                                                <span className="text-white font-semibold text-sm">{log.provider_name}</span>
                                            </div>

                                            {/* IP Address */}
                                            <div className="flex items-center gap-2 text-slate-400 text-sm flex-shrink-0">
                                                <Globe className="w-4 h-4" />
                                                <span className="font-mono text-xs">{formatIPAddress(log.ip_address, true)}</span>
                                            </div>

                                            {/* Timestamp */}
                                            <div className="flex items-center gap-2 text-slate-400 text-sm flex-shrink-0">
                                                <Clock className="w-4 h-4" />
                                                <span className="hidden md:inline text-xs">{formatDateTime(log.created_at)}</span>
                                            </div>
                                        </div>

                                        {/* Chevron */}
                                        <div className="flex-shrink-0 ml-4">
                                            {expandedId === log.id ? (
                                                <ChevronUp size={22} className="text-indigo-400 transition-transform" />
                                            ) : (
                                                <ChevronDown size={22} className="text-slate-500 group-hover:text-slate-400 transition-all" />
                                            )}
                                        </div>
                                    </button>

                                    {/* Expanded Content */}
                                    {expandedId === log.id && (
                                        <div className="border-t border-slate-700/50 px-6 py-8 space-y-8 bg-slate-900/40">
                                            {/* Event Details */}
                                            <div>
                                                <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                                                    <div className="w-1 h-4 bg-indigo-500 rounded-full"></div>
                                                    Event Details
                                                </h3>
                                                <div className="bg-slate-950/60 rounded-lg p-4 border border-slate-700/50 overflow-x-auto max-h-96 overflow-y-auto">
                                                    <pre className="text-slate-300 text-xs font-mono whitespace-pre-wrap break-words leading-relaxed">
                                                        {JSON.stringify(log.details, null, 2)}
                                                    </pre>
                                                </div>
                                            </div>

                                            {/* Details Grid */}
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                {/* Event Type */}
                                                <div className="bg-slate-950/40 rounded-lg p-4 border border-slate-700/30">
                                                    <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">Event Type</label>
                                                    <code className="text-sm font-mono text-slate-200">{log.event_type}</code>
                                                </div>

                                                {/* Provider */}
                                                <div className="bg-slate-950/40 rounded-lg p-4 border border-slate-700/30">
                                                    <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">Provider</label>
                                                    <span className="text-sm font-semibold text-white">{log.provider_name}</span>
                                                </div>

                                                {/* Client IP */}
                                                <div className="bg-slate-950/40 rounded-lg p-4 border border-slate-700/30">
                                                    <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">Client IP</label>
                                                    <code className="text-sm font-mono text-cyan-400">{log.ip_address}</code>
                                                </div>

                                                {/* Request ID */}
                                                <div className="bg-slate-950/40 rounded-lg p-4 border border-slate-700/30">
                                                    <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">Request ID</label>
                                                    <code className="text-sm font-mono text-slate-200 break-all">{log.request_id || 'N/A'}</code>
                                                </div>

                                                {/* Timestamp */}
                                                <div className="bg-slate-950/40 rounded-lg p-4 border border-slate-700/30 md:col-span-2">
                                                    <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 block">Timestamp</label>
                                                    <span className="text-sm text-slate-200">{formatDateTime(log.created_at)}</span>
                                                </div>
                                            </div>

                                            {/* Alert Banner */}
                                            <div className={`${colors.bg} rounded-lg p-4 border ${colors.border}`}>
                                                <div className="flex items-start gap-3">
                                                    <AlertTriangle className={`w-5 h-5 ${colors.icon} flex-shrink-0 mt-0.5`} />
                                                    <div>
                                                        <h4 className={`text-sm font-bold ${colors.text} mb-1`}>Security Event Detected</h4>
                                                        <p className={`text-xs ${colors.text}/80`}>This event has been logged and monitored. Review the details above for more information.</p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )
                        })}
                    </div>
                ) : (
                    <div className="text-center py-20">
                        <div className="w-16 h-16 rounded-full bg-slate-800/50 flex items-center justify-center mx-auto mb-4">
                            <AlertTriangle className="w-8 h-8 text-slate-600" />
                        </div>
                        <p className="text-slate-400 text-lg">No security events found</p>
                        <p className="text-slate-500 text-sm mt-2">Your system is secure</p>
                    </div>
                )}
            </div>

            <style jsx>{`
                @keyframes slideIn {
                    from {
                        opacity: 0;
                        transform: translateY(10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
            `}</style>
        </DashboardLayout>
    )
}
