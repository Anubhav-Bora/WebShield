

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, Package, Link as LinkIcon, ShieldAlert, Menu, X, ChevronLeft, ChevronRight } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

interface NavItem {
  href: string
  label: string
  icon: LucideIcon
  highlight?: boolean
}

interface NavGroup {
  label: string
  items: NavItem[]
}

interface SidebarProps {
  isOpen: boolean
  setIsOpen: (open: boolean) => void
}

export function Sidebar({ isOpen, setIsOpen }: SidebarProps) {
  const pathname = usePathname()

  const isActive = (path: string) => pathname === path

  const navigationGroups: NavGroup[] = [
    {
      label: 'MAIN',
      items: [
        { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
      ],
    },
    {
      label: 'GATEWAY',
      items: [
        { href: '/providers', label: 'Providers', icon: Package },
        { href: '/webhooks/logs', label: 'Webhooks', icon: LinkIcon },
      ],
    },
    {
      label: 'SECURITY',
      items: [
        { href: '/security-logs', label: 'Security Logs', icon: ShieldAlert, highlight: true },
      ],
    }
  ]

  return (
    <>
      <aside
        className={`fixed left-0 top-0 h-screen bg-[#0d0d12] border-r border-white/5 transition-all duration-300 z-40 ${isOpen ? 'w-64' : 'w-20'
          }`}
      >
        {/* Logo Section */}
        <div className="h-20 flex items-center justify-between px-6">
          <Link href="/" className="flex items-center gap-3 text-white font-bold text-xl hover:opacity-80 transition-opacity truncate">
            <div className="w-8 h-8 rounded-full border-[4px] border-white flex items-center justify-center relative">
              <div className="absolute inset-0 bg-white/20 rounded-full blur-sm" />
            </div>
            {isOpen && <span>WebShield</span>}
          </Link>
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="hidden lg:flex p-1.5 text-slate-500 hover:text-white rounded-md transition-colors"
            aria-label={isOpen ? 'Collapse sidebar' : 'Expand sidebar'}
          >
            {isOpen ? <ChevronLeft size={18} /> : <ChevronRight size={18} />}
          </button>
        </div>

        {/* Navigation */}
        <div className="py-4 overflow-y-auto h-[calc(100vh-5rem)] custom-scrollbar">
          {navigationGroups.map((group, idx) => (
            <div key={idx} className="mb-6 px-4">
              {isOpen && (
                <h3 className="text-[10px] uppercase font-bold text-slate-500 tracking-wider mb-3 px-2">
                  {group.label}
                </h3>
              )}
              <nav className="space-y-1">
                {group.items.map((item) => {
                  const Icon = item.icon
                  const active = isActive(item.href)

                  return (
                    <Link
                      key={item.label}
                      href={item.href}
                      className={`flex items-center justify-between px-2 py-2.5 rounded-lg transition-all group ${active
                        ? 'text-white'
                        : 'text-slate-400 hover:text-white'
                        }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`p-1.5 rounded-lg transition-colors ${active ? 'text-emerald-400' : 'text-slate-500 group-hover:text-slate-300'}`}>
                          <Icon size={18} strokeWidth={active ? 2.5 : 2} />
                        </div>
                        {isOpen && <span className={`text-sm tracking-wide ${active ? 'font-semibold' : 'font-medium'}`}>{item.label}</span>}
                      </div>

                      {isOpen && item.highlight && (
                        <span className="px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-400 text-[10px] font-bold">
                          15
                        </span>
                      )}

                      {isOpen && !item.highlight && active && (
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
                      )}
                    </Link>
                  )
                })}
              </nav>
            </div>
          ))}
        </div>
      </aside>

      {/* Mobile Toggle */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-4 right-4 lg:hidden z-50 p-3 bg-[#0d0d12] border border-white/10 text-white rounded-full shadow-lg"
      >
        {isOpen ? <X size={20} /> : <Menu size={20} />}
      </button>
    </>
  )
}
