'use client'

import React from 'react'

export function StatCardSkeleton() {
    return (
        <div
            className="relative rounded-2xl p-6 border border-slate-700/50 transition-all duration-300 overflow-hidden"
            style={{
                backdropFilter: 'blur(12px)',
                WebkitBackdropFilter: 'blur(12px)',
                backgroundColor: 'rgba(20, 20, 25, 0.4)',
                background: 'linear-gradient(135deg, rgba(71, 85, 105, 0.1) 0%, rgba(30, 41, 59, 0.05) 100%)'
            }}
        >
            <div className="relative z-10 flex flex-col h-full justify-between space-y-4 animate-pulse">
                <div>
                    <div className="flex justify-between items-start mb-2">
                        {/* Title skeleton */}
                        <div className="h-4 w-24 bg-slate-700/50 rounded"/>
                        {/* Icon skeleton */}
                        <div className="h-5 w-5 bg-slate-700/40 rounded"/>
                    </div>

                    <div className="flex items-end justify-between mt-4">
                        {/* Value skeleton */}
                        <div className="h-10 w-32 bg-slate-700/50 rounded"/>
                        
                        {/* Trend skeleton */}
                        <div className="flex items-center gap-1 space-x-1">
                            <div className="h-5 w-12 bg-slate-700/40 rounded"/>
                            <div className="h-4 w-4 bg-slate-700/40 rounded"/>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
