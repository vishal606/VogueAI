'use client'
import { Suspense } from 'react'
import { CheckoutSuccessPage } from '@/components/payment/PaymentPages'
export default function CheckoutSuccess() { return <Suspense fallback={<div className="min-h-screen bg-[#0A0A0F] flex items-center justify-center"><div style={{width:24,height:24,border:'2px solid #1E1E2E',borderTopColor:'#C9A96E',borderRadius:'50%',animation:'spin 0.7s linear infinite'}} /></div>}><CheckoutSuccessPage /></Suspense> }
