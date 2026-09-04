import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router'

import { ApiError } from '../../shared/api/client'
import { posterUrl } from '../../shared/catalogue'
import { fetchPersonalRecommendations, type SimilarTitle } from './api'
import { Card } from '../../shared/ui/Card'
import { SiteHeader } from '../navigation/SiteHeader'

export function PersonalRecommendationsPage() {
  const query = useQuery({
    queryKey: ['recommendations', 'personal'],
    queryFn: fetchPersonalRecommendations,
  })
  if (query.isLoading) {
    return <main className="mx-auto w-full max-w-360 px-[4vw] py-24 font-display text-3xl">Reading your taste profile…</main>
  }
  if (query.isError) return <RecommendationError error={query.error} />
  if (!query.data) return null

  return (
    <main className="mx-auto w-full max-w-360 px-[4vw] pb-16">
      <SiteHeader />
      <section className="max-w-4xl py-[clamp(3rem,7vw,6rem)]">
        <p className="m-0 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">
          From your ratings
        </p>
        <h1 className="mt-2 font-display text-[clamp(3rem,6vw,5.5rem)] font-semibold leading-[.92] tracking-[-.06em]">
          Made for your next watch.
        </h1>
        <p className="max-w-2xl text-lg leading-7 text-muted-foreground">
          Semantic recommendations shaped by the titles you rated highly, with watched and
          not-interested titles kept out.
        </p>
      </section>
      <RecommendationSection title="Movies" items={query.data.movies.items} />
      <RecommendationSection title="TV series" items={query.data.tvSeries.items} />
    </main>
  )
}

function RecommendationError({ error }: { error: Error }) {
  const status = error instanceof ApiError ? error.status : 0
  const needsSetup = status === 401 || status === 403
  let destination = '/auth/sign-in'
  let action = 'Sign in'
  let body = 'Personal recommendations are unavailable right now. Try again shortly.'
  if (status === 403) {
    destination = '/onboarding'
    action = 'Complete taste setup'
    body = 'Rate ten familiar titles to unlock your personal recommendations.'
  } else if (status === 401) {
    body = 'Sign in to see recommendations based on your ratings.'
  }

  return (
    <main className="mx-auto grid min-h-screen w-full max-w-360 place-items-center px-[4vw]">
      <Card className="max-w-xl p-8">
        <h1 className="font-display text-4xl">Your recommendations need a little setup.</h1>
        <p className="text-muted-foreground">{body}</p>
        {needsSetup ? <Link className="inline-block rounded-sm border-primary bg-primary px-4 py-3 text-primary-foreground" to={destination}>{action}</Link> : null}
      </Card>
    </main>
  )
}

function RecommendationSection({ title, items }: { title: string; items: SimilarTitle[] }) {
  return (
    <section className="border-t py-12" aria-labelledby={`recommendations-${title}`}>
      <p className="m-0 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">
        Personal picks
      </p>
      <h2 id={`recommendations-${title}`} className="mt-2 font-display text-4xl font-semibold tracking-[-.05em]">
        {title}
      </h2>
      {items.length === 0 ? (
        <Card className="mt-6 p-6 text-muted-foreground">
          Rate a few titles above 3.0 to give this section a clearer direction.
        </Card>
      ) : (
        <div className="mt-7 grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 lg:grid-cols-4">
          {items.map((item) => <RecommendationCard key={item.id} item={item} />)}
        </div>
      )}
    </section>
  )
}

function RecommendationCard({ item }: { item: SimilarTitle }) {
  const poster = posterUrl(item.posterPath)
  return (
    <Link to={`/catalogue/${item.id}`} className="group grid gap-3">
      <div className="aspect-2/3 overflow-hidden bg-card">
        {poster ? <img className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105" src={poster} alt="" /> : <span className="grid h-full place-items-center text-sm text-muted-foreground">No image</span>}
      </div>
      <div>
        <p className="m-0 font-mono text-xs uppercase tracking-[.08em] text-primary">
          {item.type === 'movie' ? 'Film' : 'TV series'}
        </p>
        <h3 className="mt-1 font-display text-2xl font-semibold leading-none">{item.title}</h3>
        <p className="mb-0 mt-2 text-sm text-muted-foreground">{item.reason}</p>
      </div>
    </Link>
  )
}
