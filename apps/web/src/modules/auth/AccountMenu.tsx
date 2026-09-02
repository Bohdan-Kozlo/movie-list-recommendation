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
      <div className="account-menu">
        <span>{accountQuery.data.email}</span>
        <Button variant="ghost" size="compact" type="button" onClick={() => logoutMutation.mutate()}>
          Sign out
        </Button>
      </div>
    )
  }

  return (
    <nav className="account-menu" aria-label="Account">
      <Button asChild variant="ghost" size="compact">
        <Link to="/auth/sign-in">Sign in</Link>
      </Button>
      <Button asChild size="compact">
        <Link to="/auth/register">Create account</Link>
      </Button>
    </nav>
  )
}
