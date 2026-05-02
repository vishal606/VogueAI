import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import Cookies from 'js-cookie'
import type {
  AuthTokens, User, Trend, TrendListResponse, TrendFilter,
  TrendPrediction, SeasonForecast, Recommendation, Alert, AlertCreateRequest,
  Report, ReportCreateRequest, SubscriptionPlan, Subscription, DashboardSummary,
  ColorPalette, AdvisorResponse,
} from '@/types'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_PREFIX = '/api/v1'

const api: AxiosInstance = axios.create({
  baseURL: `${BASE_URL}${API_PREFIX}`,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30_000,
})

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = Cookies.get('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

let refreshing = false
api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
    if (error.response?.status === 401 && !original._retry && !refreshing) {
      original._retry = true
      refreshing = true
      try {
        const refresh = Cookies.get('refresh_token')
        if (refresh) {
          const { data } = await axios.post<AuthTokens>(`${BASE_URL}${API_PREFIX}/auth/refresh`, { refresh_token: refresh })
          Cookies.set('access_token', data.access_token, { expires: 1 })
          Cookies.set('refresh_token', data.refresh_token, { expires: 30 })
          original.headers.Authorization = `Bearer ${data.access_token}`
          return api(original)
        }
      } catch {
        Cookies.remove('access_token'); Cookies.remove('refresh_token')
        window.location.href = '/login'
      } finally { refreshing = false }
    }
    return Promise.reject(error)
  }
)

// ── Auth ─────────────────────────────────────────────────────
export const authApi = {
  login: (email: string, password: string) => api.post<AuthTokens>('/auth/login', { email, password }).then(r => r.data),
  register: (data: { name: string; email: string; password: string; role: string }) => api.post<User>('/auth/register', data).then(r => r.data),
  me: () => api.get<User>('/auth/me').then(r => r.data),
  logout: () => { Cookies.remove('access_token'); Cookies.remove('refresh_token') },
}

// ── Trends ───────────────────────────────────────────────────
export const trendsApi = {
  list: (filters?: TrendFilter) => api.get<TrendListResponse>('/trends/', { params: filters }).then(r => r.data),
  get: (id: string) => api.get<Trend>(`/trends/${id}`).then(r => r.data),
  dashboard: () => api.get<DashboardSummary>('/trends/dashboard').then(r => r.data),
  rising: (limit = 10, region?: string) => api.get<Trend[]>('/trends/rising', { params: { limit, region } }).then(r => r.data),
  categories: () => api.get<string[]>('/trends/categories').then(r => r.data),
}

// ── Predictions ──────────────────────────────────────────────
export const predictionsApi = {
  list: (trend_id?: string) => api.get<TrendPrediction[]>('/predictions/', { params: { trend_id } }).then(r => r.data),
  generate: (trend_id: string, horizon_days = 30) => api.post<TrendPrediction[]>('/predictions/generate', { trend_id, horizon_days }).then(r => r.data),
  seasons: () => api.get<SeasonForecast[]>('/predictions/seasons').then(r => r.data),
}

// ── Recommendations ──────────────────────────────────────────
export const recommendationsApi = {
  list: (params?: { priority?: string; unread_only?: boolean }) => api.get<Recommendation[]>('/recommendations/', { params }).then(r => r.data),
  markRead: (id: string) => api.patch<Recommendation>(`/recommendations/${id}`, { is_read: true }).then(r => r.data),
  refresh: () => api.post('/advisor/recommendations/refresh').then(r => r.data),
}

// ── Alerts ───────────────────────────────────────────────────
export const alertsApi = {
  list: () => api.get<Alert[]>('/alerts/').then(r => r.data),
  create: (data: AlertCreateRequest) => api.post<Alert>('/alerts/', data).then(r => r.data),
  delete: (id: string) => api.delete(`/alerts/${id}`).then(r => r.data),
  toggle: (id: string) => api.patch<Alert>(`/alerts/${id}/toggle`).then(r => r.data),
}

// ── Reports ──────────────────────────────────────────────────
export const reportsApi = {
  list: () => api.get<Report[]>('/reports/').then(r => r.data),
  generate: (data: ReportCreateRequest) => api.post<Report>('/reports/', data).then(r => r.data),
  get: (id: string) => api.get<Report>(`/reports/${id}`).then(r => r.data),
  delete: (id: string) => api.delete(`/reports/${id}`).then(r => r.data),
}

// ── Subscriptions ────────────────────────────────────────────
export const subscriptionsApi = {
  plans: () => api.get<SubscriptionPlan[]>('/subscriptions/plans').then(r => r.data),
  current: () => api.get<Subscription>('/subscriptions/me').then(r => r.data),
  subscribe: (plan_id: string) => api.post('/subscriptions/', { plan_id }).then(r => r.data),
  cancel: () => api.delete('/subscriptions/me').then(r => r.data),
}

// ── Advisor ──────────────────────────────────────────────────
export const advisorApi = {
  chat: (message: string, context?: Record<string, unknown>) => api.post<AdvisorResponse>('/advisor/chat', { message, context }).then(r => r.data),
}

// ── Colors ───────────────────────────────────────────────────
export const colorsApi = {
  palette: () => api.get<ColorPalette>('/colors/palette').then(r => r.data),
  rising: () => api.get('/colors/rising').then(r => r.data),
}

export default api

// ── Payments ─────────────────────────────────────────────────────────────────
export const paymentsApi = {
  checkoutSession: (plan_id: string, trial_days = 14) =>
    api.post('/payments/checkout-session', {
      plan_id, trial_days,
      success_url: `${typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000'}/checkout/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url:  `${typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000'}/subscription`,
    }).then(r => r.data),
  verifySession: (session_id: string) => api.get(`/payments/checkout-session/${session_id}`).then(r => r.data),
  billingPortal: (return_url?: string) => api.post('/payments/billing-portal', { return_url: return_url || (typeof window !== 'undefined' ? window.location.origin : '') + '/billing' }).then(r => r.data),
  invoices: (limit = 10) => api.get('/payments/invoices', { params: { limit } }).then(r => r.data),
  paymentMethods: () => api.get('/payments/payment-methods').then(r => r.data),
  upgrade: (new_plan_id: string, prorate = true) => api.post('/payments/upgrade', { new_plan_id, prorate }).then(r => r.data),
  cancel: (immediately = false) => api.post(`/payments/cancel?immediately=${immediately}`).then(r => r.data),
  reactivate: () => api.post('/payments/reactivate').then(r => r.data),
  deletePaymentMethod: (pm_id: string) => api.delete(`/payments/payment-methods/${pm_id}`).then(r => r.data),
}
