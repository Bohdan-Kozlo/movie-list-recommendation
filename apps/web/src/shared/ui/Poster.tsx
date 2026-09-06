import type { ReactNode } from 'react'
import { posterUrl } from '../catalogue'

type PosterProps = {
  path: string | null
  className?: string
  fallback?: ReactNode
}

export function Poster({ path, className = 'h-full w-full object-cover', fallback }: PosterProps) {
  const source = posterUrl(path)
  if (!source) {
    return fallback ?? <span className="grid h-full place-items-center text-sm text-muted-foreground">No image</span>
  }
  return <img className={className} src={source} alt="" />
}
