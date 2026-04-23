import { ref, shallowRef } from 'vue'

import { getStoredAccessToken } from '@/lib/accessToken'

/**
 * 與後端約定的單則訊息外層格式（JSON）。
 * 伺服器推送與客戶端送出皆應符合此結構。
 */
export type WsMessage = {
  type: string
  payload: Record<string, unknown>
}

/** 僅關心特定 `type` 時，只收到該則的 `payload` */
export type WsPayloadHandler = (payload: Record<string, unknown>) => void

/** 需要依完整訊息判斷邏輯時使用（會比 `onType` 先執行） */
type WsAnyHandler = (message: WsMessage) => void

/** 依 `type` 字串分派的處理函式（可多個 handler 訂閱同一 type） */
const handlersByType = new Map<string, Set<WsPayloadHandler>>()

/** 不分 type、每則合法訊息都會呼叫一次 */
const anyHandlers = new Set<WsAnyHandler>()

/** 全 App 共用一條連線，避免重複 ticket／多 socket 競態 */
let sharedSocket: WebSocket | null = null

/**
 * 進行中的連線 Promise（模組層級單例）。
 * 任何後續的 connect() 呼叫直接 await 同一份 Promise，
 * 不會重新換票或建立第二條連線。
 */
let connectingPromise: Promise<void> | null = null

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

/**
 * 解析文字訊息為 `WsMessage`；格式不符則回傳 `null`（靜默略過）。
 * 與後端一致：`type` 為字串、`payload` 為 JSON object（非陣列）。
 */
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

/** 掛上 `message` 監聽：先跑 `onAny`，再跑對應 `type` 的 `onType` */
function wireSocket(socket: WebSocket): void {
  socket.addEventListener('message', (ev: MessageEvent<string | ArrayBuffer>) => {
    if (typeof ev.data !== 'string') return
    const msg = parseWsMessage(ev.data)
    if (!msg) return
    for (const h of anyHandlers) {
      h(msg)
    }
    const set = handlersByType.get(msg.type)
    if (!set) return
    for (const h of set) {
      h(msg.payload)
    }
  })
}

/**
 * 與後端 WebSocket 連線（JWT 換一次性 ticket 後連 `/websocket/ws`），
 * 並依訊息 `type` 分派給已註冊的 handler。
 *
 * - 模組層級單例連線：各處 `useAppWebSocket()` 共用同一 `sharedSocket`。
 * - `onType` / `onAny` 回傳的函式請在適當時機呼叫以取消訂閱（例如 `onUnmounted`）。
 */
export function useAppWebSocket() {
  /** 目前是否已進入 OPEN（可 `send`） */
  const connected = ref(false)
  /** 換票或 TCP 連線建立中的過渡狀態 */
  const connecting = ref(false)
  /** 最近一次 `connect` 失敗的錯誤（成功連線後不會自動清空） */
  const lastError = shallowRef<Error | null>(null)

  /**
   * 訂閱指定 `type`；收到訊息時以 `payload` 呼叫 handler。
   * @returns 取消訂閱函式
   */
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

  /**
   * 訂閱所有通過格式檢查的訊息（含尚未被 `onType` 處理的）。
   * @returns 取消訂閱函式
   */
  function onAny(handler: WsAnyHandler): () => void {
    anyHandlers.add(handler)
    return () => {
      anyHandlers.delete(handler)
    }
  }

  /**
   * 送出符合 `WsMessage` 格式的 JSON（須已連線）。
   * @param messageType 對應後端約定的 `type` 字串
   * @param payload 預設空物件 `{}`
   */
  function send(messageType: string, payload: Record<string, unknown> = {}): void {
    const s = sharedSocket
    if (!s || s.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket 尚未連線')
    }
    const body: WsMessage = { type: messageType, payload }
    s.send(JSON.stringify(body))
  }

  /** 關閉連線並清除 ref 狀態（handler 註冊不會自動移除） */
  function disconnect(): void {
    if (sharedSocket) {
      sharedSocket.close()
      sharedSocket = null
    }
    connected.value = false
    connecting.value = false
  }

  /**
   * 以 Bearer token 向 `POST /websocket/ticket` 換票後建立 WebSocket。
   * @param accessToken 若省略則從 `localStorage`（`getStoredAccessToken`）讀取
   */
  async function connect(accessToken?: string | null): Promise<void> {
    const token = accessToken ?? getStoredAccessToken()
    if (!token) {
      throw new Error('需要 access token 才能換取 WebSocket 票證')
    }

    if (sharedSocket?.readyState === WebSocket.OPEN) {
      connected.value = true
      return
    }

    // 若已有進行中的連線流程，直接共用同一份 Promise，不重複換票
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

        disconnect()

        const wsBase = httpBaseToWsBase(base)
        const url = `${wsBase}/websocket/ws?ticket=${encodeURIComponent(ticketJson.ticket)}`
        const socket = new WebSocket(url)
        sharedSocket = socket
        wireSocket(socket)

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
            socket.removeEventListener('open', onOpen)
            socket.removeEventListener('error', onError)
          }
          socket.addEventListener('open', onOpen, { once: true })
          socket.addEventListener('error', onError, { once: true })
        })

        socket.addEventListener('close', () => {
          if (sharedSocket === socket) {
            sharedSocket = null
            connected.value = false
          }
        })
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

  return {
    connected,
    connecting,
    lastError,
    connect,
    disconnect,
    send,
    onType,
    onAny,
  }
}
