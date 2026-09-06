import { recommendationKeys } from './queries'
import { useQuery } from '@tanstack/react-query'

import { fetchSimilarTitles } from './api'
import { RecommendationCard } from './RecommendationCard'

type SimilarTitlesProps = { titleId: string }

export function SimilarTitles({ titleId }: SimilarTitlesProps) {
  const query = useQuery({
    queryKey: recommendationKeys.similar(titleId),
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
        {query.data.items.map((title) => <RecommendationCard key={title.id} item={title} />)}
      </div>
    </section>
  )
}
