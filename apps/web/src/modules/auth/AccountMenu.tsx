import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { fetchCurrentUser, logout } from './api'

type AccountMenuProps = {
  onNavigate: (path: string) => void
}

export function AccountMenu({ onNavigate }: AccountMenuProps) {
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
        <button className="text-button" type="button" onClick={() => logoutMutation.mutate()}>
          Sign out
        </button>
      </div>
    )
  }

  return (
    <nav className="account-menu" aria-label="Account">
      <button className="text-button" type="button" onClick={() => onNavigate('/auth/sign-in')}>
        Sign in
      </button>
      <button className="account-register" type="button" onClick={() => onNavigate('/auth/register')}>
        Create account
      </button>
    </nav>
  )
}
