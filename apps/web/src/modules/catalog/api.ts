import { ApiError, apiRequest } from '../../shared/api/client'
import { posterUrl, type TitleCard } from '../../shared/catalogue'

export type CatalogueTitle = TitleCard
export { posterUrl }

export type CataloguePage = {
  items: CatalogueTitle[]
  total: number
  page: number
  pageSize: number
}

export type SemanticDescriptionSearch = {
  items: CatalogueTitle[]
}

export type CatalogueFilters = {
  genres: string[]
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

export type ExternalTitle = {
  tmdbId: number
  type: 'movie' | 'tv'
  title: string
  releaseDate: string | null
  posterPath: string | null
}

export type BrowseParameters = {
  query: string
  type: '' | 'movie' | 'tv'
  genre: string
  year: string
  page: number
}

export type SemanticDescriptionParameters = {
  description: string
  type: '' | 'movie' | 'tv'
}

export async function fetchCatalogue(parameters: BrowseParameters): Promise<CataloguePage> {
  const searchParameters = new URLSearchParams({ page: String(parameters.page) })
  if (parameters.query) searchParameters.set('query', parameters.query)
  if (parameters.type) searchParameters.set('type', parameters.type)
  if (parameters.genre) searchParameters.set('genre', parameters.genre)
  if (parameters.year) searchParameters.set('year', parameters.year)
  return catalogueRequest<CataloguePage>(`/catalogue/titles?${searchParameters}`)
}

export function searchCatalogueByDescription(
  parameters: SemanticDescriptionParameters,
): Promise<SemanticDescriptionSearch> {
  return catalogueRequest<SemanticDescriptionSearch>('/catalogue/semantic-search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      description: parameters.description,
      ...(parameters.type ? { type: parameters.type } : {}),
    }),
  })
}

export function fetchCatalogueFilters(): Promise<CatalogueFilters> {
  return catalogueRequest<CatalogueFilters>('/catalogue/filters')
}

export function fetchCatalogueTitle(titleId: string): Promise<CatalogueTitleDetails> {
  return catalogueRequest<CatalogueTitleDetails>(`/catalogue/titles/${titleId}`)
}

export function searchTmdbTitles(query: string, type: '' | 'movie' | 'tv'): Promise<{ items: ExternalTitle[] }> {
  const parameters = new URLSearchParams({ query })
  if (type) parameters.set('type', type)
  return catalogueRequest<{ items: ExternalTitle[] }>(`/catalogue/tmdb-search?${parameters}`)
}

export function importTmdbTitle(type: 'movie' | 'tv', tmdbId: number): Promise<CatalogueTitleDetails> {
  return catalogueRequest<CatalogueTitleDetails>(`/catalogue/tmdb-titles/${type}/${tmdbId}`, { method: 'POST' })
}

async function catalogueRequest<T>(path: string, init?: RequestInit): Promise<T> {
  try {
    return await apiRequest<T>(path, init)
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      throw new Error('This title is no longer in the catalogue.')
    }
    throw new Error('Catalogue unavailable.')
  }
}
