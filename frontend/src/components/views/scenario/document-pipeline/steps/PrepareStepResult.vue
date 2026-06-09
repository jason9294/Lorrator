<script setup lang="ts">
import type { PrepareStepResult } from '@/types/document-processing'
import PipelineStatCard from '../PipelineStatCard.vue'

defineProps<{
  result: PrepareStepResult
}>()
</script>

<template>
  <div class="space-y-4">
    <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
      <PipelineStatCard label="字元數">
        <p class="text-lg font-semibold">{{ result.characterCount.toLocaleString() }}</p>
      </PipelineStatCard>
      <PipelineStatCard label="行數">
        <p class="text-lg font-semibold">{{ result.lineCount }}</p>
      </PipelineStatCard>
      <PipelineStatCard label="檔案路徑" class="col-span-2 sm:col-span-1">
        <p class="text-xs font-mono break-all">{{ result.mdPath }}</p>
      </PipelineStatCard>
    </div>
    <div class="space-y-2">
      <p class="text-sm font-medium">Markdown 預覽</p>
      <pre
        class="text-xs leading-relaxed whitespace-pre-wrap rounded-lg border bg-muted/20 p-4 max-h-96 overflow-y-auto font-mono"
      >{{ result.preview }}</pre>
    </div>
  </div>
</template>
