'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import toast from 'react-hot-toast'
import { Eye, EyeOff, ArrowRight, Sparkles } from 'lucide-react'
import { authApi } from '@/lib/api'
import { useAuthStore } from '@/lib/store'
import { Button, Input } from '@/components/ui'

// ── Shared Background ─────────────────────────────────────────────────────────
function AuthBg() {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none">
      <div className="absolute inset-0 bg-[#0A0A0F]" />
      {/* Gold radial glow */}
      <div className="absolute -top-40 -right-40 w-[600px] h-[600px] rounded-full" style={{ background: 'radial-gradient(ellipse at center, rgba(201,169,110,0.06) 0%, transparent 70%)' }} />
      <div className="absolute -bottom-40 -left-40 w-[500px] h-[500px] rounded-full" style={{ background: 'radial-gradient(ellipse at center, rgba(78,205,196,0.04) 0%, transparent 70%)' }} />
      {/* Decorative grid lines */}
      <div className="absolute inset-0" style={{ backgroundImage: 'linear-gradient(rgba(30,30,46,0.4) 1px, transparent 1px), linear-gradient(90deg, rgba(30,30,46,0.4) 1px, transparent 1px)', backgroundSize: '80px 80px' }} />
      {/* Floating orbs */}
      <div className="absolute top-1/4 right-1/4 w-2 h-2 rounded-full bg-[#C9A96E] opacity-40" style={{ animation: 'float 6s ease-in-out infinite' }} />
      <div className="absolute top-3/4 left-1/3 w-1.5 h-1.5 rounded-full bg-[#4ECDC4] opacity-30" style={{ animation: 'float 8s ease-in-out infinite 2s' }} />
      <div className="absolute top-1/2 right-1/3 w-1 h-1 rounded-full bg-[#D4688A] opacity-25" style={{ animation: 'float 7s ease-in-out infinite 1s' }} />
    </div>
  )
}

// ── Logo Mark ─────────────────────────────────────────────────────────────────
function LogoMark() {
  return (
    <div className="text-center mb-8">
      <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-gradient-to-br from-[#C9A96E] to-[#8B6F47] mb-4 shadow-[0_0_40px_rgba(201,169,110,0.3)]">
        <Sparkles size={22} className="text-[#0A0A0F]" />
      </div>
      <h1 className="font-serif text-[32px] font-semibold text-[#C9A96E] tracking-[0.01em]">Vōgue·AI</h1>
      <p className="text-[11px] tracking-[0.18em] uppercase text-[#6B6B7A] mt-1">Fashion Intelligence Platform</p>
    </div>
  )
}

// ── Social Proof ──────────────────────────────────────────────────────────────
function SocialProof() {
  return (
    <div className="mt-6 pt-6 border-t border-[#1E1E2E]">
      <div className="flex items-center justify-center gap-6">
        {[
          { num: '1,247', label: 'trends tracked' },
          { num: '438', label: 'active brands' },
          { num: '89%', label: 'accuracy' },
        ].map(s => (
          <div key={s.label} className="text-center">
            <div className="font-serif text-[18px] font-semibold text-[#C9A96E]">{s.num}</div>
            <div className="text-[10px] text-[#6B6B7A] tracking-[0.06em]">{s.label}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ── LOGIN PAGE ────────────────────────────────────────────────────────────────
export function LoginPage() {
  const router = useRouter()
  const { login, setUser } = useAuthStore()
  const [form, setForm] = useState({ email: '', password: '' })
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const validate = () => {
    const e: Record<string, string> = {}
    if (!form.email.includes('@')) e.email = 'Enter a valid email'
    if (form.password.length < 6) e.password = 'Password too short'
    setErrors(e)
    return !Object.keys(e).length
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return
    setLoading(true)
    try {
      const tokens = await authApi.login(form.email, form.password)
      login(tokens)
      const user = await authApi.me()
      setUser(user)
      toast.success(`Welcome back, ${user.name.split(' ')[0]}!`)
      router.push('/dashboard')
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Invalid email or password'
      toast.error(typeof msg === 'string' ? msg : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center relative px-4">
      <AuthBg />
      <div className="relative z-10 w-full max-w-[400px] page-enter">
        <div className="bg-[#111118]/90 border border-[#1E1E2E] rounded-[16px] p-8 shadow-[0_24px_64px_rgba(0,0,0,0.6)] backdrop-blur-sm">
          <LogoMark />

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Email address"
              type="email"
              placeholder="you@brand.com"
              value={form.email}
              onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
              error={errors.email}
              autoComplete="email"
            />
            <div className="flex flex-col gap-1.5">
              <label className="text-[11px] tracking-[0.1em] uppercase text-[#6B6B7A] font-medium">Password</label>
              <div className="relative">
                <input
                  type={showPw ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={form.password}
                  onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                  autoComplete="current-password"
                  className={`w-full bg-[#0A0A0F] border rounded-[8px] px-3.5 py-2.5 pr-10 text-[13px] text-[#F0EEE8] placeholder-[#6B6B7A] outline-none transition-colors ${errors.password ? 'border-[#D4688A]/60 focus:border-[#D4688A]' : 'border-[#1E1E2E] focus:border-[#C9A96E]/50'}`}
                />
                <button type="button" onClick={() => setShowPw(s => !s)} className="absolute right-3 top-1/2 -translate-y-1/2 text-[#6B6B7A] hover:text-[#C9A96E] transition-colors">
                  {showPw ? <EyeOff size={14} /> : <Eye size={14} />}
                </button>
              </div>
              {errors.password && <p className="text-[11px] text-[#D4688A]">{errors.password}</p>}
            </div>

            <Button type="submit" loading={loading} className="w-full mt-2 py-3 text-[14px]" size="lg">
              Sign in <ArrowRight size={14} />
            </Button>
          </form>

          {/* Demo credentials hint */}
          <div className="mt-4 p-3 rounded-[8px] bg-[#C9A96E]/06 border border-[#C9A96E]/15">
            <p className="text-[11px] text-[#C9A96E] text-center font-medium mb-1">Demo credentials</p>
            <p className="text-[10px] text-[#6B6B7A] text-center">pro@test.com · password123</p>
          </div>

          <p className="text-center text-[12px] text-[#6B6B7A] mt-5">
            No account?{' '}
            <Link href="/register" className="text-[#C9A96E] hover:text-[#DCC08E] transition-colors font-medium">
              Create one free
            </Link>
          </p>
          <SocialProof />
        </div>
      </div>
    </div>
  )
}

// ── REGISTER PAGE ─────────────────────────────────────────────────────────────
const ROLES = [
  { value: 'boutique_owner', label: 'Boutique Owner' },
  { value: 'online_store',   label: 'Online Fashion Store' },
  { value: 'fashion_designer', label: 'Fashion Designer' },
]

export function RegisterPage() {
  const router = useRouter()
  const { login, setUser } = useAuthStore()
  const [form, setForm] = useState({ name: '', email: '', password: '', role: 'boutique_owner' })
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const validate = () => {
    const e: Record<string, string> = {}
    if (form.name.trim().length < 2) e.name = 'Name must be at least 2 characters'
    if (!form.email.includes('@')) e.email = 'Enter a valid email'
    if (form.password.length < 8) e.password = 'Password must be at least 8 characters'
    setErrors(e)
    return !Object.keys(e).length
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return
    setLoading(true)
    try {
      await authApi.register(form)
      const tokens = await authApi.login(form.email, form.password)
      login(tokens)
      const user = await authApi.me()
      setUser(user)
      toast.success('Welcome to Vōgue·AI!')
      router.push('/dashboard')
    } catch (err: any) {
      const detail = err?.response?.data?.detail
      if (detail?.includes('already')) toast.error('Email already registered')
      else toast.error('Registration failed. Try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center relative px-4 py-8">
      <AuthBg />
      <div className="relative z-10 w-full max-w-[420px] page-enter">
        <div className="bg-[#111118]/90 border border-[#1E1E2E] rounded-[16px] p-8 shadow-[0_24px_64px_rgba(0,0,0,0.6)] backdrop-blur-sm">
          <LogoMark />

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input label="Full name" type="text" placeholder="Alex Chen" value={form.name}
              onChange={e => setForm(f => ({ ...f, name: e.target.value }))} error={errors.name} autoComplete="name" />
            <Input label="Email address" type="email" placeholder="you@brand.com" value={form.email}
              onChange={e => setForm(f => ({ ...f, email: e.target.value }))} error={errors.email} autoComplete="email" />

            <div className="flex flex-col gap-1.5">
              <label className="text-[11px] tracking-[0.1em] uppercase text-[#6B6B7A] font-medium">Password</label>
              <div className="relative">
                <input type={showPw ? 'text' : 'password'} placeholder="Min 8 characters" value={form.password}
                  onChange={e => setForm(f => ({ ...f, password: e.target.value }))} autoComplete="new-password"
                  className={`w-full bg-[#0A0A0F] border rounded-[8px] px-3.5 py-2.5 pr-10 text-[13px] text-[#F0EEE8] placeholder-[#6B6B7A] outline-none transition-colors ${errors.password ? 'border-[#D4688A]/60' : 'border-[#1E1E2E] focus:border-[#C9A96E]/50'}`}
                />
                <button type="button" onClick={() => setShowPw(s => !s)} className="absolute right-3 top-1/2 -translate-y-1/2 text-[#6B6B7A] hover:text-[#C9A96E] transition-colors">
                  {showPw ? <EyeOff size={14} /> : <Eye size={14} />}
                </button>
              </div>
              {errors.password && <p className="text-[11px] text-[#D4688A]">{errors.password}</p>}
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-[11px] tracking-[0.1em] uppercase text-[#6B6B7A] font-medium">I am a</label>
              <div className="grid grid-cols-3 gap-2">
                {ROLES.map(r => (
                  <button key={r.value} type="button" onClick={() => setForm(f => ({ ...f, role: r.value }))}
                    className={`py-2.5 px-3 rounded-[8px] text-[11px] font-medium border transition-all ${form.role === r.value ? 'border-[#C9A96E]/40 bg-[#C9A96E]/08 text-[#C9A96E]' : 'border-[#1E1E2E] text-[#6B6B7A] hover:border-[#C9A96E]/20'}`}>
                    {r.label}
                  </button>
                ))}
              </div>
            </div>

            <Button type="submit" loading={loading} className="w-full mt-2" size="lg">
              Create account <ArrowRight size={14} />
            </Button>
          </form>

          {/* Features */}
          <div className="mt-4 grid grid-cols-2 gap-2">
            {['14-day free trial', 'No credit card needed', 'Cancel anytime', 'AI-powered insights'].map(f => (
              <div key={f} className="flex items-center gap-1.5 text-[10px] text-[#6B6B7A]">
                <span className="text-[#52C97A]">✓</span>{f}
              </div>
            ))}
          </div>

          <p className="text-center text-[12px] text-[#6B6B7A] mt-5">
            Already have an account?{' '}
            <Link href="/login" className="text-[#C9A96E] hover:text-[#DCC08E] transition-colors font-medium">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
