'use client'
import { useState, useEffect, useCallback, useRef } from 'react'
import { useAuthStore } from '@/lib/store'
import { authApi } from '@/lib/api'
import Cookies from 'js-cookie'

export function useAuth() {
  const { user, subscription, isAuthenticated, isLoading, setUser, setLoading, logout } = useAuthStore()
  useEffect(() => {
    const token = Cookies.get('access_token')
    if (token && !user) {
      authApi.me().then(setUser).catch(logout).finally(() => setLoading(false))
    } else { setLoading(false) }
  }, [])
  return { user, subscription, isAuthenticated, isLoading }
}

export function useDebounce<T>(value: T, delay = 300): T {
  const [dv, setDv] = useState(value)
  useEffect(() => { const t = setTimeout(() => setDv(value), delay); return () => clearTimeout(t) }, [value, delay])
  return dv
}

export function useOnClickOutside<T extends HTMLElement>(ref: React.RefObject<T>, handler: () => void) {
  useEffect(() => {
    const listener = (e: MouseEvent) => { if (!ref.current?.contains(e.target as Node)) handler() }
    document.addEventListener('mousedown', listener)
    return () => document.removeEventListener('mousedown', listener)
  }, [ref, handler])
}

export function useLocalStorage<T>(key: string, init: T) {
  const [val, setVal] = useState<T>(() => {
    if (typeof window === 'undefined') return init
    try { const item = localStorage.getItem(key); return item ? JSON.parse(item) : init } catch { return init }
  })
  const setValue = useCallback((v: T | ((prev: T) => T)) => {
    const next = v instanceof Function ? v(val) : v
    setVal(next)
    localStorage.setItem(key, JSON.stringify(next))
  }, [key, val])
  return [val, setValue] as const
}
