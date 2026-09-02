import { FormEvent, useEffect, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router'

import { Button } from '../../shared/ui/Button'
import { Card } from '../../shared/ui/Card'
import { Input } from '../../shared/ui/Input'
import { beginGoogleLogin, fetchCurrentUser, login, register } from './api'

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
    onSuccess: (user) => {
      queryClient.setQueryData(['auth', 'me'], user)
      navigate('/catalogue')
    },
  })

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    mutation.mutate()
  }

  return (
    <main className="auth-page">
      <Card className="auth-panel" aria-labelledby="auth-title">
        <Button asChild className="wordmark" variant="ghost" size="compact">
          <Link to="/catalogue">
          REEL / INDEX
          </Link>
        </Button>
        <p className="eyebrow">Your index</p>
        <h1 id="auth-title">{mode === 'register' ? 'Make your watchlist personal.' : 'Welcome back.'}</h1>
        <p className="auth-copy">
          {mode === 'register'
            ? 'Save your ratings and build a recommendation profile.'
            : 'Pick up your catalogue and recommendations where you left off.'}
        </p>
        <form className="auth-form" onSubmit={submit}>
          <label>
            Email
            <Input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </label>
          <label>
            Password
            <Input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              minLength={8}
              required
            />
          </label>
          {mutation.isError && <p className="auth-error">{mutation.error.message}</p>}
          <Button className="auth-submit" type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? 'Working…' : mode === 'register' ? 'Create account' : 'Sign in'}
          </Button>
        </form>
        <div className="auth-divider">or</div>
        <Button className="google-button" variant="outline" type="button" onClick={beginGoogleLogin}>
          Continue with Google
        </Button>
        <p className="auth-switch">
          {mode === 'register' ? 'Already have an account?' : 'New to Reel / Index?'}{' '}
          <Button asChild className="text-button" variant="ghost" size="compact">
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
  const queryClient = useQueryClient()
  const [message, setMessage] = useState('Completing your sign-in…')

  useEffect(() => {
    const status = new URLSearchParams(window.location.search).get('status')
    if (status !== 'success') {
      setMessage('Google could not sign you in. Please try again.')
      return
    }
    fetchCurrentUser()
      .then((user) => {
        if (!user) throw new Error()
        queryClient.setQueryData(['auth', 'me'], user)
        setMessage('Signed in. Your account is ready.')
      })
      .catch(() => setMessage('Google could not sign you in. Please try again.'))
  }, [queryClient])

  return (
    <main className="auth-page">
      <Card className="auth-panel auth-callback">
        <Button asChild className="wordmark" variant="ghost" size="compact">
          <Link to="/catalogue">
          REEL / INDEX
          </Link>
        </Button>
        <p className="eyebrow">Account</p>
        <h1>{message}</h1>
        <Button asChild className="auth-submit">
          <Link to="/catalogue">
          Browse the catalogue
          </Link>
        </Button>
      </Card>
    </main>
  )
}
