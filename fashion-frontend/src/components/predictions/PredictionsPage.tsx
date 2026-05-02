'use client'
import { useState, useEffect } from 'react'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, ReferenceLine } from 'recharts'
import { Sparkles, Cpu, TrendingUp } from 'lucide-react'
import { predictionsApi } from '@/lib/api'
import type { SeasonForecast, TrendPrediction } from '@/types'
import { Card, CardHeader, CardTitle, CardBody, Progress, Button, SectionHeader, Tag, Skeleton } from '@/components/ui'

const MOCK_SEASONS: SeasonForecast[] = [
  { season: 'Summer 2025', trend_name: 'Fluid Metallics', confidence: 87, description: 'Liquid silver and gold fabrics dominating resort collections globally.', predicted_score: 82, key_factors: ['social_momentum', 'runway_adoption', 'search_volume'] },
  { season: 'Fall 2025', trend_name: 'Deep Forest Palette', confidence: 79, description: 'Mossy greens, earth browns, bark neutrals replacing maximalist brights.', predicted_score: 74, key_factors: ['color_cycle', 'sustainability', 'seasonal_pattern'] },
  { season: 'Winter 2025', trend_name: 'Artisan Knitwear', confidence: 91, description: 'Handcraft-aesthetic chunky knits with visible texture and raw edges.', predicted_score: 88, key_factors: ['engagement_rate', 'e_commerce_demand', 'designer_adoption'] },
  { season: 'Spring 2026', trend_name: 'Gossamer Layers', confidence: 72, description: 'Ultra-sheer, weight-free fabrics in tonal layered compositions.', predicted_score: 68, key_factors: ['emerging_signal', 'influencer_adoption'] },
]

const MOCK_PREDICTIONS: TrendPrediction[] = Array.from({ length: 30 }, (_, i) => ({
  id: String(i), trend_id: '1', model_used: i % 3 === 0 ? 'prophet' : i % 3 === 1 ? 'lstm' : 'xgboost',
  predicted_value: 60 + Math.sin(i * 0.4) * 20 + i * 0.8,
  prediction_date: new Date(Date.now() + i * 86400000).toISOString().split('T')[0],
  confidence: 0.85 - i * 0.008, horizon_days: i + 1,
  lower_bound: 55 + i * 0.5, upper_bound: 70 + i * 1.2,
  factors: {}, season: 'Summer 2025', created_at: '',
}))

const CHART_DATA = MOCK_PREDICTIONS.map((p, i) => ({
  day: `Day ${i + 1}`,
  prophet: p.model_used === 'prophet' ? p.predicted_value : null,
  lstm: p.model_used === 'lstm' ? p.predicted_value : null,
  xgboost: p.model_used === 'xgboost' ? p.predicted_value : null,
  lower: p.lower_bound,
  upper: p.upper_bound,
}))

const RADAR_DATA = [
  { factor: 'Social', prophet: 85, lstm: 78, xgboost: 82 },
  { factor: 'Search', prophet: 72, lstm: 80, xgboost: 75 },
  { factor: 'E-comm', prophet: 68, lstm: 71, xgboost: 79 },
  { factor: 'Runway', prophet: 90, lstm: 85, xgboost: 82 },
  { factor: 'Sentiment', prophet: 77, lstm: 83, xgboost: 70 },
  { factor: 'Growth', prophet: 82, lstm: 76, xgboost: 85 },
]

const MODELS = [
  { name: 'Prophet', color: '#C9A96E', desc: 'Meta Prophet — seasonality-aware time-series with fashion quarter patterns', accuracy: 87 },
  { name: 'LSTM', color: '#4ECDC4', desc: 'PyTorch LSTM — deep sequence model with 30-day look-back window', accuracy: 82 },
  { name: 'XGBoost', color: '#D4688A', desc: 'Feature-based ensemble — lag features, rolling stats, engagement signals', accuracy: 79 },
]

const CONFIDENCE_COLORS: Record<number, string> = {}
const getConfColor = (c: number) => c >= 85 ? '#52C97A' : c >= 70 ? '#C9A96E' : '#D4688A'

export default function PredictionsPage() {
  const [seasons, setSeasons] = useState<SeasonForecast[]>(MOCK_SEASONS)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [activeModel, setActiveModel] = useState('All')

  useEffect(() => {
    predictionsApi.seasons()
      .then(setSeasons)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="p-6 max-w-[1400px] space-y-6 page-enter">
      <SectionHeader
        title="Season Forecasts"
        subtitle="AI-powered predictions using Prophet + LSTM + XGBoost ensemble"
        action={
          <Button loading={generating} onClick={() => {}} variant="outline" size="sm">
            <Sparkles size={13} /> Generate New
          </Button>
        }
      />

      {/* Season cards */}
      <div className="grid grid-cols-2 gap-4 page-enter-delay-1">
        {(loading ? Array(4).fill(null) : seasons).map((s, i) => (
          s === null ? (
            <Card key={i}><div className="p-5 space-y-3"><div className="shimmer h-3 w-24 rounded" /><div className="shimmer h-6 w-48 rounded" /><div className="shimmer h-3 w-full rounded" /></div></Card>
          ) : (
            <Card key={i} hover accentColor={getConfColor(s.confidence)} className="border-l-[2px]" style={{ borderLeftColor: getConfColor(s.confidence) } as React.CSSProperties}>
              <div className="p-5">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="text-[10px] tracking-[0.12em] uppercase font-medium mb-1.5" style={{ color: getConfColor(s.confidence) }}>{s.season}</div>
                    <h3 className="font-serif text-[22px] font-semibold">{s.trend_name}</h3>
                  </div>
                  <div className="text-right flex-shrink-0 ml-4">
                    <div className="font-serif text-[28px] font-semibold" style={{ color: getConfColor(s.confidence) }}>{s.confidence}%</div>
                    <div className="text-[10px] text-[#6B6B7A]">confidence</div>
                  </div>
                </div>
                <p className="text-[12px] text-[#6B6B7A] leading-relaxed mb-4">{s.description}</p>
                <Progress value={s.confidence / 100} color={getConfColor(s.confidence)} height={3} />
                <div className="flex items-center justify-between mt-3">
                  <div className="flex gap-1.5 flex-wrap">
                    {s.key_factors.map(f => (
                      <span key={f} className="text-[9px] text-[#6B6B7A] bg-[#1E1E2E] px-2 py-0.5 rounded tracking-wider uppercase">{f.replace('_', ' ')}</span>
                    ))}
                  </div>
                  <div className="text-[11px] text-[#6B6B7A]">Score: <span className="text-[#F0EEE8] font-medium">{s.predicted_score}</span></div>
                </div>
              </div>
            </Card>
          )
        ))}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-3 gap-5 page-enter-delay-2">
        {/* Forecast chart — 2 cols */}
        <Card className="col-span-2">
          <CardHeader>
            <CardTitle>30-Day Trend Trajectory</CardTitle>
            <div className="flex gap-2">
              {['All', ...MODELS.map(m => m.name)].map(m => (
                <button key={m} onClick={() => setActiveModel(m)}
                  className={`text-[10px] px-2.5 py-1 rounded border transition-all ${activeModel === m ? 'border-[#C9A96E]/40 text-[#C9A96E] bg-[#C9A96E]/08' : 'border-[#1E1E2E] text-[#6B6B7A]'}`}>
                  {m}
                </button>
              ))}
            </div>
          </CardHeader>
          <CardBody>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={CHART_DATA} margin={{ top: 5, right: 5, bottom: 0, left: -20 }}>
                <defs>
                  <linearGradient id="gBand" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#C9A96E" stopOpacity={0.08} />
                    <stop offset="95%" stopColor="#C9A96E" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="day" tick={{ fill: '#6B6B7A', fontSize: 10 }} axisLine={false} tickLine={false} interval={4} />
                <YAxis tick={{ fill: '#6B6B7A', fontSize: 10 }} axisLine={false} tickLine={false} domain={[40, 100]} />
                <Tooltip contentStyle={{ background: '#16161F', border: '1px solid #1E1E2E', borderRadius: 8, fontSize: 11, fontFamily: 'var(--font-sans)' }} />
                <Area type="monotone" dataKey="upper" stroke="transparent" fill="url(#gBand)" />
                {(activeModel === 'All' || activeModel === 'Prophet') && <Area type="monotone" dataKey="prophet" stroke="#C9A96E" strokeWidth={1.5} fill="transparent" dot={false} connectNulls />}
                {(activeModel === 'All' || activeModel === 'LSTM') && <Area type="monotone" dataKey="lstm" stroke="#4ECDC4" strokeWidth={1.5} fill="transparent" dot={false} connectNulls />}
                {(activeModel === 'All' || activeModel === 'XGBoost') && <Area type="monotone" dataKey="xgboost" stroke="#D4688A" strokeWidth={1.5} fill="transparent" dot={false} connectNulls />}
                <ReferenceLine y={80} stroke="#1E1E2E" strokeDasharray="3 3" label={{ value: 'Peak threshold', fill: '#6B6B7A', fontSize: 10 }} />
              </AreaChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>

        {/* Radar — 1 col */}
        <Card>
          <CardHeader><CardTitle>Feature Importance</CardTitle></CardHeader>
          <CardBody>
            <ResponsiveContainer width="100%" height={200}>
              <RadarChart data={RADAR_DATA}>
                <PolarGrid stroke="#1E1E2E" />
                <PolarAngleAxis dataKey="factor" tick={{ fill: '#6B6B7A', fontSize: 10 }} />
                <Radar name="Prophet" dataKey="prophet" stroke="#C9A96E" fill="#C9A96E" fillOpacity={0.1} strokeWidth={1.5} />
                <Radar name="LSTM" dataKey="lstm" stroke="#4ECDC4" fill="#4ECDC4" fillOpacity={0.08} strokeWidth={1.5} />
              </RadarChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>
      </div>

      {/* Model cards */}
      <div className="page-enter-delay-3">
        <div className="text-[10px] tracking-[0.14em] uppercase text-[#6B6B7A] mb-3">Model Architecture</div>
        <div className="grid grid-cols-3 gap-4">
          {MODELS.map(m => (
            <Card key={m.name} accentColor={m.color}>
              <div className="p-4">
                <div className="flex items-center gap-2.5 mb-3">
                  <Cpu size={14} style={{ color: m.color }} />
                  <div className="font-medium text-[13px]">{m.name}</div>
                  <span className="ml-auto text-[11px] font-medium" style={{ color: m.color }}>{m.accuracy}% acc.</span>
                </div>
                <p className="text-[11px] text-[#6B6B7A] leading-relaxed mb-3">{m.desc}</p>
                <Progress value={m.accuracy / 100} color={m.color} height={3} />
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
