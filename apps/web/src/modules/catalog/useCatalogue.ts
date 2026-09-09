import { useMutation, useQuery } from '@tanstack/react-query'
import { type FormEvent, useState } from 'react'
import { useNavigate } from 'react-router'
import {
  type BrowseParameters,
  type SemanticDescriptionParameters,
  fetchCatalogue,
  fetchCatalogueFilters,
  importTmdbTitle,
  searchCatalogueByDescription,
  searchTmdbTitles,
} from './api'
import { catalogueKeys } from './queries'

const initialParameters: BrowseParameters = {
  query: '',
  type: '',
  genre: '',
  year: '',
  page: 1,
}

const initialSemanticParameters: SemanticDescriptionParameters = {
  description: '',
  type: '',
}

export type CatalogueSearchMode = 'title' | 'description'

export function useCatalogue() {
  const navigate = useNavigate()
  const [mode, setMode] = useState<CatalogueSearchMode>('title')
  const [parameters, setParameters] = useState(initialParameters)
  const [titleSearchDraft, setTitleSearchDraft] = useState('')
  const [descriptionDraft, setDescriptionDraft] = useState('')
  const [semanticParameters, setSemanticParameters] = useState(initialSemanticParameters)
  const [descriptionValidationError, setDescriptionValidationError] = useState<string | null>(null)
  const catalogueQuery = useQuery({
    queryKey: catalogueKeys.list(parameters),
    queryFn: () => fetchCatalogue(parameters),
  })
  const filtersQuery = useQuery({ queryKey: catalogueKeys.filters, queryFn: fetchCatalogueFilters })
  const semanticQuery = useQuery({
    queryKey: catalogueKeys.semantic(semanticParameters),
    queryFn: () => searchCatalogueByDescription(semanticParameters),
    enabled: Boolean(semanticParameters.description),
  })
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
    if (mode === 'title') {
      setParameters((current) => ({ ...current, query: titleSearchDraft.trim(), page: 1 }))
      return
    }

    const description = descriptionDraft.trim()
    if (description.length < 3 || description.length > 500) {
      setDescriptionValidationError('Use a description from 3 to 500 characters.')
      return
    }
    setDescriptionValidationError(null)
    if (description === semanticParameters.description) {
      void semanticQuery.refetch()
      return
    }
    setSemanticParameters((current) => ({ ...current, description }))
  }

  function resetFilters() {
    if (mode === 'title') {
      setTitleSearchDraft('')
      setParameters(initialParameters)
      return
    }
    setDescriptionDraft('')
    setSemanticParameters(initialSemanticParameters)
    setDescriptionValidationError(null)
  }

  function changeSemanticFormat(value: SemanticDescriptionParameters['type']) {
    setSemanticParameters((current) => ({ ...current, type: value }))
  }

  return {
    mode, setMode,
    parameters, setParameters, titleSearchDraft, setTitleSearchDraft,
    descriptionDraft, setDescriptionDraft, semanticParameters, descriptionValidationError,
    catalogueQuery, filtersQuery, semanticQuery, tmdbQuery, shouldSearchTmdb, importMutation,
    pageCount, changeFilter, submitSearch, resetFilters,
    changeSemanticFormat,
    openTitle: (id: string) => navigate(`/catalogue/${id}`),
  }
}
