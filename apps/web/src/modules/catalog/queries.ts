import type { BrowseParameters, SemanticDescriptionParameters } from './api'

export const catalogueKeys = {
  list: (parameters: BrowseParameters) => ['catalogue', parameters] as const,
  filters: ['catalogue', 'filters'] as const,
  details: (titleId: string | undefined) => ['catalogue', 'title', titleId] as const,
  external: (query: string, type: string) => ['catalogue', 'tmdb-search', query, type] as const,
  semantic: (parameters: SemanticDescriptionParameters) => ['catalogue', 'semantic-search', parameters] as const,
}
