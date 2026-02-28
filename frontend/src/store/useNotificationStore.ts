/**
 * Notification Zustand store
 * Manages toast notifications and alerts
 */

import { create } from 'zustand'
import { Notification } from '@/types'

interface NotificationStoreState {
    // State
    notifications: Notification[]

    // Actions
    addNotification: (notification: Omit<Notification, 'id'>) => string
    removeNotification: (id: string) => void
    clearNotifications: () => void

    // Convenience methods
    success: (title: string, message: string, duration?: number) => string
    error: (title: string, message: string, duration?: number) => string
    warning: (title: string, message: string, duration?: number) => string
    info: (title: string, message: string, duration?: number) => string
}

export const useNotificationStore = create<NotificationStoreState>((set: any) => ({
    notifications: [],

    addNotification: (notification: Omit<Notification, 'id'>) => {
        const id = `notification-${Date.now()}-${Math.random()}`
        set((state: NotificationStoreState) => ({
            notifications: [
                ...state.notifications,
                {
                    ...notification,
                    id,
                    duration: notification.duration || 5000,
                },
            ],
        }))

        // Auto-remove notification after duration
        if (notification.duration !== 0) {
            setTimeout(() => {
                set((state: NotificationStoreState) => ({
                    notifications: state.notifications.filter((n: Notification) => n.id !== id),
                }))
            }, notification.duration || 5000)
        }

        return id
    },

    removeNotification: (id: string) =>
        set((state: NotificationStoreState) => ({
            notifications: state.notifications.filter((n: Notification) => n.id !== id),
        })),

    clearNotifications: () => set({ notifications: [] }),

    success: (title: string, message: string, duration?: number) => {
        const id = `notification-${Date.now()}-${Math.random()}`
        const notification: Notification = {
            id,
            type: 'success',
            title,
            message,
            duration: duration || 5000,
        }
        set((state: NotificationStoreState) => ({
            notifications: [...state.notifications, notification],
        }))

        if (duration !== 0) {
            setTimeout(() => {
                set((state: NotificationStoreState) => ({
                    notifications: state.notifications.filter((n: Notification) => n.id !== id),
                }))
            }, duration || 5000)
        }

        return id
    },

    error: (title: string, message: string, duration?: number) => {
        const id = `notification-${Date.now()}-${Math.random()}`
        const notification: Notification = {
            id,
            type: 'error',
            title,
            message,
            duration: duration || 5000,
        }
        set((state: NotificationStoreState) => ({
            notifications: [...state.notifications, notification],
        }))

        if (duration !== 0) {
            setTimeout(() => {
                set((state: NotificationStoreState) => ({
                    notifications: state.notifications.filter((n: Notification) => n.id !== id),
                }))
            }, duration || 5000)
        }

        return id
    },

    warning: (title: string, message: string, duration?: number) => {
        const id = `notification-${Date.now()}-${Math.random()}`
        const notification: Notification = {
            id,
            type: 'warning',
            title,
            message,
            duration: duration || 5000,
        }
        set((state: NotificationStoreState) => ({
            notifications: [...state.notifications, notification],
        }))

        if (duration !== 0) {
            setTimeout(() => {
                set((state: NotificationStoreState) => ({
                    notifications: state.notifications.filter((n: Notification) => n.id !== id),
                }))
            }, duration || 5000)
        }

        return id
    },

    info: (title: string, message: string, duration?: number) => {
        const id = `notification-${Date.now()}-${Math.random()}`
        const notification: Notification = {
            id,
            type: 'info',
            title,
            message,
            duration: duration || 5000,
        }
        set((state: NotificationStoreState) => ({
            notifications: [...state.notifications, notification],
        }))

        if (duration !== 0) {
            setTimeout(() => {
                set((state: NotificationStoreState) => ({
                    notifications: state.notifications.filter((n: Notification) => n.id !== id),
                }))
            }, duration || 5000)
        }

        return id
    },
}))

export default useNotificationStore
