'use client'

import React, { useEffect, useRef } from 'react'
import gsap from 'gsap'

interface Column {
    key: string
    title: string
    render?: (item: any) => React.ReactNode
}

interface DataTableProps {
    title?: string
    columns: Column[]
    data: any[]
    delay?: number
}

export function DataTable({ title, columns, data, delay = 0 }: DataTableProps) {
    const containerRef = useRef<HTMLDivElement>(null)
    const titleRef = useRef<HTMLDivElement>(null)
    const rowsRef = useRef<(HTMLTableRowElement | null)[]>([])

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
                '-=0.6'
            )
        }

        // Animate rows
        rowsRef.current.forEach((row, index) => {
            if (row) {
                gsap.fromTo(
                    row,
                    { opacity: 0, x: -20 },
                    {
                        opacity: 1,
                        x: 0,
                        duration: 0.5,
                        delay: delay + 0.2 + (index * 0.05),
                        ease: 'power2.out'
                    }
                )
            }
        })
    }, [delay, data])

    return (
        <div
            ref={containerRef}
            className="glass rounded-2xl border border-slate-700/50 overflow-hidden hover:border-indigo-500/30 transition-all duration-500 group"
        >
            {/* Gradient overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/0 via-purple-500/0 to-transparent group-hover:from-indigo-500/5 group-hover:via-purple-500/5 transition-all duration-700 rounded-2xl pointer-events-none" />

            {title && (
                <div ref={titleRef} className="px-6 py-5 border-b border-slate-700/50 relative z-10">
                    <h2 className="text-xl font-bold text-white flex items-center gap-3">
                        <span className="w-1 h-6 bg-gradient-to-b from-indigo-500 to-purple-500 rounded-full"></span>
                        {title}
                    </h2>
                </div>
            )}

            <div className="overflow-x-auto relative z-10">
                <table className="w-full">
                    <thead className="bg-slate-900/30 border-b border-slate-700/50">
                        <tr>
                            {columns.map((column) => (
                                <th
                                    key={column.key}
                                    className="px-6 py-4 text-left text-xs font-bold text-slate-400 uppercase tracking-wider"
                                >
                                    {column.title}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700/30">
                        {data.length > 0 ? (
                            data.map((item, index) => (
                                <tr
                                    key={index}
                                    ref={(el) => { rowsRef.current[index] = el }}
                                    className="hover:bg-slate-700/30 transition-all duration-300 cursor-pointer group/row"
                                >
                                    {columns.map((column) => (
                                        <td
                                            key={column.key}
                                            className="px-6 py-4 text-sm text-slate-300 group-hover/row:text-white transition-colors"
                                        >
                                            {column.render ? column.render(item) : item[column.key]}
                                        </td>
                                    ))}
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td
                                    colSpan={columns.length}
                                    className="px-6 py-12 text-center text-slate-400"
                                >
                                    <div className="flex flex-col items-center gap-3">
                                        <div className="w-16 h-16 rounded-full bg-slate-700/30 flex items-center justify-center">
                                            <svg className="w-8 h-8 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                                            </svg>
                                        </div>
                                        <p className="text-sm font-medium">No data available</p>
                                    </div>
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
