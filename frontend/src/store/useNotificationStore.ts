/**
 * Notification Zustand store - Simplified
 * Manages toast notifications only
 */

import { create } from 'zustand'
import { Notification } from '@/types'

interface NotificationStoreState {
    notifications: Notification[]
    addNotification: (notification: Omit<Notification, 'id'>) => string
    removeNotification: (id: string) => void
    clearNotifications: () => void
    success: (title: string, message: string, duration?: number) => string
    error: (title: string, message: string, duration?: number) => string
    warning: (title: string, message: string, duration?: number) => string
    info: (title: string, message: string, duration?: number) => string
}

export const useNotificationStore = create<NotificationStoreState>((set) => ({
    notifications: [],

    addNotification: (notification) => {
        const id = `${Date.now()}-${Math.random()}`
        set((state) => ({
            notifications: [...state.notifications, { ...notification, id, duration: notification.duration || 5000 }],
        }))

        if (notification.duration !== 0) {
            setTimeout(() => {
                set((state) => ({
                    notifications: state.notifications.filter((n) => n.id !== id),
                }))
            }, notification.duration || 5000)
        }

        return id
    },

    removeNotification: (id) =>
        set((state) => ({
            notifications: state.notifications.filter((n) => n.id !== id),
        })),

    clearNotifications: () => set({ notifications: [] }),

    success: (title, message, duration) => {
        const id = `${Date.now()}-${Math.random()}`
        set((state) => ({
            notifications: [...state.notifications, { id, type: 'success', title, message, duration: duration || 5000 }],
        }))
        if (duration !== 0) {
            setTimeout(() => {
                set((state) => ({
                    notifications: state.notifications.filter((n) => n.id !== id),
                }))
            }, duration || 5000)
        }
        return id
    },

    error: (title, message, duration) => {
        const id = `${Date.now()}-${Math.random()}`
        set((state) => ({
            notifications: [...state.notifications, { id, type: 'error', title, message, duration: duration || 5000 }],
        }))
        if (duration !== 0) {
            setTimeout(() => {
                set((state) => ({
                    notifications: state.notifications.filter((n) => n.id !== id),
                }))
            }, duration || 5000)
        }
        return id
    },

    warning: (title, message, duration) => {
        const id = `${Date.now()}-${Math.random()}`
        set((state) => ({
            notifications: [...state.notifications, { id, type: 'warning', title, message, duration: duration || 5000 }],
        }))
        if (duration !== 0) {
            setTimeout(() => {
                set((state) => ({
                    notifications: state.notifications.filter((n) => n.id !== id),
                }))
            }, duration || 5000)
        }
        return id
    },

    info: (title, message, duration) => {
        const id = `${Date.now()}-${Math.random()}`
        set((state) => ({
            notifications: [...state.notifications, { id, type: 'info', title, message, duration: duration || 5000 }],
        }))
        if (duration !== 0) {
            setTimeout(() => {
                set((state) => ({
                    notifications: state.notifications.filter((n) => n.id !== id),
                }))
            }, duration || 5000)
        }
        return id
    },
}))

export default useNotificationStore
