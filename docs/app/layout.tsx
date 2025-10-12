import type { Metadata } from 'next'
import './globals.css'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'BlueTrace API - Marine & Coastal Data',
  description: 'Production-grade REST API for marine and coastal datasets',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen bg-gray-50">
          {/* Header */}
          <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center h-16">
                <div className="flex items-center">
                  <Link href="/" className="flex items-center">
                    <span className="text-2xl font-bold text-primary-600">🌊 BlueTrace</span>
                  </Link>
                </div>
                <nav className="flex space-x-8">
                  <Link href="/" className="text-gray-700 hover:text-primary-600">Home</Link>
                  <Link href="/quickstart" className="text-gray-700 hover:text-primary-600">Quickstart</Link>
                  <Link href="/pricing" className="text-gray-700 hover:text-primary-600">Pricing</Link>
                  <Link href="/api/v1/tides" className="text-gray-700 hover:text-primary-600">API Docs</Link>
                  <a href="http://localhost:8080/docs" className="text-gray-700 hover:text-primary-600" target="_blank">OpenAPI</a>
                </nav>
              </div>
            </div>
          </header>

          {/* Main Content */}
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </main>

          {/* Footer */}
          <footer className="bg-white border-t border-gray-200 mt-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
              <div className="text-center text-gray-500 text-sm">
                © 2024 BlueTrace. Open source marine data API.
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  )
}

