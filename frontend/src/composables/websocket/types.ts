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
export type WsAnyHandler = (message: WsMessage) => void

export type TopicSubscriptionAction = 'subscribe' | 'unsubscribe'
