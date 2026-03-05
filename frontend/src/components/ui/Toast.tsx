'use client'

import React, { useEffect } from 'react'
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react'
import { useNotificationStore } from '@/store/useNotificationStore'

export function ToastContainer() {
    const { notifications, removeNotification } = useNotificationStore()

    return (
        <div className="fixed top-4 right-4 z-50 space-y-3 max-w-md">
            {notifications.map((notification) => (
                <Toast
                    key={notification.id}
                    {...notification}
                    onClose={() => removeNotification(notification.id)}
                />
            ))}
        </div>
    )
}

interface ToastProps {
    id: string
    type: 'success' | 'error' | 'info' | 'warning'
    title: string
    message?: string
    duration?: number
    onClose: () => void
}

function Toast({ id, type, title, message, duration = 5000, onClose }: ToastProps) {
    useEffect(() => {
        if (duration > 0) {
            const timer = setTimeout(() => {
                onClose()
            }, duration)
            return () => clearTimeout(timer)
        }
    }, [duration, onClose])

    const icons = {
        success: <CheckCircle className="w-5 h-5 text-emerald-400" />,
        error: <AlertCircle className="w-5 h-5 text-rose-400" />,
        info: <Info className="w-5 h-5 text-blue-400" />,
        warning: <AlertTriangle className="w-5 h-5 text-amber-400" />
    }

    const colors = {
        success: 'border-emerald-500/30 bg-emerald-500/10',
        error: 'border-rose-500/30 bg-rose-500/10',
        info: 'border-blue-500/30 bg-blue-500/10',
        warning: 'border-amber-500/30 bg-amber-500/10'
    }

    return (
        <div
            className={`glass rounded-xl border ${colors[type]} p-4 shadow-2xl animate-slideInRight flex items-start gap-3 min-w-[320px]`}
        >
            <div className="flex-shrink-0 mt-0.5">
                {icons[type]}
            </div>
            <div className="flex-1 min-w-0">
                <h4 className="text-white font-semibold text-sm mb-1">{title}</h4>
                {message && (
                    <p className="text-slate-300 text-sm">{message}</p>
                )}
            </div>
            <button
                onClick={onClose}
                className="flex-shrink-0 text-slate-400 hover:text-white transition-colors"
            >
                <X className="w-4 h-4" />
            </button>
        </div>
    )
}
