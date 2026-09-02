import { useEffect, useState } from 'react'

import { CataloguePage } from '../modules/catalog/CataloguePage'
import { TitleDetailsPage } from '../modules/catalog/TitleDetailsPage'
import { AuthCallbackPage, AuthPage } from '../modules/auth/AuthPage'

function currentLocation(): string {
  return `${window.location.pathname}${window.location.search}`
}

function currentTitleId(pathname: string): string | null {
  const match = pathname.match(/^\/catalogue\/([^/]+)$/)
  return match?.[1] ?? null
}

export function App() {
  const [location, setLocation] = useState(currentLocation)
  const pathname = location.split('?')[0]
  const titleId = currentTitleId(pathname)

  useEffect(() => {
    function updateLocation() {
      setLocation(currentLocation())
    }
    window.addEventListener('popstate', updateLocation)
    return () => window.removeEventListener('popstate', updateLocation)
  }, [])

  function navigate(path: string) {
    window.history.pushState({}, '', path)
    setLocation(currentLocation())
  }

  if (pathname === '/auth/register') return <AuthPage mode="register" onNavigate={navigate} />
  if (pathname === '/auth/sign-in') return <AuthPage mode="sign-in" onNavigate={navigate} />
  if (pathname === '/auth/callback') return <AuthCallbackPage onNavigate={navigate} />

  return titleId ? (
    <TitleDetailsPage titleId={titleId} onBack={() => navigate('/catalogue')} onNavigate={navigate} />
  ) : (
    <CataloguePage onOpenTitle={(id) => navigate(`/catalogue/${id}`)} onNavigate={navigate} />
  )
}
