import { useMutation, useQuery } from '@tanstack/react-query'
import { type FormEvent, useState } from 'react'
import { useNavigate } from 'react-router'
import { type BrowseParameters, fetchCatalogue, fetchCatalogueFilters, importTmdbTitle, searchTmdbTitles } from './api'
import { catalogueKeys } from './queries'

const initialParameters: BrowseParameters = {
  query: '',
  type: '',
  genre: '',
  year: '',
  page: 1,
}

export function useCatalogue() {
  const navigate = useNavigate()
  const [parameters, setParameters] = useState(initialParameters)
  const [searchDraft, setSearchDraft] = useState('')
  const catalogueQuery = useQuery({
    queryKey: catalogueKeys.list(parameters),
    queryFn: () => fetchCatalogue(parameters),
  })
  const filtersQuery = useQuery({ queryKey: catalogueKeys.filters, queryFn: fetchCatalogueFilters })
  const shouldSearchTmdb = Boolean(
    parameters.query && !parameters.genre && !parameters.year && catalogueQuery.data?.total === 0,
  )
  const tmdbQuery = useQuery({
    queryKey: catalogueKeys.external(parameters.query, parameters.type),
    queryFn: () => searchTmdbTitles(parameters.query, parameters.type),
    enabled: shouldSearchTmdb,
  })
  const importMutation = useMutation({
    mutationFn: ({ type, tmdbId }: { type: 'movie' | 'tv'; tmdbId: number }) =>
      importTmdbTitle(type, tmdbId),
    onSuccess: (title) => navigate(`/catalogue/${title.id}`),
  })
  const pageCount = catalogueQuery.data
    ? Math.max(1, Math.ceil(catalogueQuery.data.total / catalogueQuery.data.pageSize))
    : 1

  function changeFilter<K extends 'type' | 'genre' | 'year'>(name: K, value: BrowseParameters[K]) {
    setParameters((current) => ({ ...current, [name]: value, page: 1 }))
  }

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setParameters((current) => ({ ...current, query: searchDraft.trim(), page: 1 }))
  }

  function resetFilters() {
    setSearchDraft('')
    setParameters(initialParameters)
  }

  return {
    parameters, setParameters, searchDraft, setSearchDraft,
    catalogueQuery, filtersQuery, tmdbQuery, shouldSearchTmdb, importMutation,
    pageCount, changeFilter, submitSearch, resetFilters,
    openTitle: (id: string) => navigate(`/catalogue/${id}`),
  }
}
