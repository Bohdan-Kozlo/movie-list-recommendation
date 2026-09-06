import { invalidateTitleInteractions } from './queries'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'

import { addNotInterested, addWatchlist, markWatched } from './api'

type QuickLibraryActionsProps = {
  titleId: string
}

type LibraryAction = 'watchlist' | 'watched' | 'not-interested'

const actions: Array<{
  id: LibraryAction
  emoji: string
  label: string
  successMessage: string
  run: (titleId: string) => Promise<void>
}> = [
    { id: 'watchlist', emoji: '🔖', label: 'Add to watchlist', successMessage: 'Saved', run: addWatchlist },
    { id: 'watched', emoji: '✅', label: 'Mark as watched', successMessage: 'Watched', run: markWatched },
    { id: 'not-interested', emoji: '🚫', label: 'Mark as not interested', successMessage: 'Hidden', run: addNotInterested },
  ]

export function QuickLibraryActions({ titleId }: QuickLibraryActionsProps) {
  const queryClient = useQueryClient()
  const [message, setMessage] = useState<string | null>(null)
  const mutation = useMutation({
    mutationFn: (action: LibraryAction) => actions.find((item) => item.id === action)!.run(titleId),
    onSuccess: (_data, action) => {
      setMessage(actions.find((item) => item.id === action)!.successMessage)
      invalidateTitleInteractions(queryClient, titleId)
    },
    onError: () => setMessage('Try again'),
  })

  return (
    <div className="absolute inset-x-0 top-0 flex items-start justify-between p-2.5">
      <p
        className="rounded-full bg-[#122231]/90 px-2 py-1 font-mono text-[10px] font-bold uppercase tracking-[.08em] text-[#edf4f7] shadow-sm backdrop-blur-sm"
        aria-live="polite"
      >
        {message ?? 'Quick save'}
      </p>
      <div className="flex gap-1.5">
        {
          actions.map((action) => (
            <button
              aria-label={action.label}
              className="grid size-9 place-items-center rounded-full border border-[#d9e4eb]/35 bg-[#122231]/92 text-base shadow-sm transition hover:scale-110 hover:bg-[#e9a958] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:cursor-wait disabled:opacity-60 motion-reduce:transition-none"
              disabled={mutation.isPending}
              key={action.id}
              onClick={(event) => {
                event.stopPropagation()
                setMessage(null)
                mutation.mutate(action.id)
              }}
              title={action.label}
              type="button"
            >
              <span aria-hidden="true">{action.emoji}</span>
            </button>
          ))
        }
      </div>
    </div>
  )
}
