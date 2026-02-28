'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { useProviders, useDeleteProvider } from '@/hooks/useProviders'
import { useNotificationStore } from '@/store/useNotificationStore'

export default function ProvidersPage() {
    const { data: providers, isLoading, error } = useProviders()
    const deleteProvider = useDeleteProvider('')
    const [selectedProvider, setSelectedProvider] = useState<string | null>(null)

    const handleDelete = async (name: string) => {
        if (confirm(`Are you sure you want to delete provider "${name}"?`)) {
            try {
                await deleteProvider.mutateAsync()
            } catch (err) {
                console.error('Error deleting provider:', err)
            }
        }
    }

    return (
        <main className="min-h-screen bg-slate-900 p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-4xl font-bold text-white mb-2">Providers</h1>
                        <p className="text-slate-400">Manage your webhook providers</p>
                    </div>
                    <Link
                        href="/providers/create"
                        className="px-6 py-2 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition"
                    >
                        + Create Provider
                    </Link>
                </div>

                {/* Providers Table */}
                <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
                    {isLoading ? (
                        <div className="p-8 text-center text-slate-400">Loading providers...</div>
                    ) : error ? (
                        <div className="p-8 text-center text-red-400">Error loading providers</div>
                    ) : providers && providers.length > 0 ? (
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-slate-700 border-b border-slate-600">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-sm font-semibold text-white">Name</th>
                                        <th className="px-6 py-3 text-left text-sm font-semibold text-white">Forwarding URL</th>
                                        <th className="px-6 py-3 text-left text-sm font-semibold text-white">Status</th>
                                        <th className="px-6 py-3 text-left text-sm font-semibold text-white">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-700">
                                    {providers.map((provider: any) => (
                                        <tr key={provider.id} className="hover:bg-slate-700 transition">
                                            <td className="px-6 py-4 text-white font-semibold">{provider.name}</td>
                                            <td className="px-6 py-4 text-slate-300 text-sm truncate">{provider.forwarding_url}</td>
                                            <td className="px-6 py-4">
                                                <span className={`px-3 py-1 rounded text-sm font-semibold ${provider.is_active ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'}`}>
                                                    {provider.is_active ? 'Active' : 'Inactive'}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex gap-2">
                                                    <Link
                                                        href={`/providers/${provider.name}`}
                                                        className="px-3 py-1 bg-slate-600 text-white rounded text-sm hover:bg-slate-500 transition"
                                                    >
                                                        View
                                                    </Link>
                                                    <button
                                                        onClick={() => handleDelete(provider.name)}
                                                        className="px-3 py-1 bg-red-900 text-red-200 rounded text-sm hover:bg-red-800 transition"
                                                    >
                                                        Delete
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <div className="p-8 text-center text-slate-400">
                            <p className="mb-4">No providers found</p>
                            <Link
                                href="/providers/create"
                                className="inline-block px-6 py-2 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition"
                            >
                                Create Your First Provider
                            </Link>
                        </div>
                    )}
                </div>
            </div>
        </main>
    )
}
