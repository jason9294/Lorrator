import { z } from "zod"

export const roomsCreateMessagePayloadSchema = z.object({
  id: z.string(),
  room_id: z.string(),
  role: z.enum(['PLAYER', 'AGENT']),
  sender_id: z.string().nullable(),
  content: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
})

export const roomsSetReadyPayloadSchema = z.object({
  room_id: z.string(),
  user_id: z.string(),
  is_ready: z.boolean(),
})

export const roomsJoinRoomPayloadSchema = z.object({
  room_id: z.string(),
  user_id: z.string(),
  role: z.enum(['PLAYER', 'AGENT']),
  is_ready: z.boolean(),
  joined_at: z.string(),
})

export const roomsKickPayloadSchema = z.object({
  room_id: z.string(),
  user_id: z.string(),
})
