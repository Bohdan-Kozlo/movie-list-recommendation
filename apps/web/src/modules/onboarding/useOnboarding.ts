import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { type FormEvent, useState } from 'react'
import type { TitleCard } from '../../shared/catalogue'
import { createRating } from '../interactions/api'
import { interactionKeys } from '../interactions/queries'
import { fetchOnboarding, searchOnboardingTitles, type OnboardingProgress } from './api'
import { onboardingKeys } from './queries'

export function useOnboarding() {
  const queryClient = useQueryClient()
  const [candidateIndex, setCandidateIndex] = useState(0)
  const [selectedTitle, setSelectedTitle] = useState<TitleCard | null>(null)
  const [rating, setRating] = useState(4)
  const [searchDraft, setSearchDraft] = useState('')
  const [searchType, setSearchType] = useState<'' | 'movie' | 'tv'>('')
  const [submittedSearch, setSubmittedSearch] = useState('')
  const onboardingQuery = useQuery({
    queryKey: onboardingKeys.progress,
    queryFn: fetchOnboarding,
    staleTime: Infinity,
  })
  const searchQuery = useQuery({
    queryKey: onboardingKeys.search(submittedSearch, searchType),
    queryFn: () => searchOnboardingTitles(submittedSearch, searchType),
    enabled: Boolean(submittedSearch),
  })
  const ratingMutation = useMutation({
    mutationFn: ({ titleId, value }: { titleId: string; value: number }) => createRating(titleId, value),
    onSuccess: (_, variables) => {
      let wasInQueue = false
      queryClient.setQueryData<OnboardingProgress>(onboardingKeys.progress, (current) => {
        if (!current) return current
        wasInQueue = [...current.movies, ...current.tvSeries].some(
          (title) => title.id === variables.titleId,
        )
        const ratingsRecorded = current.ratingsRecorded + 1
        return {
          ...current,
          ratingsRecorded,
          ratingsRemaining: Math.max(0, current.ratingsRequired - ratingsRecorded),
          isComplete: ratingsRecorded >= current.ratingsRequired,
          movies: current.movies.filter((title) => title.id !== variables.titleId),
          tvSeries: current.tvSeries.filter((title) => title.id !== variables.titleId),
        }
      })
      setSelectedTitle(null)
      if (!wasInQueue) setCandidateIndex((current) => current + 1)
      void queryClient.invalidateQueries({ queryKey: interactionKeys.all })
    },
  })

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setSubmittedSearch(searchDraft.trim())
  }

  const candidates = [...(onboardingQuery.data?.movies ?? []), ...(onboardingQuery.data?.tvSeries ?? [])]
  const visibleIndex = Math.min(candidateIndex, Math.max(0, candidates.length - 1))
  const title = selectedTitle ?? candidates[visibleIndex]

  function previous() {
    setSelectedTitle(null)
    setCandidateIndex((current) => Math.max(0, current - 1))
  }

  function next() {
    setSelectedTitle(null)
    setCandidateIndex((current) => Math.min(candidates.length - 1, current + 1))
  }

  return {
    onboardingQuery, searchQuery, ratingMutation, candidates, visibleIndex, title,
    selectedTitle, setSelectedTitle, rating, setRating, searchDraft, setSearchDraft,
    searchType, setSearchType, submitSearch, previous, next,
  }
}
