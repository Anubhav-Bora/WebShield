'use client'

export function StatCardSkeleton() {
    return (
        <div className="bg-slate-800/80 backdrop-blur-md rounded-xl p-6 border border-slate-700 animate-pulse">
            <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                    <div className="h-4 bg-slate-700 rounded w-24 mb-3"></div>
                    <div className="h-8 bg-slate-700 rounded w-16"></div>
                </div>
                <div className="w-6 h-6 bg-slate-700 rounded"></div>
            </div>
            <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-slate-700 rounded"></div>
                <div className="h-4 bg-slate-700 rounded w-20"></div>
            </div>
        </div>
    )
}
