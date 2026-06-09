<script setup lang="ts">
import type { ClearGraphStepResult } from '@/types/document-processing'
import PipelineStatCard from '../PipelineStatCard.vue'

defineProps<{
  result: ClearGraphStepResult
}>()
</script>

<template>
  <div class="space-y-4">
    <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
      <PipelineStatCard label="刪除 Chunk">
        <p class="text-lg font-semibold">{{ result.chunksDeleted }}</p>
      </PipelineStatCard>
      <PipelineStatCard label="刪除舊 Chunk">
        <p class="text-lg font-semibold">{{ result.legacyChunksDeleted }}</p>
      </PipelineStatCard>
      <PipelineStatCard label="刪除孤立實體">
        <p class="text-lg font-semibold">{{ result.orphanEntitiesDeleted }}</p>
      </PipelineStatCard>
    </div>
  </div>
</template>
