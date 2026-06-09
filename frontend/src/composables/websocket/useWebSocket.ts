import { storeToRefs } from 'pinia'

import { useWebSocketStore } from '@/stores/websocket'

/**
 * 讀取全域 WebSocket store 狀態與操作。
 * 連線生命週期由 store 管理；component 請優先使用 `useSocketTopic` / `useSocketOnType`。
 */
export function useWebSocket() {
  const store = useWebSocketStore()
  const { connected, connecting, lastError, subscribedTopics } = storeToRefs(store)

  return {
    connected,
    connecting,
    lastError,
    subscribedTopics,
    ensureConnected: store.ensureConnected,
    subscribeTopic: store.subscribeTopic,
    unsubscribeTopic: store.unsubscribeTopic,
    onType: store.onType,
    onAny: store.onAny,
    disconnect: store.disconnect,
  }
}
