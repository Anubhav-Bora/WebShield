'use client'

export function StatCardSkeleton() {
    return (
        <div className="relative glass rounded-2xl p-6 border border-slate-700/50 overflow-hidden">
            {/* Shimmer effect */}
            <div className="absolute inset-0 shimmer" />

            <div className="relative z-10">
                <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                        <div className="h-4 bg-slate-700/50 rounded-md w-28 mb-3 animate-pulse"></div>
                        <div className="h-10 bg-slate-700/50 rounded-lg w-20 animate-pulse"></div>
                    </div>
                    <div className="w-14 h-14 bg-slate-700/50 rounded-xl animate-pulse"></div>
                </div>
                <div className="pt-3 border-t border-slate-700/50">
                    <div className="h-4 bg-slate-700/50 rounded-md w-32 animate-pulse"></div>
                </div>
            </div>
        </div>
    )
}
