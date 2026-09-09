import type { FormEvent } from 'react'
import type {
  BrowseParameters,
  CatalogueFilters as FilterOptions,
  SemanticDescriptionParameters,
} from './api'
import type { CatalogueSearchMode } from './useCatalogue'

type CatalogueFiltersProps = {
  mode: CatalogueSearchMode
  setMode: (mode: CatalogueSearchMode) => void
  parameters: BrowseParameters
  semanticParameters: SemanticDescriptionParameters
  filters: FilterOptions | undefined
  titleSearchDraft: string
  setTitleSearchDraft: (value: string) => void
  descriptionDraft: string
  setDescriptionDraft: (value: string) => void
  changeFilter: <K extends 'type' | 'genre' | 'year'>(name: K, value: BrowseParameters[K]) => void
  changeSemanticFormat: (value: SemanticDescriptionParameters['type']) => void
  submitSearch: (event: FormEvent<HTMLFormElement>) => void
  resetFilters: () => void
}

export function CatalogueFilters({ mode, setMode, parameters, semanticParameters, filters, titleSearchDraft, setTitleSearchDraft, descriptionDraft, setDescriptionDraft, changeFilter, changeSemanticFormat, submitSearch, resetFilters }: CatalogueFiltersProps) {
  const descriptionMode = mode === 'description'

  return (
    <section
      className="grid grid-cols-[minmax(18rem,1.2fr)_1.5fr_auto] items-end gap-x-8 gap-y-5 border-b py-8 max-md:grid-cols-1"
      aria-label="Catalogue search and filters"
    >
      <div className="col-span-3 flex gap-2 max-md:col-span-1" role="group" aria-label="Search mode">
        <button
          className={`rounded-sm px-4 py-2 font-mono text-xs font-bold uppercase tracking-[.1em] ${!descriptionMode ? 'bg-primary text-primary-foreground' : 'bg-card text-muted-foreground'}`}
          type="button"
          aria-pressed={!descriptionMode}
          onClick={() => setMode('title')}
        >Title</button>
        <button
          className={`rounded-sm px-4 py-2 font-mono text-xs font-bold uppercase tracking-[.1em] ${descriptionMode ? 'bg-primary text-primary-foreground' : 'bg-card text-muted-foreground'}`}
          type="button"
          aria-pressed={descriptionMode}
          onClick={() => setMode('description')}
        >Description</button>
      </div>
      <form className="grid gap-2" onSubmit={submitSearch}>
        <label
          className="font-mono text-xs font-bold uppercase tracking-[.1em] text-muted-foreground"
          htmlFor="title-search"
        >{descriptionMode ? 'Describe what you want to watch in English' : 'Search titles'}</label>
        <div className="flex">
          <input
            className="min-w-0 flex-1 rounded-l-sm border-r-0 bg-card px-3.5 py-3 text-foreground placeholder:text-muted-foreground"
            id="title-search"
            value={descriptionMode ? descriptionDraft : titleSearchDraft}
            onChange={(event) => (descriptionMode ? setDescriptionDraft : setTitleSearchDraft)(event.target.value)}
            placeholder={descriptionMode ? 'A tense mystery in a small coastal town' : 'Try “Dune” or “The Bear”'}
            maxLength={descriptionMode ? 500 : 200}
          />
          <button
            className="rounded-r-sm border-primary bg-primary px-4 py-3 text-primary-foreground"
            type="submit"
          >Search</button>
        </div>
      </form>

      <div className={`grid gap-2 ${descriptionMode ? 'grid-cols-1' : 'grid-cols-3'} max-sm:grid-cols-1`}>
        <label className="grid gap-2 font-mono text-xs font-bold uppercase tracking-[.1em] text-muted-foreground">
          Format
          <select
            className="min-w-0 rounded-sm bg-card px-3.5 py-3 text-foreground"
            value={descriptionMode ? semanticParameters.type : parameters.type}
            onChange={(event) => {
              const value = event.target.value as BrowseParameters['type']
              if (descriptionMode) changeSemanticFormat(value)
              else changeFilter('type', value)
            }}
          >
            <option value="">All formats</option>
            <option value="movie">Movies</option>
            <option value="tv">TV series</option>
          </select>
        </label>
        {!descriptionMode && <label className="grid gap-2 font-mono text-xs font-bold uppercase tracking-[.1em] text-muted-foreground">
          Genre
          <select
            className="min-w-0 rounded-sm bg-card px-3.5 py-3 text-foreground"
            value={parameters.genre}
            onChange={(event) => changeFilter('genre', event.target.value)}
          >
            <option value="">Every genre</option>
            {filters?.genres.map((genre) => <option key={genre}>{genre}</option>)}
          </select>
        </label>}
        {!descriptionMode && <label className="grid gap-2 font-mono text-xs font-bold uppercase tracking-[.1em] text-muted-foreground">
          Year
          <select
            className="min-w-0 rounded-sm bg-card px-3.5 py-3 text-foreground"
            value={parameters.year}
            onChange={(event) => changeFilter('year', event.target.value)}
          >
            <option value="">Any year</option>
            {filters?.years.map((year) => <option key={year}>{year}</option>)}
          </select>
        </label>}
      </div>
      <button
        className="border-b border-current pb-0.5 text-[#d9e4eb]"
        type="button"
        onClick={resetFilters}
      >Clear filters</button>
    </section>
  )
}
