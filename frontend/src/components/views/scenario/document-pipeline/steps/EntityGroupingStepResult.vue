<script setup lang="ts">
import { ref } from 'vue'
import { ChevronRight } from 'lucide-vue-next'
import type { EntityGroupingStepResult } from '@/types/document-processing'
import { Badge } from '@/components/ui/badge'
import PipelineStatCard from '../PipelineStatCard.vue'

defineProps<{
  result: EntityGroupingStepResult
}>()

const expandedChunkKeys = ref<Set<string>>(new Set())

function chunkExpandKey(roundIteration: number, tempId: string) {
  return `${roundIteration}-${tempId}`
}

function isChunkExpanded(roundIteration: number, tempId: string) {
  return expandedChunkKeys.value.has(chunkExpandKey(roundIteration, tempId))
}

function toggleChunkExpanded(roundIteration: number, tempId: string) {
  const key = chunkExpandKey(roundIteration, tempId)
  const next = new Set(expandedChunkKeys.value)
  if (next.has(key)) {
    next.delete(key)
  } else {
    next.add(key)
  }
  expandedChunkKeys.value = next
}
</script>

<template>
  <div class="space-y-4">
    <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
      <PipelineStatCard label="分群輪次">
        <p class="text-lg font-semibold">{{ result.totalIterations }}</p>
      </PipelineStatCard>
      <PipelineStatCard label="合併實體數">
        <p class="text-lg font-semibold">{{ result.totalMerges }}</p>
      </PipelineStatCard>
    </div>

    <div
      v-for="round in result.iterations"
      :key="round.iteration"
      class="rounded-lg border overflow-hidden space-y-0"
    >
      <div class="px-4 py-2.5 bg-muted/40 border-b">
        <p class="text-sm font-medium">
          第 {{ round.iteration }} 輪 · 種子節點 {{ round.seedName }}
          <span class="text-muted-foreground font-normal">
            （{{ round.seedSimilarityDegree }} 條相似邊）
          </span>
        </p>
      </div>
      <div class="p-4 space-y-4">
        <div class="space-y-2">
          <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            送入 LLM 的實體
          </p>
          <div class="border rounded-lg overflow-hidden">
            <table class="w-full text-sm">
              <thead>
                <tr class="bg-muted/50 border-b">
                  <th class="text-left px-3 py-2 text-xs text-muted-foreground font-medium w-16">
                    ID
                  </th>
                  <th class="text-left px-3 py-2 text-xs text-muted-foreground font-medium w-32">
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
                  v-for="entity in round.inputEntities"
                  :key="`${round.iteration}-${entity.tempId}`"
                  class="border-b last:border-b-0"
                >
                  <td class="px-3 py-2 font-mono text-xs">{{ entity.tempId }}</td>
                  <td class="px-3 py-2 font-medium">{{ entity.name }}</td>
                  <td class="px-3 py-2 text-muted-foreground">
                    <template v-if="entity.chunkIndex >= 0">#{{ entity.chunkIndex }}</template>
                    <template v-else>—</template>
                  </td>
                  <td class="px-3 py-2 text-muted-foreground">{{ entity.description }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="space-y-2">
          <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            相關 Chunk 文本
          </p>
          <div
            v-for="chunk in round.inputChunks"
            :key="`${round.iteration}-${chunk.tempId}`"
            class="rounded-lg border overflow-hidden"
          >
            <button
              type="button"
              class="flex w-full flex-wrap items-center gap-2 px-4 py-2.5 bg-muted/40 text-xs text-left hover:bg-muted/60 transition-colors"
              :class="{
                'border-b': isChunkExpanded(round.iteration, chunk.tempId),
              }"
              @click="toggleChunkExpanded(round.iteration, chunk.tempId)"
            >
              <ChevronRight
                class="size-3.5 shrink-0 text-muted-foreground transition-transform"
                :class="{
                  'rotate-90': isChunkExpanded(round.iteration, chunk.tempId),
                }"
              />
              <Badge variant="outline">{{ chunk.tempId }}</Badge>
              <span class="text-muted-foreground">Chunk #{{ chunk.chunkIndex }}</span>
              <span
                v-if="!isChunkExpanded(round.iteration, chunk.tempId)"
                class="text-muted-foreground ml-auto"
              >
                點擊展開
              </span>
            </button>
            <pre
              v-if="isChunkExpanded(round.iteration, chunk.tempId)"
              class="text-xs leading-relaxed whitespace-pre-wrap p-4 font-mono"
            >{{ chunk.content }}</pre>
          </div>
        </div>

        <div class="space-y-2">
          <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            LLM 分群結果
          </p>
          <div class="flex flex-wrap gap-2">
            <div
              v-for="(group, groupIndex) in round.llmGroups"
              :key="`${round.iteration}-group-${groupIndex}`"
              class="rounded-lg border px-3 py-2 text-sm"
            >
              <span class="text-xs text-muted-foreground">群 {{ groupIndex + 1 }}：</span>
              <span class="font-mono">{{ group.join(', ') }}</span>
            </div>
          </div>
        </div>

        <div v-if="round.merges.length > 0" class="space-y-2">
          <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            合併紀錄
          </p>
          <div class="border rounded-lg overflow-hidden">
            <table class="w-full text-sm">
              <thead>
                <tr class="bg-muted/50 border-b">
                  <th class="text-left px-3 py-2 text-xs text-muted-foreground font-medium w-32">
                    保留節點
                  </th>
                  <th class="text-left px-3 py-2 text-xs text-muted-foreground font-medium w-32">
                    合併節點
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
                  v-for="merge in round.merges"
                  :key="`${round.iteration}-${merge.targetName}-${merge.sourceName}`"
                  class="border-b last:border-b-0"
                >
                  <td class="px-3 py-2 font-medium">{{ merge.targetName }}</td>
                  <td class="px-3 py-2">{{ merge.sourceName }}</td>
                  <td class="px-3 py-2 text-muted-foreground">
                    <template v-if="merge.sourceChunkIndex >= 0">
                      #{{ merge.sourceChunkIndex }}
                    </template>
                    <template v-else>—</template>
                  </td>
                  <td class="px-3 py-2 text-muted-foreground">{{ merge.sourceDescription }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <p v-else class="text-sm text-muted-foreground">此輪未執行合併</p>
      </div>
    </div>
  </div>
</template>
