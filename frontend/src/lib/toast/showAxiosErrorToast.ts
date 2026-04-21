import type { AxiosError } from 'axios'
import { markRaw } from 'vue'
import { toast } from 'vue-sonner'

import AxiosErrorToast from '@/components/toasts/AxiosErrorToast.vue'

type UnknownRecord = Record<string, unknown>

function isRecord(v: unknown): v is UnknownRecord {
  return typeof v === 'object' && v !== null && !Array.isArray(v)
}

function pickServerMessage(data: unknown): string | undefined {
  if (!isRecord(data)) return undefined
  const candidates = [data.detail, data.message, data.error, data.title]
  for (const c of candidates) {
    if (typeof c === 'string' && c.trim()) return c.trim()
  }
  return undefined
}

export function showAxiosErrorToast(error: AxiosError, opts?: { durationMs?: number }) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  if ((error as any)?.code === 'ERR_CANCELED') return

  const durationMs = opts?.durationMs ?? 6500

  const status = error.response?.status
  const statusText = error.response?.statusText

  const method = error.config?.method?.toUpperCase()
  const url = error.config?.url

  const serverMessage = pickServerMessage(error.response?.data)
  const description =
    serverMessage ||
    (typeof error.message === 'string' && error.message.trim() ? error.message.trim() : undefined) ||
    '發生未知的網路錯誤'

  const title = status
    ? `${status}${statusText ? ` ${statusText}` : ''}`
    : statusText || '請求失敗'

  toast.custom(markRaw(AxiosErrorToast), {
    duration: durationMs,
    componentProps: {
      title,
      description,
      status,
      method,
      url,
      durationMs,
    },
  })
}

