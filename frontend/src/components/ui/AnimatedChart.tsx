'use client'

import React, { useEffect } from 'react'
import gsap from 'gsap'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface AnimatedChartProps {
    title: string
    data: any[]
    dataKey: string
    xAxisKey: string
    delay?: number
}

export function AnimatedChart({ title, data, dataKey, xAxisKey, delay = 0 }: AnimatedChartProps) {
    const containerRef = React.useRef(null)

    useEffect(() => {
        gsap.from(containerRef.current, {
            opacity: 0,
            y: 20,
            duration: 0.6,
            delay,
            ease: 'power2.out'
        })
    }, [delay])

    return (
        <div
            ref={containerRef}
            className="bg-slate-800/80 backdrop-blur-md rounded-xl p-6 border border-slate-700"
        >
            <h2 className="text-xl font-bold text-white mb-6">{title}</h2>
            <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey={xAxisKey} stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#1e293b',
                            border: '1px solid #334155',
                            borderRadius: '8px'
                        }}
                        labelStyle={{ color: '#f1f5f9' }}
                    />
                    <Line
                        type="monotone"
                        dataKey={dataKey}
                        stroke="#6366f1"
                        strokeWidth={2}
                        dot={false}
                        isAnimationActive={true}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    )
}
