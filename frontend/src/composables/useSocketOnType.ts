import { onMounted, onUnmounted } from 'vue'

import { useAppWebSocket, type WsPayloadHandler } from './useAppWebSocket'

export function useSocketOnType<T = unknown>(
  type: string,
  handler: WsPayloadHandler
) {
  const ws = useAppWebSocket()
  let unsubscribe: (() => void) | null = null

  onMounted(async () => {
    await ws.connect()
    unsubscribe = ws.onType(type, handler)
  })

  onUnmounted(() => {
    unsubscribe?.()
    unsubscribe = null
  })
}
