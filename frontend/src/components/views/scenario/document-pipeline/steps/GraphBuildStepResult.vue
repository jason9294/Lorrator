<script setup lang="ts">
import type { GraphBuildStepResult } from '@/types/document-processing'
import { getNodeTypeLabel } from '@/types/graph'
import PipelineStatCard from '../PipelineStatCard.vue'

defineProps<{
  result: GraphBuildStepResult
}>()

function entityTypeLabel(type: string) {
  return getNodeTypeLabel(type)
}
</script>

<template>
  <div class="space-y-4">
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <PipelineStatCard label="Chunk 節點">
        <p class="text-lg font-semibold">{{ result.chunksCreated }}</p>
      </PipelineStatCard>
      <PipelineStatCard label="實體節點">
        <p class="text-lg font-semibold">{{ result.entitiesCreated }}</p>
      </PipelineStatCard>
      <PipelineStatCard label="合併實體">
        <p class="text-lg font-semibold">{{ result.entitiesMerged }}</p>
      </PipelineStatCard>
      <PipelineStatCard label="關係邊">
        <p class="text-lg font-semibold">{{ result.relationshipsCreated }}</p>
      </PipelineStatCard>
    </div>
    <div class="space-y-2">
      <p class="text-sm font-medium">寫入的節點</p>
      <div class="border rounded-lg overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-muted/50 border-b">
              <th class="text-left px-3 py-2 text-xs text-muted-foreground font-medium w-24">
                類型
              </th>
              <th class="text-left px-3 py-2 text-xs text-muted-foreground font-medium w-36">
                名稱
              </th>
              <th class="text-left px-3 py-2 text-xs text-muted-foreground font-medium w-24">
                來源 Chunk
              </th>
              <th class="text-left px-3 py-2 text-xs text-muted-foreground font-medium">
                描述
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="node in result.nodes"
              :key="node.id"
              class="border-b last:border-b-0"
            >
              <td class="px-3 py-2 text-xs">{{ entityTypeLabel(node.type) }}</td>
              <td class="px-3 py-2 font-medium">{{ node.name }}</td>
              <td class="px-3 py-2 text-muted-foreground">
                <template v-if="node.type === 'CHUNK'">—</template>
                <template v-else>#{{ node.sourceChunkIndex }}</template>
              </td>
              <td class="px-3 py-2 text-muted-foreground">{{ node.description }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="space-y-2">
      <p class="text-sm font-medium">寫入的關係</p>
      <div class="border rounded-lg overflow-hidden">
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
              v-for="edge in result.edges"
              :key="edge.id"
              class="border-b last:border-b-0"
            >
              <td class="px-3 py-2">{{ edge.sourceName }}</td>
              <td class="px-3 py-2 font-mono text-xs">{{ edge.type }}</td>
              <td class="px-3 py-2">{{ edge.targetName }}</td>
              <td class="px-3 py-2 text-muted-foreground">{{ edge.description }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
