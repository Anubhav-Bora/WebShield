/**
 * UI Zustand store
 * Manages UI state (modals, sidebars, etc.)
 */

import { create } from 'zustand'

interface UIStoreState {
    // Modal states
    modals: {
        createProvider: boolean
        editProvider: boolean
        deleteProvider: boolean
        testWebhook: boolean
        viewWebhookDetails: boolean
        viewSecurityLog: boolean
    }

    // Sidebar state
    sidebarOpen: boolean

    // Theme state
    theme: 'light' | 'dark'

    // Loading states
    isLoading: boolean
    loadingMessage: string

    // Actions
    openModal: (modal: keyof UIStoreState['modals']) => void
    closeModal: (modal: keyof UIStoreState['modals']) => void
    closeAllModals: () => void
    toggleSidebar: () => void
    setSidebarOpen: (open: boolean) => void
    setTheme: (theme: 'light' | 'dark') => void
    setLoading: (isLoading: boolean, message?: string) => void
    reset: () => void
}

const initialState = {
    modals: {
        createProvider: false,
        editProvider: false,
        deleteProvider: false,
        testWebhook: false,
        viewWebhookDetails: false,
        viewSecurityLog: false,
    },
    sidebarOpen: true,
    theme: 'dark' as const,
    isLoading: false,
    loadingMessage: '',
}

export const useUIStore = create<UIStoreState>((set: any) => ({
    ...initialState,

    openModal: (modal: keyof UIStoreState['modals']) =>
        set((state: UIStoreState) => ({
            modals: {
                ...state.modals,
                [modal]: true,
            },
        })),

    closeModal: (modal: keyof UIStoreState['modals']) =>
        set((state: UIStoreState) => ({
            modals: {
                ...state.modals,
                [modal]: false,
            },
        })),

    closeAllModals: () =>
        set({
            modals: {
                createProvider: false,
                editProvider: false,
                deleteProvider: false,
                testWebhook: false,
                viewWebhookDetails: false,
                viewSecurityLog: false,
            },
        }),

    toggleSidebar: () =>
        set((state: UIStoreState) => ({
            sidebarOpen: !state.sidebarOpen,
        })),

    setSidebarOpen: (open: boolean) => set({ sidebarOpen: open }),

    setTheme: (theme: 'light' | 'dark') => set({ theme }),

    setLoading: (isLoading: boolean, message = '') =>
        set({ isLoading, loadingMessage: message }),

    reset: () => set(initialState),
}))

export default useUIStore
