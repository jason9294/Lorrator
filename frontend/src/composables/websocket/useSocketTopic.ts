import { onMounted, onUnmounted, toValue, type MaybeRefOrGetter } from 'vue'

import { useWebSocketStore } from '@/stores/websocket'

/**
 * 在 component 掛載時訂閱 topic、卸載時取消訂閱。
 * 訂閱前會由 store 確保連線已建立（含並發鎖）。
 */
export function useSocketTopic(topic: MaybeRefOrGetter<string>) {
  const store = useWebSocketStore()

  onMounted(async () => {
    await store.subscribeTopic(toValue(topic))
  })

  onUnmounted(() => {
    void store.unsubscribeTopic(toValue(topic))
  })
}
