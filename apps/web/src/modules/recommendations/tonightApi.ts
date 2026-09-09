import { authenticatedApiRequest } from '../../shared/api/client'
import type { SimilarTitle } from './api'

export type TonightPreferences = {
  type: 'movie' | 'tv'
  genres: string[]
  max_minutes: number | null
  year_from: number | null
  year_to: number | null
  mode: 'familiar' | 'discover'
}

export type TonightResults = {
  items: SimilarTitle[]
  status: 'ready' | 'no_profile' | 'no_matches'
}

export function fetchTonightRecommendations(preferences: TonightPreferences): Promise<TonightResults> {
  return authenticatedApiRequest<TonightResults>('/recommendations/tonight', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(preferences),
  })
}
