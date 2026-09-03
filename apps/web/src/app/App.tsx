import { Navigate, Route, Routes } from 'react-router'

import { CataloguePage } from '../modules/catalog/CataloguePage'
import { TitleDetailsPage } from '../modules/catalog/TitleDetailsPage'
import { AuthCallbackPage, AuthPage } from '../modules/auth/AuthPage'
import { LibraryPage } from '../modules/interactions/LibraryPage'
import { OnboardingPage } from '../modules/onboarding/OnboardingPage'

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate replace to="/catalogue" />} />
      <Route path="/catalogue" element={<CataloguePage />} />
      <Route path="/catalogue/:titleId" element={<TitleDetailsPage />} />
      <Route path="/library" element={<Navigate replace to="/library/watchlist" />} />
      <Route path="/library/:collection" element={<LibraryPage />} />
      <Route path="/onboarding" element={<OnboardingPage />} />
      <Route path="/auth/register" element={<AuthPage mode="register" />} />
      <Route path="/auth/sign-in" element={<AuthPage mode="sign-in" />} />
      <Route path="/auth/callback" element={<AuthCallbackPage />} />
      <Route path="*" element={<Navigate replace to="/catalogue" />} />
    </Routes>
  )
}
