import { computed, ref, shallowRef } from 'vue'
import { defineStore } from 'pinia'

import { getStoredAccessToken } from '@/lib/accessToken'

import type { TopicSubscriptionAction, WsAnyHandler, WsMessage, WsPayloadHandler } from '@/composables/websocket/types'

const WS_TOPIC_SUBSCRIPTION_ACK = 'topic.subscription_ack'
const IDLE_DISCONNECT_MS = 60_000

/** 讀取 `VITE_API_URL`（REST 換票用），去掉結尾斜線方便拼接路徑 */
function apiBaseUrl(): string {
  const base = import.meta.env.VITE_API_URL
  if (typeof base !== 'string' || !base.trim()) {
    throw new Error('缺少環境變數 VITE_API_URL')
  }
  return base.replace(/\/$/, '')
}

/** 將 HTTP(S) API base 成 WS(S) base（路徑與 port 一併保留） */
function httpBaseToWsBase(httpBase: string): string {
  const u = new URL(httpBase)
  u.protocol = u.protocol === 'https:' ? 'wss:' : 'ws:'
  return u.href.replace(/\/$/, '')
}

function parseWsMessage(raw: string): WsMessage | null {
  try {
    const data: unknown = JSON.parse(raw)
    if (typeof data !== 'object' || data === null || Array.isArray(data)) {
      return null
    }
    const o = data as Record<string, unknown>
    if (typeof o.type !== 'string') return null
    const p = o.payload
    if (typeof p !== 'object' || p === null || Array.isArray(p)) return null
    return { type: o.type, payload: p as Record<string, unknown> }
  } catch {
    return null
  }
}

function isTopicSubscriptionAction(value: unknown): value is TopicSubscriptionAction {
  return value === 'subscribe' || value === 'unsubscribe'
}

export const useWebSocketStore = defineStore('websocket', () => {
  const connected = ref(false)
  const connecting = ref(false)
  const lastError = shallowRef<Error | null>(null)

  // 唯一的 socket instance
  let socket: WebSocket | null = null

  let connectingPromise: Promise<void> | null = null
  let subscribeLock = Promise.resolve()
  let idleDisconnectTimer: ReturnType<typeof setTimeout> | null = null

  /** 客戶端主動訂閱的 topic 引用計數（含多個 component 共用同一 topic） */
  const topicRefCounts = new Map<string, number>()
  /** 已送出、等待伺服器 `topic.subscription_ack` 的 topic 訂閱請求 */
  const pendingTopicSubscriptions = new Map<string, TopicSubscriptionAction>()
  /** 依 `type` 字串分派的處理函式 */
  const handlersByType = new Map<string, Set<WsPayloadHandler>>()
  /** 不分 type、每則合法訊息都會呼叫一次 */
  const anyHandlers = new Set<WsAnyHandler>()

  // * getters
  /** 已訂閱的 topic */
  const subscribedTopics = computed(() => [...topicRefCounts.keys()])

  // * methods
  // 獨佔執行任務，避免多個 component 同時訂閱同一 topic 造成競態
  function runExclusive<T>(task: () => Promise<T>): Promise<T> {
    const result = subscribeLock.then(() => task())
    subscribeLock = result.then(
      () => undefined,
      () => undefined,
    )
    return result
  }

  // 取消閒置斷線計時器
  function cancelIdleDisconnectTimer(): void {
    if (idleDisconnectTimer !== null) {
      clearTimeout(idleDisconnectTimer)
      idleDisconnectTimer = null
    }
  }

  // 閒置 60 秒後無訂閱 topic 則斷線
  function scheduleIdleDisconnect(): void {
    cancelIdleDisconnectTimer()
    idleDisconnectTimer = setTimeout(() => {
      idleDisconnectTimer = null
      if (topicRefCounts.size === 0) {
        disconnect()
      }
    }, IDLE_DISCONNECT_MS)
  }

  function handleTopicSubscriptionAck(payload: Record<string, unknown>): void {
    const topic = typeof payload.topic === 'string' ? payload.topic : null
    const action = isTopicSubscriptionAction(payload.action) ? payload.action : null
    const ok = payload.ok === true

    if (!topic || !action) {
      console.warn('[WS] invalid topic.subscription_ack payload', payload)
      return
    }

    const pending = pendingTopicSubscriptions.get(topic)
    const wasPending = pending === action
    if (wasPending) {
      pendingTopicSubscriptions.delete(topic)
    }

    if (ok) {
      if (wasPending) {
        console.log(`[WS] subscription confirmed (${action}):`, topic)
      } else {
        console.log(`[WS] subscription confirmed (server, ${action}):`, topic)
      }
      return
    }

    if (wasPending) {
      console.warn(`[WS] subscription denied (${action}):`, topic)
    } else {
      console.warn(`[WS] subscription denied (server, ${action}):`, topic)
    }
  }

  function dispatchMessage(msg: WsMessage): void {
    for (const h of anyHandlers) {
      h(msg)
    }
    const set = handlersByType.get(msg.type)
    if (!set) return
    for (const h of set) {
      h(msg.payload)
    }
  }

  function wireSocket(ws: WebSocket): void {
    ws.addEventListener('message', (ev: MessageEvent<string | ArrayBuffer>) => {
      if (typeof ev.data !== 'string') return
      const msg = parseWsMessage(ev.data)
      if (!msg) return

      if (msg.type === WS_TOPIC_SUBSCRIPTION_ACK) {
        handleTopicSubscriptionAck(msg.payload)
      }

      dispatchMessage(msg)
    })
  }

  function send(messageType: string, payload: Record<string, unknown> = {}): void {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket 尚未連線')
    }
    const body: WsMessage = { type: messageType, payload }
    socket.send(JSON.stringify(body))
  }

  function sendTopicSubscribe(topic: string): void {
    pendingTopicSubscriptions.set(topic, 'subscribe')
    console.log('[WS] subscription sent (subscribe):', topic)
    send('subscribe', { topic })
  }

  function sendTopicUnsubscribe(topic: string): void {
    pendingTopicSubscriptions.set(topic, 'unsubscribe')
    console.log('[WS] subscription sent (unsubscribe):', topic)
    send('unsubscribe', { topic })
  }

  async function resubscribeActiveTopics(): Promise<void> {
    for (const topic of topicRefCounts.keys()) {
      sendTopicSubscribe(topic)
    }
  }

  function disconnect(): void {
    cancelIdleDisconnectTimer()
    if (socket) {
      socket.close()
      socket = null
    }
    pendingTopicSubscriptions.clear()
    connected.value = false
    connecting.value = false
  }

  async function connect(accessToken?: string | null): Promise<void> {
    const token = accessToken ?? getStoredAccessToken()
    if (!token) {
      throw new Error('需要 access token 才能換取 WebSocket 票證')
    }

    if (socket?.readyState === WebSocket.OPEN) {
      connected.value = true
      return
    }

    if (connectingPromise) return connectingPromise

    connectingPromise = (async () => {
      connecting.value = true
      lastError.value = null
      try {
        const base = apiBaseUrl()
        const ticketRes = await fetch(`${base}/websocket/ticket`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            Accept: 'application/json',
          },
        })
        if (!ticketRes.ok) {
          throw new Error(`換取票證失敗：HTTP ${ticketRes.status}`)
        }
        const ticketJson = (await ticketRes.json()) as {
          ticket?: string
          expires_in_seconds?: number
        }
        if (!ticketJson.ticket) {
          throw new Error('票證回應格式錯誤')
        }

        if (socket) {
          socket.close()
          socket = null
        }

        const wsBase = httpBaseToWsBase(base)
        const url = `${wsBase}/websocket/ws?ticket=${encodeURIComponent(ticketJson.ticket)}`
        const ws = new WebSocket(url)
        socket = ws
        wireSocket(ws)

        await new Promise<void>((resolve, reject) => {
          const onOpen = () => {
            cleanup()
            connected.value = true
            connecting.value = false
            resolve()
          }
          const onError = () => {
            cleanup()
            connecting.value = false
            connected.value = false
            reject(new Error('WebSocket 連線失敗'))
          }
          const cleanup = () => {
            ws.removeEventListener('open', onOpen)
            ws.removeEventListener('error', onError)
          }
          ws.addEventListener('open', onOpen, { once: true })
          ws.addEventListener('error', onError, { once: true })
        })

        ws.addEventListener('close', () => {
          if (socket === ws) {
            socket = null
            connected.value = false
            pendingTopicSubscriptions.clear()
          }
        })

        await resubscribeActiveTopics()
      } catch (e) {
        connecting.value = false
        connected.value = false
        const err = e instanceof Error ? e : new Error(String(e))
        lastError.value = err
        throw err
      } finally {
        connecting.value = false
        connectingPromise = null
      }
    })()

    return connectingPromise
  }

  async function ensureConnected(accessToken?: string | null): Promise<void> {
    cancelIdleDisconnectTimer()
    await connect(accessToken)
  }

  /** 僅需連線收訊、不訂閱 topic 時使用（例如伺服器自動推送的 documents 事件） */
  async function retainConnection(accessToken?: string | null): Promise<void> {
    await ensureConnected(accessToken)
  }

  function releaseConnection(): void {
    if (topicRefCounts.size === 0) {
      scheduleIdleDisconnect()
    }
  }

  async function subscribeTopic(topic: string): Promise<void> {
    return runExclusive(async () => {
      cancelIdleDisconnectTimer()

      const count = topicRefCounts.get(topic) ?? 0
      topicRefCounts.set(topic, count + 1)
      if (count > 0) return

      await ensureConnected()
      sendTopicSubscribe(topic)
    })
  }

  async function unsubscribeTopic(topic: string): Promise<void> {
    return runExclusive(async () => {
      const count = topicRefCounts.get(topic) ?? 0
      if (count <= 0) return

      // 更新 topic 引用計數
      const next = count - 1
      if (next > 0) {
        topicRefCounts.set(topic, next)
        return // 引用計數不為 0，直接返回
      }

      // 引用為 0 則刪除 topic
      topicRefCounts.delete(topic)

      if (socket?.readyState === WebSocket.OPEN) {
        sendTopicUnsubscribe(topic)
      }

      if (topicRefCounts.size === 0) {
        scheduleIdleDisconnect()
      }
    })
  }

  function onType(type: string, handler: WsPayloadHandler): () => void {
    if (!handlersByType.has(type)) {
      handlersByType.set(type, new Set())
    }
    handlersByType.get(type)!.add(handler)
    return () => {
      const set = handlersByType.get(type)
      if (!set) return
      set.delete(handler)
      if (set.size === 0) handlersByType.delete(type)
    }
  }

  function onAny(handler: WsAnyHandler): () => void {
    anyHandlers.add(handler)
    return () => {
      anyHandlers.delete(handler)
    }
  }

  return {
    connected,
    connecting,
    lastError,
    subscribedTopics,
    ensureConnected,
    retainConnection,
    releaseConnection,
    subscribeTopic,
    unsubscribeTopic,
    onType,
    onAny,
    disconnect,
  }
})
