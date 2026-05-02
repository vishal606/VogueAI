import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import Cookies from 'js-cookie'
import type { User, Subscription, Trend, AdvisorMessage } from '@/types'

interface AuthState {
  user: User | null
  subscription: Subscription | null
  isAuthenticated: boolean
  isLoading: boolean
  setUser: (user: User | null) => void
  setSubscription: (sub: Subscription | null) => void
  setLoading: (v: boolean) => void
  login: (tokens: { access_token: string; refresh_token: string; expires_in: number }) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      subscription: null,
      isAuthenticated: false,
      isLoading: true,
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setSubscription: (subscription) => set({ subscription }),
      setLoading: (isLoading) => set({ isLoading }),
      login: ({ access_token, refresh_token, expires_in }) => {
        Cookies.set('access_token', access_token, { expires: expires_in / 86400 })
        Cookies.set('refresh_token', refresh_token, { expires: 30 })
        set({ isAuthenticated: true })
      },
      logout: () => {
        Cookies.remove('access_token'); Cookies.remove('refresh_token')
        set({ user: null, subscription: null, isAuthenticated: false })
      },
    }),
    { name: 'auth-store', storage: createJSONStorage(() => sessionStorage), partialize: (s) => ({ user: s.user, isAuthenticated: s.isAuthenticated }) }
  )
)

interface UIState {
  sidebarCollapsed: boolean
  activePage: string
  setSidebarCollapsed: (v: boolean) => void
  setActivePage: (page: string) => void
}

export const useUIStore = create<UIState>((set) => ({
  sidebarCollapsed: false,
  activePage: 'dashboard',
  setSidebarCollapsed: (sidebarCollapsed) => set({ sidebarCollapsed }),
  setActivePage: (activePage) => set({ activePage }),
}))

interface TrendState {
  selectedTrend: Trend | null
  filters: Record<string, string>
  setSelectedTrend: (t: Trend | null) => void
  setFilters: (f: Record<string, string>) => void
}

export const useTrendStore = create<TrendState>((set) => ({
  selectedTrend: null,
  filters: {},
  setSelectedTrend: (selectedTrend) => set({ selectedTrend }),
  setFilters: (filters) => set({ filters }),
}))

interface ChatState {
  messages: AdvisorMessage[]
  isTyping: boolean
  addMessage: (msg: AdvisorMessage) => void
  setTyping: (v: boolean) => void
  clearChat: () => void
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [{
    role: 'ai',
    text: "Hello! I'm your AI Fashion Advisor. Ask me about trends, colors, what to stock next season, or competitor insights.",
    timestamp: new Date().toISOString(),
  }],
  isTyping: false,
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  setTyping: (isTyping) => set({ isTyping }),
  clearChat: () => set({ messages: [] }),
}))
