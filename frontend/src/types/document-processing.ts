import type { LlmCall } from './llm-call'

export type ProcessingStepId =
  | 'prepare'
  | 'clear_graph'
  | 'chunk'
  | 'entity_extraction'
  | 'graph_build'
  | 'entity_embedding'
  | 'entity_grouping'

export type ProcessingStepStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped'

export interface ProcessingStepBase {
  id: ProcessingStepId
  title: string
  description: string
  status: ProcessingStepStatus
  durationMs: number
  summary?: string
  error?: string
}

export interface PrepareStepResult {
  mdPath: string
  characterCount: number
  lineCount: number
  preview: string
}

export interface ClearGraphStepResult {
  chunksDeleted: number
  legacyChunksDeleted: number
  orphanEntitiesDeleted: number
}

export interface ChunkItem {
  index: number
  startToken: number
  endToken: number
  tokenCount: number
  text: string
}

export interface ChunkStepResult {
  chunkSize: number
  overlap: number
  totalTokens: number
  chunks: ChunkItem[]
}

export interface ExtractedEntity {
  name: string
  type: string
  description: string
}

export interface ExtractedRelationship {
  sourceName: string
  targetName: string
  type: string
  description: string
}

export interface ChunkExtractionResult {
  chunkIndex: number
  entities: ExtractedEntity[]
  relationships: ExtractedRelationship[]
}

export interface EntityExtractionStepResult {
  model: string
  chunkResults: ChunkExtractionResult[]
  totalEntities: number
  totalRelationships: number
}

export interface GraphNodeCreated {
  id: string
  name: string
  type: string
  description: string
  sourceChunkIndex: number
}

export interface GraphEdgeCreated {
  id: string
  sourceName: string
  targetName: string
  type: string
  description: string
}

export interface GraphBuildStepResult {
  chunksCreated: number
  entitiesCreated: number
  entitiesMerged: number
  relationshipsCreated: number
  nodes: GraphNodeCreated[]
  edges: GraphEdgeCreated[]
}

export interface EntityEmbeddingStepResult {
  modelKey: string
  entitiesEmbedded: number
  cacheHits: number
  cacheMisses: number
  similarityEdgesCreated: number
}

export interface EntityGroupingInputEntity {
  tempId: string
  name: string
  chunkIndex: number
  description: string
}

export interface EntityGroupingInputChunk {
  tempId: string
  chunkIndex: number
  content: string
}

export interface EntityGroupingMergeRecord {
  targetName: string
  sourceName: string
  sourceChunkIndex: number
  sourceDescription: string
  aliasesAdded: string[]
}

export interface EntityGroupingIteration {
  iteration: number
  seedName: string
  seedSimilarityDegree: number
  inputEntities: EntityGroupingInputEntity[]
  inputChunks: EntityGroupingInputChunk[]
  llmGroups: string[][]
  merges: EntityGroupingMergeRecord[]
}

export interface EntityGroupingStepResult {
  totalIterations: number
  totalMerges: number
  iterations: EntityGroupingIteration[]
}

export type ProcessingStep =
  | (ProcessingStepBase & { id: 'prepare'; result?: PrepareStepResult })
  | (ProcessingStepBase & { id: 'clear_graph'; result?: ClearGraphStepResult })
  | (ProcessingStepBase & { id: 'chunk'; result?: ChunkStepResult })
  | (ProcessingStepBase & { id: 'entity_extraction'; result?: EntityExtractionStepResult })
  | (ProcessingStepBase & { id: 'graph_build'; result?: GraphBuildStepResult })
  | (ProcessingStepBase & { id: 'entity_embedding'; result?: EntityEmbeddingStepResult })
  | (ProcessingStepBase & { id: 'entity_grouping'; result?: EntityGroupingStepResult })

export type DocumentProcessingLlmCall = LlmCall & { stepId: ProcessingStepId }

export interface DocumentProcessingPipeline {
  documentId: string
  filename: string
  startedAt: string
  completedAt: string
  totalDurationMs: number
  steps: ProcessingStep[]
  llmCalls: DocumentProcessingLlmCall[]
}
