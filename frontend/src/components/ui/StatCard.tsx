'use client'

import React, { useEffect, useRef } from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'
import gsap from 'gsap'

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
    const cardRef = useRef<HTMLDivElement>(null)
    const valueRef = useRef<HTMLParagraphElement>(null)
    const iconRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        if (!cardRef.current) return

        // Card entrance animation
        gsap.fromTo(
            cardRef.current,
            {
                opacity: 0,
                y: 30,
                scale: 0.95
            },
            {
                opacity: 1,
                y: 0,
                scale: 1,
                duration: 0.6,
                delay: delay,
                ease: 'power3.out'
            }
        )

        // Value counter animation
        if (valueRef.current && typeof value === 'number') {
            const counter = { val: 0 }
            gsap.to(counter, {
                val: value,
                duration: 1.5,
                delay: delay + 0.3,
                ease: 'power2.out',
                onUpdate: function () {
                    if (valueRef.current) {
                        valueRef.current.textContent = Math.floor(counter.val).toString()
                    }
                }
            })
        }

        // Icon float animation
        if (iconRef.current) {
            gsap.to(iconRef.current, {
                y: -5,
                duration: 2,
                repeat: -1,
                yoyo: true,
                ease: 'sine.inOut'
            })
        }
    }, [delay, value])

    const handleMouseEnter = () => {
        if (cardRef.current) {
            gsap.to(cardRef.current, {
                scale: 1.05,
                duration: 0.3,
                ease: 'power2.out'
            })
        }
    }

    const handleMouseLeave = () => {
        if (cardRef.current) {
            gsap.to(cardRef.current, {
                scale: 1,
                duration: 0.3,
                ease: 'power2.out'
            })
        }
    }

    return (
        <div
            ref={cardRef}
            className="relative glass rounded-2xl p-6 border border-slate-700/50 hover:border-indigo-500/50 transition-all duration-300 group cursor-pointer overflow-hidden"
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
        >
            {/* Gradient overlay on hover */}
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/0 via-purple-500/0 to-pink-500/0 group-hover:from-indigo-500/10 group-hover:via-purple-500/5 group-hover:to-pink-500/10 transition-all duration-500 rounded-2xl" />

            {/* Glow effect */}
            <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-2xl opacity-0 group-hover:opacity-20 blur-xl transition-opacity duration-500" />

            <div className="relative z-10">
                <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                        <p className="text-slate-400 text-sm font-medium tracking-wide uppercase mb-3">{title}</p>
                        <p
                            ref={valueRef}
                            className="text-white text-4xl font-bold tracking-tight bg-gradient-to-br from-white to-slate-300 bg-clip-text text-transparent"
                        >
                            {value}
                        </p>
                    </div>
                    <div
                        ref={iconRef}
                        className="p-3 rounded-xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border border-indigo-500/30 group-hover:border-indigo-400/50 transition-all duration-300"
                    >
                        <div className="text-indigo-400 group-hover:text-indigo-300 transition-colors">
                            {icon}
                        </div>
                    </div>
                </div>

                {trend && (
                    <div className="flex items-center gap-2 text-sm pt-3 border-t border-slate-700/50">
                        <div className={`p-1 rounded-md ${trendUp ? 'bg-emerald-500/10' : 'bg-rose-500/10'}`}>
                            {trendUp ? (
                                <TrendingUp size={14} className="text-emerald-400" />
                            ) : (
                                <TrendingDown size={14} className="text-rose-400" />
                            )}
                        </div>
                        <span className={`font-medium ${trendUp ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {trend}
                        </span>
                    </div>
                )}
            </div>
        </div>
    )
}
