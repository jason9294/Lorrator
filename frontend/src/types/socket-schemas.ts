import { z } from "zod"

const llmCallPayloadSchema = z.object({
  id: z.string(),
  step_id: z.string(),
  call_key: z.string(),
  label: z.string(),
  model: z.string(),
  request: z.array(z.record(z.string(), z.unknown())),
  response: z.union([z.record(z.string(), z.unknown()), z.string()]),
  sequence: z.number(),
})

export const roomsCreateMessagePayloadSchema = z.object({
  id: z.string(),
  room_id: z.string(),
  role: z.enum(['PLAYER', 'AGENT', 'SYSTEM']),
  type: z.enum(['CHAT', 'DICE', 'DEBUG']),
  sender_id: z.string().nullable(),
  content: z.string(),
  detail: z.string().nullable().optional(),
  llm_calls: z.array(llmCallPayloadSchema).optional().default([]),
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

export const roomsSelectCharacterPayloadSchema = z.object({
  room_id: z.string(),
  user_id: z.string(),
  character_id: z.string().nullable(),
  character_name: z.string().nullable(),
})

export const documentProcessUpdatedPayloadSchema = z.object({
  document_id: z.string(),
  scenario_id: z.string(),
  status: z.enum(['READY', 'PROCESSING', 'COMPLETED', 'FAILED']),
  error: z.string().optional(),
})

export const roomsAiThinkingPayloadSchema = z.object({
  room_id: z.string(),
  active: z.boolean().default(true),
})

export type DocumentProcessUpdatedPayload = z.infer<typeof documentProcessUpdatedPayloadSchema>
