'use client'

import { useEffect, useRef } from 'react'
import Link from 'next/link'
import gsap from 'gsap'

export default function Home() {
    const containerRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        const ctx = gsap.context(() => {
            // Animate hero text (staggered upward fade)
            gsap.from('.hero-reveal', {
                y: 50,
                opacity: 0,
                duration: 1.2,
                stagger: 0.15,
                ease: 'power4.out',
            })

            // Animate CTAs
            gsap.from('.hero-btn', {
                y: 30,
                opacity: 0,
                duration: 0.8,
                stagger: 0.1,
                ease: 'back.out(1.2)',
                delay: 0.4,
            })

            // Feature cards scale and fade
            gsap.from('.feature-card', {
                scale: 0.9,
                opacity: 0,
                y: 40,
                duration: 1,
                stagger: 0.15,
                ease: 'expo.out',
                delay: 0.6,
            })

            // Live traffic terminal slide up
            gsap.from('.live-terminal', {
                y: 100,
                opacity: 0,
                duration: 1.2,
                ease: 'power3.out',
                delay: 0.8,
            })

            // Terminal blinking cursor
            gsap.to('.blinking-cursor', {
                opacity: 0,
                duration: 0.5,
                repeat: -1,
                yoyo: true,
                ease: 'steps(1)'
            })

            // Orb slow pulse
            gsap.to('.ambient-orb-1', {
                scale: 1.1,
                opacity: 0.6,
                duration: 8,
                repeat: -1,
                yoyo: true,
                ease: 'sine.inOut',
            })
            gsap.to('.ambient-orb-2', {
                scale: 1.2,
                opacity: 0.5,
                duration: 10,
                repeat: -1,
                yoyo: true,
                ease: 'sine.inOut',
            })
        }, containerRef)

        return () => ctx.revert()
    }, [])

    return (
        <main className="min-h-screen bg-slate-950 overflow-hidden relative selection:bg-indigo-500/30 font-sans text-slate-200">
            {/* Ambient Lighting Orbs */}
            <div className="ambient-orb-1 absolute top-[-20%] left-[-10%] w-[50vw] h-[50vw] bg-indigo-600/20 blur-[140px] rounded-full pointer-events-none mix-blend-screen" />
            <div className="ambient-orb-2 absolute bottom-[-10%] right-[-10%] w-[60vw] h-[60vw] bg-purple-600/10 blur-[160px] rounded-full pointer-events-none mix-blend-screen" />
            <div className="absolute top-[40%] left-[50%] -translate-x-1/2 -translate-y-1/2 w-[80vw] h-[80vw] bg-cyan-900/10 blur-[180px] rounded-full pointer-events-none mix-blend-screen" />

            {/* Subtle Grid Background */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)] opacity-20 pointer-events-none" />

            <div className="container mx-auto px-6 py-24 md:py-32 relative z-10" ref={containerRef}>

                {/* Hero Section */}
                <div className="max-w-5xl mx-auto text-center mb-32">
                    <div className="hero-reveal inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/50 border border-slate-700 backdrop-blur-md mb-8">
                        <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></span>
                        <span className="text-sm font-medium text-slate-300">WebShield Gateway v2.0 is live</span>
                    </div>

                    <h1 className="hero-reveal text-6xl md:text-8xl font-black tracking-tight mb-8">
                        <span className="block text-white drop-shadow-xl">Enterprise Webhook</span>
                        <span className="block text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-cyan-400 to-purple-500 pb-2">
                            Infrastructure
                        </span>
                    </h1>

                    <p className="hero-reveal text-xl md:text-2xl text-slate-400 mb-12 font-light max-w-3xl mx-auto leading-relaxed">
                        Secure, reliable, and observable webhook delivery for modern engineering teams. Handle millions of events with bank-grade security out of the box.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-5 justify-center mt-12">
                        <Link
                            href="/dashboard"
                            className="hero-btn group px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl font-bold transition-all shadow-[0_0_40px_-10px_rgba(99,102,241,0.5)] border border-indigo-400/20 hover:scale-105 flex items-center justify-center gap-3"
                        >
                            Open Dashboard
                            <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                            </svg>
                        </Link>
                        <Link
                            href="/providers"
                            className="hero-btn px-8 py-4 bg-slate-800/30 hover:bg-slate-800/60 backdrop-blur-xl border border-slate-700 hover:border-slate-500 text-slate-200 rounded-xl font-semibold transition-all hover:scale-105"
                        >
                            View Docs
                        </Link>
                    </div>
                </div>

                {/* Features HexGrid (Asymmetrical) */}
                <div className="grid grid-cols-1 md:grid-cols-12 gap-6 mb-32">
                    {/* Security (Spans 5) */}
                    <div className="feature-card md:col-span-5 bg-slate-900/60 backdrop-blur-2xl border border-slate-700/50 p-10 rounded-3xl hover:border-purple-500/50 transition-colors group relative overflow-hidden">
                        <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-purple-500/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                        <div className="w-14 h-14 bg-purple-950/50 text-purple-400 border border-purple-500/20 rounded-2xl flex items-center justify-center mb-8 shadow-[0_0_30px_-5px_var(--tw-shadow-color)] shadow-purple-500/20">
                            <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                            </svg>
                        </div>
                        <h3 className="text-2xl font-bold text-white mb-4">Bank-Grade Security</h3>
                        <p className="text-slate-400 text-lg leading-relaxed font-light">End-to-end encryption with AES-256. Automated HMAC signatures for every payload ensure data integrity and prevent tampering.</p>
                    </div>

                    {/* Routing (Spans 7) */}
                    <div className="feature-card md:col-span-7 bg-slate-900/60 backdrop-blur-2xl border border-slate-700/50 p-10 rounded-3xl hover:border-cyan-500/50 transition-colors group relative overflow-hidden">
                        <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                        <div className="w-14 h-14 bg-cyan-950/50 text-cyan-400 border border-cyan-500/20 rounded-2xl flex items-center justify-center mb-8 shadow-[0_0_30px_-5px_var(--tw-shadow-color)] shadow-cyan-500/20">
                            <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                        </div>
                        <h3 className="text-2xl font-bold text-white mb-4">Intelligent Routing Mesh</h3>
                        <p className="text-slate-400 text-lg leading-relaxed font-light">Smart retry logic with exponential backoff. Our mesh network automatically reroutes traffic around outages to guarantee delivery at scale.</p>
                    </div>

                    {/* Observability (Spans 12 - Full Width layout) */}
                    <div className="feature-card md:col-span-12 bg-slate-900/60 backdrop-blur-2xl border border-slate-700/50 p-10 rounded-3xl hover:border-indigo-500/50 transition-colors group relative overflow-hidden flex flex-col md:flex-row gap-10 items-center">
                        <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-indigo-500/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                        <div className="flex-1">
                            <div className="w-14 h-14 bg-indigo-950/50 text-indigo-400 border border-indigo-500/20 rounded-2xl flex items-center justify-center mb-8 shadow-[0_0_30px_-5px_var(--tw-shadow-color)] shadow-indigo-500/20">
                                <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                </svg>
                            </div>
                            <h3 className="text-2xl font-bold text-white mb-4">Real-time Observability</h3>
                            <p className="text-slate-400 text-lg leading-relaxed font-light">Drill down into individual requests. Full payload inspection, replay capabilities, and comprehensive audit logs at your fingertips.</p>
                        </div>
                        <div className="flex-1 w-full bg-slate-950 rounded-xl border border-slate-800 p-6 font-mono text-sm leading-relaxed shadow-inner">
                            <div className="text-slate-500 mb-2">// Event stream connection established</div>
                            <div className="flex justify-between items-center py-1">
                                <span className="text-indigo-400">evt_1A2B3C...</span>
                                <span className="text-slate-300">stripe.payment_intent.succeeded</span>
                                <span className="px-2 py-0.5 bg-emerald-950 text-emerald-400 rounded text-xs border border-emerald-800">200 OK</span>
                            </div>
                            <div className="flex justify-between items-center py-1">
                                <span className="text-indigo-400">evt_9X8Y7Z...</span>
                                <span className="text-slate-300">github.push.main</span>
                                <span className="px-2 py-0.5 bg-emerald-950 text-emerald-400 rounded text-xs border border-emerald-800">200 OK</span>
                            </div>
                            <div className="flex justify-between items-center py-1">
                                <span className="text-indigo-400">evt_4D5E6F...</span>
                                <span className="text-slate-300">twilio.message.received</span>
                                <span className="px-2 py-0.5 bg-rose-950 text-rose-400 rounded text-xs border border-rose-800">401 Auth Error</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Simulated Live Traffic Terminal */}
                <div className="live-terminal max-w-5xl mx-auto rounded-2xl overflow-hidden border border-slate-700/50 shadow-2xl bg-[#0d1117] relative">
                    {/* Header Bar */}
                    <div className="bg-slate-800/80 backdrop-blur-md px-4 py-3 flex items-center gap-2 border-b border-slate-700/50">
                        <div className="flex gap-1.5">
                            <div className="w-3 h-3 rounded-full bg-rose-500/80"></div>
                            <div className="w-3 h-3 rounded-full bg-amber-500/80"></div>
                            <div className="w-3 h-3 rounded-full bg-emerald-500/80"></div>
                        </div>
                        <div className="mx-auto text-xs font-mono text-slate-400 flex items-center gap-2">
                            <svg className="w-3 h-3 text-emerald-400 animate-pulse" fill="currentColor" viewBox="0 0 20 20"><circle cx="10" cy="10" r="10" /></svg>
                            Live Traffic Feed: WebShield Edge
                        </div>
                    </div>
                    {/* Content */}
                    <div className="p-8 font-mono text-sm">
                        <div className="text-indigo-400 mb-4">$ tail -f /var/log/webshield/ingress.log</div>

                        <div className="space-y-3">
                            <div className="flex gap-4 opacity-70">
                                <span className="text-slate-500">14:02:11.041</span>
                                <span className="text-cyan-400">[info]</span>
                                <span className="text-slate-300">Connection established from 192.168.1.1</span>
                            </div>
                            <div className="flex gap-4">
                                <span className="text-slate-500">14:02:12.155</span>
                                <span className="text-emerald-400">[success]</span>
                                <span className="text-slate-300">Verified Payload | Signature: HMAC-SHA256 valid</span>
                            </div>
                            <div className="flex gap-4 opacity-80">
                                <span className="text-slate-500">14:02:12.189</span>
                                <span className="text-purple-400">[routing]</span>
                                <span className="text-slate-300">Forwarding to target: https://api.internal.corp/webhook</span>
                            </div>
                            <div className="flex gap-4">
                                <span className="text-slate-500">14:02:12.442</span>
                                <span className="text-emerald-400">[200 OK]</span>
                                <span className="text-slate-300">Delivery successful. Latency: 253ms</span>
                            </div>
                            <div className="flex gap-4">
                                <span className="text-slate-500">14:02:14.001</span>
                                <span className="text-slate-300 blinking-cursor">_</span>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </main>
    )
}
