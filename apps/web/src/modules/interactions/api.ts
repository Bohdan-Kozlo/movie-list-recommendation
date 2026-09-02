import { ApiError, authenticatedApiRequest } from '../../shared/api/client'
import type { TitleCard } from '../../shared/catalogue'

export type InteractionStatus = {
  rating: number | null
  is_watchlisted: boolean
  is_watched: boolean
  is_not_interested: boolean
}

export type LibraryCollection = 'ratings' | 'watchlist' | 'watched' | 'not-interested'

export type LibraryItem = TitleCard & { rating: number | null }

export type LibraryResponse = {
  collection: LibraryCollection
  items: LibraryItem[]
}

export async function fetchInteractionStatus(titleId: string): Promise<InteractionStatus | null> {
  try {
    return await interactionApiRequest<InteractionStatus>(`/interactions/titles/${titleId}`)
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) return null
    throw new Error('Library status is unavailable.')
  }
}

export function createRating(titleId: string, value: number): Promise<void> {
  return interactionRequest(`/interactions/titles/${titleId}/ratings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ value }),
  })
}

export function deleteRating(titleId: string): Promise<void> {
  return interactionRequest(`/interactions/titles/${titleId}/ratings`, { method: 'DELETE' })
}

export function addWatchlist(titleId: string): Promise<void> {
  return interactionRequest(`/interactions/titles/${titleId}/watchlist`, { method: 'POST' })
}

export function removeWatchlist(titleId: string): Promise<void> {
  return interactionRequest(`/interactions/titles/${titleId}/watchlist`, { method: 'DELETE' })
}

export function markWatched(titleId: string): Promise<void> {
  return interactionRequest(`/interactions/titles/${titleId}/watched`, { method: 'POST' })
}

export function removeWatched(titleId: string): Promise<void> {
  return interactionRequest(`/interactions/titles/${titleId}/watched`, { method: 'DELETE' })
}

export function addNotInterested(titleId: string): Promise<void> {
  return interactionRequest(`/interactions/titles/${titleId}/not-interested`, { method: 'POST' })
}

export function removeNotInterested(titleId: string): Promise<void> {
  return interactionRequest(`/interactions/titles/${titleId}/not-interested`, { method: 'DELETE' })
}

export async function fetchLibrary(collection: LibraryCollection): Promise<LibraryResponse> {
  try {
    return await interactionApiRequest<LibraryResponse>(`/interactions/library/${collection}`)
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) throw new Error('Sign in to view your library.')
    throw new Error('Your library is unavailable.')
  }
}

async function interactionRequest(path: string, init: RequestInit): Promise<void> {
  try {
    await interactionApiRequest<void>(path, init)
  } catch (error) {
    if (error instanceof ApiError) throw new Error(error.message)
    throw new Error('Your library could not be updated. Please try again.')
  }
}

const interactionApiRequest = authenticatedApiRequest
