import { clsx, type ClassValue } from 'clsx'
import { format, formatDistanceToNow } from 'date-fns'
import { useDebounce } from '@/hooks'

export function cn(...inputs: ClassValue[]) { return clsx(inputs) }

export const formatDate = (d: string) => format(new Date(d), 'MMM d, yyyy')
export const formatDateShort = (d: string) => format(new Date(d), 'MMM d')
export const formatTimeAgo = (d: string) => formatDistanceToNow(new Date(d), { addSuffix: true })
export const formatNum = (n: number) => n >= 1_000_000 ? `${(n/1_000_000).toFixed(1)}M` : n >= 1_000 ? `${(n/1_000).toFixed(1)}K` : String(n)
export const formatPct = (n: number, decimals = 1) => `${n >= 0 ? '+' : ''}${n.toFixed(decimals)}%`
export const formatScore = (n: number) => n.toFixed(1)
export const formatCurrency = (n: number, currency = 'USD') => new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(n)

export const STATUS_COLORS: Record<string, string> = {
  rising: '#52C97A', peak: '#C9A96E', emerging: '#4ECDC4', declining: '#D4688A', stable: '#9191A0',
}
export const STATUS_BG: Record<string, string> = {
  rising: 'rgba(82,201,122,0.12)', peak: 'rgba(201,169,110,0.12)', emerging: 'rgba(78,205,196,0.12)', declining: 'rgba(212,104,138,0.12)', stable: 'rgba(107,107,122,0.12)',
}
export const CATEGORY_COLORS: Record<string, string> = {
  Style: '#C9A96E', Color: '#D4688A', Texture: '#4ECDC4', Accessory: '#7C5CBF', Footwear: '#52C97A', Outerwear: '#F5A623',
}
export const PRIORITY_COLORS: Record<string, string> = {
  high: '#D4688A', medium: '#C9A96E', low: '#6B6B7A',
}
export const ACTION_LABELS: Record<string, string> = {
  stock_now: 'Stock Now', avoid: 'Avoid', monitor: 'Monitor', reduce_inventory: 'Reduce Stock', feature_prominently: 'Feature',
}

export const MOCK_SPARKLINE = () => Array.from({ length: 12 }, (_, i) => Math.round(40 + Math.sin(i * 0.6) * 20 + Math.random() * 15))

export function truncate(str: string, n: number) { return str.length > n ? str.slice(0, n) + '…' : str }

// Re-export hooks for convenience
export { useDebounce } from '@/hooks'
