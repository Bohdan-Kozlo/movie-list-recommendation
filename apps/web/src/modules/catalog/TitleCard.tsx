import type { CatalogueTitle } from './api'
import { Poster } from '../../shared/ui/Poster'
import { QuickLibraryActions } from '../interactions/QuickLibraryActions'

export function TitleCard({ title, onOpen }: { title: CatalogueTitle; onOpen: (titleId: string) => void }) {
  return (
    <article className="min-w-0">
      <div className="group relative aspect-2/3 overflow-hidden bg-[#31485c]">
        <button
          className="block h-full w-full"
          onClick={() => onOpen(title.id)}
          aria-label={`Open ${title.title}`}
        >
          <Poster
            path={title.posterPath}
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.045] motion-reduce:transition-none"
            fallback={<span className="grid h-full w-full place-items-center font-display italic leading-[1.1] text-muted-foreground">No image<br />available</span>}
          />
        </button>
        <QuickLibraryActions titleId={title.id} />
      </div>
      <div className="pt-3">
        <p className="m-0 font-mono text-xs uppercase tracking-[.045em] text-[#d0dbe3]">
          {title.type === 'movie' ? 'Film' : 'Series'} · {title.releaseDate?.slice(0, 4) ?? '—'}
        </p>
        <h2 className="my-1.5 font-display text-[clamp(1.3rem,1.8vw,1.8rem)] font-semibold leading-[1.05] tracking-[-.035em]">
          <button className="text-left" onClick={() => onOpen(title.id)}>{title.title}</button>
        </h2>
        <span className="font-mono text-xs uppercase tracking-[.045em] text-[#d0dbe3]">
          {title.genres.slice(0, 2).join(' · ')}
        </span>
      </div>
    </article>
  )
}
