import type { FormEvent } from 'react'
import type { BrowseParameters, CatalogueFilters as FilterOptions } from './api'

type CatalogueFiltersProps = {
  parameters: BrowseParameters
  filters: FilterOptions | undefined
  searchDraft: string
  setSearchDraft: (value: string) => void
  changeFilter: <K extends 'type' | 'genre' | 'year'>(name: K, value: BrowseParameters[K]) => void
  submitSearch: (event: FormEvent<HTMLFormElement>) => void
  resetFilters: () => void
}

export function CatalogueFilters({ parameters, filters, searchDraft, setSearchDraft, changeFilter, submitSearch, resetFilters }: CatalogueFiltersProps) {
  return (
    <section
      className="grid grid-cols-[minmax(18rem,1.2fr)_1.5fr_auto] items-end gap-x-8 gap-y-5 border-b py-8 max-md:grid-cols-1"
      aria-label="Catalogue search and filters"
    >
      <form className="grid gap-2" onSubmit={submitSearch}>
        <label
          className="font-mono text-xs font-bold uppercase tracking-[.1em] text-muted-foreground"
          htmlFor="title-search"
        >Search titles</label>
        <div className="flex">
          <input
            className="min-w-0 flex-1 rounded-l-sm border-r-0 bg-card px-3.5 py-3 text-foreground placeholder:text-muted-foreground"
            id="title-search"
            value={searchDraft}
            onChange={(event) => setSearchDraft(event.target.value)}
            placeholder="Try “Dune” or “The Bear”"
          />
          <button
            className="rounded-r-sm border-primary bg-primary px-4 py-3 text-primary-foreground"
            type="submit"
          >Search</button>
        </div>
      </form>

      <div className="grid grid-cols-3 gap-2 max-sm:grid-cols-1">
        <label className="grid gap-2 font-mono text-xs font-bold uppercase tracking-[.1em] text-muted-foreground">
          Format
          <select
            className="min-w-0 rounded-sm bg-card px-3.5 py-3 text-foreground"
            value={parameters.type}
            onChange={(event) => changeFilter('type', event.target.value as BrowseParameters['type'])}
          >
            <option value="">All formats</option>
            <option value="movie">Movies</option>
            <option value="tv">TV series</option>
          </select>
        </label>
        <label className="grid gap-2 font-mono text-xs font-bold uppercase tracking-[.1em] text-muted-foreground">
          Genre
          <select
            className="min-w-0 rounded-sm bg-card px-3.5 py-3 text-foreground"
            value={parameters.genre}
            onChange={(event) => changeFilter('genre', event.target.value)}
          >
            <option value="">Every genre</option>
            {filters?.genres.map((genre) => <option key={genre}>{genre}</option>)}
          </select>
        </label>
        <label className="grid gap-2 font-mono text-xs font-bold uppercase tracking-[.1em] text-muted-foreground">
          Year
          <select
            className="min-w-0 rounded-sm bg-card px-3.5 py-3 text-foreground"
            value={parameters.year}
            onChange={(event) => changeFilter('year', event.target.value)}
          >
            <option value="">Any year</option>
            {filters?.years.map((year) => <option key={year}>{year}</option>)}
          </select>
        </label>
      </div>
      <button
        className="border-b border-current pb-0.5 text-[#d9e4eb]"
        type="button"
        onClick={resetFilters}
      >Clear filters</button>
    </section>
  )
}
