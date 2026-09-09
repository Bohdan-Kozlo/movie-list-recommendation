import { useState, type FormEvent } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchCatalogueFilters } from '../catalog/api'
import { catalogueKeys } from '../catalog/queries'
import { Button } from '../../shared/ui/Button'
import type { TonightPreferences } from './tonightApi'

type Props = {
  pending: boolean
  onSubmit: (preferences: TonightPreferences) => void
  onChange: () => void
}

const inputClass = 'mt-2 w-full rounded-sm border border-border bg-card px-3 py-3 text-foreground'

export function TonightForm({ pending, onSubmit, onChange }: Props) {
  const [type, setType] = useState<'movie' | 'tv'>('movie')
  const [genres, setGenres] = useState<string[]>([])
  const [maxMinutes, setMaxMinutes] = useState('')
  const [yearFrom, setYearFrom] = useState('')
  const [yearTo, setYearTo] = useState('')
  const [mode, setMode] = useState<'familiar' | 'discover'>('familiar')
  const [error, setError] = useState('')
  const filters = useQuery({ queryKey: catalogueKeys.filters, queryFn: fetchCatalogueFilters })

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (yearFrom && yearTo && Number(yearFrom) > Number(yearTo)) {
      setError('The start year must not be later than the end year.')
      return
    }
    setError('')
    onSubmit({
      type, genres, mode,
      max_minutes: maxMinutes ? Number(maxMinutes) : null,
      year_from: yearFrom ? Number(yearFrom) : null,
      year_to: yearTo ? Number(yearTo) : null,
    })
  }

  return (
    <form onSubmit={submit} onChange={() => { setError(''); onChange() }} className="border-b py-8">
      <fieldset disabled={pending} className="min-w-0 space-y-7 disabled:opacity-60">
        <legend className="sr-only">Tonight's viewing preferences</legend>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <label className="text-sm font-medium">
            What would you like to watch?
            <select
              className={inputClass}
              value={type}
              onChange={(event) => setType(event.target.value as 'movie' | 'tv')}
            >
              <option value="movie">Movie</option>
              <option value="tv">TV series</option>
            </select>
          </label>
          <label className="text-sm font-medium">
            {type === 'tv' ? 'Maximum minutes per episode' : 'Maximum minutes'}
            <input
              type="number"
              min="1"
              max="1440"
              step="1"
              placeholder="No limit"
              value={maxMinutes}
              className={inputClass}
              onChange={(event) => setMaxMinutes(event.target.value)}
              aria-describedby="runtime-note"
            />
          </label>
          <label className="text-sm font-medium">
            Released from
            <input
              type="number"
              min="1800"
              max="2100"
              step="1"
              placeholder="Any year"
              value={yearFrom}
              className={inputClass}
              onChange={(event) => setYearFrom(event.target.value)}
            />
          </label>
          <label className="text-sm font-medium">
            Released through
            <input
              type="number"
              min="1800"
              max="2100"
              step="1"
              placeholder="Any year"
              value={yearTo}
              className={inputClass}
              onChange={(event) => setYearTo(event.target.value)}
            />
          </label>
        </div>
        <p id="runtime-note" className="text-sm text-muted-foreground">
          {
            type === 'tv' ? 'For TV, the time limit applies to the listed episode runtime, and years refer to the series premiere. ' : ''
          }
          With a time limit, titles without a known runtime are left out.
        </p>
        <fieldset>
          <legend className="mb-3 text-sm font-medium">Genres — choose any, or leave all unchecked</legend>
          <div className="flex flex-wrap gap-2">
            {
              filters.data?.genres.map((genre) => (
                <label
                  key={genre}
                  className="flex cursor-pointer items-center gap-2 rounded-sm border border-border bg-card px-3 py-2 text-sm has-checked:border-primary has-checked:text-primary"
                >
                  <input
                    type="checkbox"
                    checked={genres.includes(genre)}
                    onChange={(event) => setGenres((current) => event.target.checked ? [...current, genre] : current.filter((value) => value !== genre))}
                  />
                  {genre}
                </label>
              ))
            }
          </div>
          {filters.isPending && <p className="text-sm text-muted-foreground">Loading genres…</p>}
          {
            filters.isError && <p role="alert" className="text-sm text-muted-foreground">
              Genres could not be loaded. You can still search without them.{' '}
              <button type="button" className="text-primary underline" onClick={() => void filters.refetch()}>Retry genres</button>
            </p>
          }
        </fieldset>
        <fieldset>
          <legend className="mb-3 text-sm font-medium">How adventurous is your evening?</legend>
          <div className="grid gap-3 sm:grid-cols-2">
            {
              ([
                ['familiar', 'Close to my taste', 'Prioritize the strongest matches to your ratings.'],
                ['discover', 'More variety', 'Explore a less repetitive mix of matches to your taste.'],
              ] as const).map(([value, title, description]) => (
                <label
                  key={value}
                  className="flex cursor-pointer items-start gap-3 rounded-sm border border-border bg-card p-4 has-checked:border-primary"
                >
                  <input
                    className="mt-1"
                    type="radio"
                    name="mode"
                    value={value}
                    checked={mode === value}
                    onChange={() => setMode(value)}
                  />
                  <span>
                    <span className="block font-medium">{title}</span>
                    <span className="mt-1 block text-sm text-muted-foreground">{description}</span>
                  </span>
                </label>
              ))
            }
          </div>
        </fieldset>
        {error && <p role="alert" className="text-rose-300">{error}</p>}
        <Button type="submit" disabled={pending}>
          {pending ? 'Finding your picks…' : 'Find tonight’s picks'}
        </Button>
      </fieldset>
    </form>
  )
}
