import { catalogueKeys } from './queries'
import { useQuery } from '@tanstack/react-query'
import { useNavigate, useParams } from 'react-router'

import { fetchCatalogueTitle, posterUrl } from './api'
import { CatalogueMessage } from './CatalogueMessage'
import { InteractionControls } from '../interactions/InteractionControls'
import { SimilarTitles } from '../recommendations/SimilarTitles'
import { SiteHeader } from '../navigation/SiteHeader'

export function TitleDetailsPage() {
  const navigate = useNavigate()
  const { titleId } = useParams()
  const onBack = () => navigate('/catalogue')
  const titleQuery = useQuery({
    queryKey: catalogueKeys.details(titleId),
    queryFn: () => fetchCatalogueTitle(titleId ?? ''),
    enabled: titleId !== undefined,
  })
  if (!titleId) return null
  if (titleQuery.isLoading) return <main className="mx-auto w-full max-w-360 px-[4vw] pb-16">
    <div className="py-40 font-display text-3xl">Loading title…</div>
  </main>
  if (titleQuery.isError || !titleQuery.data) return <main className="mx-auto w-full max-w-360 px-[4vw] pb-16">
    <button className="border-b border-current pb-0.5 text-[#d9e4eb]" onClick={onBack}>← Back to catalogue</button>
    <CatalogueMessage
      title="This title is unavailable"
      body="Return to the catalogue and choose another title."
    />
  </main>

  const title = titleQuery.data
  const backdrop = posterUrl(title.backdropPath, 'original')
  const poster = posterUrl(title.posterPath)
  return (
    <main className="min-h-screen bg-background text-foreground">
      <div
        className="min-h-[min(54rem,100vh)] bg-[#162636] bg-cover bg-center bg-no-repeat"
        style={backdrop ? { backgroundImage: `linear-gradient(90deg, #172331 8%, rgba(23,35,49,.84) 42%, rgba(23,35,49,.28)), url(${backdrop})` } : undefined}
      >
        <div className="mx-auto w-[92vw]"><SiteHeader className="border-[#dae6ed]/35" /></div>
        <section className="mx-auto grid w-[84vw] max-w-280 grid-cols-[minmax(11rem,19rem)_minmax(0,42rem)] items-end gap-[clamp(2rem,6vw,7rem)] py-[clamp(4rem,12vh,10rem)] pb-20 max-md:grid-cols-1 max-md:pt-16">
          <div className="aspect-2/3 w-full max-w-76 overflow-hidden bg-[#31485c] max-md:w-48">
            {
              poster ? <img className="h-full w-full object-cover" src={poster} alt="" /> : <span className="grid h-full w-full place-items-center font-display italic leading-[1.1] text-muted-foreground">No image<br />available</span>
            }
          </div>
          <div>
            <p className="m-0 font-mono text-xs font-bold uppercase tracking-[.12em] text-[#d4e0e8]">
              {title.type === 'movie' ? 'Film' : 'TV series'} · {title.releaseDate?.slice(0, 4) ?? '—'}
            </p>
            <h1 className="mt-2 font-display text-[clamp(2.85rem,5.5vw,5.25rem)] font-semibold leading-[.92] tracking-[-.06em]">
              {title.title}
            </h1>
            {title.tagline && <p className="mt-6 font-display text-2xl italic text-primary">{title.tagline}</p>}
            <p className="mt-6 font-mono text-xs uppercase tracking-[.045em] text-[#d4e0e8]">
              {title.genres.join(' · ')} {title.runtimeMinutes ? `· ${title.runtimeMinutes} min` : ''} {title.voteAverage ? `· ${title.voteAverage.toFixed(1)} / 10` : ''}
            </p>
            <p className="max-w-152 font-sans text-[1.2rem] leading-[1.52] text-[#e3eaef]">
              {title.overview || 'No overview is available for this title.'}
            </p>
            {
              title.creators.length > 0 && <p className="mt-6 font-mono text-xs uppercase tracking-[.045em] text-[#d4e0e8]">
                <strong>{title.type === 'movie' ? 'Director' : 'Created by'}</strong> {title.creators.join(', ')}
              </p>
            }
            <InteractionControls titleId={title.id} />
          </div>
        </section>
      </div>
      {
        title.cast.length > 0 && <section className="mx-auto w-[84vw] max-w-280 py-14">
          <p className="m-0 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">Featured cast</p>
          <div className="mt-5 grid grid-cols-[repeat(auto-fit,minmax(11rem,1fr))] border-t">
            {
              title.cast.map((person) => <div
                className="grid min-h-22 gap-1.5 border-r border-b p-4"
                key={`${person.name}-${person.character}`}
              >
                <strong>{person.name}</strong>
                <span className="font-mono text-xs uppercase tracking-[.045em] text-[#d0dbe3]">
                  {person.character}
                </span>
              </div>)
            }
          </div>
        </section>
      }
      <SimilarTitles titleId={title.id} />
    </main>
  )
}
