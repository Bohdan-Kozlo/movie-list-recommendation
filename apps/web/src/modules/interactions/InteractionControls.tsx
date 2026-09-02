import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router'
import { useState } from 'react'

import {
  addNotInterested,
  addWatchlist,
  createRating,
  deleteRating,
  fetchInteractionStatus,
  markWatched,
  removeNotInterested,
  removeWatched,
  removeWatchlist,
} from './api'
import { Button } from '../../shared/ui/Button'
import { Card } from '../../shared/ui/Card'

type InteractionControlsProps = {
  titleId: string
}

const ratingValues = Array.from({ length: 10 }, (_, index) => (index + 1) / 2)

export function InteractionControls({ titleId }: InteractionControlsProps) {
  const queryClient = useQueryClient()
  const [rating, setRating] = useState('4.0')
  const statusQuery = useQuery({
    queryKey: ['interactions', 'title', titleId],
    queryFn: () => fetchInteractionStatus(titleId),
  })
  const mutation = useMutation({
    mutationFn: (action: () => Promise<void>) => action(),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['interactions', 'title', titleId] })
      void queryClient.invalidateQueries({ queryKey: ['interactions', 'library'] })
    },
  })

  if (statusQuery.isLoading || statusQuery.data === undefined) {
    return <p className="text-sm text-muted-foreground">Loading your library…</p>
  }
  if (statusQuery.isError) return <p role="alert" className="text-sm text-red-800">Library actions are unavailable.</p>
  const status = statusQuery.data
  if (status === null) {
    return <p className="text-sm text-muted-foreground"><Link className="underline" to="/auth/sign-in">Sign in</Link> to rate and save this title.</p>
  }

  const run = (action: () => Promise<void>) => mutation.mutate(action)
  return (
    <Card className="mt-8 grid gap-4 p-5">
      <div>
        <p className="eyebrow">Your library</p>
        <h2 className="mt-1 font-serif text-2xl">Make this title yours</h2>
      </div>
      {status.rating === null ? (
        <div className="flex flex-wrap items-end gap-3">
          <label className="grid gap-1 text-sm text-muted-foreground">
            Rating
            <select value={rating} onChange={(event) => setRating(event.target.value)} className="h-11 border border-border bg-background px-3 text-foreground">
              {ratingValues.map((value) => <option key={value} value={value}>{value.toFixed(1)} / 5</option>)}
            </select>
          </label>
          <Button type="button" onClick={() => run(() => createRating(titleId, Number(rating)))} disabled={mutation.isPending}>Save rating</Button>
        </div>
      ) : (
        <div className="flex flex-wrap items-center gap-3"><span className="text-sm">Your rating: <strong>{status.rating.toFixed(1)} / 5</strong></span><Button variant="outline" type="button" onClick={() => run(() => deleteRating(titleId))} disabled={mutation.isPending}>Delete rating</Button></div>
      )}
      <div className="flex flex-wrap gap-2">
        <Button variant={status.is_watchlisted ? 'outline' : 'default'} type="button" onClick={() => run(() => status.is_watchlisted ? removeWatchlist(titleId) : addWatchlist(titleId))} disabled={mutation.isPending}>{status.is_watchlisted ? 'Remove from watchlist' : 'Add to watchlist'}</Button>
        <Button variant={status.is_watched ? 'outline' : 'default'} type="button" onClick={() => run(() => status.is_watched ? removeWatched(titleId) : markWatched(titleId))} disabled={mutation.isPending}>{status.is_watched ? 'Remove watched' : 'Mark watched'}</Button>
        <Button variant={status.is_not_interested ? 'outline' : 'ghost'} type="button" onClick={() => run(() => status.is_not_interested ? removeNotInterested(titleId) : addNotInterested(titleId))} disabled={mutation.isPending}>{status.is_not_interested ? 'Restore interest' : 'Not interested'}</Button>
      </div>
      {mutation.isError && <p role="alert" className="text-sm text-red-800">{mutation.error.message}</p>}
    </Card>
  )
}
