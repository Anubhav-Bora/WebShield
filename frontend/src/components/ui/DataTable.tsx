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
            className="rounded-2xl border border-white/5 overflow-hidden bg-[#141419]/90 backdrop-blur-xl"
        >
            {title && (
                <div ref={titleRef} className="px-6 py-5 border-b border-white/5 relative z-10 flex justify-between items-center">
                    <div>
                        <h2 className="text-xl font-bold text-white mb-1">
                            {title}
                        </h2>
                        <p className="text-sm text-slate-500">Lorem ipsum dolor sit amet, consectetur adipis.</p>
                    </div>
                    <button className="px-4 py-2 rounded-lg bg-white/5 text-slate-300 text-sm hover:bg-white/10 transition-colors border border-white/5 flex items-center gap-2">
                        This Month
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
                    </button>
                </div>
            )}

            <div className="overflow-x-auto relative z-10 p-2">
                <table className="w-full border-collapse">
                    <thead className="hidden">
                        <tr>
                            {columns.map((column) => (
                                <th key={column.key}>{column.title}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {data.length > 0 ? (
                            data.map((item, index) => (
                                <tr
                                    key={index}
                                    ref={(el) => { rowsRef.current[index] = el }}
                                    className="hover:bg-white/5 transition-all duration-300 group/row"
                                >
                                    {columns.map((column) => (
                                        <td
                                            key={column.key}
                                            className="px-6 py-4 text-sm text-slate-300 group-hover/row:text-white transition-colors border-none"
                                        >
                                            {column.render ? column.render(item) : item[column.key]}
                                        </td>
                                    ))}
                                    <td className="px-6 py-4 text-right">
                                        <button className="text-slate-500 hover:text-white">•••</button>
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td
                                    colSpan={columns.length + 1}
                                    className="px-6 py-12 text-center text-slate-400"
                                >
                                    <div className="flex flex-col items-center gap-3">
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
