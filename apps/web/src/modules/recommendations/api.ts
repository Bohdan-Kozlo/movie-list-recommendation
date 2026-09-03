import { apiRequest } from '../../shared/api/client'
import type { TitleCard } from '../../shared/catalogue'

export type SimilarTitle = TitleCard & { reason: string }

export function fetchSimilarTitles(titleId: string): Promise<{ items: SimilarTitle[] }> {
  return apiRequest<{ items: SimilarTitle[] }>(`/recommendations/titles/${titleId}/similar`)
}
