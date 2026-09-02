import { Navigate, Route, Routes } from 'react-router'

import { CataloguePage } from '../modules/catalog/CataloguePage'
import { TitleDetailsPage } from '../modules/catalog/TitleDetailsPage'
import { AuthCallbackPage, AuthPage } from '../modules/auth/AuthPage'

export function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate replace to="/catalogue" />} />
      <Route path="/catalogue" element={<CataloguePage />} />
      <Route path="/catalogue/:titleId" element={<TitleDetailsPage />} />
      <Route path="/auth/register" element={<AuthPage mode="register" />} />
      <Route path="/auth/sign-in" element={<AuthPage mode="sign-in" />} />
      <Route path="/auth/callback" element={<AuthCallbackPage />} />
      <Route path="*" element={<Navigate replace to="/catalogue" />} />
    </Routes>
  )
}
