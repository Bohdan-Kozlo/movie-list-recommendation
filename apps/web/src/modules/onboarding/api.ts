import { ApiError, authenticatedApiRequest } from '../../shared/api/client'
import type { TitleCard } from '../../shared/catalogue'

export type OnboardingProgress = {
  ratingsRecorded: number
  ratingsRequired: number
  ratingsRemaining: number
  isComplete: boolean
  movies: TitleCard[]
  tvSeries: TitleCard[]
}

export async function fetchOnboarding(): Promise<OnboardingProgress> {
  try {
    return await authenticatedApiRequest<OnboardingProgress>('/onboarding')
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) throw new Error('Sign in to set up your taste profile.')
    throw new Error('Taste onboarding is unavailable. Please try again.')
  }
}

export async function searchOnboardingTitles(
  query: string,
  type: '' | 'movie' | 'tv',
): Promise<{ items: TitleCard[] }> {
  const parameters = new URLSearchParams({ query })
  if (type) parameters.set('type', type)
  try {
    return await authenticatedApiRequest<{ items: TitleCard[] }>(`/onboarding/search?${parameters}`)
  } catch {
    throw new Error('Search is unavailable. Please try again.')
  }
}
