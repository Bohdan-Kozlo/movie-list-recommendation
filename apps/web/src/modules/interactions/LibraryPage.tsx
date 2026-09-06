import { interactionKeys } from './queries'
import { useQuery } from '@tanstack/react-query'
import { Link, Navigate, useParams } from 'react-router'

import { fetchLibrary, type LibraryCollection } from './api'
import { posterUrl } from '../../shared/catalogue'
import { Card } from '../../shared/ui/Card'
import { SiteHeader } from '../navigation/SiteHeader'

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
    queryKey: interactionKeys.library(activeCollection),
    queryFn: () => fetchLibrary(activeCollection),
    enabled: isCollection(collection),
  })
  if (!isCollection(collection)) return <Navigate replace to="/library/watchlist" />

  return (
    <main className="mx-auto w-full max-w-360 px-[4vw] pb-16">
      <SiteHeader />
      <section className="py-12">
        <p className="m-0 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">Personal collection</p>
        <h1 className="mt-2 font-display text-5xl font-semibold tracking-[-.055em] sm:text-7xl">My library</h1>
        <nav
          aria-label="Library collection"
          className="mt-8 flex flex-wrap gap-2 border-b border-border pb-5"
        >
          {
            collections.map((item) => <Link
              key={item.id}
              to={`/library/${item.id}`}
              className={item.id === activeCollection ? 'rounded-sm border-primary bg-primary px-3 py-2 text-sm text-primary-foreground' : 'rounded-sm px-3 py-2 text-sm hover:bg-card'}
            >
              {item.label}
            </Link>)
          }
        </nav>
      </section>
      {libraryQuery.isLoading && <p className="py-8 text-muted-foreground">Loading your library…</p>}
      {
        libraryQuery.isError && <p role="alert" className="py-8 text-rose-300">{libraryQuery.error.message}</p>
      }
      {
        libraryQuery.data && (libraryQuery.data.items.length === 0 ? (
          <Card className="p-8 text-muted-foreground">No titles in this collection yet. Browse the catalogue to make it personal.</Card>
        ) : (
          <section className="grid gap-4 pb-12 sm:grid-cols-2 lg:grid-cols-3">
            {
              libraryQuery.data.items.map((item) => {
                const poster = posterUrl(item.posterPath)
                return <Link key={item.id} to={`/catalogue/${item.id}`}>
                  <Card className="flex min-h-40 gap-4 p-4 transition-colors hover:bg-background">
                    <div className="w-20 shrink-0 bg-background">
                      {
                        poster ? <img className="h-full w-full object-cover" src={poster} alt="" /> : <span className="p-2 text-xs text-muted-foreground">No image</span>
                      }
                    </div>
                    <div>
                      <p className="m-0 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">
                        {item.type === 'movie' ? 'Film' : 'TV series'}
                        {item.releaseDate ? ` · ${item.releaseDate.slice(0, 4)}` : ''}
                      </p>
                      <h2 className="mt-2 font-display text-2xl font-semibold leading-none tracking-tight">
                        {item.title}
                      </h2>
                      <p className="mt-3 text-sm text-muted-foreground">
                        {item.rating === null ? item.genres.join(' · ') : `Your rating: ${item.rating.toFixed(1)} / 5`}
                      </p>
                    </div>
                  </Card>
                </Link>
              })
            }
          </section>
        ))
      }
    </main>
  )
}
