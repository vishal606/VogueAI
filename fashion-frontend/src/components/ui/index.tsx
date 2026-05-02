'use client'
import { cn } from '@/lib/utils'
import { Loader2 } from 'lucide-react'
import React from 'react'

// ── Button ────────────────────────────────────────────────────────────────────
interface BtnProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'ghost' | 'danger' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
}
export function Button({ variant = 'primary', size = 'md', loading, className, children, disabled, ...props }: BtnProps) {
  const base = 'inline-flex items-center justify-center gap-2 font-sans font-medium rounded-[8px] transition-all duration-150 select-none outline-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed'
  const variants = {
    primary: 'bg-[#C9A96E] text-[#0A0A0F] hover:bg-[#DCC08E] active:scale-[0.98]',
    ghost: 'bg-transparent border border-[#1E1E2E] text-[#6B6B7A] hover:border-[#C9A96E]/40 hover:text-[#C9A96E]',
    danger: 'bg-[#D4688A]/10 border border-[#D4688A]/30 text-[#D4688A] hover:bg-[#D4688A]/20',
    outline: 'bg-transparent border border-[#C9A96E]/30 text-[#C9A96E] hover:bg-[#C9A96E]/10',
  }
  const sizes = { sm: 'text-[11px] px-3 py-1.5', md: 'text-[13px] px-4 py-2.5', lg: 'text-[14px] px-6 py-3' }
  return (
    <button className={cn(base, variants[variant], sizes[size], className)} disabled={disabled || loading} {...props}>
      {loading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
      {children}
    </button>
  )
}

// ── Input ─────────────────────────────────────────────────────────────────────
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> { label?: string; error?: string; hint?: string }
export function Input({ label, error, hint, className, ...props }: InputProps) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && <label className="text-[11px] tracking-[0.1em] uppercase text-[#6B6B7A] font-medium">{label}</label>}
      <input
        className={cn('w-full bg-[#111118] border rounded-[8px] px-3.5 py-2.5 text-[13px] text-[#F0EEE8] font-sans placeholder-[#6B6B7A] outline-none transition-colors duration-150', error ? 'border-[#D4688A]/60 focus:border-[#D4688A]' : 'border-[#1E1E2E] focus:border-[#C9A96E]/50', className)}
        {...props}
      />
      {error && <p className="text-[11px] text-[#D4688A]">{error}</p>}
      {hint && !error && <p className="text-[11px] text-[#6B6B7A]">{hint}</p>}
    </div>
  )
}

// ── Select ────────────────────────────────────────────────────────────────────
interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> { label?: string; options: { value: string; label: string }[] }
export function Select({ label, options, className, ...props }: SelectProps) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && <label className="text-[11px] tracking-[0.1em] uppercase text-[#6B6B7A] font-medium">{label}</label>}
      <select className={cn('w-full bg-[#111118] border border-[#1E1E2E] rounded-[8px] px-3.5 py-2.5 text-[13px] text-[#F0EEE8] font-sans outline-none focus:border-[#C9A96E]/50 transition-colors', className)} {...props}>
        {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  )
}

// ── Card ──────────────────────────────────────────────────────────────────────
interface CardProps { children: React.ReactNode; className?: string; hover?: boolean; accentColor?: string; onClick?: () => void }
export function Card({ children, className, hover, accentColor, onClick }: CardProps) {
  return (
    <div onClick={onClick} className={cn('bg-[#16161F] border border-[#1E1E2E] rounded-[12px] overflow-hidden relative', hover && 'transition-all duration-200 hover:-translate-y-0.5 hover:shadow-[0_12px_40px_rgba(0,0,0,0.5)] hover:border-[#C9A96E]/20', onClick && 'cursor-pointer', className)}>
      {accentColor && <div className="absolute top-0 left-0 right-0 h-[1.5px]" style={{ background: `linear-gradient(90deg, ${accentColor}, transparent)` }} />}
      {children}
    </div>
  )
}
export function CardHeader({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn('px-5 py-4 border-b border-[#1E1E2E] flex items-center justify-between', className)}>{children}</div>
}
export function CardTitle({ children, className }: { children: React.ReactNode; className?: string }) {
  return <h3 className={cn('font-serif text-[17px] font-semibold', className)}>{children}</h3>
}
export function CardBody({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn('p-5', className)}>{children}</div>
}

// ── Badge ─────────────────────────────────────────────────────────────────────
const BADGE_MAP: Record<string, string> = {
  rising: 'badge-rising', peak: 'badge-peak', emerging: 'badge-emerging',
  declining: 'badge-declining', stable: 'badge-stable', active: 'badge-rising',
  canceled: 'badge-declining', pending: 'badge-emerging',
  high: 'badge-declining', medium: 'badge-peak', low: 'badge-stable',
}
export function Badge({ status, children, className }: { status?: string; children?: React.ReactNode; className?: string }) {
  return <span className={cn('badge', BADGE_MAP[status || ''] || 'badge-stable', className)}>{children || status}</span>
}

// ── Stat Card ─────────────────────────────────────────────────────────────────
export function StatCard({ label, value, change, color, icon }: { label: string; value: string | number; change?: string; color?: string; icon?: React.ReactNode }) {
  return (
    <Card accentColor={color}>
      <div className="p-5">
        <div className="flex items-center justify-between mb-3">
          <span className="text-[10px] tracking-[0.12em] uppercase text-[#6B6B7A] font-medium">{label}</span>
          {icon && <span className="opacity-50">{icon}</span>}
        </div>
        <div className="font-serif text-[34px] font-semibold leading-none mb-1.5" style={{ color: color || '#C9A96E' }}>{value}</div>
        {change && <div className="text-[11px] text-[#52C97A]">{change}</div>}
      </div>
    </Card>
  )
}

// ── Score Bar ─────────────────────────────────────────────────────────────────
export function ScoreBar({ score, color = '#C9A96E', width = 80 }: { score: number; color?: string; width?: number }) {
  return (
    <div style={{ width }}>
      <div className="score-track mb-1">
        <div className="score-fill" style={{ width: `${Math.min(score, 100)}%`, background: color }} />
      </div>
      <span className="text-[10px] text-[#6B6B7A]">{score.toFixed(0)}</span>
    </div>
  )
}

// ── Sparkline ─────────────────────────────────────────────────────────────────
export function Sparkline({ data, color = '#C9A96E', height = 32 }: { data: number[]; color?: string; height?: number }) {
  const max = Math.max(...data, 1)
  return (
    <div className="sparkline" style={{ height }}>
      {data.map((v, i) => (
        <div key={i} className="spark-bar" style={{ height: `${(v / max) * 100}%`, background: `linear-gradient(180deg, ${color}, ${color}44)` }} />
      ))}
    </div>
  )
}

// ── Spinner ───────────────────────────────────────────────────────────────────
export function Spinner({ size = 16 }: { size?: number }) {
  return <div style={{ width: size, height: size, border: '2px solid #1E1E2E', borderTopColor: '#C9A96E', borderRadius: '50%', animation: 'spin 0.7s linear infinite', flexShrink: 0 }} />
}

// ── Empty ─────────────────────────────────────────────────────────────────────
export function Empty({ icon, title, description, action }: { icon?: React.ReactNode; title: string; description?: string; action?: React.ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-3 text-center">
      {icon && <div className="text-[#1E1E2E] mb-2 text-[40px]">{icon}</div>}
      <p className="font-serif text-[18px]">{title}</p>
      {description && <p className="text-[12px] text-[#6B6B7A] max-w-sm">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}

// ── Skeleton ──────────────────────────────────────────────────────────────────
export function Skeleton({ className }: { className?: string }) {
  return <div className={cn('shimmer rounded-[6px]', className)} />
}
export function SkeletonCard() {
  return <Card><div className="p-5 flex flex-col gap-3"><Skeleton className="h-3 w-24" /><Skeleton className="h-8 w-32" /><Skeleton className="h-2.5 w-16" /></div></Card>
}

// ── Section Header ────────────────────────────────────────────────────────────
export function SectionHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: React.ReactNode }) {
  return (
    <div className="flex items-end justify-between mb-6">
      <div>
        <h2 className="font-serif text-[26px] font-normal">{title}</h2>
        {subtitle && <p className="text-[12px] text-[#6B6B7A] mt-0.5">{subtitle}</p>}
      </div>
      {action}
    </div>
  )
}

// ── Tag ───────────────────────────────────────────────────────────────────────
export function Tag({ children, color = '#C9A96E' }: { children: React.ReactNode; color?: string }) {
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium tracking-[0.04em] border" style={{ color, background: `${color}15`, borderColor: `${color}25` }}>
      {children}
    </span>
  )
}

// ── Color Dot ─────────────────────────────────────────────────────────────────
export function ColorDot({ color, size = 10 }: { color?: string; size?: number }) {
  return <div style={{ width: size, height: size, borderRadius: '50%', background: color || '#6B6B7A', flexShrink: 0, boxShadow: color ? `0 0 6px ${color}66` : 'none' }} />
}

// ── Progress ──────────────────────────────────────────────────────────────────
export function Progress({ value, color = '#C9A96E', height = 3 }: { value: number; color?: string; height?: number }) {
  return (
    <div style={{ height, background: '#1E1E2E', borderRadius: height, overflow: 'hidden' }}>
      <div style={{ height: '100%', width: `${Math.min(value * 100, 100)}%`, background: `linear-gradient(90deg, ${color}, ${color}99)`, borderRadius: height, transition: 'width 0.8s cubic-bezier(0.16,1,0.3,1)' }} />
    </div>
  )
}
