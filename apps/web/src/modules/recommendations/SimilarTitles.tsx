import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router'

import { fetchSimilarTitles } from './api'
import { posterUrl } from '../../shared/catalogue'

type SimilarTitlesProps = { titleId: string }

export function SimilarTitles({ titleId }: SimilarTitlesProps) {
  const query = useQuery({
    queryKey: ['recommendations', 'similar', titleId],
    queryFn: () => fetchSimilarTitles(titleId),
  })
  if (query.isLoading) return <p className="py-10 text-muted-foreground">Finding related stories…</p>
  if (query.isError) return <p className="py-10 text-muted-foreground">Similar titles are unavailable right now.</p>
  if (!query.data?.items.length) return <p className="py-10 text-muted-foreground">No similar titles are indexed yet.</p>

  return (
    <section className="mx-auto w-[84vw] max-w-280 py-14" aria-labelledby="similar-titles">
      <p className="m-0 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">Related by signal</p>
      <h2 id="similar-titles" className="mt-2 font-display text-4xl font-semibold tracking-[-.05em]">Similar titles</h2>
      <div className="mt-7 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {query.data.items.map((title) => {
          const poster = posterUrl(title.posterPath)
          return (
            <Link key={title.id} to={`/catalogue/${title.id}`} className="group grid gap-3">
              <div className="aspect-2/3 overflow-hidden bg-card">{poster ? <img className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105" src={poster} alt="" /> : <span className="grid h-full place-items-center text-sm text-muted-foreground">No image</span>}</div>
              <div><p className="m-0 font-mono text-xs uppercase tracking-[.08em] text-primary">{title.type === 'movie' ? 'Film' : 'TV series'}</p><h3 className="mt-1 font-display text-2xl font-semibold leading-none">{title.title}</h3><p className="mb-0 mt-2 text-sm text-muted-foreground">{title.reason}</p></div>
            </Link>
          )
        })}
      </div>
    </section>
  )
}
