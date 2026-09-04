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
import { StarRating } from '../../shared/ui/StarRating'

type InteractionControlsProps = { titleId: string }

export function InteractionControls({ titleId }: InteractionControlsProps) {
  const queryClient = useQueryClient()
  const [rating, setRating] = useState(4)
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
  if (statusQuery.isError) return <p role="alert" className="text-sm text-rose-300">Library actions are unavailable.</p>
  const status = statusQuery.data
  if (status === null) {
    return <p className="text-sm text-muted-foreground"><Link className="underline" to="/auth/sign-in">Sign in</Link> to rate and save this title.</p>
  }

  const run = (action: () => Promise<void>) => mutation.mutate(action)
  return (
    <div className="mt-8 grid gap-4">
      {status.rating === null ? (
        <Card className="grid gap-5 p-5">
          <div className="flex items-end justify-between gap-4">
            <div>
              <p className="m-0 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">Your rating</p>
              <h2 className="mt-1 font-display text-2xl font-semibold tracking-tight">How much did it land?</h2>
            </div>
            <output className="font-display text-4xl font-semibold tracking-[-.06em] text-primary" aria-live="polite">{rating.toFixed(1)}<span className="ml-1 text-base font-normal text-muted-foreground">/ 5</span></output>
          </div>
          <StarRating label="Choose a rating from 0.5 to 5.0" value={rating} onChange={setRating} disabled={mutation.isPending} />
          <div className="flex flex-wrap items-center justify-between gap-3 border-t pt-4">
            <p className="m-0 text-sm text-muted-foreground">Choose in half-star steps. Ratings cannot be edited after saving.</p>
            <Button type="button" onClick={() => run(() => createRating(titleId, rating))} disabled={mutation.isPending}>Save {rating.toFixed(1)} rating</Button>
          </div>
        </Card>
      ) : (
        <Card className="flex flex-wrap items-center justify-between gap-4 p-5">
          <div><p className="m-0 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">Your rating</p><p className="mt-1 font-display text-3xl font-semibold tracking-[-.05em]">{status.rating.toFixed(1)} <span className="text-base font-normal text-muted-foreground">/ 5</span></p></div>
          <Button variant="outline" type="button" onClick={() => run(() => deleteRating(titleId))} disabled={mutation.isPending}>Delete rating</Button>
        </Card>
      )}
      <Card className="grid gap-4 p-5">
        <div><p className="m-0 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">Watch status</p><h2 className="mt-1 font-display text-2xl font-semibold tracking-tight">Keep it in the right place</h2><p className="mb-0 mt-2 text-sm text-muted-foreground">Watched and not interested titles are removed from your watchlist automatically.</p></div>
        <div className="flex flex-wrap gap-2">
          <Button variant={status.is_watchlisted ? 'outline' : 'default'} type="button" onClick={() => run(() => status.is_watchlisted ? removeWatchlist(titleId) : addWatchlist(titleId))} disabled={mutation.isPending}>{status.is_watchlisted ? 'Remove from watchlist' : 'Add to watchlist'}</Button>
          <Button variant="outline" type="button" onClick={() => run(() => status.is_watched ? removeWatched(titleId) : markWatched(titleId))} disabled={mutation.isPending}>{status.is_watched ? 'Remove watched' : 'Mark watched'}</Button>
          <Button variant={status.is_not_interested ? 'outline' : 'ghost'} type="button" onClick={() => run(() => status.is_not_interested ? removeNotInterested(titleId) : addNotInterested(titleId))} disabled={mutation.isPending}>{status.is_not_interested ? 'Restore interest' : 'Not interested'}</Button>
        </div>
        {mutation.isError && <p role="alert" className="m-0 text-sm text-rose-300">{mutation.error.message}</p>}
      </Card>
    </div>
  )
}
