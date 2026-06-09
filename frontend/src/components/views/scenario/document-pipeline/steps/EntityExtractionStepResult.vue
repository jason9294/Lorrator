<script setup lang="ts">
import type {
  DocumentProcessingLlmCall,
  EntityExtractionStepResult,
} from '@/types/document-processing'
import { findLlmCallsForChunk } from '@/composables/documentProcessingLlmCalls'
import { getNodeTypeLabel } from '@/types/graph'
import PipelineLlmCallButton from '../PipelineLlmCallButton.vue'
import PipelineStatCard from '../PipelineStatCard.vue'

defineProps<{
  result: EntityExtractionStepResult
  llmCalls: DocumentProcessingLlmCall[]
}>()

function entityTypeLabel(type: string) {
  return getNodeTypeLabel(type)
}
</script>

<template>
  <div class="space-y-4">
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <PipelineStatCard label="模型">
        <p class="text-sm font-semibold font-mono">{{ result.model }}</p>
      </PipelineStatCard>
      <PipelineStatCard label="處理 chunk">
        <p class="text-lg font-semibold">{{ result.chunkResults.length }}</p>
      </PipelineStatCard>
      <PipelineStatCard label="實體總數">
        <p class="text-lg font-semibold">{{ result.totalEntities }}</p>
      </PipelineStatCard>
      <PipelineStatCard label="關係總數">
        <p class="text-lg font-semibold">{{ result.totalRelationships }}</p>
      </PipelineStatCard>
    </div>
    <div
      v-for="chunkResult in result.chunkResults"
      :key="chunkResult.chunkIndex"
      class="rounded-lg border overflow-hidden space-y-0"
    >
      <div class="px-4 py-2.5 bg-muted/40 border-b flex flex-wrap items-center justify-between gap-2">
        <p class="text-sm font-medium">Chunk #{{ chunkResult.chunkIndex }} 抽取結果</p>
        <div class="flex flex-wrap items-center gap-2">
          <PipelineLlmCallButton
            :call="findLlmCallsForChunk(llmCalls, chunkResult.chunkIndex).initial"
            label="初次抽取 LLM"
          />
          <PipelineLlmCallButton
            :call="findLlmCallsForChunk(llmCalls, chunkResult.chunkIndex).continueCall"
            label="補充抽取 LLM"
          />
        </div>
      </div>
      <div class="p-4 space-y-4">
        <div class="space-y-2">
          <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            實體 ({{ chunkResult.entities.length }})
          </p>
          <div class="border rounded-lg overflow-hidden">
            <table class="w-full text-sm">
              <thead>
                <tr class="bg-muted/50 border-b">
                  <th class="text-left px-3 py-2 text-xs text-muted-foreground font-medium w-24">
                    類型
                  </th>
                  <th class="text-left px-3 py-2 text-xs text-muted-foreground font-medium w-32">
                    名稱
                  </th>
                  <th class="text-left px-3 py-2 text-xs text-muted-foreground font-medium">
                    描述
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="entity in chunkResult.entities"
                  :key="`${chunkResult.chunkIndex}-${entity.name}`"
                  class="border-b last:border-b-0"
                >
                  <td class="px-3 py-2 text-xs">{{ entityTypeLabel(entity.type) }}</td>
                  <td class="px-3 py-2 font-medium">{{ entity.name }}</td>
                  <td class="px-3 py-2 text-muted-foreground">{{ entity.description }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="space-y-2">
          <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            關係 ({{ chunkResult.relationships.length }})
          </p>
          <div
            v-if="chunkResult.relationships.length === 0"
            class="text-sm text-muted-foreground border rounded-lg px-3 py-4 text-center"
          >
            此 chunk 未抽取到關係
          </div>
          <div v-else class="border rounded-lg overflow-hidden">
            <table class="w-full text-sm">
              <thead>
                <tr class="bg-muted/50 border-b">
                  <th class="text-left px-3 py-2 text-xs text-muted-foreground font-medium w-28">
                    來源
                  </th>
                  <th class="text-left px-3 py-2 text-xs text-muted-foreground font-medium w-24">
                    類型
                  </th>
                  <th class="text-left px-3 py-2 text-xs text-muted-foreground font-medium w-28">
                    目標
                  </th>
                  <th class="text-left px-3 py-2 text-xs text-muted-foreground font-medium">
                    描述
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="rel in chunkResult.relationships"
                  :key="`${chunkResult.chunkIndex}-${rel.sourceName}-${rel.targetName}-${rel.type}`"
                  class="border-b last:border-b-0"
                >
                  <td class="px-3 py-2">{{ rel.sourceName }}</td>
                  <td class="px-3 py-2 font-mono text-xs">{{ rel.type }}</td>
                  <td class="px-3 py-2">{{ rel.targetName }}</td>
                  <td class="px-3 py-2 text-muted-foreground">{{ rel.description }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
