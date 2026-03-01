'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useCreateProvider } from '@/hooks/useProviders'
import DashboardLayout from '@/components/layout/DashboardLayout'

export default function CreateProviderPage() {
    const router = useRouter()
    const createProvider = useCreateProvider()

    const [formData, setFormData] = useState({
        name: '',
        secret_key: '',
        forwarding_url: '',
        is_active: true,
    })

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value, type } = e.target
        setFormData((prev) => ({
            ...prev,
            [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
        }))
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()

        try {
            await createProvider.mutateAsync(formData)
            router.push('/providers')
        } catch (error) {
            console.error('Error creating provider:', error)
        }
    }

    return (
        <DashboardLayout>
            <div className="max-w-2xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <Link href="/providers" className="text-indigo-400 hover:text-indigo-300 mb-4 inline-block text-sm">
                        ← Back to Providers
                    </Link>
                    <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400 mb-2">Create Provider</h1>
                    <p className="text-slate-400">Add a new webhook provider to your gateway</p>
                </div>

                {/* Form */}
                <div className="bg-slate-800/80 backdrop-blur-sm rounded-xl border border-slate-700 p-8">
                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* Name */}
                        <div>
                            <label htmlFor="name" className="block text-sm font-semibold text-white mb-2">
                                Provider Name
                            </label>
                            <input
                                type="text"
                                id="name"
                                name="name"
                                value={formData.name}
                                onChange={handleChange}
                                placeholder="e.g., Stripe, GitHub, Twilio"
                                required
                                className="w-full px-4 py-2.5 bg-slate-900/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition"
                            />
                        </div>

                        {/* Secret Key */}
                        <div>
                            <label htmlFor="secret_key" className="block text-sm font-semibold text-white mb-2">
                                Secret Key (min 32 characters)
                            </label>
                            <input
                                type="password"
                                id="secret_key"
                                name="secret_key"
                                value={formData.secret_key}
                                onChange={handleChange}
                                placeholder="Enter a secure secret key"
                                required
                                minLength={32}
                                className="w-full px-4 py-2.5 bg-slate-900/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition"
                            />
                            <p className="text-xs text-slate-400 mt-1">Used for HMAC signature verification</p>
                        </div>

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
                                placeholder="https://your-api.example.com/webhooks"
                                required
                                className="w-full px-4 py-2.5 bg-slate-900/50 border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition"
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
                                disabled={createProvider.isPending}
                                className="flex-1 px-6 py-2.5 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-500 transition shadow-lg shadow-indigo-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {createProvider.isPending ? 'Creating...' : 'Create Provider'}
                            </button>
                            <Link
                                href="/providers"
                                className="flex-1 px-6 py-2.5 bg-slate-700 text-white rounded-lg font-semibold hover:bg-slate-600 transition text-center"
                            >
                                Cancel
                            </Link>
                        </div>
                    </form>
                </div>
            </div>
        </DashboardLayout>
    )
}

