'use client'
import { useState, useEffect } from 'react'
import { usePathname } from 'next/navigation'
import { RefreshCw, Bell } from 'lucide-react'
import { Tag } from '@/components/ui'
import { cn } from '@/lib/utils'

const PAGE_TITLES: Record<string, string> = {
  '/dashboard':    'Dashboard',
  '/trends':       'Live Trends',
  '/predictions':  'Season Predictions',
  '/agents':       'AI Agents',
  '/colors':       'Color Trends',
  '/advisor':      'AI Advisor',
  '/reports':      'Reports',
  '/subscription': 'Subscription',
}

const TICKER_ITEMS = [
  { tag: '#QuietLuxury', val: '94.2K posts today' },
  { tag: '#ButterYellow', val: '62.1K posts' },
  { tag: '#CobaltBlue', val: '78.3K posts' },
  { tag: '#MicroPleats', val: '41.8K posts' },
  { tag: 'TREND ALERT:', val: 'Sculptural bags +44% this week' },
  { tag: '#NeoBoho', val: '33.5K posts' },
  { tag: '#MinimalistFashion', val: '55.2K posts' },
  { tag: 'NEW TREND:', val: 'Butter yellow knit +52% growth' },
]

export default function Topbar() {
  const pathname = usePathname()
  const [agentCount] = useState(5)

  const title = PAGE_TITLES[pathname] || 'Dashboard'
  const doubled = [...TICKER_ITEMS, ...TICKER_ITEMS]

  return (
    <div className="border-b border-[#1E1E2E] bg-[#0A0A0F]/90 backdrop-blur-md sticky top-0 z-40">
      {/* Main bar */}
      <div className="flex items-center justify-between px-6 py-3">
        <div className="flex items-center gap-3">
          <h1 className="font-serif text-[20px] font-normal italic">{title}</h1>
          <Tag color="#52C97A">Live</Tag>
        </div>
        <div className="flex items-center gap-4">
          {/* Agent status */}
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#52C97A]" style={{ boxShadow: '0 0 6px #52C97A', animation: 'pulseGold 2s infinite' }} />
            <span className="text-[11px] text-[#6B6B7A]">{agentCount} agents active</span>
          </div>
          <button className="flex items-center gap-1.5 text-[11px] text-[#6B6B7A] hover:text-[#C9A96E] transition-colors border border-[#1E1E2E] rounded-[7px] px-3 py-1.5">
            <RefreshCw size={11} />
            <span>Refresh</span>
          </button>
          <button className="relative text-[#6B6B7A] hover:text-[#C9A96E] transition-colors p-1.5">
            <Bell size={15} />
            <div className="absolute top-0.5 right-0.5 w-2 h-2 rounded-full bg-[#D4688A]" />
          </button>
        </div>
      </div>

      {/* Live ticker */}
      <div className="ticker-wrap border-t border-[#1E1E2E] bg-[#111118]/60 overflow-hidden py-2 px-0">
        <div className="ticker-inner">
          {doubled.map((item, i) => (
            <span key={i} className="inline-flex items-center gap-2 px-6 text-[11px] text-[#6B6B7A]">
              <span className="font-medium text-[#C9A96E]">{item.tag}</span>
              <span>{item.val}</span>
              <span className="text-[#1E1E2E] ml-2">·</span>
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
