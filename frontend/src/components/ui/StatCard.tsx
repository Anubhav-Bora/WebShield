'use client'

import React, { useEffect, useRef } from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'
import gsap from 'gsap'

export type StatCardTheme = 'emerald' | 'blue' | 'dark'

interface StatCardProps {
    title: string
    value: string | number
    icon?: React.ReactNode
    trend?: string
    trendUp?: boolean
    delay?: number
    colorTheme?: StatCardTheme
}

export function StatCard({
    title,
    value,
    icon,
    trend,
    trendUp = true,
    delay = 0,
    colorTheme = 'dark'
}: StatCardProps) {
    const cardRef = useRef<HTMLDivElement>(null)
    const valueRef = useRef<HTMLParagraphElement>(null)

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
    }, [delay, value])

    const handleMouseEnter = () => {
        if (cardRef.current) {
            gsap.to(cardRef.current, {
                y: -5,
                duration: 0.3,
                ease: 'power2.out'
            })
        }
    }

    const handleMouseLeave = () => {
        if (cardRef.current) {
            gsap.to(cardRef.current, {
                y: 0,
                duration: 0.3,
                ease: 'power2.out'
            })
        }
    }

    const getThemeStyles = () => {
        switch (colorTheme) {
            case 'emerald':
                return {
                    wrapper: 'bg-gradient-to-br from-emerald-500/20 via-emerald-900/10 to-transparent border-emerald-500/20',
                    text: 'text-emerald-50',
                    trend: 'text-emerald-400'
                }
            case 'blue':
                return {
                    wrapper: 'bg-gradient-to-br from-blue-500/20 via-blue-900/10 to-transparent border-blue-500/20',
                    text: 'text-blue-50',
                    trend: 'text-rose-400' // Using rose for negative trend as in image
                }
            case 'dark':
            default:
                return {
                    wrapper: 'bg-gradient-to-br from-slate-700/30 via-slate-800/10 to-transparent border-slate-700/50',
                    text: 'text-white',
                    trend: 'text-emerald-400'
                }
        }
    }

    const theme = getThemeStyles()

    return (
        <div
            ref={cardRef}
            className={`relative rounded-2xl p-6 border transition-all duration-300 group cursor-pointer overflow-hidden ${theme.wrapper}`}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            style={{
                backdropFilter: 'blur(12px)',
                WebkitBackdropFilter: 'blur(12px)',
                backgroundColor: 'rgba(20, 20, 25, 0.4)'
            }}
        >
            <div className="relative z-10 flex flex-col h-full justify-between">
                <div>
                    <div className="flex justify-between items-start mb-2">
                        <p className="text-slate-300 text-sm font-semibold tracking-wide uppercase">{title}</p>
                        {icon && (
                            <div className="text-slate-400 opacity-50">
                                {icon}
                            </div>
                        )}
                    </div>

                    <div className="flex items-end justify-between mt-4">
                        <p
                            ref={valueRef}
                            className={`text-4xl font-bold tracking-tight ${theme.text}`}
                        >
                            {typeof value === 'number' ? 0 : value}
                        </p>

                        {trend && (
                            <div className="flex items-center gap-1 text-sm font-medium pb-1">
                                <span className={theme.trend}>
                                    {trend}
                                </span>
                                {trendUp ? (
                                    <TrendingUp size={16} className={theme.trend} />
                                ) : (
                                    <TrendingDown size={16} className={theme.trend} />
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}
