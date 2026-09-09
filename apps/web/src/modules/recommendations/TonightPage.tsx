import { useMutation, useQuery } from '@tanstack/react-query'
import { Link } from 'react-router'
import { ApiError } from '../../shared/api/client'
import { Button } from '../../shared/ui/Button'
import { fetchCurrentUser } from '../auth/api'
import { authKeys } from '../auth/queries'
import { SiteHeader } from '../navigation/SiteHeader'
import { RecommendationCard } from './RecommendationCard'
import { TonightForm } from './TonightForm'
import { fetchTonightRecommendations } from './tonightApi'

export function TonightPage() {
  const account = useQuery({ queryKey: authKeys.currentUser, queryFn: fetchCurrentUser })
  return (
    <main className="mx-auto w-full max-w-360 px-[4vw] pb-16">
      <SiteHeader />
      <section className="border-b py-12">
        <p className="font-mono text-xs font-bold uppercase tracking-[.12em] text-primary">An evening well spent</p>
        <h1 className="max-w-[16ch] font-display text-[clamp(2.8rem,6vw,5rem)] font-semibold leading-none tracking-[-.05em]">What should I watch tonight?</h1>
        <p className="mt-6 max-w-2xl text-muted-foreground">Your taste, tonight's plans. Choose what fits your evening and get up to six personal picks. These choices won't change your saved preferences.</p>
      </section>
      {account.isPending && <p role="status" className="py-8">Loading your account…</p>}
      {
        account.isError && <div role="alert" className="space-y-4 py-8">
          <p>Could not check your account.</p>
          <Button onClick={() => void account.refetch()}>Try again</Button>
        </div>
      }
      {
        account.isSuccess && !account.data && <div className="space-y-4 py-8">
          <p>Sign in and complete taste setup with ten ratings to get your personal picks.</p>
          <Button asChild><Link to="/auth/sign-in">Sign in</Link></Button>
        </div>
      }
      {account.data && <TonightPicker key={account.data.id} />}
    </main>
  )
}

function TonightPicker() {
  const picks = useMutation({ mutationFn: fetchTonightRecommendations })
  const errorStatus = picks.error instanceof ApiError ? picks.error.status : null
  return (
    <>
      <TonightForm
        pending={picks.isPending}
        onSubmit={(preferences) => picks.mutate(preferences)}
        onChange={() => picks.reset()}
      />
      <section className="py-8" aria-live="polite" aria-busy={picks.isPending}>
        {
          picks.isIdle && <p className="text-muted-foreground">Set your preferences above, then find your picks.</p>
        }
        {picks.isPending && <p role="status">Matching your ratings with tonight's plans…</p>}
        {
          picks.isError && <div role="alert" className="space-y-4">
            <p>
              {
                errorStatus === 403 ? 'Rate ten familiar titles to unlock tonight’s picks.'
                  : errorStatus === 401 ? 'Your session has ended. Sign in to continue.'
                    : errorStatus === 422 ? 'Please check the time limit and year range, then try again.'
                      : 'Tonight’s picks are unavailable. Please try again.'
              }
            </p>
            {
              errorStatus === 403 || errorStatus === 401 ? (
                <Button asChild>
                  <Link to={errorStatus === 403 ? '/onboarding' : '/auth/sign-in'}>
                    {errorStatus === 403 ? 'Complete taste setup' : 'Sign in'}
                  </Link>
                </Button>
              ) : <Button onClick={() => picks.variables && picks.mutate(picks.variables)}>Try again</Button>
            }
          </div>
        }
        {
          picks.data?.status === 'no_profile' && <div className="space-y-4">
            <p>Your ratings don't give us a clear direction yet. Rate a few titles you enjoyed above 3 stars.</p>
            <Button asChild><Link to="/catalogue">Find titles to rate</Link></Button>
          </div>
        }
        {
          picks.data?.status === 'no_matches' && <p>No available picks match these choices. Try clearing the genre selection, a wider year range, or more time. Your watched, rated and hidden titles stay excluded.</p>
        }
        {
          picks.data?.status === 'ready' && <>
            <h2 className="font-display text-3xl font-semibold">Your evening shortlist</h2>
            <p className="mb-6 text-sm text-muted-foreground">
              {picks.data.items.length} {picks.data.items.length === 1 ? 'pick' : 'picks'} matching your choices. Open a title to see details or save it.</p>
            <div className="grid grid-cols-2 gap-x-4 gap-y-8 md:grid-cols-3 lg:grid-cols-6">
              {picks.data.items.map((item) => <RecommendationCard key={item.id} item={item} />)}
            </div>
          </>
        }
      </section>
    </>
  )
}
