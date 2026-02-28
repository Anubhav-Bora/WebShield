'use client'

import React from 'react'
import Link from 'next/link'

export default function Home() {
    return (
        <main className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
            <div className="container mx-auto px-4 py-20">
                <div className="text-center">
                    <h1 className="text-5xl font-bold text-white mb-4">
                        Webhook Gateway Dashboard
                    </h1>
                    <p className="text-xl text-slate-300 mb-8">
                        Professional webhook management with HMAC verification, rate limiting, and replay protection
                    </p>

                    <div className="flex gap-4 justify-center mb-12">
                        <Link
                            href="/dashboard"
                            className="px-8 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition"
                        >
                            Go to Dashboard
                        </Link>
                        <Link
                            href="/providers"
                            className="px-8 py-3 bg-slate-700 text-white rounded-lg font-semibold hover:bg-slate-600 transition"
                        >
                            Manage Providers
                        </Link>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16">
                        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                            <h3 className="text-lg font-semibold text-white mb-2">Secure</h3>
                            <p className="text-slate-400">HMAC signature verification and replay protection</p>
                        </div>
                        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                            <h3 className="text-lg font-semibold text-white mb-2">Reliable</h3>
                            <p className="text-slate-400">Rate limiting and automatic retry mechanisms</p>
                        </div>
                        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                            <h3 className="text-lg font-semibold text-white mb-2">Observable</h3>
                            <p className="text-slate-400">Comprehensive security logs and monitoring</p>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    )
}
