import type {
  DocumentProcessingLlmCall,
  ProcessingStepId,
} from '@/types/document-processing'

export function findLlmCall(
  llmCalls: DocumentProcessingLlmCall[],
  stepId: ProcessingStepId,
  callKey: string,
): DocumentProcessingLlmCall | undefined {
  return llmCalls.find((call) => call.stepId === stepId && call.callKey === callKey)
}

export function findLlmCallsForChunk(
  llmCalls: DocumentProcessingLlmCall[],
  chunkIndex: number,
): {
  initial?: DocumentProcessingLlmCall
  continueCall?: DocumentProcessingLlmCall
} {
  const stepId: ProcessingStepId = 'entity_extraction'
  return {
    initial: findLlmCall(llmCalls, stepId, `chunk_${chunkIndex}_initial`),
    continueCall: findLlmCall(llmCalls, stepId, `chunk_${chunkIndex}_continue`),
  }
}

export function findLlmCallForGroupingIteration(
  llmCalls: DocumentProcessingLlmCall[],
  iteration: number,
): DocumentProcessingLlmCall | undefined {
  return findLlmCall(llmCalls, 'entity_grouping', `iteration_${iteration}`)
}
