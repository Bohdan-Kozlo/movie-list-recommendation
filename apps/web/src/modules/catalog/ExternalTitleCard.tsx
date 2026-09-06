import type { ExternalTitle } from './api'
import { Poster } from '../../shared/ui/Poster'

type ExternalTitleCardProps = {
  title: ExternalTitle
  onImport: () => void
  disabled: boolean
}

export function ExternalTitleCard({ title, onImport, disabled }: ExternalTitleCardProps) {
  return (
    <article className="min-w-0">
      <button
        className="group block aspect-2/3 w-full overflow-hidden bg-[#31485c] disabled:opacity-60"
        onClick={onImport}
        disabled={disabled}
        aria-label={`Import ${title.title}`}
      >
        <Poster
          path={title.posterPath}
          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-[1.045]"
          fallback={<span className="grid h-full place-items-center font-display italic text-muted-foreground">No image</span>}
        />
      </button>
      <div className="pt-3">
        <p className="m-0 font-mono text-xs uppercase tracking-[.045em] text-[#d0dbe3]">
          {title.type === 'movie' ? 'Film' : 'Series'} · {title.releaseDate?.slice(0, 4) ?? '—'}
        </p>
        <h2 className="my-1.5 font-display text-[clamp(1.3rem,1.8vw,1.8rem)] font-semibold leading-[1.05] tracking-[-.035em]">
          {title.title}
        </h2>
        <span className="font-mono text-xs uppercase tracking-[.045em] text-primary">Add and find similar</span>
      </div>
    </article>
  )
}
