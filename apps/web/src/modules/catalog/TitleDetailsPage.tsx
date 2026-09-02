import { useQuery } from '@tanstack/react-query'

import { fetchCatalogueTitle, posterUrl } from './api'
import { CatalogueMessage } from './CatalogueMessage'
import { AccountMenu } from '../auth/AccountMenu'

type TitleDetailsPageProps = {
  titleId: string
  onBack: () => void
  onNavigate: (path: string) => void
}

export function TitleDetailsPage({ titleId, onBack, onNavigate }: TitleDetailsPageProps) {
  const titleQuery = useQuery({ queryKey: ['catalogue', 'title', titleId], queryFn: () => fetchCatalogueTitle(titleId) })
  if (titleQuery.isLoading) return <main className="catalogue-shell"><div className="detail-loading">Loading title…</div></main>
  if (titleQuery.isError || !titleQuery.data) return <main className="catalogue-shell"><button className="back-link" onClick={onBack}>← Back to catalogue</button><CatalogueMessage title="This title is unavailable" body="Return to the catalogue and choose another title." /></main>

  const title = titleQuery.data
  const backdrop = posterUrl(title.backdropPath, 'original')
  const poster = posterUrl(title.posterPath)
  return (
    <main className="detail-page">
      <div className="detail-backdrop" style={backdrop ? { backgroundImage: `linear-gradient(90deg, #111114 8%, rgba(17,17,20,.82) 42%, rgba(17,17,20,.24)), url(${backdrop})` } : undefined}>
        <header className="masthead"><button className="wordmark" onClick={onBack}>REEL / INDEX</button><div className="masthead-right"><AccountMenu onNavigate={onNavigate} /><button className="back-link" onClick={onBack}>← Catalogue</button></div></header>
        <section className="detail-hero">
          <div className="detail-poster">{poster ? <img src={poster} alt="" /> : <span className="poster-fallback">No image<br />available</span>}</div>
          <div className="detail-copy">
            <p className="eyebrow">{title.type === 'movie' ? 'Film' : 'TV series'} · {title.releaseDate?.slice(0, 4) ?? '—'}</p>
            <h1>{title.title}</h1>
            {title.tagline && <p className="tagline">{title.tagline}</p>}
            <p className="metadata">{title.genres.join(' · ')} {title.runtimeMinutes ? `· ${title.runtimeMinutes} min` : ''} {title.voteAverage ? `· ${title.voteAverage.toFixed(1)} / 10` : ''}</p>
            <p className="overview">{title.overview || 'No overview is available for this title.'}</p>
            {title.creators.length > 0 && <p className="credit"><strong>{title.type === 'movie' ? 'Director' : 'Created by'}</strong> {title.creators.join(', ')}</p>}
          </div>
        </section>
      </div>
      {title.cast.length > 0 && <section className="cast-section"><p className="eyebrow">Featured cast</p><div className="cast-list">{title.cast.map((person) => <div key={`${person.name}-${person.character}`}><strong>{person.name}</strong><span>{person.character}</span></div>)}</div></section>}
    </main>
  )
}
