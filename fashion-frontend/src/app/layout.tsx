import type { Metadata } from 'next'
import { Toaster } from 'react-hot-toast'
import '@/styles/globals.css'

export const metadata: Metadata = {
  title: { default: 'Vōgue·AI — Fashion Trend Intelligence', template: '%s | Vōgue·AI' },
  description: 'AI-powered fashion trend prediction for boutique owners and fashion brands.',
  keywords: ['fashion trends', 'AI predictions', 'trend analysis', 'boutique'],
  authors: [{ name: 'Vōgue·AI' }],
  themeColor: '#0A0A0F',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
      </head>
      <body>
        {children}
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: '#16161F', color: '#F0EEE8', border: '1px solid #1E1E2E',
              fontFamily: 'var(--font-sans)', fontSize: '13px', borderRadius: '10px',
            },
            success: { iconTheme: { primary: '#52C97A', secondary: '#0A0A0F' } },
            error:   { iconTheme: { primary: '#D4688A', secondary: '#0A0A0F' } },
          }}
        />
      </body>
    </html>
  )
}
