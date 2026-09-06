import { useMutation, useQueryClient } from '@tanstack/react-query'
import { invalidateTitleInteractions } from './queries'

export function useTitleInteractionMutation(titleId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (action: () => Promise<void>) => action(),
    onSuccess: () => invalidateTitleInteractions(queryClient, titleId),
  })
}
