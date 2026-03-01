/**
 * UI Zustand store - Simplified
 * Manages only essential UI state (modals, sidebar)
 */

import { create } from 'zustand'

interface UIStoreState {
    sidebarOpen: boolean
    modals: {
        createProvider: boolean
        editProvider: boolean
        deleteProvider: boolean
    }
    openModal: (modal: keyof UIStoreState['modals']) => void
    closeModal: (modal: keyof UIStoreState['modals']) => void
    closeAllModals: () => void
    toggleSidebar: () => void
}

export const useUIStore = create<UIStoreState>((set) => ({
    sidebarOpen: true,
    modals: {
        createProvider: false,
        editProvider: false,
        deleteProvider: false,
    },

    openModal: (modal) =>
        set((state) => ({
            modals: { ...state.modals, [modal]: true },
        })),

    closeModal: (modal) =>
        set((state) => ({
            modals: { ...state.modals, [modal]: false },
        })),

    closeAllModals: () =>
        set({
            modals: {
                createProvider: false,
                editProvider: false,
                deleteProvider: false,
            },
        }),

    toggleSidebar: () =>
        set((state) => ({
            sidebarOpen: !state.sidebarOpen,
        })),
}))

export default useUIStore
