'use client'
import { useRouter } from 'next/navigation'
import { useState, useEffect } from 'react'
import { colorsApi } from '@/lib/api'
import type { ColorPalette, ColorTrend } from '@/types'
import { Card, CardHeader, CardTitle, CardBody, Badge, SectionHeader, Sparkline, Progress } from '@/components/ui'
import { MOCK_SPARKLINE, formatPct } from '@/lib/utils'

const MOCK_PALETTE: ColorPalette = {
  season: 'Spring / Summer 2025',
  generated_at: new Date().toISOString(),
  colors: [
    { color_name: 'Butter Yellow', hex_code: '#F5E06E', percentage: 18.2, growth_rate: 52, trend_status: 'peak', category_breakdown: { Tops: 45, Dresses: 35, Accessories: 20 }, top_brands: ['Zara', 'H&M', 'ASOS'] },
    { color_name: 'Cobalt Blue', hex_code: '#2D5BE3', percentage: 14.1, growth_rate: 44, trend_status: 'peak', category_breakdown: { Dresses: 50, Outerwear: 30, Bottoms: 20 }, top_brands: ['Mango', 'Massimo Dutti'] },
    { color_name: 'Dusty Rose', hex_code: '#D4688A', percentage: 12.3, growth_rate: 28, trend_status: 'rising', category_breakdown: { Tops: 60, Accessories: 25, Shoes: 15 }, top_brands: ['& Other Stories', 'COS'] },
    { color_name: 'Sage Green', hex_code: '#8FAF8A', percentage: 10.4, growth_rate: 19, trend_status: 'rising', category_breakdown: { Knitwear: 55, Trousers: 30, Tops: 15 }, top_brands: ['Arket', 'Reiss'] },
    { color_name: 'Champagne', hex_code: '#C9A96E', percentage: 9.2, growth_rate: 14, trend_status: 'stable', category_breakdown: { Eveningwear: 60, Accessories: 40 }, top_brands: ['Ted Baker', 'Phase Eight'] },
    { color_name: 'Terracotta', hex_code: '#C4744A', percentage: 8.1, growth_rate: -6, trend_status: 'declining', category_breakdown: { Knitwear: 70, Accessories: 30 }, top_brands: ['Toast', 'Anthropologie'] },
    { color_name: 'Lavender Mist', hex_code: '#B8A9D4', percentage: 7.3, growth_rate: 33, trend_status: 'rising', category_breakdown: { Dresses: 65, Tops: 35 }, top_brands: ['Rixo', 'Reformation'] },
    { color_name: 'Forest', hex_code: '#2D5A3A', percentage: 5.9, growth_rate: 11, trend_status: 'stable', category_breakdown: { Outerwear: 70, Trousers: 30 }, top_brands: ['Barbour', 'Hunter'] },
    { color_name: 'Warm White', hex_code: '#F5F0E8', percentage: 5.4, growth_rate: 8, trend_status: 'stable', category_breakdown: { Tops: 55, Dresses: 45 }, top_brands: ['The White Company', 'Marks & Spencer'] },
    { color_name: 'Bordeaux', hex_code: '#7A2040', percentage: 4.2, growth_rate: -14, trend_status: 'declining', category_breakdown: { Knitwear: 80, Accessories: 20 }, top_brands: ['Hobbs'] },
    { color_name: 'Teal', hex_code: '#4ECDC4', percentage: 3.8, growth_rate: 41, trend_status: 'emerging', category_breakdown: { Swimwear: 55, Dresses: 45 }, top_brands: ['Boden', 'Joules'] },
    { color_name: 'Caramel', hex_code: '#C4874A', percentage: 3.1, growth_rate: 22, trend_status: 'rising', category_breakdown: { Accessories: 70, Footwear: 30 }, top_brands: ['Mulberry', 'Aspinal'] },
  ],
}

export function ColorsPage() {
  const [palette, setPalette] = useState<ColorPalette>(MOCK_PALETTE)
  const [selected, setSelected] = useState<ColorTrend | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    colorsApi.palette()
      .then(setPalette)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="p-6 max-w-[1400px] space-y-6 page-enter">
      <SectionHeader title="Color Trend Analyzer" subtitle={`${palette.season} · Extracted from 148K images via CNN Vision Model`} />

      <div className="grid grid-cols-3 gap-5">
        {/* Palette grid — 2 cols */}
        <div className="col-span-2 space-y-5">
          <Card>
            <CardHeader><CardTitle>Trending Palette</CardTitle><span className="text-[11px] text-[#6B6B7A]">Click a color to explore</span></CardHeader>
            <CardBody>
              <div className="flex flex-wrap gap-5">
                {palette.colors.map((c, i) => (
                  <button key={i} onClick={() => setSelected(selected?.color_name === c.color_name ? null : c)}
                    className={`flex flex-col items-center gap-2 group transition-all ${selected?.color_name === c.color_name ? 'scale-110' : 'hover:scale-105'}`}>
                    <div className="w-14 h-14 rounded-full border-2 transition-all shadow-lg"
                      style={{ background: c.hex_code, borderColor: selected?.color_name === c.color_name ? '#F0EEE8' : 'transparent', boxShadow: `0 4px 16px ${c.hex_code}44` }} />
                    <div className="text-[10px] text-[#6B6B7A] text-center max-w-[64px] leading-tight group-hover:text-[#F0EEE8]">{c.color_name}</div>
                    <div className="text-[10px] font-medium" style={{ color: c.growth_rate >= 0 ? '#52C97A' : '#D4688A' }}>{formatPct(c.growth_rate)}</div>
                  </button>
                ))}
              </div>
            </CardBody>
          </Card>

          {/* Color details */}
          {selected && (
            <Card accentColor={selected.hex_code}>
              <CardBody>
                <div className="flex items-start gap-5">
                  <div className="w-20 h-20 rounded-[12px] flex-shrink-0 shadow-lg" style={{ background: selected.hex_code, boxShadow: `0 8px 24px ${selected.hex_code}55` }} />
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-serif text-[22px] font-semibold">{selected.color_name}</h3>
                      <Badge status={selected.trend_status} />
                    </div>
                    <div className="text-[12px] text-[#6B6B7A] font-mono mb-4">{selected.hex_code}</div>
                    <div className="grid grid-cols-3 gap-4">
                      <div><div className="text-[10px] text-[#6B6B7A] uppercase tracking-wider mb-1">Share</div><div className="font-serif text-[20px] font-semibold" style={{ color: selected.hex_code }}>{selected.percentage}%</div></div>
                      <div><div className="text-[10px] text-[#6B6B7A] uppercase tracking-wider mb-1">Growth</div><div className={`font-serif text-[20px] font-semibold ${selected.growth_rate >= 0 ? 'text-[#52C97A]' : 'text-[#D4688A]'}`}>{formatPct(selected.growth_rate)}</div></div>
                      <div><div className="text-[10px] text-[#6B6B7A] uppercase tracking-wider mb-1">Top Brands</div><div className="text-[12px] text-[#F0EEE8]">{selected.top_brands.slice(0, 2).join(', ')}</div></div>
                    </div>
                    <div className="mt-4">
                      <div className="text-[10px] text-[#6B6B7A] uppercase tracking-wider mb-2">Category breakdown</div>
                      <div className="space-y-2">
                        {Object.entries(selected.category_breakdown).map(([cat, pct]) => (
                          <div key={cat} className="flex items-center gap-3">
                            <span className="text-[11px] text-[#6B6B7A] w-24">{cat}</span>
                            <Progress value={pct / 100} color={selected.hex_code} />
                            <span className="text-[11px] text-[#6B6B7A] w-8 text-right">{pct}%</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </CardBody>
            </Card>
          )}
        </div>

        {/* Side column */}
        <div className="space-y-4">
          <Card>
            <CardHeader><CardTitle>Rising Colors</CardTitle></CardHeader>
            <CardBody className="space-y-1">
              {palette.colors.filter(c => c.growth_rate > 20).sort((a, b) => b.growth_rate - a.growth_rate).map((c, i) => (
                <div key={i} className="flex items-center justify-between py-2.5 border-b border-[#1E1E2E]/40 last:border-0">
                  <div className="flex items-center gap-2.5">
                    <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ background: c.hex_code, boxShadow: `0 0 6px ${c.hex_code}66` }} />
                    <span className="text-[12px]">{c.color_name}</span>
                  </div>
                  <span className="text-[12px] font-medium text-[#52C97A]">{formatPct(c.growth_rate)}</span>
                </div>
              ))}
            </CardBody>
          </Card>
          <Card>
            <CardHeader><CardTitle>Declining Colors</CardTitle></CardHeader>
            <CardBody className="space-y-1">
              {palette.colors.filter(c => c.growth_rate < 0).sort((a, b) => a.growth_rate - b.growth_rate).map((c, i) => (
                <div key={i} className="flex items-center justify-between py-2.5 border-b border-[#1E1E2E]/40 last:border-0">
                  <div className="flex items-center gap-2.5">
                    <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ background: c.hex_code }} />
                    <span className="text-[12px] text-[#6B6B7A]">{c.color_name}</span>
                  </div>
                  <span className="text-[12px] font-medium text-[#D4688A]">{formatPct(c.growth_rate)}</span>
                </div>
              ))}
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  )
}

// ── AGENTS PAGE ───────────────────────────────────────────────────────────────
export function AgentsPage() {
  const [activeAgent, setActiveAgent] = useState(0)

  const agents = [
    { icon: '🤖', name: 'Agent 1: Trend Collector', color: '#C9A96E', status: 'active', task: 'Scanning 4 sources',
      stats: [{ label: 'Collected', value: '2.4M' }, { label: 'Alerts', value: '12' }, { label: 'Sources', value: '8' }],
      tasks: ['Continuous data collection from 8 sources', 'Source monitoring & deduplication', 'New trend detection alerts', 'Data quality validation & scoring'],
      desc: 'Continuously scrapes Instagram, TikTok, Pinterest, Google Trends every 15 minutes. Uses Apify API for high-volume collection with deduplication.' },
    { icon: '👁', name: 'Agent 2: Vision Analyzer', color: '#4ECDC4', status: 'active', task: 'Processing images',
      stats: [{ label: 'Analyzed', value: '148K' }, { label: 'Colors', value: '24' }, { label: 'Accuracy', value: '91%' }],
      tasks: ['Image classification by clothing type (CLIP ViT)', 'Dominant color extraction (K-means)', 'Pattern & texture detection', 'Style recognition and embedding'],
      desc: 'Uses OpenAI CLIP model for zero-shot image classification. Extracts color palettes via K-means clustering. Stores 512-dim embeddings in Pinecone for similarity search.' },
    { icon: '📊', name: 'Agent 3: Trend Analyzer', color: '#D4688A', status: 'active', task: 'Scoring hashtags',
      stats: [{ label: 'Hashtags', value: '38K' }, { label: 'Sentiment', value: '+0.73' }, { label: 'Score', value: '94.2' }],
      tasks: ['Hashtag frequency and virality analysis', 'Keyword extraction (KeyBERT)', 'Sentiment analysis on fashion content', 'Engagement-weighted trend scoring'],
      desc: 'NLP pipeline using KeyBERT for keyword extraction, TextBlob for sentiment. Computes engagement-weighted trend scores using likes, comments, shares weighting.' },
    { icon: '🔮', name: 'Agent 4: Forecast Agent', color: '#7C5CBF', status: 'active', task: 'Running LSTM',
      stats: [{ label: 'Predictions', value: '18' }, { label: 'Accuracy', value: '89%' }, { label: 'Horizon', value: '90 days' }],
      tasks: ['Time-series forecasting (Prophet + LSTM)', 'Seasonality pattern detection', 'Demand prediction and inventory signals', 'Risk/decline alerts for fading trends'],
      desc: 'Ensemble of Meta Prophet (seasonality), PyTorch LSTM (sequence), and XGBoost (features). Each model has graceful fallbacks. Results averaged with weighted confidence.' },
    { icon: '💡', name: 'Agent 5: Business Advisor', color: '#52C97A', status: 'active', task: 'Generating insights',
      stats: [{ label: 'Insights', value: '34' }, { label: 'Brands', value: '438' }, { label: 'Alerts', value: '7' }],
      tasks: ['Insight generation for boutique owners', 'What-to-stock recommendations via Claude', 'Market opportunity detection', 'Custom alert rule evaluation'],
      desc: 'Uses Claude with live trend context injected into system prompt. Generates personalized inventory recommendations per user. Evaluates custom alert thresholds every 5 minutes.' },
  ]

  const active = agents[activeAgent]

  return (
    <div className="p-6 max-w-[1400px] space-y-6 page-enter">
      <SectionHeader title="Multi-Agent AI System" subtitle="5 specialized agents running in parallel" />

      {/* Agent selector */}
      <div className="grid grid-cols-5 gap-3 page-enter-delay-1">
        {agents.map((a, i) => (
          <Card key={i} hover onClick={() => setActiveAgent(i)}
            className={i === activeAgent ? 'border-[#C9A96E]/40' : ''}
            accentColor={i === activeAgent ? a.color : undefined}>
            <div className="p-4 text-center">
              <div className="text-[28px] mb-2">{a.icon}</div>
              <div className="text-[11px] font-medium mb-1.5 leading-snug">{a.name.split(':')[1]?.trim()}</div>
              <div className="flex items-center justify-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-[#52C97A]" style={{ animation: 'pulseGold 2s infinite' }} />
                <span className="text-[10px] text-[#52C97A]">{a.task}</span>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Agent detail */}
      <Card accentColor={active.color} className="page-enter-delay-2">
        <CardHeader>
          <div className="flex items-center gap-3">
            <span className="text-[28px]">{active.icon}</span>
            <div>
              <CardTitle>{active.name}</CardTitle>
              <div className="flex items-center gap-1.5 mt-0.5">
                <div className="w-1.5 h-1.5 rounded-full bg-[#52C97A]" style={{ animation: 'pulseGold 2s infinite' }} />
                <span className="text-[11px] text-[#52C97A]">Active · {active.task}</span>
              </div>
            </div>
          </div>
          <div className="flex gap-6">
            {active.stats.map(s => (
              <div key={s.label} className="text-right">
                <div className="font-serif text-[22px] font-semibold" style={{ color: active.color }}>{s.value}</div>
                <div className="text-[10px] text-[#6B6B7A] capitalize">{s.label}</div>
              </div>
            ))}
          </div>
        </CardHeader>
        <CardBody className="space-y-4">
          <p className="text-[13px] text-[#6B6B7A] leading-relaxed">{active.desc}</p>
          <div>
            <div className="text-[10px] tracking-[0.12em] uppercase text-[#6B6B7A] mb-2.5">Capabilities</div>
            <div className="flex flex-wrap gap-2">
              {active.tasks.map((t, i) => (
                <div key={i} className="flex items-center gap-2 text-[12px] text-[#6B6B7A] bg-[#111118] border border-[#1E1E2E] px-3 py-1.5 rounded-[8px]">
                  <span style={{ color: active.color, fontSize: 8 }}>◆</span>{t}
                </div>
              ))}
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}

// ── REPORTS PAGE ──────────────────────────────────────────────────────────────
export function ReportsPage() {
  const [reports] = useState([
    { id: '1', title: 'Weekly Trends Report — Apr 28', report_type: 'weekly_trends', status: 'ready', created_at: '2025-04-28T09:00:00Z', filters: {} },
    { id: '2', title: 'Color Palette Q2 2025', report_type: 'color_palette', status: 'ready', created_at: '2025-04-26T14:30:00Z', filters: {} },
    { id: '3', title: 'Season Forecast — Summer 2025', report_type: 'season_forecast', status: 'ready', created_at: '2025-04-24T10:00:00Z', filters: {} },
    { id: '4', title: 'Recommendations Report', report_type: 'recommendations', status: 'generating', created_at: '2025-04-29T08:00:00Z', filters: {} },
  ])
  const [generating, setGenerating] = useState(false)
  const TYPE_ICONS: Record<string, string> = { weekly_trends: '📊', color_palette: '🎨', season_forecast: '🔮', recommendations: '💡', custom: '📄' }
  const TYPE_LABELS: Record<string, string> = { weekly_trends: 'Weekly Trends', color_palette: 'Color Palette', season_forecast: 'Season Forecast', recommendations: 'Recommendations', custom: 'Custom' }

  return (
    <div className="p-6 max-w-[1100px] space-y-6 page-enter">
      <SectionHeader title="Reports & Exports" subtitle="Downloadable trend reports and custom analytics" />

      <div className="grid grid-cols-3 gap-5">
        <div className="col-span-2 space-y-3">
          {reports.map(r => (
            <Card key={r.id} hover>
              <CardBody className="flex items-center gap-4">
                <div className="text-[28px] flex-shrink-0">{TYPE_ICONS[r.report_type] || '📄'}</div>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-[14px] mb-0.5">{r.title}</div>
                  <div className="flex items-center gap-3">
                    <span className="text-[11px] text-[#6B6B7A]">{TYPE_LABELS[r.report_type]}</span>
                    <span className="text-[#1E1E2E]">·</span>
                    <span className="text-[11px] text-[#6B6B7A]">{formatTimeAgo(r.created_at)}</span>
                  </div>
                </div>
                <div className="flex items-center gap-3 flex-shrink-0">
                  <Badge status={r.status} />
                  {r.status === 'ready' && (
                    <button className="text-[11px] text-[#C9A96E] border border-[#C9A96E]/30 rounded-[7px] px-3 py-1.5 hover:bg-[#C9A96E]/08 transition-colors">↓ Download</button>
                  )}
                </div>
              </CardBody>
            </Card>
          ))}
        </div>

        <Card>
          <CardHeader><CardTitle>Generate Report</CardTitle></CardHeader>
          <CardBody className="space-y-4">
            {[{ label: 'Report Type', options: [{ value: 'weekly_trends', label: 'Weekly Trends' }, { value: 'color_palette', label: 'Color Palette' }, { value: 'season_forecast', label: 'Season Forecast' }, { value: 'recommendations', label: 'Recommendations' }] },
              { label: 'Region', options: [{ value: 'all', label: 'Global' }, { value: 'europe', label: 'Europe' }, { value: 'asia', label: 'Asia' }, { value: 'americas', label: 'Americas' }] },
              { label: 'Format', options: [{ value: 'pdf', label: 'PDF' }, { value: 'excel', label: 'Excel (.xlsx)' }, { value: 'json', label: 'JSON' }] },
            ].map(f => (
              <div key={f.label}>
                <label className="text-[10px] tracking-[0.1em] uppercase text-[#6B6B7A] font-medium block mb-1.5">{f.label}</label>
                <select className="w-full bg-[#0A0A0F] border border-[#1E1E2E] rounded-[8px] px-3 py-2.5 text-[12px] text-[#F0EEE8] outline-none focus:border-[#C9A96E]/40">
                  {f.options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                </select>
              </div>
            ))}
            <button onClick={() => setGenerating(true)} className="w-full bg-[#C9A96E] text-[#0A0A0F] rounded-[8px] py-2.5 text-[13px] font-medium hover:bg-[#DCC08E] transition-colors mt-2">
              Generate Report ↗
            </button>
            <p className="text-[10px] text-[#6B6B7A] text-center">Reports require Pro or Premium plan</p>
          </CardBody>
        </Card>
      </div>
    </div>
  )
}

function formatTimeAgo(d: string) {
  const diff = Date.now() - new Date(d).getTime()
  const days = Math.floor(diff / 86400000)
  if (days === 0) return 'Today'
  if (days === 1) return 'Yesterday'
  return `${days} days ago`
}

// ── SUBSCRIPTION PAGE ─────────────────────────────────────────────────────────
export function SubscriptionPage() {
  const router = useRouter()
  const [billing, setBilling] = useState<'monthly' | 'yearly'>('monthly')
  const [selected, setSelected] = useState('Pro')

  const plans = [
    { name: 'Basic', price: { monthly: 49, yearly: 39 }, color: '#6B6B7A',
      features: ['Weekly trend reports', 'Top 10 trending colors', 'Basic style explorer', 'Email support', '1 user'] },
    { name: 'Pro', price: { monthly: 149, yearly: 119 }, color: '#C9A96E',
      features: ['Daily trend predictions', 'AI Advisor chat', 'Color palette generator', 'Custom reports (PDF/Excel)', 'Recommendation engine', '5 users', 'API access'] },
    { name: 'Premium', price: { monthly: 399, yearly: 319 }, color: '#7C5CBF',
      features: ['Everything in Pro', 'Real-time AI recommendations', 'Competitor tracking', 'Custom alert rules', 'White-label reports', 'Unlimited users', 'Priority support'] },
  ]

  return (
    <div className="p-6 max-w-[1100px] space-y-6 page-enter">
      <SectionHeader title="Subscription Plans" subtitle="Choose the intelligence tier for your fashion business" />

      {/* Billing toggle */}
      <div className="flex items-center gap-3 page-enter-delay-1">
        <div className="flex border border-[#1E1E2E] rounded-[10px] overflow-hidden">
          {(['monthly', 'yearly'] as const).map(b => (
            <button key={b} onClick={() => setBilling(b)}
              className={`px-5 py-2.5 text-[12px] font-medium capitalize transition-colors ${billing === b ? 'bg-[#C9A96E]/10 text-[#C9A96E]' : 'text-[#6B6B7A] hover:text-[#F0EEE8]'}`}>
              {b}
            </button>
          ))}
        </div>
        {billing === 'yearly' && <span className="text-[11px] text-[#52C97A] font-medium">Save up to 20%</span>}
      </div>

      {/* Plan cards */}
      <div className="grid grid-cols-3 gap-5 page-enter-delay-2">
        {plans.map(plan => {
          const isSelected = selected === plan.name
          const isCurrent = plan.name === 'Pro'
          return (
            <Card key={plan.name} hover onClick={() => setSelected(plan.name)}
              className={`cursor-pointer ${isSelected ? 'border-[#C9A96E]/40' : ''}`}
              accentColor={isSelected ? plan.color : undefined}>
              <div className="p-6">
                {isCurrent && (
                  <div className="inline-flex items-center gap-1 bg-[#C9A96E]/10 border border-[#C9A96E]/20 rounded-full px-2.5 py-0.5 text-[9px] tracking-[0.12em] uppercase text-[#C9A96E] font-medium mb-3">Current Plan</div>
                )}
                <div className="text-[10px] tracking-[0.14em] uppercase text-[#6B6B7A] mb-2 font-medium">{plan.name}</div>
                <div className="flex items-end gap-1 mb-1">
                  <span className="font-serif text-[40px] font-semibold" style={{ color: plan.color }}>${plan.price[billing]}</span>
                  <span className="text-[12px] text-[#6B6B7A] mb-2">/mo</span>
                </div>
                {billing === 'yearly' && <div className="text-[11px] text-[#52C97A] mb-4">Billed annually</div>}
                <ul className="space-y-2.5 mb-6 mt-4">
                  {plan.features.map((f, i) => (
                    <li key={i} className="flex items-center gap-2 text-[12px] text-[#6B6B7A]">
                      <span className="text-[#52C97A] text-[11px]">✓</span>{f}
                    </li>
                  ))}
                </ul>
                <button
                  className={`w-full py-2.5 rounded-[8px] text-[13px] font-medium transition-all ${isCurrent ? 'bg-[#C9A96E]/10 border border-[#C9A96E]/30 text-[#C9A96E]' : 'border border-[#1E1E2E] text-[#6B6B7A] hover:border-[#C9A96E]/30 hover:text-[#C9A96E]'}`}>
                  {isCurrent ? 'Current Plan' : `Upgrade to ${plan.name}`}
                </button>
              </div>
            </Card>
          )
        })}
      </div>

      {/* Payment info */}
      <Card className="page-enter-delay-3">
        <CardBody className="flex items-center justify-between">
          <div>
            <div className="font-serif text-[16px] font-semibold mb-1">Secure Payment</div>
            <div className="text-[12px] text-[#6B6B7A]">All plans include a 14-day free trial. Cancel anytime. No hidden fees.</div>
          </div>
          <div className="flex gap-3">
            {['Stripe', 'PayPal', 'SSL Secured'].map(b => (
              <span key={b} className="text-[10px] text-[#C9A96E] bg-[#C9A96E]/08 border border-[#C9A96E]/20 px-3 py-1.5 rounded-full tracking-wider">{b}</span>
            ))}
          </div>
        </CardBody>
      </Card>
    </div>
  )
}
