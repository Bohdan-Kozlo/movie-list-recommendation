import { SiteHeader } from '../navigation/SiteHeader'
import { CatalogueMessage } from './CatalogueMessage'
import { CatalogueFilters } from './CatalogueFilters'
import { TitleCard } from './TitleCard'
import { ExternalTitleCard } from './ExternalTitleCard'
import { useCatalogue } from './useCatalogue'

export function CataloguePage() {
  const {
    parameters, setParameters, searchDraft, setSearchDraft,
    catalogueQuery, filtersQuery, tmdbQuery, shouldSearchTmdb, importMutation,
    pageCount, changeFilter, submitSearch, resetFilters, openTitle,
  } = useCatalogue()
  return (
    <main className="mx-auto w-full max-w-360 px-[4vw] pb-16">
      <SiteHeader onBrandClick={resetFilters} />

      <section
        className="grid grid-cols-[minmax(5rem,.35fr)_1fr] gap-x-8 border-b py-[clamp(2.5rem,6vw,5.5rem)] max-md:grid-cols-1"
        aria-labelledby="catalogue-title"
      >
        <p className="m-0 mt-2 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary max-md:mb-5">The catalogue</p>
        <h1
          id="catalogue-title"
          className="m-0 max-w-[14ch] font-display text-[clamp(2.85rem,5.5vw,5.25rem)] font-semibold leading-[.92] tracking-[-.06em] max-md:col-start-1"
        >Find the next story worth your evening.</h1>
      </section>

      <CatalogueFilters
        parameters={parameters}
        filters={filtersQuery.data}
        searchDraft={searchDraft}
        setSearchDraft={setSearchDraft}
        changeFilter={changeFilter}
        submitSearch={submitSearch}
        resetFilters={resetFilters}
      />

      <section className="pt-8" aria-live="polite">
        <div className="mb-6 flex items-baseline justify-between max-sm:flex-col max-sm:items-start max-sm:gap-2">
          <p className="m-0 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">Results</p>
          <p className="m-0 font-mono text-xs text-muted-foreground">
            {catalogueQuery.data ? `${catalogueQuery.data.total} titles in the index` : 'Reading the index…'}
          </p>
        </div>

        {
          catalogueQuery.isError && <CatalogueMessage
            title="The catalogue is unavailable"
            body="Start the API and sync the catalogue, then try again."
          />
        }
        {
          catalogueQuery.isLoading && <div className="grid grid-cols-4 gap-x-4 gap-y-[clamp(1rem,2.2vw,2.75rem)] max-md:grid-cols-2">
            {
              Array.from({ length: 8 }, (_, index) => <div
                className="aspect-2/3 animate-[catalogue-scan_1.5s_linear_infinite] bg-[linear-gradient(110deg,#24384a_25%,#334e63_37%,#24384a_63%)] bg-size-[200%_100%] motion-reduce:animate-none"
                key={index}
              />)
            }
          </div>
        }
        {
          catalogueQuery.data?.items.length === 0 && !shouldSearchTmdb && (
            <CatalogueMessage
              title="No titles match these filters"
              body="Broaden a filter or search for another title."
            />
          )
        }
        {
          shouldSearchTmdb && tmdbQuery.isLoading && <CatalogueMessage title="Searching TMDB" body="Looking beyond the local catalogue…" />
        }
        {
          shouldSearchTmdb && tmdbQuery.isError && <CatalogueMessage title="No local titles match" body="TMDB search is unavailable right now." />
        }
        {
          shouldSearchTmdb && tmdbQuery.data?.items.length === 0 && <CatalogueMessage title="No titles match this search" body="Try another title." />
        }
        {
          shouldSearchTmdb && tmdbQuery.data && tmdbQuery.data.items.length > 0 && (
            <div>
              <CatalogueMessage
                title="Available from TMDB"
                body="Choose a title to add it to the catalogue and find similar stories."
              />
              <div className="grid grid-cols-4 gap-x-4 gap-y-[clamp(1rem,2.2vw,2.75rem)] max-md:grid-cols-2">
                {
                  tmdbQuery.data.items.map((title) => (
                    <ExternalTitleCard
                      key={`${title.type}-${title.tmdbId}`}
                      title={title}
                      onImport={() => importMutation.mutate(title)}
                      disabled={importMutation.isPending}
                    />
                  ))
                }
              </div>
              {
                importMutation.isError && (
                  <p role="alert" className="mt-5 text-rose-300">Could not import this title. Try again.</p>
                )
              }
            </div>
          )
        }
        {
          catalogueQuery.data && catalogueQuery.data.items.length > 0 && (
            <div className="grid grid-cols-4 gap-x-4 gap-y-[clamp(1rem,2.2vw,2.75rem)] max-md:grid-cols-2">
              {
                catalogueQuery.data.items.map((title) => <TitleCard key={title.id} title={title} onOpen={openTitle} />)
              }
            </div>
          )
        }
      </section>

      {
        catalogueQuery.data && catalogueQuery.data.total > 0 && (
          <nav
            className="mt-16 flex items-center justify-center gap-4 font-mono text-xs text-muted-foreground max-sm:gap-2"
            aria-label="Catalogue pages"
          >
            <button
              className="rounded-sm border-primary bg-primary px-4 py-3 text-primary-foreground disabled:cursor-not-allowed disabled:opacity-35"
              disabled={parameters.page === 1}
              onClick={() => setParameters((current) => ({ ...current, page: current.page - 1 }))}
            >Previous</button>
            <span>Page {parameters.page} of {pageCount}</span>
            <button
              className="rounded-sm border-primary bg-primary px-4 py-3 text-primary-foreground disabled:cursor-not-allowed disabled:opacity-35"
              disabled={parameters.page >= pageCount}
              onClick={() => setParameters((current) => ({ ...current, page: current.page + 1 }))}
            >Next</button>
          </nav>
        )
      }
    </main>
  )
}
