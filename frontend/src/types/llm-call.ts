export interface LlmCall {
  id: string
  stepId: string
  callKey: string
  label: string
  model: string
  request: Array<Record<string, unknown>>
  response: Record<string, unknown> | string
  sequence: number
}

export interface LlmCallResponseShape {
  id: string
  step_id: string
  call_key: string
  label: string
  model: string
  request: Array<Record<string, unknown>>
  response: Record<string, unknown> | string
  sequence: number
}

export function mapLlmCallResponse(call: LlmCallResponseShape): LlmCall {
  return {
    id: call.id,
    stepId: call.step_id,
    callKey: call.call_key,
    label: call.label,
    model: call.model,
    request: call.request,
    response: call.response,
    sequence: call.sequence,
  }
}
