import { apiRequest, authenticatedApiRequest } from '../../shared/api/client'
import type { TitleCard } from '../../shared/catalogue'

export type SimilarTitle = TitleCard & { reason: string }
export type PersonalRecommendations = {
  movies: { items: SimilarTitle[] }
  tvSeries: { items: SimilarTitle[] }
}

export function fetchSimilarTitles(titleId: string): Promise<{ items: SimilarTitle[] }> {
  return apiRequest<{ items: SimilarTitle[] }>(`/recommendations/titles/${titleId}/similar`)
}

export function fetchPersonalRecommendations(): Promise<PersonalRecommendations> {
  return authenticatedApiRequest<PersonalRecommendations>('/recommendations/personal')
}
