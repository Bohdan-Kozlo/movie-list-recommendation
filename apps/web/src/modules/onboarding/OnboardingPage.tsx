import { useState } from 'react'
import { Link, Navigate } from 'react-router'
import type { TitleCard } from '../../shared/catalogue'
import { Poster } from '../../shared/ui/Poster'
import { Button } from '../../shared/ui/Button'
import { Card } from '../../shared/ui/Card'
import { StarRating } from '../../shared/ui/StarRating'
import { SiteHeader } from '../navigation/SiteHeader'
import { useOnboarding } from './useOnboarding'

export function OnboardingPage() {
  const {
    onboardingQuery, searchQuery, ratingMutation, candidates, visibleIndex, title,
    selectedTitle, setSelectedTitle, rating, setRating, searchDraft, setSearchDraft,
    searchType, setSearchType, submitSearch, previous, next,
  } = useOnboarding()

  if (onboardingQuery.isLoading) return <main className="grid min-h-screen place-items-center p-8 font-display text-3xl">Preparing your first pick…</main>
  if (onboardingQuery.isError) return <OnboardingError message={onboardingQuery.error.message} />
  if (!onboardingQuery.data || onboardingQuery.data.isComplete) return <Navigate replace to="/catalogue" />

  const progress = onboardingQuery.data
  if (!title) return <main className="grid min-h-screen place-items-center p-8">
    <Card className="max-w-xl p-8">No more unrated titles are available right now.</Card>
  </main>

  return (
    <main className="mx-auto w-full max-w-360 px-[4vw] pb-16">
      <SiteHeader />
      <section className="grid max-w-4xl gap-5 border-b py-[clamp(3rem,7vw,6rem)]">
        <p className="m-0 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">Your starting signal</p>
        <h1 className="m-0 max-w-[14ch] font-display text-[clamp(3rem,6vw,5.5rem)] font-semibold leading-[.92] tracking-[-.06em]">One story at a time.</h1>
        <p className="max-w-2xl text-lg leading-7 text-muted-foreground">Rate titles you recognize, or move forward when you do not know one. You can always return to finish taste setup.</p>
        <div
          className="h-2 overflow-hidden bg-card"
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={progress.ratingsRequired}
          aria-valuenow={progress.ratingsRecorded}
          aria-label="Onboarding progress"
        >
          <div
            className="h-full bg-primary transition-[width]"
            style={{ width: `${(progress.ratingsRecorded / progress.ratingsRequired) * 100}%` }}
          />
        </div>
        <p className="m-0 font-mono text-xs uppercase tracking-[.08em] text-muted-foreground">
          {progress.ratingsRemaining} more {progress.ratingsRemaining === 1 ? 'rating' : 'ratings'} to unlock recommendations</p>
      </section>
      <section
        className="grid gap-8 py-12 lg:grid-cols-[minmax(16rem,22rem)_minmax(0,1fr)] lg:items-center"
        aria-labelledby="onboarding-title"
      >
        <TitlePoster title={title} />
        <div className="grid max-w-2xl gap-6">
          <p className="m-0 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">
            {selectedTitle ? 'Search result' : `Pick ${visibleIndex + 1} of ${candidates.length}`}
          </p>
          <div>
            <p className="m-0 font-mono text-xs uppercase tracking-[.06em] text-muted-foreground">
              {title.type === 'movie' ? 'Film' : 'TV series'} · {title.releaseDate?.slice(0, 4) ?? '—'}
            </p>
            <h2
              id="onboarding-title"
              className="mt-2 font-display text-[clamp(3rem,5vw,5rem)] font-semibold leading-[.92] tracking-[-.06em]"
            >
              {title.title}
            </h2>
            <p className="mb-0 mt-4 text-muted-foreground">{title.genres.join(' · ')}</p>
          </div>
          <div className="border-y py-6">
            <p className="m-0 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">How much did it land?</p>
            <div className="mt-4">
              <StarRating
                label={`Your rating for ${title.title}`}
                value={rating}
                onChange={setRating}
                disabled={ratingMutation.isPending}
              />
            </div>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button
              type="button"
              onClick={() => ratingMutation.mutate({ titleId: title.id, value: rating })}
              disabled={ratingMutation.isPending}
            >Rate {rating.toFixed(1)} and continue</Button>
            <Button
              variant="outline"
              type="button"
              onClick={previous}
              disabled={ratingMutation.isPending || (!selectedTitle && visibleIndex === 0)}
            >← Back</Button>
            <Button
              variant="ghost"
              type="button"
              onClick={next}
              disabled={ratingMutation.isPending || (!selectedTitle && visibleIndex === candidates.length - 1)}
            >Next →</Button>
          </div>
          {
            ratingMutation.isError && <p role="alert" className="m-0 text-rose-300">{ratingMutation.error.message}</p>
          }
        </div>
      </section>
      <section className="border-t py-12" aria-labelledby="onboarding-search-title">
        <p className="m-0 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">Know something else?</p>
        <h2
          id="onboarding-search-title"
          className="mt-2 font-display text-4xl font-semibold tracking-[-.05em]"
        >Choose a different title.</h2>
        <form className="mt-6 grid max-w-3xl gap-3 sm:grid-cols-[1fr_10rem_auto]" onSubmit={submitSearch}>
          <label className="sr-only" htmlFor="onboarding-search">Search local titles</label>
          <input
            id="onboarding-search"
            className="min-w-0 border bg-card px-3.5 py-3"
            value={searchDraft}
            onChange={(event) => setSearchDraft(event.target.value)}
            placeholder="Try “Dune” or “The Bear”"
          />
          <select
            className="border bg-card px-3.5 py-3"
            value={searchType}
            onChange={(event) => setSearchType(event.target.value as '' | 'movie' | 'tv')}
            aria-label="Title type"
          >
            <option value="">Films and TV</option>
            <option value="movie">Films</option>
            <option value="tv">TV series</option>
          </select>
          <Button type="submit">Search</Button>
        </form>
        {
          searchQuery.isLoading && <p className="mt-6 text-muted-foreground">Searching the local catalogue…</p>
        }
        {
          searchQuery.isError && <p role="alert" className="mt-6 text-rose-300">{searchQuery.error.message}</p>
        }
        {
          searchQuery.data && searchQuery.data.items.length === 0 && <p className="mt-6 text-muted-foreground">No unrated local titles match this search.</p>
        }
        {
          searchQuery.data && searchQuery.data.items.length > 0 && <SearchChoice titles={searchQuery.data.items} onChoose={setSelectedTitle} />
        }
      </section>
    </main>
  )
}

function TitlePoster({ title }: { title: TitleCard }) {
  return <div className="aspect-2/3 overflow-hidden bg-card">
    <Poster
      path={title.posterPath}
      className="h-full w-full object-cover"
      fallback={<span className="grid h-full place-items-center text-sm text-muted-foreground">No image available</span>}
    />
  </div>
}

function OnboardingError({ message }: { message: string }) {
  return <main className="grid min-h-screen place-items-center p-8">
    <Card className="max-w-xl p-8">
      <p role="alert">{message}</p>
      <Button asChild><Link to="/auth/sign-in">Sign in</Link></Button>
    </Card>
  </main>
}

function SearchChoice({ titles, onChoose }: { titles: TitleCard[]; onChoose: (title: TitleCard) => void }) {
  const [titleId, setTitleId] = useState(titles[0]?.id ?? '')
  const selected = titles.find((title) => title.id === titleId)
  return <div className="mt-6 flex flex-wrap gap-3">
    <select
      className="min-w-64 border bg-card px-3.5 py-3"
      value={titleId}
      onChange={(event) => setTitleId(event.target.value)}
      aria-label="Search results"
    >
      {
        titles.map((title) => <option key={title.id} value={title.id}>
          {title.title} · {title.type === 'movie' ? 'Film' : 'TV series'}
        </option>)
      }
    </select>
    <Button type="button" onClick={() => selected && onChoose(selected)}>Rate this title</Button>
  </div>
}
