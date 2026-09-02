export type TitleCard = {
  id: string
  title: string
  type: 'movie' | 'tv'
  releaseDate: string | null
  originalLanguage: string
  posterPath: string | null
  popularity: number
  genres: string[]
}

export function posterUrl(path: string | null, size = 'w500'): string | null {
  return path ? `https://image.tmdb.org/t/p/${size}${path}` : null
}
