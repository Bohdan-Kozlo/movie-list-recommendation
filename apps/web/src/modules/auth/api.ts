import { ApiError, apiRequest, apiUrl, authenticatedApiRequest } from '../../shared/api/client'

export type AuthenticatedUser = {
  id: string
  email: string
}

export async function register(email: string, password: string): Promise<AuthenticatedUser> {
  return sendCredentials('/auth/register', email, password)
}

export async function login(email: string, password: string): Promise<AuthenticatedUser> {
  return sendCredentials('/auth/login', email, password)
}

export async function fetchCurrentUser(): Promise<AuthenticatedUser | null> {
  try {
    return await authenticatedApiRequest<AuthenticatedUser>('/auth/me')
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) return null
    throw new Error('Account status is unavailable.')
  }
}

export async function logout(): Promise<void> {
  await authRequest<void>('/auth/logout', { method: 'POST' })
}

export function beginGoogleLogin() {
  window.location.assign(apiUrl('/auth/google/login'))
}

async function sendCredentials(
  path: string,
  email: string,
  password: string,
): Promise<AuthenticatedUser> {
  return authRequest<AuthenticatedUser>(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
}

async function authRequest<T>(path: string, init: RequestInit): Promise<T> {
  try {
    return await apiRequest<T>(path, init)
  } catch (error) {
    if (error instanceof ApiError) throw new Error(error.message)
    throw new Error('Authentication is unavailable. Please try again.')
  }
}
