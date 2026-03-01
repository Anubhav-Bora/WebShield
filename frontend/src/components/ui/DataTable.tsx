'use client'

import React from 'react'

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
    const animationDelay = `${delay}s`

    return (
        <div
            className="bg-slate-800/80 backdrop-blur-md rounded-xl border border-slate-700 overflow-hidden animate-fadeInUp"
            style={{ animationDelay }}
        >
            {title && (
                <div className="px-6 py-4 border-b border-slate-700">
                    <h2 className="text-lg font-bold text-white">{title}</h2>
                </div>
            )}

            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead className="bg-slate-900/50 border-b border-slate-700">
                        <tr>
                            {columns.map((column) => (
                                <th
                                    key={column.key}
                                    className="px-6 py-4 text-left text-sm font-semibold text-slate-300"
                                >
                                    {column.title}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700">
                        {data.length > 0 ? (
                            data.map((item, index) => (
                                <tr
                                    key={index}
                                    className="hover:bg-slate-700/50 transition-colors animate-fadeInUp"
                                    style={{ 
                                        animationDelay: `${delay + (index * 0.05)}s`
                                    }}
                                >
                                    {columns.map((column) => (
                                        <td 
                                            key={column.key} 
                                            className="px-6 py-4 text-sm text-slate-300"
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
                                    className="px-6 py-8 text-center text-slate-400"
                                >
                                    No data available
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
