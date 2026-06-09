<script setup lang="ts">
import type { EntityEmbeddingStepResult } from '@/types/document-processing'
import PipelineStatCard from '../PipelineStatCard.vue'

defineProps<{
  result: EntityEmbeddingStepResult
}>()
</script>

<template>
  <div class="space-y-4">
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <PipelineStatCard label="模型">
        <p class="text-sm font-semibold font-mono">{{ result.modelKey }}</p>
      </PipelineStatCard>
      <PipelineStatCard label="向量化實體">
        <p class="text-lg font-semibold">{{ result.entitiesEmbedded }}</p>
      </PipelineStatCard>
      <PipelineStatCard label="相似邊">
        <p class="text-lg font-semibold">{{ result.similarityEdgesCreated }}</p>
      </PipelineStatCard>
      <PipelineStatCard label="快取命中">
        <p class="text-lg font-semibold">{{ result.cacheHits }} / {{ result.cacheMisses }}</p>
      </PipelineStatCard>
    </div>
  </div>
</template>
