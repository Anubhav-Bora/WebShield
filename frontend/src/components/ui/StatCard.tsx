'use client'

import React from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface StatCardProps {
    title: string
    value: string | number
    icon: React.ReactNode
    trend?: string
    trendUp?: boolean
    delay?: number
}

export function StatCard({ 
    title, 
    value, 
    icon, 
    trend, 
    trendUp = true, 
    delay = 0 
}: StatCardProps) {
    // CSS animation delay in seconds
    const animationDelay = `${delay}s`

    return (
        <div
            className="bg-slate-800/80 backdrop-blur-md rounded-xl p-6 border border-slate-700 hover:border-indigo-500 transition-all duration-300 group cursor-pointer animate-fadeInUp hover:scale-105"
            style={{ animationDelay }}
            onMouseEnter={(e) => {
                e.currentTarget.style.boxShadow = '0 20px 40px rgba(99, 102, 241, 0.2)'
            }}
            onMouseLeave={(e) => {
                e.currentTarget.style.boxShadow = 'none'
            }}
        >
            <div className="flex items-start justify-between mb-4">
                <div>
                    <p className="text-slate-400 text-sm font-medium">{title}</p>
                    <p className="text-white text-3xl font-bold mt-2">{value}</p>
                </div>
                <div className="text-indigo-500 group-hover:scale-110 transition-transform duration-300">
                    {icon}
                </div>
            </div>

            {trend && (
                <div className="flex items-center gap-2 text-sm">
                    {trendUp ? (
                        <TrendingUp size={16} className="text-emerald-400" />
                    ) : (
                        <TrendingDown size={16} className="text-rose-400" />
                    )}
                    <span className={trendUp ? 'text-emerald-400' : 'text-rose-400'}>
                        {trend}
                    </span>
                </div>
            )}
        </div>
    )
}
