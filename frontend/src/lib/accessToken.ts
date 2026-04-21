const STORAGE_KEY = 'lorrator_access_token'

export function getStoredAccessToken(): string | null {
  if (typeof localStorage === 'undefined') return null
  return localStorage.getItem(STORAGE_KEY)
}

export function setStoredAccessToken(token: string): void {
  localStorage.setItem(STORAGE_KEY, token)
}

export function clearStoredAccessToken(): void {
  localStorage.removeItem(STORAGE_KEY)
}
