'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useProvider, useUpdateProvider, useDeleteProvider } from '@/hooks/useProviders'

export default function ProviderDetailPage({ params }: { params: { name: string } }) {
    const router = useRouter()
    const { data: provider, isLoading, error } = useProvider(params.name)
    const updateProvider = useUpdateProvider(params.name)
    const deleteProvider = useDeleteProvider(params.name)

    const [isEditing, setIsEditing] = useState(false)
    const [formData, setFormData] = useState({
        forwarding_url: '',
        is_active: true,
    })

    React.useEffect(() => {
        if (provider) {
            setFormData({
                forwarding_url: provider.forwarding_url,
                is_active: provider.is_active,
            })
        }
    }, [provider])

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value, type } = e.target
        setFormData((prev) => ({
            ...prev,
            [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
        }))
    }

    const handleUpdate = async (e: React.FormEvent) => {
        e.preventDefault()
        try {
            await updateProvider.mutateAsync(formData)
            setIsEditing(false)
        } catch (error) {
            console.error('Error updating provider:', error)
        }
    }

    const handleDelete = async () => {
        if (confirm(`Are you sure you want to delete provider "${params.name}"?`)) {
            try {
                await deleteProvider.mutateAsync()
                router.push('/providers')
            } catch (error) {
                console.error('Error deleting provider:', error)
            }
        }
    }

    if (isLoading) {
        return (
            <main className="min-h-screen bg-slate-900 p-8">
                <div className="max-w-2xl mx-auto text-center text-slate-400">
                    Loading provider...
                </div>
            </main>
        )
    }

    if (error || !provider) {
        return (
            <main className="min-h-screen bg-slate-900 p-8">
                <div className="max-w-2xl mx-auto">
                    <Link href="/providers" className="text-indigo-400 hover:text-indigo-300 mb-4 inline-block">
                        ← Back to Providers
                    </Link>
                    <div className="text-center text-red-400">
                        Error loading provider
                    </div>
                </div>
            </main>
        )
    }

    return (
        <main className="min-h-screen bg-slate-900 p-8">
            <div className="max-w-2xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <Link href="/providers" className="text-indigo-400 hover:text-indigo-300 mb-4 inline-block">
                        ← Back to Providers
                    </Link>
                    <h1 className="text-4xl font-bold text-white mb-2">{provider.name}</h1>
                    <p className="text-slate-400">Manage provider settings</p>
                </div>

                {/* Provider Details */}
                <div className="bg-slate-800 rounded-lg border border-slate-700 p-8">
                    {!isEditing ? (
                        <div className="space-y-6">
                            {/* Name */}
                            <div>
                                <label className="block text-sm font-semibold text-slate-400 mb-2">
                                    Provider Name
                                </label>
                                <p className="text-white text-lg">{provider.name}</p>
                            </div>

                            {/* Forwarding URL */}
                            <div>
                                <label className="block text-sm font-semibold text-slate-400 mb-2">
                                    Forwarding URL
                                </label>
                                <p className="text-white break-all">{provider.forwarding_url}</p>
                            </div>

                            {/* Status */}
                            <div>
                                <label className="block text-sm font-semibold text-slate-400 mb-2">
                                    Status
                                </label>
                                <span className={`px-3 py-1 rounded text-sm font-semibold ${provider.is_active ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'}`}>
                                    {provider.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </div>

                            {/* Actions */}
                            <div className="flex gap-4 pt-4">
                                <button
                                    onClick={() => setIsEditing(true)}
                                    className="flex-1 px-6 py-2 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition"
                                >
                                    Edit
                                </button>
                                <button
                                    onClick={handleDelete}
                                    disabled={deleteProvider.isPending}
                                    className="flex-1 px-6 py-2 bg-red-900 text-red-200 rounded-lg font-semibold hover:bg-red-800 transition disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {deleteProvider.isPending ? 'Deleting...' : 'Delete'}
                                </button>
                            </div>
                        </div>
                    ) : (
                        <form onSubmit={handleUpdate} className="space-y-6">
                            {/* Forwarding URL */}
                            <div>
                                <label htmlFor="forwarding_url" className="block text-sm font-semibold text-white mb-2">
                                    Forwarding URL
                                </label>
                                <input
                                    type="url"
                                    id="forwarding_url"
                                    name="forwarding_url"
                                    value={formData.forwarding_url}
                                    onChange={handleChange}
                                    required
                                    className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                                />
                            </div>

                            {/* Active Status */}
                            <div className="flex items-center">
                                <input
                                    type="checkbox"
                                    id="is_active"
                                    name="is_active"
                                    checked={formData.is_active}
                                    onChange={handleChange}
                                    className="w-4 h-4 rounded border-slate-600 text-indigo-600 focus:ring-indigo-500"
                                />
                                <label htmlFor="is_active" className="ml-3 text-sm font-semibold text-white">
                                    Active
                                </label>
                            </div>

                            {/* Buttons */}
                            <div className="flex gap-4 pt-4">
                                <button
                                    type="submit"
                                    disabled={updateProvider.isPending}
                                    className="flex-1 px-6 py-2 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {updateProvider.isPending ? 'Saving...' : 'Save Changes'}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setIsEditing(false)}
                                    className="flex-1 px-6 py-2 bg-slate-700 text-white rounded-lg font-semibold hover:bg-slate-600 transition"
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    )}
                </div>
            </div>
        </main>
    )
}
