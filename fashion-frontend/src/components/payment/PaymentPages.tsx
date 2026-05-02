'use client'
import { useState, useEffect } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { CreditCard, Shield, CheckCircle, XCircle, ExternalLink, Download, RefreshCw, AlertTriangle, Loader2, ArrowRight, Zap, Star } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '@/lib/api'
import { useAuthStore } from '@/lib/store'
import { Card, CardHeader, CardTitle, CardBody, Button, Badge, SectionHeader, Spinner, Progress } from '@/components/ui'
import { formatCurrency, formatDate } from '@/lib/utils'
import type { SubscriptionPlan, Subscription } from '@/types'

// ── API helpers ───────────────────────────────────────────────────────────────
const paymentsApi = {
  checkoutSession: (plan_id: string) =>
    api.post('/payments/checkout-session', {
      plan_id,
      success_url: `${window.location.origin}/checkout/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${window.location.origin}/subscription`,
      trial_days: 14,
    }).then(r => r.data),
  verifySession: (session_id: string) =>
    api.get(`/payments/checkout-session/${session_id}`).then(r => r.data),
  billingPortal: () =>
    api.post('/payments/billing-portal', {
      return_url: `${window.location.origin}/billing`,
    }).then(r => r.data),
  invoices: () => api.get('/payments/invoices').then(r => r.data),
  paymentMethods: () => api.get('/payments/payment-methods').then(r => r.data),
  upgrade: (new_plan_id: string) =>
    api.post('/payments/upgrade', { new_plan_id, prorate: true }).then(r => r.data),
  cancel: (immediately = false) =>
    api.post(`/payments/cancel?immediately=${immediately}`).then(r => r.data),
  reactivate: () => api.post('/payments/reactivate').then(r => r.data),
  plans: () => api.get('/subscriptions/plans').then(r => r.data),
  current: () => api.get('/subscriptions/me').then(r => r.data),
}

// ── Plan metadata ─────────────────────────────────────────────────────────────
const PLAN_META: Record<string, { color: string; icon: string; highlight?: boolean }> = {
  Basic:   { color: '#6B6B7A', icon: '◇' },
  Pro:     { color: '#C9A96E', icon: '◆', highlight: true },
  Premium: { color: '#7C5CBF', icon: '✦' },
}
const PLAN_FEATURES: Record<string, string[]> = {
  Basic:   ['Weekly trend reports', 'Top 10 trending colors', 'Basic style explorer', 'Email support', '1 user'],
  Pro:     ['Daily trend predictions', 'AI Advisor (Claude)', 'Color palette generator', 'Custom PDF/Excel reports', 'Recommendation engine', '5 users', 'API access'],
  Premium: ['Everything in Pro', 'Real-time AI recommendations', 'Competitor tracking', 'Custom alert rules', 'White-label reports', 'Unlimited users', 'Priority support', 'Dedicated CSM'],
}

// ─────────────────────────────────────────────────────────────────────────────
// CHECKOUT PAGE
// ─────────────────────────────────────────────────────────────────────────────
export function CheckoutPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [plans, setPlans] = useState<SubscriptionPlan[]>([])
  const [selected, setSelected] = useState<SubscriptionPlan | null>(null)
  const [billing, setBilling] = useState<'monthly' | 'yearly'>('monthly')
  const [loading, setLoading] = useState(false)
  const [fetching, setFetching] = useState(true)

  useEffect(() => {
    paymentsApi.plans()
      .then((data: SubscriptionPlan[]) => { setPlans(data); setSelected(data.find(p => p.name === 'Pro') || data[0]) })
      .catch(() => {
        // Mock plans in dev
        const mock: SubscriptionPlan[] = [
          { id: 'plan_basic', name: 'Basic', type: 'monthly', price: 49, features: {}, is_active: true },
          { id: 'plan_pro', name: 'Pro', type: 'monthly', price: 149, features: {}, is_active: true },
          { id: 'plan_premium', name: 'Premium', type: 'monthly', price: 399, features: {}, is_active: true },
        ]
        setPlans(mock); setSelected(mock[1])
      })
      .finally(() => setFetching(false))
  }, [])

  const handleCheckout = async () => {
    if (!selected) return
    setLoading(true)
    try {
      const res = await paymentsApi.checkoutSession(selected.id)
      if (res.checkout_url) {
        window.location.href = res.checkout_url
      } else {
        toast.success('Subscription activated! (dev mode)')
        router.push('/dashboard')
      }
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Checkout failed. Try again.')
    } finally { setLoading(false) }
  }

  const yearlyPrice = (p: number) => Math.round(p * 0.8)

  return (
    <div className="min-h-screen bg-[#0A0A0F] flex items-center justify-center px-4 py-12">
      {/* Background glow */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px]" style={{ background: 'radial-gradient(ellipse at top, rgba(201,169,110,0.08) 0%, transparent 70%)' }} />
      </div>

      <div className="relative z-10 w-full max-w-[900px]">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 bg-[#C9A96E]/10 border border-[#C9A96E]/20 rounded-full px-4 py-1.5 text-[11px] text-[#C9A96E] font-medium mb-4">
            <Shield size={11} /> 14-day free trial · No credit card required
          </div>
          <h1 className="font-serif text-[40px] font-normal mb-2">Choose Your Plan</h1>
          <p className="text-[14px] text-[#6B6B7A]">Start your free trial today. Upgrade, downgrade or cancel anytime.</p>
        </div>

        {/* Billing toggle */}
        <div className="flex justify-center mb-8">
          <div className="flex border border-[#1E1E2E] rounded-[10px] overflow-hidden">
            {(['monthly', 'yearly'] as const).map(b => (
              <button key={b} onClick={() => setBilling(b)}
                className={`px-6 py-2.5 text-[13px] font-medium capitalize transition-colors ${billing === b ? 'bg-[#C9A96E]/10 text-[#C9A96E]' : 'text-[#6B6B7A] hover:text-[#F0EEE8]'}`}>
                {b} {b === 'yearly' && <span className="ml-1.5 text-[10px] text-[#52C97A] font-medium">Save 20%</span>}
              </button>
            ))}
          </div>
        </div>

        {/* Plan cards */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          {(fetching ? [null, null, null] : plans).map((plan, i) => {
            if (!plan) return (
              <Card key={i}><div className="p-6 space-y-4"><div className="shimmer h-4 w-16 rounded" /><div className="shimmer h-10 w-24 rounded" /><div className="space-y-2">{Array(5).fill(0).map((_, j) => <div key={j} className="shimmer h-3 rounded" />)}</div></div></Card>
            )
            const meta = PLAN_META[plan.name] || { color: '#6B6B7A', icon: '◇' }
            const price = billing === 'yearly' ? yearlyPrice(plan.price) : plan.price
            const isSelected = selected?.id === plan.id
            return (
              <Card key={plan.id} onClick={() => setSelected(plan)}
                className={`cursor-pointer transition-all ${isSelected ? 'border-[#C9A96E]/50 shadow-[0_0_30px_rgba(201,169,110,0.15)]' : 'hover:border-[#1E1E2E]/80'} ${meta.highlight ? 'relative' : ''}`}
                accentColor={isSelected ? meta.color : undefined}>
                {meta.highlight && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[#C9A96E] text-[#0A0A0F] text-[9px] font-bold tracking-[0.1em] uppercase px-3 py-1 rounded-full">
                    Most Popular
                  </div>
                )}
                <div className="p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <span style={{ color: meta.color, fontSize: 16 }}>{meta.icon}</span>
                    <span className="text-[11px] tracking-[0.14em] uppercase text-[#6B6B7A] font-medium">{plan.name}</span>
                    {isSelected && <CheckCircle size={14} className="ml-auto text-[#C9A96E]" />}
                  </div>
                  <div className="mb-1">
                    <span className="font-serif text-[36px] font-semibold" style={{ color: isSelected ? meta.color : '#F0EEE8' }}>${price}</span>
                    <span className="text-[12px] text-[#6B6B7A] ml-1">/mo</span>
                  </div>
                  {billing === 'yearly' && <div className="text-[10px] text-[#52C97A] mb-4">Billed ${price * 12}/year</div>}
                  <div className="mt-5 space-y-2.5">
                    {(PLAN_FEATURES[plan.name] || []).map((f, j) => (
                      <div key={j} className="flex items-start gap-2 text-[12px] text-[#6B6B7A]">
                        <span className="text-[#52C97A] mt-0.5 flex-shrink-0">✓</span>{f}
                      </div>
                    ))}
                  </div>
                </div>
              </Card>
            )
          })}
        </div>

        {/* CTA */}
        {selected && (
          <div className="flex flex-col items-center gap-4">
            <Button onClick={handleCheckout} loading={loading} size="lg" className="px-12 py-4 text-[15px]">
              Start Free Trial — {selected.name} ${billing === 'yearly' ? yearlyPrice(selected.price) : selected.price}/mo
              <ArrowRight size={16} />
            </Button>
            <div className="flex items-center gap-6 text-[11px] text-[#6B6B7A]">
              <div className="flex items-center gap-1.5"><Shield size={11} className="text-[#52C97A]" /> SSL secured</div>
              <div className="flex items-center gap-1.5"><CreditCard size={11} className="text-[#52C97A]" /> Stripe payment</div>
              <div className="flex items-center gap-1.5"><RefreshCw size={11} className="text-[#52C97A]" /> Cancel anytime</div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// CHECKOUT SUCCESS PAGE
// ─────────────────────────────────────────────────────────────────────────────
export function CheckoutSuccessPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const sessionId = searchParams.get('session_id')
  const [status, setStatus] = useState<'loading' | 'success' | 'pending' | 'error'>('loading')
  const [details, setDetails] = useState<any>(null)

  useEffect(() => {
    if (!sessionId) { router.push('/subscription'); return }
    paymentsApi.verifySession(sessionId)
      .then(data => {
        setDetails(data)
        setStatus(data.status === 'success' ? 'success' : data.status === 'dev_mode' ? 'success' : 'pending')
      })
      .catch(() => setStatus('error'))
  }, [sessionId])

  return (
    <div className="min-h-screen bg-[#0A0A0F] flex items-center justify-center px-4">
      <div className="w-full max-w-[480px] text-center">
        {status === 'loading' && (
          <div className="flex flex-col items-center gap-4">
            <Spinner size={32} />
            <p className="text-[14px] text-[#6B6B7A]">Confirming your payment…</p>
          </div>
        )}

        {status === 'success' && (
          <Card>
            <div className="p-10 flex flex-col items-center gap-5">
              <div className="w-20 h-20 rounded-full bg-[#52C97A]/10 border border-[#52C97A]/20 flex items-center justify-center">
                <CheckCircle size={36} className="text-[#52C97A]" />
              </div>
              <div>
                <h1 className="font-serif text-[32px] font-normal mb-2">Payment Confirmed!</h1>
                <p className="text-[13px] text-[#6B6B7A]">Welcome to Vōgue·AI. Your subscription is now active.</p>
              </div>
              {details && (
                <div className="w-full bg-[#111118] border border-[#1E1E2E] rounded-[10px] p-4 text-left space-y-2.5">
                  {details.customer_email && (
                    <div className="flex justify-between text-[12px]">
                      <span className="text-[#6B6B7A]">Email</span>
                      <span>{details.customer_email}</span>
                    </div>
                  )}
                  {details.amount_paid > 0 && (
                    <div className="flex justify-between text-[12px]">
                      <span className="text-[#6B6B7A]">Amount</span>
                      <span>${details.amount_paid.toFixed(2)} {details.currency?.toUpperCase()}</span>
                    </div>
                  )}
                  <div className="flex justify-between text-[12px]">
                    <span className="text-[#6B6B7A]">Status</span>
                    <span className="text-[#52C97A] font-medium">Active</span>
                  </div>
                </div>
              )}
              <div className="flex flex-col gap-2.5 w-full">
                <Button onClick={() => router.push('/dashboard')} className="w-full">
                  Go to Dashboard <ArrowRight size={14} />
                </Button>
                <Button variant="ghost" onClick={() => router.push('/billing')} className="w-full">
                  View Billing Details
                </Button>
              </div>
            </div>
          </Card>
        )}

        {status === 'error' && (
          <Card>
            <div className="p-10 flex flex-col items-center gap-4">
              <div className="w-20 h-20 rounded-full bg-[#D4688A]/10 border border-[#D4688A]/20 flex items-center justify-center">
                <XCircle size={36} className="text-[#D4688A]" />
              </div>
              <div>
                <h1 className="font-serif text-[28px] font-normal mb-2">Payment Verification Failed</h1>
                <p className="text-[13px] text-[#6B6B7A]">We couldn't verify your payment. Please contact support if you were charged.</p>
              </div>
              <Button onClick={() => router.push('/subscription')} variant="ghost" className="w-full">Try Again</Button>
            </div>
          </Card>
        )}
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// BILLING PAGE (full account management)
// ─────────────────────────────────────────────────────────────────────────────
export function BillingPage() {
  const router = useRouter()
  const { user } = useAuthStore()
  const [subscription, setSubscription] = useState<Subscription | null>(null)
  const [invoices, setInvoices] = useState<any[]>([])
  const [paymentMethods, setPaymentMethods] = useState<any[]>([])
  const [plans, setPlans] = useState<SubscriptionPlan[]>([])
  const [loading, setLoading] = useState(true)
  const [portalLoading, setPortalLoading] = useState(false)
  const [cancelLoading, setCancelLoading] = useState(false)
  const [upgradeLoading, setUpgradeLoading] = useState<string | null>(null)

  useEffect(() => {
    Promise.allSettled([
      paymentsApi.current().then(setSubscription).catch(() => {}),
      paymentsApi.invoices().then((d: any) => setInvoices(d.invoices || [])).catch(() => setInvoices(_mockInvoices())),
      paymentsApi.paymentMethods().then((d: any) => setPaymentMethods(d.payment_methods || [])).catch(() => setPaymentMethods(_mockPMs())),
      paymentsApi.plans().then(setPlans).catch(() => setPlans(_mockPlans())),
    ]).finally(() => setLoading(false))
  }, [])

  const openPortal = async () => {
    setPortalLoading(true)
    try {
      const data = await paymentsApi.billingPortal()
      window.open(data.portal_url, '_blank')
    } catch {
      toast.error('Billing portal unavailable. Configure Stripe to enable.')
    } finally { setPortalLoading(false) }
  }

  const handleCancel = async () => {
    if (!confirm('Cancel your subscription? You\'ll keep access until the end of your billing period.')) return
    setCancelLoading(true)
    try {
      await paymentsApi.cancel(false)
      toast.success('Subscription will cancel at end of billing period')
      setSubscription(s => s ? { ...s, status: 'canceled' } : null)
    } catch { toast.error('Cancellation failed') } finally { setCancelLoading(false) }
  }

  const handleReactivate = async () => {
    try {
      await paymentsApi.reactivate()
      toast.success('Subscription reactivated!')
      setSubscription(s => s ? { ...s, status: 'active' } : null)
    } catch { toast.error('Reactivation failed') }
  }

  const handleUpgrade = async (planId: string, planName: string) => {
    setUpgradeLoading(planId)
    try {
      await paymentsApi.upgrade(planId)
      toast.success(`Upgraded to ${planName} plan!`)
      paymentsApi.current().then(setSubscription).catch(() => {})
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Upgrade failed')
    } finally { setUpgradeLoading(null) }
  }

  const currentPlanName = subscription?.plan?.name || 'Basic'
  const statusColor: Record<string, string> = {
    active: '#52C97A', trialing: '#4ECDC4', past_due: '#D4688A', canceled: '#6B6B7A',
  }

  return (
    <div className="min-h-screen bg-[#0A0A0F] p-6">
      <div className="max-w-[900px] mx-auto space-y-6 page-enter">
        <SectionHeader title="Billing & Subscription" subtitle="Manage your plan, payment methods and invoices" />

        {/* Current subscription */}
        <Card accentColor={statusColor[subscription?.status || 'active']}>
          <CardBody>
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-[#C9A96E]/10 border border-[#C9A96E]/20 flex items-center justify-center">
                  <Star size={20} className="text-[#C9A96E]" />
                </div>
                <div>
                  <div className="font-serif text-[22px] font-semibold mb-0.5">{currentPlanName} Plan</div>
                  <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full" style={{ background: statusColor[subscription?.status || 'active'] }} />
                    <span className="text-[12px] text-[#6B6B7A] capitalize">{subscription?.status || 'No active plan'}</span>
                    {subscription?.status === 'trialing' && <span className="text-[11px] text-[#4ECDC4]">· Free trial</span>}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2.5">
                {subscription?.status === 'canceled' ? (
                  <Button onClick={handleReactivate} size="sm" variant="outline">Reactivate</Button>
                ) : (
                  <Button onClick={handleCancel} loading={cancelLoading} size="sm" variant="danger">Cancel Plan</Button>
                )}
                <Button onClick={openPortal} loading={portalLoading} size="sm" variant="ghost">
                  <ExternalLink size={12} /> Billing Portal
                </Button>
              </div>
            </div>

            {subscription?.end_date && (
              <div className="mt-4 flex items-center gap-2 text-[11px] text-[#D4688A] bg-[#D4688A]/06 border border-[#D4688A]/15 rounded-[8px] px-3 py-2">
                <AlertTriangle size={12} />
                Subscription ends on {formatDate(subscription.end_date)}
              </div>
            )}
          </CardBody>
        </Card>

        {/* Upgrade options */}
        {plans.length > 0 && (
          <Card>
            <CardHeader><CardTitle>Available Plans</CardTitle><span className="text-[11px] text-[#6B6B7A]">Upgrade or downgrade anytime</span></CardHeader>
            <CardBody className="space-y-3">
              {plans.map(plan => {
                const meta = PLAN_META[plan.name] || { color: '#6B6B7A', icon: '◇' }
                const isCurrent = plan.name === currentPlanName
                return (
                  <div key={plan.id} className={`flex items-center justify-between p-4 rounded-[10px] border transition-all ${isCurrent ? 'border-[#C9A96E]/30 bg-[#C9A96E]/04' : 'border-[#1E1E2E] hover:border-[#1E1E2E]/80'}`}>
                    <div className="flex items-center gap-3">
                      <span style={{ color: meta.color, fontSize: 18 }}>{meta.icon}</span>
                      <div>
                        <div className="font-medium text-[13px]">{plan.name}</div>
                        <div className="text-[11px] text-[#6B6B7A]">${plan.price}/month</div>
                      </div>
                    </div>
                    {isCurrent ? (
                      <span className="text-[10px] text-[#C9A96E] bg-[#C9A96E]/10 border border-[#C9A96E]/20 px-3 py-1 rounded-full font-medium tracking-wider uppercase">Current</span>
                    ) : (
                      <Button
                        size="sm"
                        variant={plan.price > (subscription?.plan?.price || 0) ? 'primary' : 'ghost'}
                        loading={upgradeLoading === plan.id}
                        onClick={() => handleUpgrade(plan.id, plan.name)}>
                        {plan.price > (subscription?.plan?.price || 0) ? 'Upgrade' : 'Downgrade'}
                      </Button>
                    )}
                  </div>
                )
              })}
            </CardBody>
          </Card>
        )}

        <div className="grid grid-cols-2 gap-5">
          {/* Payment methods */}
          <Card>
            <CardHeader>
              <CardTitle>Payment Methods</CardTitle>
              <Button size="sm" variant="ghost" onClick={openPortal}>+ Add Card</Button>
            </CardHeader>
            <CardBody>
              {loading ? (
                <div className="space-y-3">{[1,2].map(i => <div key={i} className="shimmer h-14 rounded-[8px]" />)}</div>
              ) : paymentMethods.length === 0 ? (
                <div className="text-center py-6 text-[12px] text-[#6B6B7A]">No payment methods saved</div>
              ) : paymentMethods.map(pm => (
                <div key={pm.id} className="flex items-center justify-between p-3 bg-[#111118] border border-[#1E1E2E] rounded-[10px]">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-7 bg-[#1E1E2E] rounded-[4px] flex items-center justify-center">
                      <CreditCard size={14} className="text-[#6B6B7A]" />
                    </div>
                    <div>
                      <div className="text-[12px] font-medium capitalize">{pm.brand} ···· {pm.last4}</div>
                      <div className="text-[10px] text-[#6B6B7A]">Expires {pm.exp_month}/{pm.exp_year}</div>
                    </div>
                  </div>
                  {pm.is_default && <span className="text-[9px] text-[#52C97A] border border-[#52C97A]/30 bg-[#52C97A]/08 px-2 py-0.5 rounded-full tracking-wider">Default</span>}
                </div>
              ))}
            </CardBody>
          </Card>

          {/* Invoice history */}
          <Card>
            <CardHeader><CardTitle>Invoice History</CardTitle></CardHeader>
            <CardBody className="space-y-2">
              {loading ? (
                <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="shimmer h-12 rounded-[8px]" />)}</div>
              ) : invoices.length === 0 ? (
                <div className="text-center py-6 text-[12px] text-[#6B6B7A]">No invoices yet</div>
              ) : invoices.map(inv => (
                <div key={inv.id} className="flex items-center justify-between py-2.5 border-b border-[#1E1E2E]/40 last:border-0">
                  <div>
                    <div className="text-[12px] font-medium">{inv.description || `Invoice ${inv.number}`}</div>
                    <div className="text-[10px] text-[#6B6B7A]">{inv.period_start ? formatDate(inv.period_start) : 'N/A'}</div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <div className="text-[12px] font-medium">${typeof inv.amount_paid === 'number' ? inv.amount_paid.toFixed(2) : '0.00'}</div>
                      <div className={`text-[10px] ${inv.status === 'paid' ? 'text-[#52C97A]' : 'text-[#D4688A]'} capitalize`}>{inv.status}</div>
                    </div>
                    {inv.invoice_pdf && inv.invoice_pdf !== '#' && (
                      <a href={inv.invoice_pdf} target="_blank" rel="noopener noreferrer"
                        className="text-[#6B6B7A] hover:text-[#C9A96E] transition-colors">
                        <Download size={13} />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </CardBody>
          </Card>
        </div>

        {/* Security note */}
        <div className="flex items-center gap-4 p-4 bg-[#111118] border border-[#1E1E2E] rounded-[10px]">
          <Shield size={20} className="text-[#52C97A] flex-shrink-0" />
          <div>
            <div className="text-[12px] font-medium mb-0.5">Secure Payment Processing</div>
            <div className="text-[11px] text-[#6B6B7A]">All payments are processed by Stripe. We never store your full card details. Transactions are encrypted with TLS 1.3.</div>
          </div>
          <div className="flex gap-2 ml-auto flex-shrink-0">
            {['Stripe', 'PCI DSS', 'SSL'].map(b => (
              <span key={b} className="text-[9px] text-[#C9A96E] border border-[#C9A96E]/20 bg-[#C9A96E]/06 px-2 py-1 rounded-full tracking-wider">{b}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Mock data helpers ─────────────────────────────────────────────────────────
function _mockInvoices() {
  return [
    { id: '1', number: 'INV-0001', status: 'paid', amount_paid: 149, description: 'Pro Plan — April 2025', period_start: '2025-04-01', invoice_pdf: '#' },
    { id: '2', number: 'INV-0002', status: 'paid', amount_paid: 149, description: 'Pro Plan — March 2025', period_start: '2025-03-01', invoice_pdf: '#' },
    { id: '3', number: 'INV-0003', status: 'paid', amount_paid: 49,  description: 'Basic Plan — Feb 2025', period_start: '2025-02-01', invoice_pdf: '#' },
  ]
}
function _mockPMs() {
  return [{ id: 'pm_1', brand: 'visa', last4: '4242', exp_month: 12, exp_year: 2027, is_default: true }]
}
function _mockPlans(): SubscriptionPlan[] {
  return [
    { id: 'plan_basic',   name: 'Basic',   type: 'monthly', price: 49,  features: {}, is_active: true },
    { id: 'plan_pro',     name: 'Pro',     type: 'monthly', price: 149, features: {}, is_active: true },
    { id: 'plan_premium', name: 'Premium', type: 'monthly', price: 399, features: {}, is_active: true },
  ]
}

