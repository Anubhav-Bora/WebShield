'use client'

import React, { useEffect } from 'react'
import { X } from 'lucide-react'

interface FormModalProps {
    isOpen: boolean
    onClose: () => void
    title: string
    children: React.ReactNode
}

export function FormModal({ isOpen, onClose, title, children }: FormModalProps) {
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden'
        } else {
            document.body.style.overflow = 'unset'
        }
        return () => {
            document.body.style.overflow = 'unset'
        }
    }, [isOpen])

    if (!isOpen) return null

    return (
        <>
            {/* Backdrop */}
            <div
                onClick={onClose}
                className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm animate-fadeInUp"
                style={{
                    opacity: isOpen ? 1 : 0,
                    pointerEvents: isOpen ? 'auto' : 'none',
                    transition: 'opacity 0.3s ease-out'
                }}
            />
            
            {/* Modal */}
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
                <div
                    className="bg-slate-800 rounded-2xl w-full max-w-md shadow-2xl border border-slate-700 overflow-hidden pointer-events-auto animate-fadeInScale"
                    style={{
                        opacity: isOpen ? 1 : 0,
                        transform: isOpen ? 'scale(1)' : 'scale(0.95)',
                        transition: 'all 0.3s ease-out'
                    }}
                >
                    <div className="flex justify-between items-center p-6 border-b border-slate-700/50">
                        <h2 className="text-xl font-bold text-white">{title}</h2>
                        <button
                            onClick={onClose}
                            className="p-1 text-slate-400 hover:text-white hover:bg-slate-700 rounded-full transition-colors duration-200"
                        >
                            <X size={20} />
                        </button>
                    </div>
                    <div className="p-6">
                        {children}
                    </div>
                </div>
            </div>
        </>
    )
}
