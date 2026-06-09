import type { DocumentProcessingPipelineResponse } from '@/services'
import { mapLlmCallResponse } from '@/types/llm-call'
import type {
  ChunkExtractionResult,
  ChunkItem,
  ChunkStepResult,
  ClearGraphStepResult,
  DocumentProcessingLlmCall,
  DocumentProcessingPipeline,
  EntityEmbeddingStepResult,
  EntityExtractionStepResult,
  EntityGroupingIteration,
  EntityGroupingStepResult,
  ExtractedEntity,
  ExtractedRelationship,
  GraphBuildStepResult,
  GraphEdgeCreated,
  GraphNodeCreated,
  PrepareStepResult,
  ProcessingStep,
  ProcessingStepBase,
  ProcessingStepId,
  ProcessingStepStatus,
} from '@/types/document-processing'

type ApiStep = DocumentProcessingPipelineResponse['steps'][number]

type EntityGroupingApiResult = {
  total_iterations: number
  total_merges: number
  iterations: Array<{
    iteration: number
    seed_name: string
    seed_similarity_degree: number
    input_entities: Array<{
      temp_id: string
      name: string
      chunk_index: number
      description: string
    }>
    input_chunks: Array<{
      temp_id: string
      chunk_index: number
      content: string
    }>
    llm_groups: string[][]
    merges: Array<{
      target_name: string
      source_name: string
      source_chunk_index: number
      source_description: string
      aliases_added: string[]
    }>
  }>
}

type EntityGroupingApiStep = ProcessingStepBase & {
  id: 'entity_grouping'
  result?: EntityGroupingApiResult
}

function mapStepBase(step: ApiStep): ProcessingStepBase {
  return {
    id: step.id as ProcessingStepId,
    title: step.title,
    description: step.description,
    status: step.status as ProcessingStepStatus,
    durationMs: step.duration_ms ?? 0,
    summary: step.summary ?? undefined,
    error: step.error ?? undefined,
  }
}

function mapPrepareStep(step: Extract<ApiStep, { id: 'prepare' }>): ProcessingStep {
  const base = mapStepBase(step)
  const result: PrepareStepResult | undefined = step.result
    ? {
        mdPath: step.result.md_path,
        characterCount: step.result.character_count,
        lineCount: step.result.line_count,
        preview: step.result.preview,
      }
    : undefined
  return { ...base, id: 'prepare', result }
}

function mapClearGraphStep(step: Extract<ApiStep, { id: 'clear_graph' }>): ProcessingStep {
  const base = mapStepBase(step)
  const result: ClearGraphStepResult | undefined = step.result
    ? {
        chunksDeleted: step.result.chunks_deleted,
        legacyChunksDeleted: step.result.legacy_chunks_deleted,
        orphanEntitiesDeleted: step.result.orphan_entities_deleted,
      }
    : undefined
  return { ...base, id: 'clear_graph', result }
}

function mapChunkStep(step: Extract<ApiStep, { id: 'chunk' }>): ProcessingStep {
  const base = mapStepBase(step)
  const result: ChunkStepResult | undefined = step.result
    ? {
        chunkSize: step.result.chunk_size,
        overlap: step.result.overlap,
        totalTokens: step.result.total_tokens,
        chunks: step.result.chunks.map(
          (chunk): ChunkItem => ({
            index: chunk.index,
            startToken: chunk.start_token,
            endToken: chunk.end_token,
            tokenCount: chunk.token_count,
            text: chunk.text,
          }),
        ),
      }
    : undefined
  return { ...base, id: 'chunk', result }
}

function mapEntityExtractionStep(
  step: Extract<ApiStep, { id: 'entity_extraction' }>,
): ProcessingStep {
  const base = mapStepBase(step)
  const result: EntityExtractionStepResult | undefined = step.result
    ? {
        model: step.result.model,
        totalEntities: step.result.total_entities,
        totalRelationships: step.result.total_relationships,
        chunkResults: step.result.chunk_results.map(
          (chunkResult): ChunkExtractionResult => ({
            chunkIndex: chunkResult.chunk_index,
            entities: chunkResult.entities.map(
              (entity): ExtractedEntity => ({
                name: entity.name,
                type: entity.type,
                description: entity.description,
              }),
            ),
            relationships: chunkResult.relationships.map(
              (rel): ExtractedRelationship => ({
                sourceName: rel.source_name,
                targetName: rel.target_name,
                type: rel.type,
                description: rel.description,
              }),
            ),
          }),
        ),
      }
    : undefined
  return { ...base, id: 'entity_extraction', result }
}

function mapEntityEmbeddingStep(
  step: Extract<ApiStep, { id: 'entity_embedding' }>,
): ProcessingStep {
  const base = mapStepBase(step)
  const result: EntityEmbeddingStepResult | undefined = step.result
    ? {
        modelKey: step.result.model_key,
        entitiesEmbedded: step.result.entities_embedded,
        cacheHits: step.result.cache_hits,
        cacheMisses: step.result.cache_misses,
        similarityEdgesCreated: step.result.similarity_edges_created,
      }
    : undefined
  return { ...base, id: 'entity_embedding', result }
}

function mapEntityGroupingApiStep(rawStep: Record<string, unknown>): EntityGroupingApiStep {
  return {
    id: 'entity_grouping',
    title: String(rawStep.title ?? ''),
    description: String(rawStep.description ?? ''),
    status: rawStep.status as ProcessingStepStatus,
    durationMs: Number(rawStep.duration_ms ?? 0),
    summary: rawStep.summary ? String(rawStep.summary) : undefined,
    error: rawStep.error ? String(rawStep.error) : undefined,
    result: rawStep.result as EntityGroupingApiResult | undefined,
  }
}

function mapEntityGroupingStep(step: EntityGroupingApiStep): ProcessingStep {
  const base = step
  const result: EntityGroupingStepResult | undefined = step.result
    ? {
        totalIterations: step.result.total_iterations,
        totalMerges: step.result.total_merges,
        iterations: step.result.iterations.map(
          (iteration): EntityGroupingIteration => ({
            iteration: iteration.iteration,
            seedName: iteration.seed_name,
            seedSimilarityDegree: iteration.seed_similarity_degree,
            inputEntities: iteration.input_entities.map((entity) => ({
              tempId: entity.temp_id,
              name: entity.name,
              chunkIndex: entity.chunk_index,
              description: entity.description,
            })),
            inputChunks: iteration.input_chunks.map((chunk) => ({
              tempId: chunk.temp_id,
              chunkIndex: chunk.chunk_index,
              content: chunk.content,
            })),
            llmGroups: iteration.llm_groups,
            merges: iteration.merges.map((merge) => ({
              targetName: merge.target_name,
              sourceName: merge.source_name,
              sourceChunkIndex: merge.source_chunk_index,
              sourceDescription: merge.source_description,
              aliasesAdded: merge.aliases_added,
            })),
          }),
        ),
      }
    : undefined
  return { ...base, id: 'entity_grouping', result }
}

function mapGraphBuildStep(step: Extract<ApiStep, { id: 'graph_build' }>): ProcessingStep {
  const base = mapStepBase(step)
  const result: GraphBuildStepResult | undefined = step.result
    ? {
        chunksCreated: step.result.chunks_created,
        entitiesCreated: step.result.entities_created,
        entitiesMerged: step.result.entities_merged,
        relationshipsCreated: step.result.relationships_created,
        nodes: step.result.nodes.map(
          (node): GraphNodeCreated => ({
            id: node.id,
            name: node.name,
            type: node.type,
            description: node.description,
            sourceChunkIndex: node.source_chunk_index,
          }),
        ),
        edges: step.result.edges.map(
          (edge): GraphEdgeCreated => ({
            id: edge.id,
            sourceName: edge.source_name,
            targetName: edge.target_name,
            type: edge.type,
            description: edge.description,
          }),
        ),
      }
    : undefined
  return { ...base, id: 'graph_build', result }
}

function mapStep(step: ApiStep): ProcessingStep {
  switch (step.id) {
    case 'prepare':
      return mapPrepareStep(step)
    case 'clear_graph':
      return mapClearGraphStep(step)
    case 'chunk':
      return mapChunkStep(step)
    case 'entity_extraction':
      return mapEntityExtractionStep(step)
    case 'graph_build':
      return mapGraphBuildStep(step)
    case 'entity_embedding':
      return mapEntityEmbeddingStep(step)
    default:
      if ((step as { id?: string }).id === 'entity_grouping') {
        return mapEntityGroupingStep(
          mapEntityGroupingApiStep(step as Record<string, unknown>),
        )
      }
      return mapStepBase(step) as ProcessingStep
  }
}

function mapLlmCall(
  call: NonNullable<DocumentProcessingPipelineResponse['llm_calls']>[number],
): DocumentProcessingLlmCall {
  return {
    ...mapLlmCallResponse(call),
    stepId: call.step_id as ProcessingStepId,
  }
}

export function mapDocumentProcessingPipeline(
  response: DocumentProcessingPipelineResponse,
): DocumentProcessingPipeline {
  return {
    documentId: response.document_id,
    filename: response.filename,
    startedAt: response.started_at,
    completedAt: response.completed_at ?? response.started_at,
    totalDurationMs: response.total_duration_ms ?? 0,
    steps: response.steps.map(mapStep),
    llmCalls: (response.llm_calls ?? []).map(mapLlmCall),
  }
}
