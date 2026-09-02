import { useEffect, useState } from 'react'

import { CataloguePage } from '../modules/catalog/CataloguePage'
import { TitleDetailsPage } from '../modules/catalog/TitleDetailsPage'

function currentTitleId(): string | null {
  const match = window.location.pathname.match(/^\/catalogue\/([^/]+)$/)
  return match?.[1] ?? null
}

export function App() {
  const [titleId, setTitleId] = useState(currentTitleId)

  useEffect(() => {
    function updateLocation() {
      setTitleId(currentTitleId())
    }
    window.addEventListener('popstate', updateLocation)
    return () => window.removeEventListener('popstate', updateLocation)
  }, [])

  function openTitle(id: string) {
    window.history.pushState({}, '', `/catalogue/${id}`)
    setTitleId(id)
  }

  function returnToCatalogue() {
    window.history.pushState({}, '', '/catalogue')
    setTitleId(null)
  }

  return titleId ? <TitleDetailsPage titleId={titleId} onBack={returnToCatalogue} /> : <CataloguePage onOpenTitle={openTitle} />
}
