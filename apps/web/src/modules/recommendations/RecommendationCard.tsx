import { Link } from 'react-router'
import { Poster } from '../../shared/ui/Poster'
import type { SimilarTitle } from './api'

export function RecommendationCard({ item }: { item: SimilarTitle }) {
  return (
    <Link to={`/catalogue/${item.id}`} className="group grid gap-3">
      <div className="aspect-2/3 overflow-hidden bg-card">
        <Poster
          path={item.posterPath}
          className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
          fallback={<span className="grid h-full place-items-center text-sm text-muted-foreground">No image</span>}
        />
      </div>
      <div>
        <p className="m-0 font-mono text-xs uppercase tracking-[.08em] text-primary">
          {item.type === 'movie' ? 'Film' : 'TV series'}
        </p>
        <h3 className="mt-1 font-display text-2xl font-semibold leading-none">{item.title}</h3>
        <p className="mb-0 mt-2 text-sm text-muted-foreground">{item.reason}</p>
      </div>
    </Link>
  )
}
