import { useQuery } from '@tanstack/react-query'
import { Link, Navigate, useParams } from 'react-router'

import { fetchLibrary, type LibraryCollection } from './api'
import { posterUrl } from '../../shared/catalogue'
import { AccountMenu } from '../auth/AccountMenu'
import { Card } from '../../shared/ui/Card'

const collections: Array<{ id: LibraryCollection; label: string }> = [
  { id: 'ratings', label: 'Ratings' },
  { id: 'watchlist', label: 'Watchlist' },
  { id: 'watched', label: 'Watched' },
  { id: 'not-interested', label: 'Not interested' },
]

function isCollection(value: string | undefined): value is LibraryCollection {
  return collections.some((collection) => collection.id === value)
}

export function LibraryPage() {
  const { collection } = useParams()
  const activeCollection = isCollection(collection) ? collection : 'watchlist'
  const libraryQuery = useQuery({
    queryKey: ['interactions', 'library', activeCollection],
    queryFn: () => fetchLibrary(activeCollection),
    enabled: isCollection(collection),
  })
  if (!isCollection(collection)) return <Navigate replace to="/library/watchlist" />

  return (
    <main className="catalogue-shell">
      <header className="masthead">
        <Link className="wordmark" to="/catalogue">REEL / INDEX</Link>
        <AccountMenu />
      </header>
      <section className="py-12">
        <p className="eyebrow">Personal collection</p>
        <h1 className="mt-2 font-serif text-5xl tracking-tight sm:text-7xl">My library</h1>
        <nav aria-label="Library collection" className="mt-8 flex flex-wrap gap-2 border-b border-border pb-5">
          {collections.map((item) => <Link key={item.id} to={`/library/${item.id}`} className={item.id === activeCollection ? 'border border-primary bg-primary px-3 py-2 text-sm text-primary-foreground' : 'border border-border px-3 py-2 text-sm hover:bg-card'}>{item.label}</Link>)}
        </nav>
      </section>
      {libraryQuery.isLoading && <p className="py-8 text-muted-foreground">Loading your library…</p>}
      {libraryQuery.isError && <p role="alert" className="py-8 text-red-800">{libraryQuery.error.message}</p>}
      {libraryQuery.data && (libraryQuery.data.items.length === 0 ? (
        <Card className="p-8 text-muted-foreground">No titles in this collection yet. Browse the catalogue to make it personal.</Card>
      ) : (
        <section className="grid gap-4 pb-12 sm:grid-cols-2 lg:grid-cols-3">
          {libraryQuery.data.items.map((item) => {
            const poster = posterUrl(item.posterPath)
            return <Link key={item.id} to={`/catalogue/${item.id}`}><Card className="flex min-h-40 gap-4 p-4 transition-colors hover:bg-background"><div className="w-20 shrink-0 bg-background">{poster ? <img className="h-full w-full object-cover" src={poster} alt="" /> : <span className="p-2 text-xs text-muted-foreground">No image</span>}</div><div><p className="eyebrow">{item.type === 'movie' ? 'Film' : 'TV series'}{item.releaseDate ? ` · ${item.releaseDate.slice(0, 4)}` : ''}</p><h2 className="mt-2 font-serif text-2xl leading-none">{item.title}</h2><p className="mt-3 text-sm text-muted-foreground">{item.rating === null ? item.genres.join(' · ') : `Your rating: ${item.rating.toFixed(1)} / 5`}</p></div></Card></Link>
          })}
        </section>
      ))}
    </main>
  )
}
