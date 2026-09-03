import { useMutation, useQuery } from '@tanstack/react-query'
import { FormEvent, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router'

import {
  BrowseParameters,
  CatalogueTitle,
  ExternalTitle,
  fetchCatalogue,
  fetchCatalogueFilters,
  importTmdbTitle,
  posterUrl,
  searchTmdbTitles,
} from './api'
import { CatalogueMessage } from './CatalogueMessage'
import { AccountMenu } from '../auth/AccountMenu'

const initialParameters: BrowseParameters = {
  query: '',
  type: '',
  genre: '',
  year: '',
  page: 1,
}

export function CataloguePage() {
  const navigate = useNavigate()
  const [parameters, setParameters] = useState(initialParameters)
  const [searchDraft, setSearchDraft] = useState('')
  const catalogueQuery = useQuery({
    queryKey: ['catalogue', parameters],
    queryFn: () => fetchCatalogue(parameters),
  })
  const filtersQuery = useQuery({ queryKey: ['catalogue', 'filters'], queryFn: fetchCatalogueFilters })
  const shouldSearchTmdb = Boolean(
    parameters.query && !parameters.genre && !parameters.year && catalogueQuery.data?.total === 0,
  )
  const tmdbQuery = useQuery({
    queryKey: ['catalogue', 'tmdb-search', parameters.query, parameters.type],
    queryFn: () => searchTmdbTitles(parameters.query, parameters.type),
    enabled: shouldSearchTmdb,
  })
  const importMutation = useMutation({
    mutationFn: ({ type, tmdbId }: { type: 'movie' | 'tv'; tmdbId: number }) =>
      importTmdbTitle(type, tmdbId),
    onSuccess: (title) => navigate(`/catalogue/${title.id}`),
  })
  const pageCount = useMemo(
    () => Math.max(1, Math.ceil((catalogueQuery.data?.total ?? 0) / 24)),
    [catalogueQuery.data?.total],
  )

  function changeFilter(name: keyof BrowseParameters, value: string) {
    setParameters((current) => ({ ...current, [name]: value, page: 1 }))
  }

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setParameters((current) => ({ ...current, query: searchDraft.trim(), page: 1 }))
  }

  function resetFilters() {
    setSearchDraft('')
    setParameters(initialParameters)
  }

  return (
    <main className="mx-auto w-full max-w-360 px-[4vw] pb-16">
      <header className="flex min-h-21 items-center justify-between gap-4 border-b">
        <Link className="font-display text-[clamp(1.2rem,2vw,1.65rem)] font-bold tracking-[-.055em]" to="/catalogue" onClick={resetFilters}>
          REEL / INDEX
        </Link>
        <div className="flex items-center gap-4"><p className="hidden font-mono text-xs uppercase tracking-[.045em] text-[#d0dbe3] md:block">English films &amp; series · selected by signal</p><AccountMenu /></div>
      </header>

      <section className="grid grid-cols-[minmax(5rem,.35fr)_1fr] gap-x-8 border-b py-[clamp(2.5rem,6vw,5.5rem)] max-md:grid-cols-1" aria-labelledby="catalogue-title">
        <p className="m-0 mt-2 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary max-md:mb-5">The catalogue</p>
        <h1 id="catalogue-title" className="m-0 max-w-[14ch] font-display text-[clamp(2.85rem,5.5vw,5.25rem)] font-semibold leading-[.92] tracking-[-.06em] max-md:col-start-1">Find the next story worth your evening.</h1>
      </section>

      <section className="grid grid-cols-[minmax(18rem,1.2fr)_1.5fr_auto] items-end gap-x-8 gap-y-5 border-b py-8 max-md:grid-cols-1" aria-label="Catalogue search and filters">
        <form className="grid gap-2" onSubmit={submitSearch}>
          <label className="font-mono text-xs font-bold uppercase tracking-[.1em] text-muted-foreground" htmlFor="title-search">Search titles</label>
          <div className="flex">
            <input
              className="min-w-0 flex-1 rounded-l-sm border-r-0 bg-card px-3.5 py-3 text-foreground placeholder:text-muted-foreground"
              id="title-search"
              value={searchDraft}
              onChange={(event) => setSearchDraft(event.target.value)}
              placeholder="Try “Dune” or “The Bear”"
            />
            <button className="rounded-r-sm border-primary bg-primary px-4 py-3 text-primary-foreground" type="submit">Search</button>
          </div>
        </form>

        <div className="grid grid-cols-3 gap-2 max-sm:grid-cols-1">
          <label className="grid gap-2 font-mono text-xs font-bold uppercase tracking-[.1em] text-muted-foreground">
            Format
            <select className="min-w-0 rounded-sm bg-card px-3.5 py-3 text-foreground" value={parameters.type} onChange={(event) => changeFilter('type', event.target.value)}>
              <option value="">All formats</option>
              <option value="movie">Movies</option>
              <option value="tv">TV series</option>
            </select>
          </label>
          <label className="grid gap-2 font-mono text-xs font-bold uppercase tracking-[.1em] text-muted-foreground">
            Genre
            <select className="min-w-0 rounded-sm bg-card px-3.5 py-3 text-foreground" value={parameters.genre} onChange={(event) => changeFilter('genre', event.target.value)}>
              <option value="">Every genre</option>
              {filtersQuery.data?.genres.map((genre) => <option key={genre}>{genre}</option>)}
            </select>
          </label>
          <label className="grid gap-2 font-mono text-xs font-bold uppercase tracking-[.1em] text-muted-foreground">
            Year
            <select className="min-w-0 rounded-sm bg-card px-3.5 py-3 text-foreground" value={parameters.year} onChange={(event) => changeFilter('year', event.target.value)}>
              <option value="">Any year</option>
              {filtersQuery.data?.years.map((year) => <option key={year}>{year}</option>)}
            </select>
          </label>
        </div>
        <button className="border-b border-current pb-0.5 text-[#d9e4eb]" type="button" onClick={resetFilters}>Clear filters</button>
      </section>

      <section className="pt-8" aria-live="polite">
        <div className="mb-6 flex items-baseline justify-between max-sm:flex-col max-sm:items-start max-sm:gap-2">
          <p className="m-0 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">Results</p>
          <p className="m-0 font-mono text-xs text-muted-foreground">{catalogueQuery.data ? `${catalogueQuery.data.total} titles in the index` : 'Reading the index…'}</p>
        </div>

        {catalogueQuery.isError && <CatalogueMessage title="The catalogue is unavailable" body="Start the API and sync the catalogue, then try again." />}
        {catalogueQuery.isLoading && <div className="grid grid-cols-4 gap-x-4 gap-y-[clamp(1rem,2.2vw,2.75rem)] max-md:grid-cols-2">{Array.from({ length: 8 }, (_, index) => <div className="aspect-2/3 animate-[catalogue-scan_1.5s_linear_infinite] bg-[linear-gradient(110deg,#24384a_25%,#334e63_37%,#24384a_63%)] bg-size-[200%_100%] motion-reduce:animate-none" key={index} />)}</div>}
        {catalogueQuery.data?.items.length === 0 && !shouldSearchTmdb && (
          <CatalogueMessage
            title="No titles match these filters"
            body="Broaden a filter or search for another title."
          />
        )}
        {shouldSearchTmdb && tmdbQuery.isLoading && <CatalogueMessage title="Searching TMDB" body="Looking beyond the local catalogue…" />}
        {shouldSearchTmdb && tmdbQuery.isError && <CatalogueMessage title="No local titles match" body="TMDB search is unavailable right now." />}
        {shouldSearchTmdb && tmdbQuery.data?.items.length === 0 && <CatalogueMessage title="No titles match this search" body="Try another title." />}
        {shouldSearchTmdb && tmdbQuery.data && tmdbQuery.data.items.length > 0 && (
          <div>
            <CatalogueMessage
              title="Available from TMDB"
              body="Choose a title to add it to the catalogue and find similar stories."
            />
            <div className="grid grid-cols-4 gap-x-4 gap-y-[clamp(1rem,2.2vw,2.75rem)] max-md:grid-cols-2">
              {tmdbQuery.data.items.map((title) => (
                <ExternalTitleCard
                  key={`${title.type}-${title.tmdbId}`}
                  title={title}
                  onImport={() => importMutation.mutate(title)}
                  disabled={importMutation.isPending}
                />
              ))}
            </div>
            {importMutation.isError && (
              <p role="alert" className="mt-5 text-rose-300">Could not import this title. Try again.</p>
            )}
          </div>
        )}
        {catalogueQuery.data && catalogueQuery.data.items.length > 0 && (
          <div className="grid grid-cols-4 gap-x-4 gap-y-[clamp(1rem,2.2vw,2.75rem)] max-md:grid-cols-2">
            {catalogueQuery.data.items.map((title) => <TitleCard key={title.id} title={title} onOpen={(id) => navigate(`/catalogue/${id}`)} />)}
          </div>
        )}
      </section>

      {catalogueQuery.data && catalogueQuery.data.total > 0 && (
        <nav className="mt-16 flex items-center justify-center gap-4 font-mono text-xs text-muted-foreground max-sm:gap-2" aria-label="Catalogue pages">
          <button className="rounded-sm border-primary bg-primary px-4 py-3 text-primary-foreground disabled:cursor-not-allowed disabled:opacity-35" disabled={parameters.page === 1} onClick={() => setParameters((current) => ({ ...current, page: current.page - 1 }))}>Previous</button>
          <span>Page {parameters.page} of {pageCount}</span>
          <button className="rounded-sm border-primary bg-primary px-4 py-3 text-primary-foreground disabled:cursor-not-allowed disabled:opacity-35" disabled={parameters.page >= pageCount} onClick={() => setParameters((current) => ({ ...current, page: current.page + 1 }))}>Next</button>
        </nav>
      )}
    </main>
  )
}

function TitleCard({ title, onOpen }: { title: CatalogueTitle; onOpen: (titleId: string) => void }) {
  const poster = posterUrl(title.posterPath)
  return (
    <article className="min-w-0">
      <button className="group block aspect-2/3 w-full overflow-hidden bg-[#31485c]" onClick={() => onOpen(title.id)} aria-label={`Open ${title.title}`}>
        {poster ? <img className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.045] motion-reduce:transition-none" src={poster} alt="" /> : <span className="grid h-full w-full place-items-center font-display italic leading-[1.1] text-muted-foreground">No image<br />available</span>}
      </button>
      <div className="pt-3">
        <p className="m-0 font-mono text-xs uppercase tracking-[.045em] text-[#d0dbe3]">{title.type === 'movie' ? 'Film' : 'Series'} · {title.releaseDate?.slice(0, 4) ?? '—'}</p>
        <h2 className="my-1.5 font-display text-[clamp(1.3rem,1.8vw,1.8rem)] font-semibold leading-[1.05] tracking-[-.035em]"><button className="text-left" onClick={() => onOpen(title.id)}>{title.title}</button></h2>
        <span className="font-mono text-xs uppercase tracking-[.045em] text-[#d0dbe3]">{title.genres.slice(0, 2).join(' · ')}</span>
      </div>
    </article>
  )
}

type ExternalTitleCardProps = {
  title: ExternalTitle
  onImport: () => void
  disabled: boolean
}

function ExternalTitleCard({ title, onImport, disabled }: ExternalTitleCardProps) {
  const poster = posterUrl(title.posterPath)
  return (
    <article className="min-w-0">
      <button
        className="group block aspect-2/3 w-full overflow-hidden bg-[#31485c] disabled:opacity-60"
        onClick={onImport}
        disabled={disabled}
        aria-label={`Import ${title.title}`}
      >
        {poster ? <img className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.045]" src={poster} alt="" /> : <span className="grid h-full place-items-center font-display italic text-muted-foreground">No image</span>}
      </button>
      <div className="pt-3">
        <p className="m-0 font-mono text-xs uppercase tracking-[.045em] text-[#d0dbe3]">{title.type === 'movie' ? 'Film' : 'Series'} · {title.releaseDate?.slice(0, 4) ?? '—'}</p>
        <h2 className="my-1.5 font-display text-[clamp(1.3rem,1.8vw,1.8rem)] font-semibold leading-[1.05] tracking-[-.035em]">{title.title}</h2>
        <span className="font-mono text-xs uppercase tracking-[.045em] text-primary">Add and find similar</span>
      </div>
    </article>
  )
}
