import { FormEvent, useEffect, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'

import { beginGoogleLogin, fetchCurrentUser, login, register } from './api'

type AuthPageProps = {
  mode: 'sign-in' | 'register'
  onNavigate: (path: string) => void
}

export function AuthPage({ mode, onNavigate }: AuthPageProps) {
  const queryClient = useQueryClient()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const action = mode === 'register' ? register : login
  const mutation = useMutation({
    mutationFn: () => action(email, password),
    onSuccess: (user) => {
      queryClient.setQueryData(['auth', 'me'], user)
      onNavigate('/catalogue')
    },
  })

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    mutation.mutate()
  }

  return (
    <main className="auth-page">
      <section className="auth-panel" aria-labelledby="auth-title">
        <button className="wordmark" type="button" onClick={() => onNavigate('/catalogue')}>
          REEL / INDEX
        </button>
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
            <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              minLength={8}
              required
            />
          </label>
          {mutation.isError && <p className="auth-error">{mutation.error.message}</p>}
          <button className="auth-submit" type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? 'Working…' : mode === 'register' ? 'Create account' : 'Sign in'}
          </button>
        </form>
        <div className="auth-divider">or</div>
        <button className="google-button" type="button" onClick={beginGoogleLogin}>
          Continue with Google
        </button>
        <p className="auth-switch">
          {mode === 'register' ? 'Already have an account?' : 'New to Reel / Index?'}{' '}
          <button
            className="text-button"
            type="button"
            onClick={() => onNavigate(mode === 'register' ? '/auth/sign-in' : '/auth/register')}
          >
            {mode === 'register' ? 'Sign in' : 'Create one'}
          </button>
        </p>
      </section>
    </main>
  )
}

type AuthCallbackPageProps = {
  onNavigate: (path: string) => void
}

export function AuthCallbackPage({ onNavigate }: AuthCallbackPageProps) {
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
      <section className="auth-panel auth-callback">
        <button className="wordmark" type="button" onClick={() => onNavigate('/catalogue')}>
          REEL / INDEX
        </button>
        <p className="eyebrow">Account</p>
        <h1>{message}</h1>
        <button className="auth-submit" type="button" onClick={() => onNavigate('/catalogue')}>
          Browse the catalogue
        </button>
      </section>
    </main>
  )
}
