'use client'

import { Bell, User, LogOut } from 'lucide-react'

export function Header() {
    return (
        <header className="sticky top-0 z-30 bg-slate-800/80 backdrop-blur-md border-b border-slate-700">
            <div className="h-16 px-8 flex items-center justify-between">
                {/* Left side - empty for now */}
                <div />

                {/* Right side - notifications and user menu */}
                <div className="flex items-center gap-4">
                    {/* Notifications */}
                    <button className="relative p-2 text-slate-400 hover:text-white transition-colors">
                        <Bell size={20} />
                        <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
                    </button>

                    {/* User Menu */}
                    <div className="flex items-center gap-3 pl-4 border-l border-slate-700">
                        <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center">
                            <User size={16} className="text-white" />
                        </div>
                        <button className="p-2 text-slate-400 hover:text-white transition-colors">
                            <LogOut size={18} />
                        </button>
                    </div>
                </div>
            </div>
        </header>
    )
}
