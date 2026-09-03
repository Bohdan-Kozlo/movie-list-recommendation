import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { FormEvent, useState } from 'react'
import { Link, Navigate } from 'react-router'

import { createRating } from '../interactions/api'
import { posterUrl, type TitleCard } from '../../shared/catalogue'
import { Button } from '../../shared/ui/Button'
import { Card } from '../../shared/ui/Card'
import { fetchOnboarding, searchOnboardingTitles } from './api'

export function OnboardingPage() {
  const queryClient = useQueryClient()
  const [searchDraft, setSearchDraft] = useState('')
  const [searchType, setSearchType] = useState<'' | 'movie' | 'tv'>('')
  const [submittedSearch, setSubmittedSearch] = useState('')
  const onboardingQuery = useQuery({
    queryKey: ['onboarding'],
    queryFn: fetchOnboarding,
    refetchOnMount: 'always',
  })
  const searchQuery = useQuery({
    queryKey: ['onboarding', 'search', submittedSearch, searchType],
    queryFn: () => searchOnboardingTitles(submittedSearch, searchType),
    enabled: Boolean(submittedSearch),
  })
  const ratingMutation = useMutation({
    mutationFn: ({ titleId, value }: { titleId: string; value: number }) => createRating(titleId, value),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['onboarding'] })
      void queryClient.invalidateQueries({ queryKey: ['interactions'] })
    },
  })

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmittedSearch(searchDraft.trim())
  }

  if (onboardingQuery.isLoading) return <main className="grid min-h-screen place-items-center p-8 font-display text-3xl">Preparing your first picks…</main>
  if (onboardingQuery.isError) return <main className="grid min-h-screen place-items-center p-8"><Card className="max-w-xl p-8"><p role="alert">{onboardingQuery.error.message}</p><Button asChild><Link to="/auth/sign-in">Sign in</Link></Button></Card></main>
  if (!onboardingQuery.data || onboardingQuery.data.isComplete) return <Navigate replace to="/catalogue" />

  const progress = onboardingQuery.data
  const rate = (titleId: string, value: number) => ratingMutation.mutate({ titleId, value })
  return (
    <main className="mx-auto w-full max-w-360 px-[4vw] pb-16">
      <header className="flex min-h-21 items-center justify-between gap-4 border-b">
        <Link className="font-display text-[clamp(1.2rem,2vw,1.65rem)] font-bold tracking-[-.055em]" to="/catalogue">REEL / INDEX</Link>
        <p className="font-mono text-xs uppercase tracking-[.1em] text-muted-foreground">Taste setup · {progress.ratingsRecorded} / {progress.ratingsRequired}</p>
      </header>
      <section className="grid max-w-4xl gap-5 border-b py-[clamp(3rem,7vw,6rem)]">
        <p className="m-0 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">Your starting signal</p>
        <h1 className="m-0 max-w-[13ch] font-display text-[clamp(3rem,6vw,5.5rem)] font-semibold leading-[.92] tracking-[-.06em]">Rate ten stories you know.</h1>
        <p className="max-w-2xl text-lg leading-7 text-muted-foreground">We refresh the popular picks after every rating and vary genres and decades so your first recommendations have a useful signal.</p>
        <div className="h-2 overflow-hidden bg-card" role="progressbar" aria-valuemin={0} aria-valuemax={progress.ratingsRequired} aria-valuenow={progress.ratingsRecorded} aria-label="Onboarding progress"><div className="h-full bg-primary transition-[width]" style={{ width: `${(progress.ratingsRecorded / progress.ratingsRequired) * 100}%` }} /></div>
        <p className="m-0 font-mono text-xs uppercase tracking-[.08em] text-muted-foreground">{progress.ratingsRemaining} more {progress.ratingsRemaining === 1 ? 'rating' : 'ratings'} to unlock your recommendations</p>
      </section>

      <TitleSection title="Popular films" titles={progress.movies} onRate={rate} disabled={ratingMutation.isPending} />
      <TitleSection title="Popular TV series" titles={progress.tvSeries} onRate={rate} disabled={ratingMutation.isPending} />

      <section className="border-t py-12" aria-labelledby="onboarding-search-title">
        <p className="m-0 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">Know something else?</p>
        <h2 id="onboarding-search-title" className="mt-2 font-display text-4xl font-semibold tracking-[-.05em]">Search your own familiar title.</h2>
        <form className="mt-6 grid max-w-3xl gap-3 sm:grid-cols-[1fr_10rem_auto]" onSubmit={submitSearch}>
          <label className="sr-only" htmlFor="onboarding-search">Search local titles</label>
          <input id="onboarding-search" className="min-w-0 border bg-card px-3.5 py-3" value={searchDraft} onChange={(event) => setSearchDraft(event.target.value)} placeholder="Try “Dune” or “The Bear”" />
          <select className="border bg-card px-3.5 py-3" value={searchType} onChange={(event) => setSearchType(event.target.value as '' | 'movie' | 'tv')} aria-label="Title type"><option value="">Films and TV</option><option value="movie">Films</option><option value="tv">TV series</option></select>
          <Button type="submit">Search</Button>
        </form>
        {searchQuery.isLoading && <p className="mt-6 text-muted-foreground">Searching the local catalogue…</p>}
        {searchQuery.isError && <p role="alert" className="mt-6 text-rose-300">{searchQuery.error.message}</p>}
        {searchQuery.data && searchQuery.data.items.length === 0 && <p className="mt-6 text-muted-foreground">No unrated local titles match this search.</p>}
        {searchQuery.data && searchQuery.data.items.length > 0 && <div className="mt-8 grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 lg:grid-cols-4">{searchQuery.data.items.map((title) => <TitleGridCard key={title.id} title={title} onRate={rate} disabled={ratingMutation.isPending} />)}</div>}
      </section>
      {ratingMutation.isError && <p role="alert" className="text-rose-300">{ratingMutation.error.message}</p>}
    </main>
  )
}

function TitleSection({ title, titles, onRate, disabled }: { title: string; titles: TitleCard[]; onRate: (titleId: string, value: number) => void; disabled: boolean }) {
  return <section className="border-b py-12"><p className="m-0 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">{title}</p><div className="mt-6 grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 lg:grid-cols-4">{titles.map((item) => <TitleGridCard key={item.id} title={item} onRate={onRate} disabled={disabled} />)}</div></section>
}

function TitleGridCard({ title, onRate, disabled }: { title: TitleCard; onRate: (titleId: string, value: number) => void; disabled: boolean }) {
  const [rating, setRating] = useState('4.0')
  const poster = posterUrl(title.posterPath)
  return <article className="min-w-0"><div className="aspect-2/3 overflow-hidden bg-card">{poster ? <img className="h-full w-full object-cover" src={poster} alt="" /> : <span className="grid h-full place-items-center text-sm text-muted-foreground">No image</span>}</div><p className="mb-0 mt-3 font-mono text-xs uppercase tracking-[.045em] text-muted-foreground">{title.type === 'movie' ? 'Film' : 'TV series'} · {title.releaseDate?.slice(0, 4) ?? '—'}</p><h3 className="my-1 font-display text-2xl font-semibold leading-none tracking-[-.04em]">{title.title}</h3><p className="m-0 min-h-5 text-xs text-muted-foreground">{title.genres.slice(0, 2).join(' · ')}</p><div className="mt-3 grid grid-cols-[1fr_auto] items-center gap-2"><label className="sr-only" htmlFor={`rating-${title.id}`}>Rating for {title.title}</label><input id={`rating-${title.id}`} className="w-full accent-primary" type="range" min="0.5" max="5" step="0.5" value={rating} onChange={(event) => setRating(event.target.value)} /><Button size="compact" type="button" onClick={() => onRate(title.id, Number(rating))} disabled={disabled}>Rate {rating}</Button></div></article>
}
