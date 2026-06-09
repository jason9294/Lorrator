<script setup lang="ts">
import type { ChunkStepResult } from '@/types/document-processing'
import { Badge } from '@/components/ui/badge'
import PipelineStatCard from '../PipelineStatCard.vue'

defineProps<{
  result: ChunkStepResult
}>()
</script>

<template>
  <div class="space-y-4">
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <PipelineStatCard label="Chunk 大小">
        <p class="text-lg font-semibold">{{ result.chunkSize }} tokens</p>
      </PipelineStatCard>
      <PipelineStatCard label="重疊">
        <p class="text-lg font-semibold">{{ result.overlap }} tokens</p>
      </PipelineStatCard>
      <PipelineStatCard label="總 tokens">
        <p class="text-lg font-semibold">{{ result.totalTokens.toLocaleString() }}</p>
      </PipelineStatCard>
      <PipelineStatCard label="Chunk 數量">
        <p class="text-lg font-semibold">{{ result.chunks.length }}</p>
      </PipelineStatCard>
    </div>
    <div class="space-y-3">
      <p class="text-sm font-medium">分塊結果</p>
      <div
        v-for="chunk in result.chunks"
        :key="chunk.index"
        class="rounded-lg border overflow-hidden"
      >
        <div class="flex flex-wrap items-center gap-2 px-4 py-2.5 bg-muted/40 border-b text-xs">
          <Badge variant="outline">Chunk #{{ chunk.index }}</Badge>
          <span class="text-muted-foreground">
            tokens [{{ chunk.startToken }}:{{ chunk.endToken }}]
          </span>
          <span class="text-muted-foreground">{{ chunk.tokenCount }} tokens</span>
        </div>
        <pre class="text-xs leading-relaxed whitespace-pre-wrap p-4 font-mono">{{ chunk.text }}</pre>
      </div>
    </div>
  </div>
</template>
