import { useClipboard } from '@vueuse/core'

export function useCopyFeedback(duration = 2000) {
  return useClipboard({ legacy: true, copiedDuring: duration })
}
