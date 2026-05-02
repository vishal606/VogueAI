'use client'
import { useState, useEffect } from 'react'
import { LineChart, Line, AreaChart, Area, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { TrendingUp, Database, Target, Users, Activity } from 'lucide-react'
import { trendsApi } from '@/lib/api'
import type { DashboardSummary, Trend } from '@/types'
import { StatCard, Card, CardHeader, CardTitle, CardBody, Badge, ScoreBar, Sparkline, ColorDot, Skeleton, SkeletonCard, Tag } from '@/components/ui'
import { STATUS_COLORS, CATEGORY_COLORS, MOCK_SPARKLINE, formatNum, formatPct, formatScore } from '@/lib/utils'

// ── Mock data when API not connected ─────────────────────────────────────────
const MOCK_TRENDS: Trend[] = [
  { id:'1', name:'Quiet Luxury', category:'Style', trend_score:94.2, growth_rate:38, region:'Global', status:'rising', date:'2025-04', color_hex:'#C9A96E', top_hashtags:['quietluxury'], source_breakdown:{}, created_at:'', updated_at:'' },
  { id:'2', name:'Butter Yellow', category:'Color', trend_score:88.1, growth_rate:52, region:'Europe', status:'peak', date:'2025-04', color_hex:'#F5E06E', top_hashtags:['butteryellow'], source_breakdown:{}, created_at:'', updated_at:'' },
  { id:'3', name:'Micro-Pleats', category:'Texture', trend_score:76.4, growth_rate:29, region:'Asia', status:'rising', date:'2025-04', color_hex:'#A8C4D4', top_hashtags:['micropleats'], source_breakdown:{}, created_at:'', updated_at:'' },
  { id:'4', name:'Cobalt Blue', category:'Color', trend_score:83.0, growth_rate:44, region:'Global', status:'peak', date:'2025-04', color_hex:'#2D5BE3', top_hashtags:['cobaltblue'], source_breakdown:{}, created_at:'', updated_at:'' },
  { id:'5', name:'Neo-Bohemian', category:'Style', trend_score:71.2, growth_rate:17, region:'Americas', status:'emerging', date:'2025-04', color_hex:'#D4688A', top_hashtags:['neoboho'], source_breakdown:{}, created_at:'', updated_at:'' },
  { id:'6', name:'Sculptural Bags', category:'Accessory', trend_score:67.8, growth_rate:22, region:'Global', status:'emerging', date:'2025-04', color_hex:'#7C5CBF', top_hashtags:['sculpturalbags'], source_breakdown:{}, created_at:'', updated_at:'' },
]

const CHART_DATA = Array.from({ length: 14 }, (_, i) => ({
  day: `Apr ${i + 15}`,
  Instagram: Math.round(68 + Math.sin(i * 0.8) * 18 + i * 1.5),
  TikTok: Math.round(72 + Math.sin(i * 0.6 + 1) * 22 + i * 2),
  Pinterest: Math.round(55 + Math.sin(i * 0.9) * 12 + i),
}))

const AGENTS = [
  { icon: '🤖', name: 'Trend Collector', task: 'Scanning 4 sources', color: '#C9A96E' },
  { icon: '👁', name: 'Vision Analyzer', task: 'Processing images', color: '#4ECDC4' },
  { icon: '📊', name: 'Trend Analyzer', task: 'Scoring hashtags', color: '#D4688A' },
  { icon: '🔮', name: 'Forecast Agent', task: 'Running LSTM', color: '#7C5CBF' },
  { icon: '💡', name: 'Business Advisor', task: 'Generating insights', color: '#52C97A' },
]

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [trends, setTrends] = useState<Trend[]>(MOCK_TRENDS)
  const [loading, setLoading] = useState(true)
  const [activeAgent, setActiveAgent] = useState(0)

  useEffect(() => {
    trendsApi.dashboard()
      .then(d => { setSummary(d); if (d.top_trends?.length) setTrends(d.top_trends) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const stats = [
    { label: 'Trends Tracked', value: summary ? summary.total_trends_tracked.toLocaleString() : '1,247', change: '+83 this week', color: '#C9A96E', icon: <TrendingUp size={14} /> },
    { label: 'Data Points / Day', value: summary ? formatNum(summary.data_points_today) : '2.4M', change: 'Social + E-comm', color: '#D4688A', icon: <Database size={14} /> },
    { label: 'Prediction Accuracy', value: summary ? `${summary.prediction_accuracy}%` : '89%', change: '↑ 3% vs last month', color: '#4ECDC4', icon: <Target size={14} /> },
    { label: 'Active Brands', value: summary ? summary.active_brands.toLocaleString() : '438', change: '+12 new this week', color: '#7C5CBF', icon: <Users size={14} /> },
  ]

  return (
    <div className="p-6 max-w-[1400px] space-y-6 page-enter">

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 page-enter-delay-1">
        {loading ? Array(4).fill(0).map((_, i) => <SkeletonCard key={i} />) : stats.map((s, i) => <StatCard key={i} {...s} />)}
      </div>

      {/* AI Agents */}
      <div className="page-enter-delay-2">
        <div className="text-[10px] tracking-[0.14em] uppercase text-[#6B6B7A] mb-3 font-medium">Multi-Agent AI System</div>
        <div className="grid grid-cols-5 gap-3">
          {AGENTS.map((a, i) => (
            <Card key={i} hover onClick={() => setActiveAgent(i)}
              className={activeAgent === i ? 'border-[#C9A96E]/40 bg-[#C9A96E]/04' : ''}
              accentColor={activeAgent === i ? a.color : undefined}>
              <div className="p-4 text-center">
                <div className="text-[24px] mb-2">{a.icon}</div>
                <div className="text-[11px] font-medium mb-1.5">{a.name}</div>
                <div className="flex items-center justify-center gap-1.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#52C97A]" style={{ animation: 'pulseGold 2s infinite' }} />
                  <span className="text-[10px] text-[#52C97A]">{a.task}</span>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-3 gap-5 page-enter-delay-3">

        {/* Trend Table — 2 cols */}
        <Card className="col-span-2">
          <CardHeader>
            <CardTitle>Top Trending Now</CardTitle>
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-[#52C97A]" style={{ animation: 'pulseGold 2s infinite' }} />
              <span className="text-[11px] text-[#6B6B7A]">Live</span>
            </div>
          </CardHeader>
          <CardBody className="p-0 pb-2">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Trend</th><th>Score</th><th>Growth</th><th>Region</th><th>Status</th>
                </tr>
              </thead>
              <tbody>
                {trends.map(t => (
                  <tr key={t.id}>
                    <td>
                      <div className="flex items-center gap-2.5">
                        <ColorDot color={t.color_hex} size={10} />
                        <div>
                          <div className="font-medium text-[13px]">{t.name}</div>
                          <div className="text-[10px] text-[#6B6B7A] uppercase tracking-[0.06em]">{t.category}</div>
                        </div>
                      </div>
                    </td>
                    <td><ScoreBar score={t.trend_score} color={t.color_hex || CATEGORY_COLORS[t.category] || '#C9A96E'} /></td>
                    <td><span className="text-[12px] font-medium text-[#52C97A]">{formatPct(t.growth_rate)}</span></td>
                    <td><span className="text-[12px] text-[#6B6B7A]">{t.region}</span></td>
                    <td><Badge status={t.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardBody>
        </Card>

        {/* Side column */}
        <div className="space-y-4">
          {/* Social sources */}
          <Card>
            <CardHeader>
              <CardTitle>Data Sources</CardTitle>
              <span className="text-[11px] text-[#6B6B7A]">Last 24h</span>
            </CardHeader>
            <CardBody className="space-y-1">
              {[
                { name: 'Instagram', posts: '2.4M', change: '+12%', color: '#E1306C', data: MOCK_SPARKLINE() },
                { name: 'TikTok',    posts: '5.1M', change: '+31%', color: '#FF0050', data: MOCK_SPARKLINE() },
                { name: 'Pinterest', posts: '890K', change: '+8%',  color: '#E60023', data: MOCK_SPARKLINE() },
                { name: 'Google',    posts: '340K', change: '+5%',  color: '#4285F4', data: MOCK_SPARKLINE() },
              ].map((s, i) => (
                <div key={i} className="flex items-center justify-between py-2 border-b border-[#1E1E2E]/40 last:border-0">
                  <div className="flex items-center gap-2.5">
                    <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: s.color }} />
                    <div>
                      <div className="text-[12px] font-medium">{s.name}</div>
                      <div className="text-[10px] text-[#6B6B7A]">{s.posts} posts</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Sparkline data={s.data} color={s.color} height={24} />
                    <span className="text-[11px] text-[#52C97A] font-medium w-9 text-right">{s.change}</span>
                  </div>
                </div>
              ))}
            </CardBody>
          </Card>

          {/* Top categories */}
          <Card>
            <CardHeader><CardTitle>By Category</CardTitle></CardHeader>
            <CardBody className="space-y-3">
              {[
                { cat: 'Style', count: 412, pct: 0.88 },
                { cat: 'Color', count: 289, pct: 0.74 },
                { cat: 'Texture', count: 178, pct: 0.56 },
                { cat: 'Accessory', count: 134, pct: 0.44 },
                { cat: 'Footwear', count: 89, pct: 0.32 },
              ].map(c => (
                <div key={c.cat}>
                  <div className="flex justify-between mb-1">
                    <span className="text-[12px]" style={{ color: CATEGORY_COLORS[c.cat] }}>{c.cat}</span>
                    <span className="text-[11px] text-[#6B6B7A]">{c.count}</span>
                  </div>
                  <div className="h-[3px] bg-[#1E1E2E] rounded-full overflow-hidden">
                    <div style={{ width: `${c.pct * 100}%`, height: '100%', background: CATEGORY_COLORS[c.cat], borderRadius: 3, transition: 'width 0.8s cubic-bezier(0.16,1,0.3,1)' }} />
                  </div>
                </div>
              ))}
            </CardBody>
          </Card>
        </div>
      </div>

      {/* Engagement chart */}
      <Card className="page-enter-delay-4">
        <CardHeader>
          <CardTitle>Platform Engagement — Last 14 Days</CardTitle>
          <div className="flex items-center gap-4">
            {[{ label: 'Instagram', color: '#E1306C' }, { label: 'TikTok', color: '#FF0050' }, { label: 'Pinterest', color: '#E60023' }].map(l => (
              <div key={l.label} className="flex items-center gap-1.5">
                <div className="w-2.5 h-2.5 rounded-sm" style={{ background: l.color }} />
                <span className="text-[11px] text-[#6B6B7A]">{l.label}</span>
              </div>
            ))}
          </div>
        </CardHeader>
        <CardBody>
          <ResponsiveContainer width="100%" height={180}>
            <AreaChart data={CHART_DATA} margin={{ top: 5, right: 5, bottom: 0, left: -20 }}>
              <defs>
                {[{ id: 'ig', color: '#E1306C' }, { id: 'tt', color: '#FF0050' }, { id: 'pi', color: '#E60023' }].map(g => (
                  <linearGradient key={g.id} id={g.id} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={g.color} stopOpacity={0.15} />
                    <stop offset="95%" stopColor={g.color} stopOpacity={0} />
                  </linearGradient>
                ))}
              </defs>
              <XAxis dataKey="day" tick={{ fill: '#6B6B7A', fontSize: 10 }} axisLine={false} tickLine={false} interval={2} />
              <YAxis tick={{ fill: '#6B6B7A', fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: '#16161F', border: '1px solid #1E1E2E', borderRadius: 8, fontSize: 12, fontFamily: 'var(--font-sans)' }} />
              <Area type="monotone" dataKey="Instagram" stroke="#E1306C" strokeWidth={1.5} fill="url(#ig)" dot={false} />
              <Area type="monotone" dataKey="TikTok" stroke="#FF0050" strokeWidth={1.5} fill="url(#tt)" dot={false} />
              <Area type="monotone" dataKey="Pinterest" stroke="#E60023" strokeWidth={1.5} fill="url(#pi)" dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </CardBody>
      </Card>
    </div>
  )
}
