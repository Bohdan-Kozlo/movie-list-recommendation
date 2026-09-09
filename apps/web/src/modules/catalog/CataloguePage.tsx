import { SiteHeader } from '../navigation/SiteHeader'
import { CatalogueMessage } from './CatalogueMessage'
import { CatalogueFilters } from './CatalogueFilters'
import { TitleCard } from './TitleCard'
import { ExternalTitleCard } from './ExternalTitleCard'
import { useCatalogue } from './useCatalogue'

export function CataloguePage() {
  const {
    mode, setMode, parameters, setParameters, titleSearchDraft, setTitleSearchDraft,
    descriptionDraft, setDescriptionDraft, semanticParameters, descriptionValidationError,
    catalogueQuery, filtersQuery, semanticQuery, tmdbQuery, shouldSearchTmdb, importMutation,
    pageCount, changeFilter, changeSemanticFormat, submitSearch, resetFilters, openTitle,
  } = useCatalogue()
  const descriptionMode = mode === 'description'
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
        mode={mode}
        setMode={setMode}
        parameters={parameters}
        semanticParameters={semanticParameters}
        filters={filtersQuery.data}
        titleSearchDraft={titleSearchDraft}
        setTitleSearchDraft={setTitleSearchDraft}
        descriptionDraft={descriptionDraft}
        setDescriptionDraft={setDescriptionDraft}
        changeFilter={changeFilter}
        changeSemanticFormat={changeSemanticFormat}
        submitSearch={submitSearch}
        resetFilters={resetFilters}
      />

      <section className="pt-8" aria-live="polite">
        <div className="mb-6 flex items-baseline justify-between max-sm:flex-col max-sm:items-start max-sm:gap-2">
          <p className="m-0 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">Results</p>
          <p className="m-0 font-mono text-xs text-muted-foreground">
            {descriptionMode
              ? semanticParameters.description ? 'Up to 24 nearest indexed titles' : 'English descriptions only'
              : catalogueQuery.data ? `${catalogueQuery.data.total} titles in the index` : 'Reading the index…'}
          </p>
        </div>

        {
          !descriptionMode && catalogueQuery.isError && <CatalogueMessage
            title="The catalogue is unavailable"
            body="Start the API and sync the catalogue, then try again."
          />
        }
        {
          !descriptionMode && catalogueQuery.isLoading && <div className="grid grid-cols-4 gap-x-4 gap-y-[clamp(1rem,2.2vw,2.75rem)] max-md:grid-cols-2">
            {
              Array.from({ length: 8 }, (_, index) => <div
                className="aspect-2/3 animate-[catalogue-scan_1.5s_linear_infinite] bg-[linear-gradient(110deg,#24384a_25%,#334e63_37%,#24384a_63%)] bg-size-[200%_100%] motion-reduce:animate-none"
                key={index}
              />)
            }
          </div>
        }
        {
          !descriptionMode && catalogueQuery.data?.items.length === 0 && !shouldSearchTmdb && (
            <CatalogueMessage
              title="No titles match these filters"
              body="Broaden a filter or search for another title."
            />
          )
        }
        {
          !descriptionMode && shouldSearchTmdb && tmdbQuery.isLoading && <CatalogueMessage title="Searching TMDB" body="Looking beyond the local catalogue…" />
        }
        {
          !descriptionMode && shouldSearchTmdb && tmdbQuery.isError && <CatalogueMessage title="No local titles match" body="TMDB search is unavailable right now." />
        }
        {
          !descriptionMode && shouldSearchTmdb && tmdbQuery.data?.items.length === 0 && <CatalogueMessage title="No titles match this search" body="Try another title." />
        }
        {
          !descriptionMode && shouldSearchTmdb && tmdbQuery.data && tmdbQuery.data.items.length > 0 && (
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
          !descriptionMode && catalogueQuery.data && catalogueQuery.data.items.length > 0 && (
            <div className="grid grid-cols-4 gap-x-4 gap-y-[clamp(1rem,2.2vw,2.75rem)] max-md:grid-cols-2">
              {
                catalogueQuery.data.items.map((title) => <TitleCard key={title.id} title={title} onOpen={openTitle} />)
              }
            </div>
          )
        }
        {
          descriptionMode && !semanticParameters.description && !descriptionValidationError && (
            <CatalogueMessage
              title="Describe what you want to watch"
              body="Write an English plot, theme, or mood, then select Search."
            />
          )
        }
        {
          descriptionMode && descriptionValidationError && (
            <p role="alert" className="mt-5 text-rose-300">{descriptionValidationError}</p>
          )
        }
        {
          descriptionMode && semanticQuery.isLoading && <div className="grid grid-cols-4 gap-x-4 gap-y-[clamp(1rem,2.2vw,2.75rem)] max-md:grid-cols-2">
            {
              Array.from({ length: 8 }, (_, index) => <div
                className="aspect-2/3 animate-[catalogue-scan_1.5s_linear_infinite] bg-[linear-gradient(110deg,#24384a_25%,#334e63_37%,#24384a_63%)] bg-size-[200%_100%] motion-reduce:animate-none"
                key={index}
              />)
            }
          </div>
        }
        {
          descriptionMode && semanticQuery.isError && (
            <div className="my-8 border-l-4 border-primary bg-card px-6 py-5">
              <h2 className="m-0 font-display text-2xl font-medium">Description search is unavailable</h2>
              <p className="mt-1.5 text-muted-foreground">Check the local services and try again.</p>
              <button
                className="mt-4 rounded-sm bg-primary px-4 py-2 font-mono text-xs font-bold uppercase tracking-[.1em] text-primary-foreground"
                type="button"
                onClick={() => semanticQuery.refetch()}
              >Try again</button>
            </div>
          )
        }
        {
          descriptionMode && semanticQuery.data?.items.length === 0 && (
            <CatalogueMessage
              title="No indexed titles match this format"
              body="Try another description or choose a different format."
            />
          )
        }
        {
          descriptionMode && semanticQuery.data && semanticQuery.data.items.length > 0 && (
            <div>
              <p className="mb-6 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">Semantically matches your description</p>
              <div className="grid grid-cols-4 gap-x-4 gap-y-[clamp(1rem,2.2vw,2.75rem)] max-md:grid-cols-2">
                {
                  semanticQuery.data.items.map((title) => <TitleCard key={title.id} title={title} onOpen={openTitle} />)
                }
              </div>
            </div>
          )
        }
      </section>

      {
        !descriptionMode && catalogueQuery.data && catalogueQuery.data.total > 0 && (
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
