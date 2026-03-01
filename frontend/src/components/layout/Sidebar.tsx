'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, Package, Link as LinkIcon, ShieldAlert, Menu, X, ChevronLeft, ChevronRight } from 'lucide-react'

interface SidebarProps {
  isOpen: boolean
  setIsOpen: (open: boolean) => void
}

export function Sidebar({ isOpen, setIsOpen }: SidebarProps) {
  const pathname = usePathname()

  const isActive = (path: string) => pathname === path

  const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/providers', label: 'Providers', icon: Package },
    { href: '/webhooks', label: 'Webhooks', icon: LinkIcon },
    { href: '/security-logs', label: 'Security Logs', icon: ShieldAlert },
  ]

  return (
    <>
      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 h-screen bg-slate-800 border-r border-slate-700 transition-all duration-300 z-40 ${isOpen ? 'w-64' : 'w-20'
          }`}
      >
        {/* Logo — links back to home */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-slate-700">
          <Link href="/" className="flex items-center gap-2 text-indigo-500 font-bold text-xl hover:text-indigo-400 transition-colors truncate">
            {isOpen ? 'WebShield' : 'W'}
          </Link>
          {/* Desktop collapse toggle */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="hidden lg:flex p-1.5 text-slate-400 hover:text-white hover:bg-slate-700 rounded-md transition-colors"
            aria-label={isOpen ? 'Collapse sidebar' : 'Expand sidebar'}
          >
            {isOpen ? <ChevronLeft size={18} /> : <ChevronRight size={18} />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon
            const active = isActive(item.href)

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${active
                  ? 'bg-indigo-600 text-white'
                  : 'text-slate-400 hover:bg-slate-700 hover:text-white'
                  }`}
              >
                <Icon size={20} />
                {isOpen && <span className="text-sm font-medium">{item.label}</span>}
              </Link>
            )
          })}
        </nav>
      </aside>

      {/* Mobile Toggle */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-4 right-4 lg:hidden z-50 p-2 bg-indigo-600 text-white rounded-lg"
      >
        {isOpen ? <X size={20} /> : <Menu size={20} />}
      </button>
    </>
  )
}

