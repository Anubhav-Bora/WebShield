'use client'

import { useEffect, useRef } from 'react'
import gsap from 'gsap'
import { XAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'

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
                <div className="glass rounded-xl p-4 border border-emerald-500/30 shadow-2xl bg-[#141419]/90 backdrop-blur-md">
                    <p className="text-slate-300 text-sm mb-2 font-medium">{label}</p>
                    <p className="text-white text-lg font-bold">
                        <span className="text-emerald-400">{payload[0].value}</span> requests
                    </p>
                </div>
            )
        }
        return null
    }

    // Calculate tick interval based on data length
    const tickInterval = Math.ceil(data.length / 12) // Show ~12 ticks max

    return (
        <div
            ref={containerRef}
            className="relative rounded-2xl p-6 border border-slate-700/50 hover:border-emerald-500/30 transition-all duration-500 group overflow-hidden bg-gradient-to-br from-slate-800/20 to-transparent"
        >
            <div className="relative z-10">
                <div className="mb-6">
                    <h2
                        ref={titleRef}
                        className="text-xl font-bold text-white flex items-center gap-3"
                    >
                        {title}
                    </h2>
                    <p className="text-sm text-slate-400 mt-2">Data points: {data.length}</p>
                </div>

                <ResponsiveContainer width="100%" height={300}>
                    <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                        <defs>
                            <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} vertical={false} />
                        <XAxis
                            dataKey={xAxisKey}
                            stroke="#64748b"
                            style={{ fontSize: '12px', fontWeight: 500 }}
                            tickLine={false}
                            axisLine={false}
                            dy={10}
                            interval={tickInterval - 1}
                        />
                        <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#475569', strokeWidth: 1, strokeDasharray: '4 4' }} />
                        <Area
                            type="monotone"
                            dataKey={dataKey}
                            stroke="#10b981"
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
