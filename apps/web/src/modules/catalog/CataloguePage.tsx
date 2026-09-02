import { useQuery } from '@tanstack/react-query'
import { FormEvent, useMemo, useState } from 'react'

import {
  BrowseParameters,
  CatalogueTitle,
  fetchCatalogue,
  fetchCatalogueFilters,
  posterUrl,
} from './api'
import { CatalogueMessage } from './CatalogueMessage'

const initialParameters: BrowseParameters = {
  query: '',
  type: '',
  genre: '',
  language: '',
  year: '',
  page: 1,
}

type CataloguePageProps = {
  onOpenTitle: (titleId: string) => void
}

export function CataloguePage({ onOpenTitle }: CataloguePageProps) {
  const [parameters, setParameters] = useState(initialParameters)
  const [searchDraft, setSearchDraft] = useState('')
  const catalogueQuery = useQuery({
    queryKey: ['catalogue', parameters],
    queryFn: () => fetchCatalogue(parameters),
  })
  const filtersQuery = useQuery({ queryKey: ['catalogue', 'filters'], queryFn: fetchCatalogueFilters })
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
    <main className="catalogue-shell">
      <header className="masthead">
        <a className="wordmark" href="/catalogue" onClick={(event) => { event.preventDefault(); resetFilters() }}>
          REEL / INDEX
        </a>
        <p className="masthead-note">English films &amp; series · selected by signal</p>
      </header>

      <section className="catalogue-intro" aria-labelledby="catalogue-title">
        <p className="eyebrow">The catalogue</p>
        <h1 id="catalogue-title">Find the next story<br />worth your evening.</h1>
        <p>Browse a living index of films and television, refreshed from TMDB.</p>
      </section>

      <section className="discovery-panel" aria-label="Catalogue search and filters">
        <form className="search-form" onSubmit={submitSearch}>
          <label htmlFor="title-search">Search titles</label>
          <div className="search-row">
            <input
              id="title-search"
              value={searchDraft}
              onChange={(event) => setSearchDraft(event.target.value)}
              placeholder="Try “Dune” or “The Bear”"
            />
            <button type="submit">Search</button>
          </div>
        </form>

        <div className="filter-grid">
          <label>
            Format
            <select value={parameters.type} onChange={(event) => changeFilter('type', event.target.value)}>
              <option value="">All formats</option>
              <option value="movie">Movies</option>
              <option value="tv">TV series</option>
            </select>
          </label>
          <label>
            Genre
            <select value={parameters.genre} onChange={(event) => changeFilter('genre', event.target.value)}>
              <option value="">Every genre</option>
              {filtersQuery.data?.genres.map((genre) => <option key={genre}>{genre}</option>)}
            </select>
          </label>
          <label>
            Original language
            <select value={parameters.language} onChange={(event) => changeFilter('language', event.target.value)}>
              <option value="">Every language</option>
              {filtersQuery.data?.languages.map((language) => <option key={language} value={language}>{language.toUpperCase()}</option>)}
            </select>
          </label>
          <label>
            Year
            <select value={parameters.year} onChange={(event) => changeFilter('year', event.target.value)}>
              <option value="">Any year</option>
              {filtersQuery.data?.years.map((year) => <option key={year}>{year}</option>)}
            </select>
          </label>
        </div>
        <button className="text-button" type="button" onClick={resetFilters}>Clear filters</button>
      </section>

      <section className="results-section" aria-live="polite">
        <div className="results-heading">
          <p className="eyebrow">Results</p>
          <p>{catalogueQuery.data ? `${catalogueQuery.data.total} titles in the index` : 'Reading the index…'}</p>
        </div>

        {catalogueQuery.isError && <CatalogueMessage title="The catalogue is unavailable" body="Start the API and sync the catalogue, then try again." />}
        {catalogueQuery.isLoading && <div className="title-grid skeleton-grid">{Array.from({ length: 8 }, (_, index) => <div className="skeleton-card" key={index} />)}</div>}
        {catalogueQuery.data?.items.length === 0 && <CatalogueMessage title="No titles match these filters" body="Broaden a filter or search for another title." />}
        {catalogueQuery.data && catalogueQuery.data.items.length > 0 && (
          <div className="title-grid">
            {catalogueQuery.data.items.map((title) => <TitleCard key={title.id} title={title} onOpen={onOpenTitle} />)}
          </div>
        )}
      </section>

      {catalogueQuery.data && catalogueQuery.data.total > 0 && (
        <nav className="pagination" aria-label="Catalogue pages">
          <button disabled={parameters.page === 1} onClick={() => setParameters((current) => ({ ...current, page: current.page - 1 }))}>Previous</button>
          <span>Page {parameters.page} of {pageCount}</span>
          <button disabled={parameters.page >= pageCount} onClick={() => setParameters((current) => ({ ...current, page: current.page + 1 }))}>Next</button>
        </nav>
      )}
    </main>
  )
}

function TitleCard({ title, onOpen }: { title: CatalogueTitle; onOpen: (titleId: string) => void }) {
  const poster = posterUrl(title.posterPath)
  return (
    <article className="title-card">
      <button className="poster-button" onClick={() => onOpen(title.id)} aria-label={`Open ${title.title}`}>
        {poster ? <img src={poster} alt="" /> : <span className="poster-fallback">No image<br />available</span>}
      </button>
      <div className="title-card-copy">
        <p>{title.type === 'movie' ? 'Film' : 'Series'} · {title.releaseDate?.slice(0, 4) ?? '—'}</p>
        <h2><button onClick={() => onOpen(title.id)}>{title.title}</button></h2>
        <span>{title.genres.slice(0, 2).join(' · ')}</span>
      </div>
    </article>
  )
}
