'use client'

import { Bell, User, LogOut, Search } from 'lucide-react'
import { useAuthStore } from '@/store/useAuthStore'
import { useRouter } from 'next/navigation'
import { useNotificationStore } from '@/store/useNotificationStore'

export function Header() {
    const { user, clearAuth } = useAuthStore()
    const router = useRouter()
    const { info } = useNotificationStore()

    const handleLogout = () => {
        clearAuth()
        info('Logged out', 'You have been logged out successfully')
        router.push('/login')
    }

    return (
        <header className="sticky top-0 z-30 bg-[#0d0d12]/80 backdrop-blur-md border-b border-white/5">
            <div className="h-20 px-8 flex items-center justify-between">
                <div className="flex items-center gap-3 bg-white/5 border border-white/5 rounded-full px-4 py-2 w-96 transition-colors focus-within:border-white/10 focus-within:bg-white/10">
                    <Search size={18} className="text-slate-400" />
                    <input
                        type="text"
                        placeholder="Search..."
                        className="bg-transparent border-none outline-none text-sm text-white w-full placeholder:text-slate-500"
                    />
                </div>

                <div className="flex items-center gap-6">
                    <button className="relative p-2 text-slate-400 hover:text-white transition-colors bg-white/5 rounded-full">
                        <Bell size={18} />
                        <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-emerald-500 rounded-full shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
                    </button>

                    <div className="flex items-center gap-4 pl-6 border-l border-white/10">
                        <div className="flex items-center gap-3">
                            <div className="text-right hidden md:block">
                                <p className="text-sm font-semibold text-white">{user?.full_name || user?.username || 'User'}</p>
                                <p className="text-xs text-slate-500">User</p>
                            </div>
                            <div className="w-10 h-10 rounded-full bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center">
                                <User size={18} className="text-indigo-400" />
                            </div>
                            <button
                                onClick={handleLogout}
                                className="p-2 text-slate-400 hover:text-rose-400 transition-colors rounded-full hover:bg-white/5"
                                title="Logout"
                            >
                                <LogOut size={18} />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </header>
    )
}
