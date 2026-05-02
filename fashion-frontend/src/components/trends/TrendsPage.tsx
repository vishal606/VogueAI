'use client'
import { useState, useEffect, useCallback } from 'react'
import { Search, SlidersHorizontal, TrendingUp, TrendingDown, X } from 'lucide-react'
import { trendsApi } from '@/lib/api'
import type { Trend, TrendFilter, TrendStatus } from '@/types'
import { Card, CardHeader, CardTitle, CardBody, Badge, ScoreBar, Sparkline, ColorDot, Button, SectionHeader, Skeleton, Empty } from '@/components/ui'
import { STATUS_COLORS, CATEGORY_COLORS, MOCK_SPARKLINE, formatPct, useDebounce } from '@/lib/utils'

const MOCK_TRENDS: Trend[] = [
  { id:'1', name:'Quiet Luxury', category:'Style', trend_score:94.2, growth_rate:38, region:'Global', status:'rising', date:'2025-04', color_hex:'#C9A96E', top_hashtags:['quietluxury','minimalist'], source_breakdown:{}, created_at:'2025-04-01', updated_at:'' },
  { id:'2', name:'Butter Yellow', category:'Color', trend_score:88.1, growth_rate:52, region:'Europe', status:'peak', date:'2025-04', color_hex:'#F5E06E', top_hashtags:['butteryellow'], source_breakdown:{}, created_at:'2025-04-01', updated_at:'' },
  { id:'3', name:'Micro-Pleats', category:'Texture', trend_score:76.4, growth_rate:29, region:'Asia', status:'rising', date:'2025-04', color_hex:'#A8C4D4', top_hashtags:['micropleats'], source_breakdown:{}, created_at:'2025-04-01', updated_at:'' },
  { id:'4', name:'Cobalt Blue', category:'Color', trend_score:83.0, growth_rate:44, region:'Global', status:'peak', date:'2025-04', color_hex:'#2D5BE3', top_hashtags:['cobaltblue'], source_breakdown:{}, created_at:'2025-04-01', updated_at:'' },
  { id:'5', name:'Neo-Bohemian', category:'Style', trend_score:71.2, growth_rate:17, region:'Americas', status:'emerging', date:'2025-04', color_hex:'#D4688A', top_hashtags:['neoboho'], source_breakdown:{}, created_at:'2025-04-01', updated_at:'' },
  { id:'6', name:'Sculptural Bags', category:'Accessory', trend_score:67.8, growth_rate:22, region:'Global', status:'emerging', date:'2025-04', color_hex:'#7C5CBF', top_hashtags:['sculpturalbags'], source_breakdown:{}, created_at:'2025-04-01', updated_at:'' },
  { id:'7', name:'Sage Green', category:'Color', trend_score:62.3, growth_rate:14, region:'Americas', status:'stable', date:'2025-04', color_hex:'#8FAF8A', top_hashtags:['sagegreen'], source_breakdown:{}, created_at:'2025-04-01', updated_at:'' },
  { id:'8', name:'Chunky Loafers', category:'Footwear', trend_score:58.9, growth_rate:-8, region:'Europe', status:'declining', date:'2025-04', color_hex:'#8B6F47', top_hashtags:['chunkloafers'], source_breakdown:{}, created_at:'2025-04-01', updated_at:'' },
  { id:'9', name:'Sheer Layering', category:'Texture', trend_score:55.1, growth_rate:33, region:'Global', status:'emerging', date:'2025-04', color_hex:'#E8D5C4', top_hashtags:['sheerfabric'], source_breakdown:{}, created_at:'2025-04-01', updated_at:'' },
  { id:'10', name:'Platform Boots', category:'Footwear', trend_score:79.4, growth_rate:25, region:'Asia', status:'rising', date:'2025-04', color_hex:'#2A2A32', top_hashtags:['platformboots'], source_breakdown:{}, created_at:'2025-04-01', updated_at:'' },
]

const CATEGORIES = ['All', 'Style', 'Color', 'Texture', 'Accessory', 'Footwear', 'Outerwear']
const REGIONS = ['All', 'Global', 'Europe', 'Asia', 'Americas']
const STATUSES: Array<{ value: string; label: string }> = [
  { value: 'all', label: 'All Status' },
  { value: 'emerging', label: 'Emerging' },
  { value: 'rising', label: 'Rising' },
  { value: 'peak', label: 'Peak' },
  { value: 'declining', label: 'Declining' },
]

export default function TrendsPage() {
  const [trends, setTrends] = useState<Trend[]>(MOCK_TRENDS)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('All')
  const [region, setRegion] = useState('All')
  const [status, setStatus] = useState('all')
  const [sortBy, setSortBy] = useState<'trend_score' | 'growth_rate'>('trend_score')
  const [view, setView] = useState<'table' | 'grid'>('table')
  const [total, setTotal] = useState(0)

  const debouncedSearch = useDebounce(search, 400)

  const fetchTrends = useCallback(async () => {
    setLoading(true)
    try {
      const params: TrendFilter = {
        sort_by: sortBy, sort_order: 'desc', page_size: 20,
        ...(debouncedSearch && { search: debouncedSearch }),
        ...(category !== 'All' && { category }),
        ...(region !== 'All' && { region }),
        ...(status !== 'all' && { status: status as TrendStatus }),
      }
      const res = await trendsApi.list(params)
      setTrends(res.trends)
      setTotal(res.total)
    } catch {
      // Keep mock data
      setTrends(MOCK_TRENDS.filter(t => {
        if (category !== 'All' && t.category !== category) return false
        if (region !== 'All' && t.region !== region) return false
        if (status !== 'all' && t.status !== status) return false
        if (debouncedSearch && !t.name.toLowerCase().includes(debouncedSearch.toLowerCase())) return false
        return true
      }))
    } finally { setLoading(false) }
  }, [debouncedSearch, category, region, status, sortBy])

  useEffect(() => { fetchTrends() }, [fetchTrends])

  const clearFilters = () => { setSearch(''); setCategory('All'); setRegion('All'); setStatus('all') }
  const hasFilters = search || category !== 'All' || region !== 'All' || status !== 'all'

  return (
    <div className="p-6 max-w-[1400px] space-y-5 page-enter">
      <SectionHeader title="Live Trend Intelligence" subtitle="Updated every 15 minutes from 8 data sources" />

      {/* Filter bar */}
      <div className="flex items-center gap-3 flex-wrap page-enter-delay-1">
        {/* Search */}
        <div className="relative flex-1 min-w-[220px] max-w-[300px]">
          <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#6B6B7A]" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search trends…"
            className="w-full bg-[#16161F] border border-[#1E1E2E] rounded-[8px] pl-9 pr-3 py-2.5 text-[13px] text-[#F0EEE8] placeholder-[#6B6B7A] outline-none focus:border-[#C9A96E]/40 transition-colors" />
        </div>

        {/* Category filter */}
        <div className="flex items-center gap-1.5 flex-wrap">
          {CATEGORIES.map(c => (
            <button key={c} onClick={() => setCategory(c)}
              className={`px-3 py-1.5 rounded-[7px] text-[11px] font-medium border transition-all ${category === c ? 'border-[#C9A96E]/40 bg-[#C9A96E]/08 text-[#C9A96E]' : 'border-[#1E1E2E] text-[#6B6B7A] hover:text-[#F0EEE8]'}`}>
              {c}
            </button>
          ))}
        </div>

        {/* Status */}
        <select value={status} onChange={e => setStatus(e.target.value)}
          className="bg-[#16161F] border border-[#1E1E2E] rounded-[8px] px-3 py-2.5 text-[12px] text-[#6B6B7A] outline-none focus:border-[#C9A96E]/40">
          {STATUSES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
        </select>

        {/* Region */}
        <select value={region} onChange={e => setRegion(e.target.value)}
          className="bg-[#16161F] border border-[#1E1E2E] rounded-[8px] px-3 py-2.5 text-[12px] text-[#6B6B7A] outline-none focus:border-[#C9A96E]/40">
          {REGIONS.map(r => <option key={r} value={r}>{r}</option>)}
        </select>

        {/* Sort */}
        <select value={sortBy} onChange={e => setSortBy(e.target.value as any)}
          className="bg-[#16161F] border border-[#1E1E2E] rounded-[8px] px-3 py-2.5 text-[12px] text-[#6B6B7A] outline-none focus:border-[#C9A96E]/40">
          <option value="trend_score">Sort: Score</option>
          <option value="growth_rate">Sort: Growth</option>
        </select>

        {/* View toggle */}
        <div className="flex border border-[#1E1E2E] rounded-[8px] overflow-hidden ml-auto">
          {(['table', 'grid'] as const).map(v => (
            <button key={v} onClick={() => setView(v)}
              className={`px-3 py-2 text-[11px] transition-colors ${view === v ? 'bg-[#C9A96E]/10 text-[#C9A96E]' : 'text-[#6B6B7A] hover:text-[#F0EEE8]'}`}>
              {v === 'table' ? '≡' : '⊞'}
            </button>
          ))}
        </div>

        {hasFilters && (
          <button onClick={clearFilters} className="flex items-center gap-1 text-[11px] text-[#D4688A] hover:text-[#D4688A]/80 transition-colors">
            <X size={11} /> Clear
          </button>
        )}
      </div>

      {/* Results count */}
      <div className="text-[11px] text-[#6B6B7A]">{trends.length} trends {hasFilters ? 'matching filters' : 'total'}</div>

      {/* TABLE VIEW */}
      {view === 'table' && (
        <Card className="page-enter-delay-2">
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ width: 36 }}>#</th>
                  <th>Trend</th>
                  <th>Score</th>
                  <th>Growth</th>
                  <th>Hashtags</th>
                  <th>Region</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {loading
                  ? Array(8).fill(0).map((_, i) => (
                    <tr key={i}>
                      {Array(7).fill(0).map((_, j) => (
                        <td key={j}><div className="shimmer h-4 rounded w-full" /></td>
                      ))}
                    </tr>
                  ))
                  : trends.map((t, i) => (
                    <tr key={t.id}>
                      <td className="text-[#6B6B7A] text-[11px]">{String(i + 1).padStart(2, '0')}</td>
                      <td>
                        <div className="flex items-center gap-2.5">
                          <ColorDot color={t.color_hex} size={10} />
                          <div>
                            <div className="font-medium">{t.name}</div>
                            <div className="text-[10px] text-[#6B6B7A] uppercase tracking-wider">{t.category}</div>
                          </div>
                        </div>
                      </td>
                      <td>
                        <div className="flex items-center gap-3">
                          <ScoreBar score={t.trend_score} color={t.color_hex || CATEGORY_COLORS[t.category] || '#C9A96E'} />
                        </div>
                      </td>
                      <td>
                        <div className="flex items-center gap-1">
                          {t.growth_rate >= 0 ? <TrendingUp size={12} className="text-[#52C97A]" /> : <TrendingDown size={12} className="text-[#D4688A]" />}
                          <span className={`text-[12px] font-medium ${t.growth_rate >= 0 ? 'text-[#52C97A]' : 'text-[#D4688A]'}`}>{formatPct(t.growth_rate)}</span>
                        </div>
                      </td>
                      <td>
                        <div className="flex gap-1 flex-wrap max-w-[160px]">
                          {(t.top_hashtags || []).slice(0, 2).map(h => (
                            <span key={h} className="text-[10px] text-[#C9A96E] bg-[#C9A96E]/08 px-1.5 py-0.5 rounded">#{h}</span>
                          ))}
                        </div>
                      </td>
                      <td><span className="text-[12px] text-[#6B6B7A]">{t.region}</span></td>
                      <td><Badge status={t.status} /></td>
                    </tr>
                  ))
                }
              </tbody>
            </table>
            {!loading && trends.length === 0 && (
              <Empty icon="🔍" title="No trends found" description="Try adjusting your filters" />
            )}
          </div>
        </Card>
      )}

      {/* GRID VIEW */}
      {view === 'grid' && (
        <div className="grid grid-cols-3 gap-4 page-enter-delay-2">
          {loading
            ? Array(9).fill(0).map((_, i) => (
              <Card key={i}><div className="p-4 space-y-3"><div className="shimmer h-4 w-24 rounded" /><div className="shimmer h-8 w-32 rounded" /></div></Card>
            ))
            : trends.map(t => (
              <Card key={t.id} hover accentColor={t.color_hex}>
                <div className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <ColorDot color={t.color_hex} size={12} />
                      <div>
                        <div className="font-medium text-[14px]">{t.name}</div>
                        <div className="text-[10px] text-[#6B6B7A] uppercase tracking-wider">{t.category}</div>
                      </div>
                    </div>
                    <Badge status={t.status} />
                  </div>
                  <Sparkline data={MOCK_SPARKLINE()} color={t.color_hex || '#C9A96E'} height={36} />
                  <div className="flex items-center justify-between mt-3">
                    <div>
                      <div className="font-serif text-[22px] font-semibold" style={{ color: t.color_hex || '#C9A96E' }}>{t.trend_score.toFixed(0)}</div>
                      <div className="text-[10px] text-[#6B6B7A]">Score</div>
                    </div>
                    <div className="text-right">
                      <div className={`text-[14px] font-medium ${t.growth_rate >= 0 ? 'text-[#52C97A]' : 'text-[#D4688A]'}`}>{formatPct(t.growth_rate)}</div>
                      <div className="text-[10px] text-[#6B6B7A]">{t.region}</div>
                    </div>
                  </div>
                  {t.top_hashtags && t.top_hashtags.length > 0 && (
                    <div className="flex gap-1 mt-2.5 flex-wrap">
                      {t.top_hashtags.slice(0, 3).map(h => (
                        <span key={h} className="text-[10px] text-[#C9A96E] bg-[#C9A96E]/08 px-1.5 py-0.5 rounded">#{h}</span>
                      ))}
                    </div>
                  )}
                </div>
              </Card>
            ))
          }
        </div>
      )}
    </div>
  )
}
