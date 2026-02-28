'use client'

import React from 'react'
import { useSecurityLogs } from '@/hooks/useSecurityLogs'
import { formatDateTime, formatEventType, formatIPAddress } from '@/utils/formatters'

export default function SecurityLogsPage() {
    const { data: logs, isLoading, error } = useSecurityLogs()

    return (
        <main className="min-h-screen bg-slate-900 p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold text-white mb-2">Security Logs</h1>
                    <p className="text-slate-400">Monitor security events and threats</p>
                </div>

                {/* Logs Table */}
                <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
                    {isLoading ? (
                        <div className="p-8 text-center text-slate-400">Loading security logs...</div>
                    ) : error ? (
                        <div className="p-8 text-center text-red-400">Error loading security logs</div>
                    ) : logs && logs.length > 0 ? (
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-slate-700 border-b border-slate-600">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-sm font-semibold text-white">Event Type</th>
                                        <th className="px-6 py-3 text-left text-sm font-semibold text-white">Provider</th>
                                        <th className="px-6 py-3 text-left text-sm font-semibold text-white">Client IP</th>
                                        <th className="px-6 py-3 text-left text-sm font-semibold text-white">Request ID</th>
                                        <th className="px-6 py-3 text-left text-sm font-semibold text-white">Created At</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-700">
                                    {logs.map((log: any) => (
                                        <tr key={log.id} className="hover:bg-slate-700 transition">
                                            <td className="px-6 py-4">
                                                <span className="px-3 py-1 rounded text-sm font-semibold bg-red-900 text-red-200">
                                                    {formatEventType(log.event_type)}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-white font-semibold">{log.provider_name}</td>
                                            <td className="px-6 py-4 text-slate-300 text-sm font-mono">{formatIPAddress(log.ip_address, true)}</td>
                                            <td className="px-6 py-4 text-slate-300 text-sm font-mono truncate">{log.request_id || 'N/A'}</td>
                                            <td className="px-6 py-4 text-slate-300 text-sm">{formatDateTime(log.created_at)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <div className="p-8 text-center text-slate-400">
                            <p>No security events found</p>
                        </div>
                    )}
                </div>
            </div>
        </main>
    )
}
