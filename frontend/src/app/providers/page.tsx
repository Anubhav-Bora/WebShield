'use client'

import React from 'react'
import Link from 'next/link'
import { useProviders } from '@/hooks/useProviders'
import { DataTable } from '@/components/ui/DataTable'
import DashboardLayout from '@/components/layout/DashboardLayout'
import gsap from 'gsap'

export default function ProvidersPage() {
    const { data: providers, isLoading, error } = useProviders()

    React.useEffect(() => {
        gsap.from('.page-header', { opacity: 0, x: -20, duration: 0.5, ease: 'power2.out' })
    }, [])

    const handleDelete = async (name: string) => {
        if (confirm(`Are you sure you want to delete provider "${name}"?`)) {
            // Deletion is handled via the API service directly
            try {
                const { deleteProvider } = await import('@/services/providers')
                await deleteProvider(name)
                window.location.reload()
            } catch (err) {
                console.error('Error deleting provider:', err)
            }
        }
    }

    const columns = [
        { key: 'name', title: 'Name', render: (p: any) => <span className="text-white font-medium">{p.name}</span> },
        { key: 'forwarding_url', title: 'Forwarding URL', render: (p: any) => <span className="text-slate-300 text-sm truncate max-w-[300px] inline-block">{p.forwarding_url}</span> },
        {
            key: 'status', title: 'Status', render: (p: any) => (
                <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${p.is_active ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'}`}>
                    {p.is_active ? 'Active' : 'Inactive'}
                </span>
            )
        },
        {
            key: 'actions', title: 'Actions', render: (p: any) => (
                <div className="flex gap-2">
                    <Link
                        href={`/providers/${p.name}`}
                        className="px-3 py-1 bg-slate-700/50 text-white rounded text-sm hover:bg-slate-600 transition"
                    >
                        View
                    </Link>
                    <button
                        onClick={() => handleDelete(p.name)}
                        className="px-3 py-1 bg-rose-500/10 text-rose-400 border border-rose-500/20 rounded text-sm hover:bg-rose-500/20 transition"
                    >
                        Delete
                    </button>
                </div>
            )
        }
    ]

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto">
                <div className="flex justify-between items-center mb-8 page-header">
                    <div>
                        <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400 mb-2">Providers</h1>
                        <p className="text-slate-400 text-lg">Manage your webhook providers</p>
                    </div>
                    <Link
                        href="/providers/create"
                        className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-semibold shadow-lg shadow-indigo-500/20 transition-all hover:scale-105"
                    >
                        + Create Provider
                    </Link>
                </div>

                {isLoading ? (
                    <div className="p-8 text-center text-slate-400 animate-pulse">Loading providers...</div>
                ) : error ? (
                    <div className="p-8 text-center text-rose-400">Error loading providers</div>
                ) : providers && providers.length > 0 ? (
                    <DataTable
                        columns={columns}
                        data={providers}
                        delay={0.2}
                    />
                ) : (
                    <div className="bg-slate-800/80 backdrop-blur-sm rounded-xl border border-slate-700 p-12 text-center">
                        <p className="text-slate-400 mb-6 text-lg">No providers found</p>
                        <Link
                            href="/providers/create"
                            className="inline-block px-8 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-500 transition shadow-lg shadow-indigo-500/20 hover:scale-105"
                        >
                            Create Your First Provider
                        </Link>
                    </div>
                )}
            </div>
        </DashboardLayout>
    )
}

