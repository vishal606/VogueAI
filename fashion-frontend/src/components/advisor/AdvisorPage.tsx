'use client'
import { useState, useRef, useEffect } from 'react'
import { Send, Sparkles, RotateCcw, Copy, Check, Zap } from 'lucide-react'
import { advisorApi } from '@/lib/api'
import { useChatStore } from '@/lib/store'
import type { AdvisorMessage } from '@/types'
import { Card, CardHeader, CardTitle, CardBody, Button, Spinner, SectionHeader } from '@/components/ui'
import { formatTimeAgo } from '@/lib/utils'
import toast from 'react-hot-toast'

const QUICK_PROMPTS = [
  'What should I stock for next season?',
  'Which colors are trending this month?',
  'Compare quiet luxury vs neo-bohemian',
  'Top 3 emerging trends to watch',
  'Best trends for a boutique in Europe?',
  'What\'s declining I should clear stock of?',
]

function MessageBubble({ msg }: { msg: AdvisorMessage }) {
  const [copied, setCopied] = useState(false)
  const isAI = msg.role === 'ai'

  const copy = () => {
    navigator.clipboard.writeText(msg.text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
    toast.success('Copied to clipboard')
  }

  return (
    <div className={`flex gap-3 ${isAI ? '' : 'flex-row-reverse'} group`}>
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-[11px] font-bold ${isAI ? 'bg-gradient-to-br from-[#C9A96E] to-[#8B6F47] text-[#0A0A0F]' : 'bg-[#1E1E2E] text-[#6B6B7A]'}`}>
        {isAI ? '✦' : 'U'}
      </div>

      <div className={`flex flex-col gap-1 max-w-[78%] ${isAI ? '' : 'items-end'}`}>
        <div className="flex items-center gap-2">
          <span className="text-[10px] tracking-[0.06em] uppercase text-[#6B6B7A]">{isAI ? 'AI Advisor' : 'You'}</span>
          {msg.timestamp && <span className="text-[10px] text-[#6B6B7A]/60">{formatTimeAgo(msg.timestamp)}</span>}
        </div>

        <div className={`relative rounded-[12px] px-4 py-3 text-[13px] leading-relaxed ${
          isAI
            ? 'bg-[#16161F] border border-[#1E1E2E] text-[#F0EEE8]'
            : 'bg-[#C9A96E]/10 border border-[#C9A96E]/20 text-[#F0EEE8]'
        }`}>
          {msg.text}

          {/* Copy button - shows on hover */}
          {isAI && (
            <button onClick={copy}
              className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-[#1E1E2E] border border-[#2A2A38] flex items-center justify-center text-[#6B6B7A] hover:text-[#C9A96E] opacity-0 group-hover:opacity-100 transition-all">
              {copied ? <Check size={10} /> : <Copy size={10} />}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

function TypingIndicator() {
  return (
    <div className="flex gap-3">
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#C9A96E] to-[#8B6F47] flex-shrink-0 flex items-center justify-center text-[#0A0A0F] text-[11px] font-bold">✦</div>
      <div className="bg-[#16161F] border border-[#1E1E2E] rounded-[12px] px-4 py-3">
        <div className="flex gap-1.5 items-center h-4">
          {[0, 0.2, 0.4].map((d, i) => (
            <div key={i} className="w-1.5 h-1.5 rounded-full bg-[#6B6B7A]"
              style={{ animation: `pulseGold 1.2s ${d}s ease-in-out infinite` }} />
          ))}
        </div>
      </div>
    </div>
  )
}

export default function AdvisorPage() {
  const { messages, isTyping, addMessage, setTyping, clearChat } = useChatStore()
  const [input, setInput] = useState('')
  const chatEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, isTyping])

  const send = async (text?: string) => {
    const msg = (text || input).trim()
    if (!msg || isTyping) return
    setInput('')
    addMessage({ role: 'user', text: msg, timestamp: new Date().toISOString() })
    setTyping(true)
    try {
      const res = await advisorApi.chat(msg)
      addMessage({ role: 'ai', text: res.response, timestamp: new Date().toISOString() })
    } catch {
      addMessage({ role: 'ai', text: "I'm having trouble connecting right now. Please ensure your API key is configured and try again.", timestamp: new Date().toISOString() })
    } finally { setTyping(false) }
  }

  const handleKey = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() }
  }

  return (
    <div className="p-6 max-w-[1100px] space-y-5 page-enter">
      <SectionHeader
        title="AI Fashion Advisor"
        subtitle="Powered by Claude · Live trend data injected as context"
        action={
          <Button variant="ghost" size="sm" onClick={clearChat}>
            <RotateCcw size={12} /> Clear chat
          </Button>
        }
      />

      <div className="grid grid-cols-3 gap-5">
        {/* Chat — 2 cols */}
        <Card className="col-span-2 flex flex-col" style={{ height: '600px' }}>
          <CardHeader>
            <div className="flex items-center gap-2.5">
              <div className="w-2 h-2 rounded-full bg-[#52C97A]" style={{ animation: 'pulseGold 2s infinite' }} />
              <CardTitle>Business Intelligence Chat</CardTitle>
            </div>
            <div className="flex items-center gap-1.5">
              <Zap size={11} className="text-[#C9A96E]" />
              <span className="text-[11px] text-[#6B6B7A]">Live trend context</span>
            </div>
          </CardHeader>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {messages.map((m, i) => <MessageBubble key={i} msg={m} />)}
            {isTyping && <TypingIndicator />}
            <div ref={chatEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-[#1E1E2E] p-4">
            <div className="flex gap-2 items-end">
              <textarea
                ref={inputRef}
                rows={2}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKey}
                placeholder="Ask about trends, what to stock, color forecasts…  (Enter to send)"
                className="flex-1 bg-[#0A0A0F] border border-[#1E1E2E] rounded-[10px] px-4 py-3 text-[13px] text-[#F0EEE8] placeholder-[#6B6B7A] outline-none focus:border-[#C9A96E]/40 resize-none transition-colors font-sans"
                style={{ fontFamily: 'var(--font-sans)' }}
              />
              <Button onClick={() => send()} disabled={!input.trim() || isTyping} className="flex-shrink-0 px-4 py-3 h-[68px]">
                {isTyping ? <Spinner size={14} /> : <Send size={14} />}
              </Button>
            </div>
            <p className="text-[10px] text-[#6B6B7A] mt-2">Shift+Enter for new line · Powered by Claude Sonnet</p>
          </div>
        </Card>

        {/* Side panel */}
        <div className="space-y-4">
          {/* Quick prompts */}
          <Card>
            <CardHeader><CardTitle>Quick Questions</CardTitle></CardHeader>
            <CardBody className="space-y-2">
              {QUICK_PROMPTS.map(p => (
                <button key={p} onClick={() => send(p)} disabled={isTyping}
                  className="w-full text-left text-[12px] text-[#6B6B7A] hover:text-[#C9A96E] hover:bg-[#C9A96E]/05 px-3 py-2.5 rounded-[8px] border border-transparent hover:border-[#C9A96E]/15 transition-all disabled:opacity-40 leading-snug">
                  {p}
                </button>
              ))}
            </CardBody>
          </Card>

          {/* Context summary */}
          <Card>
            <CardHeader><CardTitle>Live Context</CardTitle></CardHeader>
            <CardBody className="space-y-3">
              <p className="text-[11px] text-[#6B6B7A] leading-relaxed">The advisor has access to real-time trend data:</p>
              {[
                { label: 'Top trends', value: '1,247 tracked' },
                { label: 'Data sources', value: 'Insta · TikTok · Pinterest · Google' },
                { label: 'Updated', value: 'Every 15 minutes' },
                { label: 'Predictions', value: 'Prophet + LSTM + XGBoost' },
              ].map(item => (
                <div key={item.label} className="flex justify-between py-2 border-b border-[#1E1E2E]/40 last:border-0">
                  <span className="text-[11px] text-[#6B6B7A]">{item.label}</span>
                  <span className="text-[11px] text-[#F0EEE8]">{item.value}</span>
                </div>
              ))}
            </CardBody>
          </Card>

          {/* Plan note */}
          <div className="bg-[#C9A96E]/06 border border-[#C9A96E]/20 rounded-[10px] p-4">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles size={13} className="text-[#C9A96E]" />
              <span className="text-[12px] font-medium text-[#C9A96E]">Pro Feature</span>
            </div>
            <p className="text-[11px] text-[#6B6B7A] leading-relaxed">AI Advisor is available on Pro and Premium plans. Upgrade to unlock unlimited queries.</p>
          </div>
        </div>
      </div>
    </div>
  )
}
