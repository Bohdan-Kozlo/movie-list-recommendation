export type AuthenticatedUser = {
  id: string
  email: string
}

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export async function register(email: string, password: string): Promise<AuthenticatedUser> {
  return sendCredentials('/auth/register', email, password)
}

export async function login(email: string, password: string): Promise<AuthenticatedUser> {
  return sendCredentials('/auth/login', email, password)
}

export async function fetchCurrentUser(): Promise<AuthenticatedUser | null> {
  const response = await fetch(`${apiBaseUrl}/auth/me`, { credentials: 'include' })
  if (response.status === 401) return refreshCurrentUser()
  if (!response.ok) throw new Error('Account status is unavailable.')
  return response.json() as Promise<AuthenticatedUser>
}

export async function logout(): Promise<void> {
  const response = await fetch(`${apiBaseUrl}/auth/logout`, {
    method: 'POST',
    credentials: 'include',
  })
  if (!response.ok) throw new Error('Unable to sign out.')
}

export function beginGoogleLogin() {
  window.location.assign(`${apiBaseUrl}/auth/google/login`)
}

async function refreshCurrentUser(): Promise<AuthenticatedUser | null> {
  const response = await fetch(`${apiBaseUrl}/auth/refresh`, {
    method: 'POST',
    credentials: 'include',
  })
  if (response.status === 401) return null
  if (!response.ok) throw new Error('Account status is unavailable.')
  return response.json() as Promise<AuthenticatedUser>
}

async function sendCredentials(
  path: string,
  email: string,
  password: string,
): Promise<AuthenticatedUser> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  if (!response.ok) throw new Error(await errorMessage(response))
  return response.json() as Promise<AuthenticatedUser>
}

async function errorMessage(response: Response): Promise<string> {
  const payload = await response.json().catch(() => null) as { detail?: string } | null
  return payload?.detail ?? 'Authentication is unavailable. Please try again.'
}
