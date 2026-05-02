'use client'
import { usePathname, useRouter } from 'next/navigation'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/lib/store'
import { LayoutDashboard, TrendingUp, Sparkles, Bot, Palette, MessageCircle, FileText, CreditCard, LogOut, ChevronLeft, ChevronRight, Receipt } from 'lucide-react'

const NAV_ITEMS = [
  { label: 'Analytics', items: [
    { href: '/dashboard',    icon: LayoutDashboard, label: 'Dashboard' },
    { href: '/trends',       icon: TrendingUp,      label: 'Live Trends' },
    { href: '/predictions',  icon: Sparkles,        label: 'Predictions' },
    { href: '/agents',       icon: Bot,             label: 'AI Agents' },
    { href: '/colors',       icon: Palette,         label: 'Color Trends' },
    { href: '/advisor',      icon: MessageCircle,   label: 'AI Advisor' },
  ]},
  { label: 'Account', items: [
    { href: '/reports',      icon: FileText,        label: 'Reports' },
    { href: '/subscription', icon: CreditCard,      label: 'Subscription' },
  ]},
]

export default function Sidebar({ collapsed, onToggle }: { collapsed: boolean; onToggle: () => void }) {
  const pathname = usePathname()
  const router = useRouter()
  const { user, logout } = useAuthStore()

  return (
    <aside className={cn('flex flex-col h-full bg-[#111118] border-r border-[#1E1E2E] transition-all duration-300 relative flex-shrink-0', collapsed ? 'w-[64px]' : 'w-[220px]')}>

      {/* Logo */}
      <div className={cn('border-b border-[#1E1E2E] flex items-center', collapsed ? 'p-4 justify-center' : 'px-6 py-5')}>
        {collapsed
          ? <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#C9A96E] to-[#8B6F47] flex items-center justify-center text-[#0A0A0F] text-[11px] font-bold">V</div>
          : <div>
              <div className="font-serif text-[22px] font-semibold text-[#C9A96E]">Vōgue·AI</div>
              <div className="text-[9px] tracking-[0.14em] uppercase text-[#6B6B7A] mt-0.5">Fashion Intelligence</div>
            </div>
        }
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-4">
        {NAV_ITEMS.map(section => (
          <div key={section.label}>
            {!collapsed && <div className="text-[9px] tracking-[0.18em] uppercase text-[#6B6B7A] px-3 mb-2 font-medium">{section.label}</div>}
            {section.items.map(item => {
              const Icon = item.icon
              const active = pathname === item.href || pathname.startsWith(item.href + '/')
              return (
                <button key={item.href} onClick={() => router.push(item.href)} title={collapsed ? item.label : undefined}
                  className={cn('w-full flex items-center gap-2.5 rounded-[8px] py-2.5 text-[13px] font-medium transition-all border border-transparent mb-0.5',
                    collapsed ? 'px-0 justify-center' : 'px-3',
                    active ? 'text-[#C9A96E] bg-[#C9A96E]/08 border-[#C9A96E]/15' : 'text-[#6B6B7A] hover:text-[#F0EEE8] hover:bg-white/[0.03]'
                  )}>
                  <Icon size={15} className="flex-shrink-0" />
                  {!collapsed && <span>{item.label}</span>}
                </button>
              )
            })}
          </div>
        ))}
      </nav>

      {/* User footer */}
      {!collapsed && user && (
        <div className="border-t border-[#1E1E2E] p-4">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#C9A96E] to-[#8B6F47] flex items-center justify-center text-[#0A0A0F] text-[11px] font-bold flex-shrink-0">
              {user.name.charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0">
              <div className="text-[12px] font-medium truncate">{user.name}</div>
              <div className="text-[10px] text-[#6B6B7A] truncate">{user.email}</div>
            </div>
          </div>
          <button onClick={() => { logout(); router.push('/login') }}
            className="w-full flex items-center gap-2 text-[11px] text-[#6B6B7A] hover:text-[#D4688A] transition-colors py-1.5 px-2 rounded-[6px]">
            <LogOut size={12} /><span>Sign out</span>
          </button>
        </div>
      )}

      {/* Collapse toggle */}
      <button onClick={onToggle}
        className="absolute -right-3 top-[72px] w-6 h-6 rounded-full bg-[#16161F] border border-[#1E1E2E] flex items-center justify-center text-[#6B6B7A] hover:text-[#C9A96E] transition-colors z-10">
        {collapsed ? <ChevronRight size={12} /> : <ChevronLeft size={12} />}
      </button>
    </aside>
  )
}
