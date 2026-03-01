import React from 'react'
import { Providers } from './providers'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import '../styles/globals.css'

export const metadata = {
    title: 'Webhook Gateway Dashboard',
    description: 'Professional webhook gateway management dashboard',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body>
                <ErrorBoundary>
                    <Providers>{children}</Providers>
                </ErrorBoundary>
            </body>
        </html>
    )
}
