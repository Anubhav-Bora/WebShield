'use client'

import React, { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'

interface AnimatedChartProps {
    title: string
    data: any[]
    dataKey: string
    xAxisKey: string
    delay?: number
}

export function AnimatedChart({ title, data, dataKey, xAxisKey, delay = 0 }: AnimatedChartProps) {
    const containerRef = useRef<HTMLDivElement>(null)
    const titleRef = useRef<HTMLHeadingElement>(null)

    useEffect(() => {
        if (!containerRef.current) return

        const tl = gsap.timeline()

        tl.fromTo(
            containerRef.current,
            { opacity: 0, y: 40, scale: 0.95 },
            { opacity: 1, y: 0, scale: 1, duration: 0.8, delay, ease: 'power3.out' }
        )

        if (titleRef.current) {
            tl.fromTo(
                titleRef.current,
                { opacity: 0, x: -20 },
                { opacity: 1, x: 0, duration: 0.5, ease: 'power2.out' },
                '-=0.5'
            )
        }
    }, [delay])

    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            return (
                <div className="glass rounded-xl p-4 border border-indigo-500/30 shadow-2xl">
                    <p className="text-slate-300 text-sm mb-2 font-medium">{label}</p>
                    <p className="text-white text-lg font-bold">
                        <span className="text-indigo-400">{payload[0].value}</span> requests
                    </p>
                </div>
            )
        }
        return null
    }

    return (
        <div
            ref={containerRef}
            className="relative glass rounded-2xl p-6 border border-slate-700/50 hover:border-indigo-500/30 transition-all duration-500 group overflow-hidden"
        >
            {/* Gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/0 via-purple-500/0 to-transparent group-hover:from-indigo-500/5 group-hover:via-purple-500/5 transition-all duration-700 rounded-2xl" />

            {/* Glow effect */}
            <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-2xl opacity-0 group-hover:opacity-10 blur-2xl transition-opacity duration-700" />

            <div className="relative z-10">
                <h2
                    ref={titleRef}
                    className="text-xl font-bold text-white mb-6 flex items-center gap-3"
                >
                    <span className="w-1 h-6 bg-gradient-to-b from-indigo-500 to-purple-500 rounded-full"></span>
                    {title}
                </h2>

                <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={data}>
                        <defs>
                            <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
                        <XAxis
                            dataKey={xAxisKey}
                            stroke="#94a3b8"
                            style={{ fontSize: '12px', fontWeight: 500 }}
                            tickLine={false}
                        />
                        <YAxis
                            stroke="#94a3b8"
                            style={{ fontSize: '12px', fontWeight: 500 }}
                            tickLine={false}
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <Area
                            type="monotone"
                            dataKey={dataKey}
                            stroke="#6366f1"
                            strokeWidth={3}
                            fill="url(#colorGradient)"
                            isAnimationActive={true}
                            animationDuration={1500}
                            animationEasing="ease-out"
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    )
}
