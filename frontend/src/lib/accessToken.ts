import { useStorage } from '@vueuse/core'

const accessToken = useStorage<string | null>('lorrator_access_token', null)

export function getStoredAccessToken(): string | null {
  return accessToken.value
}

export function setStoredAccessToken(token: string): void {
  accessToken.value = token
}

export function clearStoredAccessToken(): void {
  accessToken.value = null
}
