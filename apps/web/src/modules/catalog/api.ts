export type CatalogueTitle = {
  id: string
  title: string
  type: 'movie' | 'tv'
  releaseDate: string | null
  originalLanguage: string
  posterPath: string | null
  popularity: number
  genres: string[]
}

export type CataloguePage = {
  items: CatalogueTitle[]
  total: number
  page: number
  pageSize: number
}

export type CatalogueFilters = {
  genres: string[]
  languages: string[]
  years: number[]
}

export type CatalogueTitleDetails = CatalogueTitle & {
  overview: string | null
  runtimeMinutes: number | null
  backdropPath: string | null
  voteAverage: number | null
  tagline: string | null
  cast: Array<{ name: string; character: string }>
  creators: string[]
  keywords: string[]
}

export type BrowseParameters = {
  query: string
  type: '' | 'movie' | 'tv'
  genre: string
  language: string
  year: string
  page: number
}

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export async function fetchCatalogue(parameters: BrowseParameters): Promise<CataloguePage> {
  const searchParameters = new URLSearchParams({ page: String(parameters.page) })
  if (parameters.query) searchParameters.set('query', parameters.query)
  if (parameters.type) searchParameters.set('type', parameters.type)
  if (parameters.genre) searchParameters.set('genre', parameters.genre)
  if (parameters.language) searchParameters.set('language', parameters.language)
  if (parameters.year) searchParameters.set('year', parameters.year)
  return request<CataloguePage>(`/catalogue/titles?${searchParameters}`)
}

export function fetchCatalogueFilters(): Promise<CatalogueFilters> {
  return request<CatalogueFilters>('/catalogue/filters')
}

export function fetchCatalogueTitle(titleId: string): Promise<CatalogueTitleDetails> {
  return request<CatalogueTitleDetails>(`/catalogue/titles/${titleId}`)
}

export function posterUrl(path: string | null, size = 'w500'): string | null {
  return path ? `https://image.tmdb.org/t/p/${size}${path}` : null
}

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`)
  if (!response.ok) {
    throw new Error(response.status === 404 ? 'This title is no longer in the catalogue.' : 'Catalogue unavailable.')
  }
  return response.json() as Promise<T>
}
