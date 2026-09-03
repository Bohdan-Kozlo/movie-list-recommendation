import { FormEvent, useEffect, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router'

import { Button } from '../../shared/ui/Button'
import { Card } from '../../shared/ui/Card'
import { Input } from '../../shared/ui/Input'
import { beginGoogleLogin, fetchCurrentUser, login, register } from './api'
import { fetchOnboarding } from '../onboarding/api'

type AuthPageProps = {
  mode: 'sign-in' | 'register'
}

export function AuthPage({ mode }: AuthPageProps) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const action = mode === 'register' ? register : login
  const mutation = useMutation({
    mutationFn: () => action(email, password),
    onSuccess: async (user) => {
      queryClient.setQueryData(['auth', 'me'], user)
      await navigateAfterAuthentication(navigate)
    },
  })

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    mutation.mutate()
  }

  return (
    <main className="grid min-h-screen place-items-center p-8">
      <Card className="w-full max-w-124 bg-card p-[clamp(1.8rem,6vw,4.5rem)] shadow-[0_1.5rem_4rem_rgba(5,12,20,.28)]" aria-labelledby="auth-title">
        <Button asChild className="font-display text-[clamp(1.2rem,2vw,1.65rem)] font-bold tracking-[-.055em]" variant="ghost" size="compact">
          <Link to="/catalogue">
          REEL / INDEX
          </Link>
        </Button>
        <p className="mt-14 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">Your index</p>
        <h1 id="auth-title" className="my-2 max-w-[9ch] font-display text-[clamp(2.8rem,7vw,5.4rem)] font-semibold leading-[.92] tracking-[-.055em]">{mode === 'register' ? 'Make your watchlist personal.' : 'Welcome back.'}</h1>
        <p className="leading-6 text-muted-foreground">
          {mode === 'register'
            ? 'Save your ratings and build a recommendation profile.'
            : 'Pick up your catalogue and recommendations where you left off.'}
        </p>
        <form className="mt-8 grid gap-4" onSubmit={submit}>
          <label className="grid gap-2 font-mono text-xs font-bold uppercase tracking-[.1em] text-muted-foreground">
            Email
            <Input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </label>
          <label className="grid gap-2 font-mono text-xs font-bold uppercase tracking-[.1em] text-muted-foreground">
            Password
            <Input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              minLength={8}
              required
            />
          </label>
          {mutation.isError && <p className="text-destructive">{mutation.error.message}</p>}
          <Button className="w-full" type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? 'Working…' : mode === 'register' ? 'Create account' : 'Sign in'}
          </Button>
        </form>
        <div className="my-6 grid grid-cols-[1fr_auto_1fr] items-center gap-3 text-center font-mono text-xs uppercase text-muted-foreground before:h-px before:bg-border before:content-[''] after:h-px after:bg-border after:content-['']">or</div>
        <Button className="w-full" variant="outline" type="button" onClick={beginGoogleLogin}>
          Continue with Google
        </Button>
        <p className="mt-6 text-muted-foreground">
          {mode === 'register' ? 'Already have an account?' : 'New to Reel / Index?'}{' '}
          <Button asChild className="h-auto border-b border-current p-0 pb-0.5 text-[#d9e4eb] hover:bg-transparent" variant="ghost" size="compact">
            <Link to={mode === 'register' ? '/auth/sign-in' : '/auth/register'}>
            {mode === 'register' ? 'Sign in' : 'Create one'}
            </Link>
          </Button>
        </p>
      </Card>
    </main>
  )
}

export function AuthCallbackPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [message, setMessage] = useState('Completing your sign-in…')

  useEffect(() => {
    const status = new URLSearchParams(window.location.search).get('status')
    if (status !== 'success') {
      setMessage('Google could not sign you in. Please try again.')
      return
    }
    fetchCurrentUser()
      .then(async (user) => {
        if (!user) throw new Error()
        queryClient.setQueryData(['auth', 'me'], user)
        setMessage('Signed in. Your account is ready.')
        await navigateAfterAuthentication(navigate)
      })
      .catch(() => setMessage('Google could not sign you in. Please try again.'))
  }, [navigate, queryClient])

  return (
    <main className="grid min-h-screen place-items-center p-8">
      <Card className="min-h-72 w-full max-w-124 bg-card p-[clamp(1.8rem,6vw,4.5rem)] shadow-[0_1.5rem_4rem_rgba(5,12,20,.28)]">
        <Button asChild className="font-display text-[clamp(1.2rem,2vw,1.65rem)] font-bold tracking-[-.055em]" variant="ghost" size="compact">
          <Link to="/catalogue">
          REEL / INDEX
          </Link>
        </Button>
        <p className="mt-14 font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">Account</p>
        <h1 className="my-2 max-w-[9ch] font-display text-[clamp(2.8rem,7vw,5.4rem)] font-semibold leading-[.92] tracking-[-.055em]">{message}</h1>
        <Button asChild className="w-full">
          <Link to="/catalogue">
          Browse the catalogue
          </Link>
        </Button>
      </Card>
    </main>
  )
}

async function navigateAfterAuthentication(navigate: ReturnType<typeof useNavigate>) {
  const onboarding = await fetchOnboarding()
  navigate(onboarding.isComplete ? '/catalogue' : '/onboarding')
}
