import { onMounted, onUnmounted } from 'vue'

import { useWebSocketStore } from '@/stores/websocket'

import type { WsPayloadHandler } from './types'

/**
 * 在 component 掛載時確保連線並註冊訊息 handler，卸載時自動移除。
 * 適用於僅需監聽特定 `type`、不需額外 topic 訂閱的場景（例如伺服器自動訂閱的文件事件）。
 */
export function useSocketOnType(type: string, handler: WsPayloadHandler) {
  const store = useWebSocketStore()
  let unsubscribe: (() => void) | null = null

  onMounted(async () => {
    await store.retainConnection()
    unsubscribe = store.onType(type, handler)
  })

  onUnmounted(() => {
    unsubscribe?.()
    unsubscribe = null
    store.releaseConnection()
  })
}
