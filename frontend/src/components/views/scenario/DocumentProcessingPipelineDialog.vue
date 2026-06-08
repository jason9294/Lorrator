<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import {
  Bot,
  CheckCircle2,
  Circle,
  Clock,
  FileText,
  Loader2,
  Network,
  Scissors,
  Trash2,
  XCircle,
} from 'lucide-vue-next'
import type {
  DocumentProcessingPipeline,
  ProcessingStep,
  ProcessingStepId,
  ProcessingStepStatus,
} from '@/types/document-processing'
import { NODE_TYPE_LABELS, type NodeType } from '@/types/graph'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Spinner } from '@/components/ui/spinner'
import { cn } from '@/lib/utils'

const open = defineModel<boolean>('open', { required: true })

const props = defineProps<{
  pipeline: DocumentProcessingPipeline | null
  loading?: boolean
  error?: string | null
}>()

const selectedStepId = ref<ProcessingStepId>('prepare')

watch(
  () => props.pipeline,
  (pipeline) => {
    if (!pipeline) return
    selectedStepId.value = pipeline.steps[0]?.id ?? 'prepare'
  },
  { immediate: true },
)

const selectedStep = computed(() =>
  props.pipeline?.steps.find((step) => step.id === selectedStepId.value),
)

function formatDuration(ms: number) {
  if (ms < 1000) return `${ms} ms`
  return `${(ms / 1000).toFixed(1)} s`
}

function formatDateTime(iso: string) {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function stepStatusLabel(status: ProcessingStepStatus) {
  if (status === 'completed') return '完成'
  if (status === 'running') return '進行中'
  if (status === 'failed') return '失敗'
  if (status === 'skipped') return '略過'
  return '等待中'
}

function stepStatusVariant(status: ProcessingStepStatus) {
  if (status === 'completed') return 'default' as const
  if (status === 'failed') return 'destructive' as const
  return 'secondary' as const
}

function stepIcon(id: ProcessingStepId) {
  if (id === 'prepare') return FileText
  if (id === 'clear_graph') return Trash2
  if (id === 'chunk') return Scissors
  if (id === 'entity_extraction') return Bot
  return Network
}

function stepStatusIcon(status: ProcessingStepStatus) {
  if (status === 'completed') return CheckCircle2
  if (status === 'failed') return XCircle
  if (status === 'running') return Loader2
  return Circle
}

function entityTypeLabel(type: string) {
  return NODE_TYPE_LABELS[type as NodeType] ?? type
}

function selectStep(step: ProcessingStep) {
  selectedStepId.value = step.id
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent
      class="flex flex-col gap-0 p-0 sm:max-w-[calc(100vw-2rem)] w-[calc(100vw-2rem)] h-[calc(100vh-2rem)] max-h-[calc(100vh-2rem)] overflow-hidden"
    >
      <div
        v-if="loading"
        class="flex flex-1 flex-col items-center justify-center gap-3 p-12 text-muted-foreground"
      >
        <Spinner class="size-8" />
        <p class="text-sm">載入處理流程中…</p>
      </div>

      <div
        v-else-if="error"
        class="flex flex-1 flex-col items-center justify-center gap-2 p-12 text-center"
      >
        <XCircle class="size-10 text-destructive" />
        <p class="text-sm text-destructive whitespace-pre-wrap">{{ error }}</p>
      </div>

      <template v-else-if="pipeline">
        <DialogHeader class="shrink-0 px-6 pt-6 pb-4 border-b space-y-1">
          <div class="flex flex-wrap items-start justify-between gap-3 pr-8">
            <div class="space-y-1 min-w-0">
              <DialogTitle class="text-lg truncate">{{ pipeline.filename }}</DialogTitle>
              <DialogDescription>
                文件處理流程 · {{ formatDateTime(pipeline.startedAt) }} →
                {{ formatDateTime(pipeline.completedAt) }}
              </DialogDescription>
            </div>
            <div class="flex items-center gap-2 shrink-0">
              <Badge variant="secondary" class="gap-1">
                <Clock class="size-3" />
                總耗時 {{ formatDuration(pipeline.totalDurationMs) }}
              </Badge>
              <Badge variant="default">{{ pipeline.steps.length }} 個步驟</Badge>
            </div>
          </div>
        </DialogHeader>

        <div class="flex flex-1 min-h-0">
          <aside class="w-72 shrink-0 border-r bg-muted/20 flex flex-col min-h-0">
            <div class="px-4 py-3 border-b">
              <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                處理步驟
              </p>
            </div>
            <ScrollArea class="flex-1">
              <div class="p-2 space-y-1">
                <button
                  v-for="step in pipeline.steps"
                  :key="step.id"
                  type="button"
                  class="w-full text-left rounded-lg px-3 py-3 transition-colors hover:bg-muted/60"
                  :class="
                    cn(
                      selectedStepId === step.id && 'bg-muted ring-1 ring-border',
                    )
                  "
                  @click="selectStep(step)"
                >
                  <div class="flex items-start gap-2.5">
                    <component
                      :is="stepStatusIcon(step.status)"
                      class="size-4 shrink-0 mt-0.5"
                      :class="{
                        'text-emerald-600': step.status === 'completed',
                        'text-destructive': step.status === 'failed',
                        'text-primary animate-spin': step.status === 'running',
                        'text-muted-foreground': step.status === 'pending' || step.status === 'skipped',
                      }"
                    />
                    <div class="flex-1 min-w-0 space-y-1">
                      <div class="flex items-center gap-2">
                        <component :is="stepIcon(step.id)" class="size-3.5 text-muted-foreground shrink-0" />
                        <span class="text-sm font-medium truncate">{{ step.title }}</span>
                      </div>
                      <p v-if="step.summary" class="text-xs text-muted-foreground line-clamp-2">
                        {{ step.summary }}
                      </p>
                      <div class="flex items-center gap-2">
                        <Badge :variant="stepStatusVariant(step.status)" class="text-[10px] px-1.5 py-0">
                          {{ stepStatusLabel(step.status) }}
                        </Badge>
                        <span class="text-[10px] text-muted-foreground">
                          {{ formatDuration(step.durationMs) }}
                        </span>
                      </div>
                    </div>
                  </div>
                </button>
              </div>
            </ScrollArea>
          </aside>

          <ScrollArea class="flex-1 min-h-0">
            <div v-if="selectedStep" class="p-6 space-y-6">
              <div class="space-y-2">
                <h3 class="text-base font-semibold">{{ selectedStep.title }}</h3>
                <p class="text-sm text-muted-foreground">{{ selectedStep.description }}</p>
                <p v-if="selectedStep.error" class="text-sm text-destructive whitespace-pre-wrap">
                  {{ selectedStep.error }}
                </p>
              </div>

              <Separator />

              <p
                v-if="!selectedStep.result && selectedStep.status !== 'skipped'"
                class="text-sm text-muted-foreground"
              >
                此步驟尚無可顯示的結果。
              </p>
              <p
                v-else-if="selectedStep.status === 'skipped'"
                class="text-sm text-muted-foreground"
              >
                此步驟已略過。
              </p>

              <!-- Prepare step -->
              <div v-else-if="selectedStep.id === 'prepare' && selectedStep.result" class="space-y-4">
                <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  <div class="rounded-lg border bg-muted/30 px-4 py-3">
                    <p class="text-xs text-muted-foreground">字元數</p>
                    <p class="text-lg font-semibold mt-1">
                      {{ selectedStep.result.characterCount.toLocaleString() }}
                    </p>
                  </div>
                  <div class="rounded-lg border bg-muted/30 px-4 py-3">
                    <p class="text-xs text-muted-foreground">行數</p>
                    <p class="text-lg font-semibold mt-1">{{ selectedStep.result.lineCount }}</p>
                  </div>
                  <div class="rounded-lg border bg-muted/30 px-4 py-3 col-span-2 sm:col-span-1">
                    <p class="text-xs text-muted-foreground">檔案路徑</p>
                    <p class="text-xs font-mono mt-1 break-all">{{ selectedStep.result.mdPath }}</p>
                  </div>
                </div>
                <div class="space-y-2">
                  <p class="text-sm font-medium">Markdown 預覽</p>
                  <pre
                    class="text-xs leading-relaxed whitespace-pre-wrap rounded-lg border bg-muted/20 p-4 max-h-96 overflow-y-auto font-mono"
                  >{{ selectedStep.result.preview }}</pre>
                </div>
              </div>

              <!-- Clear graph step -->
              <div
                v-else-if="selectedStep.id === 'clear_graph' && selectedStep.result"
                class="space-y-4"
              >
                <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  <div class="rounded-lg border bg-muted/30 px-4 py-3">
                    <p class="text-xs text-muted-foreground">刪除 Chunk</p>
                    <p class="text-lg font-semibold mt-1">
                      {{ selectedStep.result.chunksDeleted }}
                    </p>
                  </div>
                  <div class="rounded-lg border bg-muted/30 px-4 py-3">
                    <p class="text-xs text-muted-foreground">刪除舊 Chunk</p>
                    <p class="text-lg font-semibold mt-1">
                      {{ selectedStep.result.legacyChunksDeleted }}
                    </p>
                  </div>
                  <div class="rounded-lg border bg-muted/30 px-4 py-3">
                    <p class="text-xs text-muted-foreground">刪除孤立實體</p>
                    <p class="text-lg font-semibold mt-1">
                      {{ selectedStep.result.orphanEntitiesDeleted }}
                    </p>
                  </div>
                </div>
              </div>

              <!-- Chunk step -->
              <div v-else-if="selectedStep.id === 'chunk' && selectedStep.result" class="space-y-4">
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div class="rounded-lg border bg-muted/30 px-4 py-3">
                    <p class="text-xs text-muted-foreground">Chunk 大小</p>
                    <p class="text-lg font-semibold mt-1">{{ selectedStep.result.chunkSize }} tokens</p>
                  </div>
                  <div class="rounded-lg border bg-muted/30 px-4 py-3">
                    <p class="text-xs text-muted-foreground">重疊</p>
                    <p class="text-lg font-semibold mt-1">{{ selectedStep.result.overlap }} tokens</p>
                  </div>
                  <div class="rounded-lg border bg-muted/30 px-4 py-3">
                    <p class="text-xs text-muted-foreground">總 tokens</p>
                    <p class="text-lg font-semibold mt-1">
                      {{ selectedStep.result.totalTokens.toLocaleString() }}
                    </p>
                  </div>
                  <div class="rounded-lg border bg-muted/30 px-4 py-3">
                    <p class="text-xs text-muted-foreground">Chunk 數量</p>
                    <p class="text-lg font-semibold mt-1">{{ selectedStep.result.chunks.length }}</p>
                  </div>
                </div>
                <div class="space-y-3">
                  <p class="text-sm font-medium">分塊結果</p>
                  <div
                    v-for="chunk in selectedStep.result.chunks"
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

              <!-- Entity extraction step -->
              <div
                v-else-if="selectedStep.id === 'entity_extraction' && selectedStep.result"
                class="space-y-4"
              >
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div class="rounded-lg border bg-muted/30 px-4 py-3">
                    <p class="text-xs text-muted-foreground">模型</p>
                    <p class="text-sm font-semibold mt-1 font-mono">{{ selectedStep.result.model }}</p>
                  </div>
                  <div class="rounded-lg border bg-muted/30 px-4 py-3">
                    <p class="text-xs text-muted-foreground">處理 chunk</p>
                    <p class="text-lg font-semibold mt-1">
                      {{ selectedStep.result.chunkResults.length }}
                    </p>
                  </div>
                  <div class="rounded-lg border bg-muted/30 px-4 py-3">
                    <p class="text-xs text-muted-foreground">實體總數</p>
                    <p class="text-lg font-semibold mt-1">{{ selectedStep.result.totalEntities }}</p>
                  </div>
                  <div class="rounded-lg border bg-muted/30 px-4 py-3">
                    <p class="text-xs text-muted-foreground">關係總數</p>
                    <p class="text-lg font-semibold mt-1">
                      {{ selectedStep.result.totalRelationships }}
                    </p>
                  </div>
                </div>
                <div
                  v-for="chunkResult in selectedStep.result.chunkResults"
                  :key="chunkResult.chunkIndex"
                  class="rounded-lg border overflow-hidden space-y-0"
                >
                  <div class="px-4 py-2.5 bg-muted/40 border-b">
                    <p class="text-sm font-medium">Chunk #{{ chunkResult.chunkIndex }} 抽取結果</p>
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

              <!-- Graph build step -->
              <div
                v-else-if="selectedStep.id === 'graph_build' && selectedStep.result"
                class="space-y-4"
              >
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div class="rounded-lg border bg-muted/30 px-4 py-3">
                    <p class="text-xs text-muted-foreground">Chunk 節點</p>
                    <p class="text-lg font-semibold mt-1">{{ selectedStep.result.chunksCreated }}</p>
                  </div>
                  <div class="rounded-lg border bg-muted/30 px-4 py-3">
                    <p class="text-xs text-muted-foreground">實體節點</p>
                    <p class="text-lg font-semibold mt-1">{{ selectedStep.result.entitiesCreated }}</p>
                  </div>
                  <div class="rounded-lg border bg-muted/30 px-4 py-3">
                    <p class="text-xs text-muted-foreground">合併實體</p>
                    <p class="text-lg font-semibold mt-1">{{ selectedStep.result.entitiesMerged }}</p>
                  </div>
                  <div class="rounded-lg border bg-muted/30 px-4 py-3">
                    <p class="text-xs text-muted-foreground">關係邊</p>
                    <p class="text-lg font-semibold mt-1">
                      {{ selectedStep.result.relationshipsCreated }}
                    </p>
                  </div>
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
                          v-for="node in selectedStep.result.nodes"
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
                          v-for="edge in selectedStep.result.edges"
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
            </div>
          </ScrollArea>
        </div>
      </template>
    </DialogContent>
  </Dialog>
</template>
