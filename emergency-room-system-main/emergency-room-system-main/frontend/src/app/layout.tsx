import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
// @ts-expect-error: no type declarations for side-effect CSS import
import './globals.css'
import Header from '@/components/layout/header'
import Providers from '@/components/layout/provider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Emergency Room Management System',
  description: 'Intelligent ER management with real-time patient tracking',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <div className="min-h-screen bg-gray-50">
            <Header />
            <main>{children}</main>
          </div>
        </Providers>
      </body>
    </html>
  )
}