import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router'

import { Button } from '../../shared/ui/Button'
import { fetchCurrentUser, logout } from './api'

export function AccountMenu() {
  const queryClient = useQueryClient()
  const accountQuery = useQuery({ queryKey: ['auth', 'me'], queryFn: fetchCurrentUser })
  const logoutMutation = useMutation({
    mutationFn: logout,
    onSuccess: () => queryClient.setQueryData(['auth', 'me'], null),
  })

  if (accountQuery.data) {
    return (
      <details className="group relative">
        <summary className="flex h-10 list-none items-center gap-2 border border-border bg-card px-2.5 font-mono text-xs text-foreground marker:content-none hover:border-primary [&::-webkit-details-marker]:hidden">
          <span className="grid size-6 place-items-center rounded-full bg-primary font-bold text-primary-foreground" aria-hidden="true">{accountQuery.data.email[0]?.toUpperCase()}</span>
          <span className="hidden max-w-48 truncate sm:block">{accountQuery.data.email}</span>
          <span className="text-primary transition-transform group-open:rotate-45" aria-hidden="true">+</span>
        </summary>
        <div className="absolute right-0 z-20 mt-2 grid min-w-56 gap-1 border border-border bg-[#213142] p-2 shadow-2xl">
          <p className="m-1 border-b border-border/70 pb-2 font-mono text-[10px] uppercase tracking-[.1em] text-muted-foreground">Your account</p>
          <Link className="px-3 py-2 text-sm hover:bg-[#31485c]" to="/onboarding">Taste setup</Link>
          <button className="px-3 py-2 text-left text-sm text-muted-foreground hover:bg-[#31485c] hover:text-foreground" type="button" onClick={() => logoutMutation.mutate()} disabled={logoutMutation.isPending}>
            Sign out
          </button>
        </div>
      </details>
    )
  }

  return (
    <nav className="flex items-center gap-4 font-mono text-xs uppercase tracking-[.06em] text-muted-foreground" aria-label="Account">
      <Button asChild variant="ghost" size="compact">
        <Link to="/auth/sign-in">Sign in</Link>
      </Button>
      <Button asChild size="compact">
        <Link to="/auth/register">Create account</Link>
      </Button>
    </nav>
  )
}
