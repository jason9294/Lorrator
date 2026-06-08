import type { RoomMessageResponse } from '@/services'

export function getMessageAuthorKey(msg: RoomMessageResponse): string | null {
  if (msg.type === 'DEBUG') return null
  // Dice rolls are stored as SYSTEM role but carry the roller as sender_id
  if (msg.type === 'DICE' && msg.sender_id) return msg.sender_id
  if (msg.role === 'SYSTEM') return null
  if (msg.role === 'AGENT') return '__agent__'
  if (msg.sender_id) return msg.sender_id
  return null
}

export function isSameMessageAuthor(a: RoomMessageResponse, b: RoomMessageResponse): boolean {
  const keyA = getMessageAuthorKey(a)
  const keyB = getMessageAuthorKey(b)
  return keyA !== null && keyB !== null && keyA === keyB
}

export function shouldShowMessageAuthor(messages: RoomMessageResponse[], index: number): boolean {
  if (index <= 0) return true
  return !isSameMessageAuthor(messages[index - 1]!, messages[index]!)
}
