import type { QueryClient } from '@tanstack/react-query'
import type { LibraryCollection } from './api'

export const interactionKeys = {
  all: ['interactions'] as const,
  libraries: ['interactions', 'library'] as const,
  library: (collection: LibraryCollection) => ['interactions', 'library', collection] as const,
  title: (titleId: string) => ['interactions', 'title', titleId] as const,
}

export function invalidateTitleInteractions(client: QueryClient, titleId: string) {
  void client.invalidateQueries({ queryKey: interactionKeys.title(titleId) })
  void client.invalidateQueries({ queryKey: interactionKeys.libraries })
}
