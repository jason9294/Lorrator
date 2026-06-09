<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import {
  Bot,
  CheckCircle2,
  Circle,
  Clock,
  FileText,
  GitMerge,
  Loader2,
  Network,
  Scissors,
  Sparkles,
  Trash2,
  XCircle,
} from 'lucide-vue-next'
import type {
  DocumentProcessingPipeline,
  ProcessingStep,
  ProcessingStepId,
  ProcessingStepStatus,
} from '@/types/document-processing'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Spinner } from '@/components/ui/spinner'
import { cn } from '@/lib/utils'
import PipelineStepDetail from './document-pipeline/PipelineStepDetail.vue'

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
  if (id === 'entity_embedding') return Sparkles
  if (id === 'entity_grouping') return GitMerge
  return Network
}

function stepStatusIcon(status: ProcessingStepStatus) {
  if (status === 'completed') return CheckCircle2
  if (status === 'failed') return XCircle
  if (status === 'running') return Loader2
  return Circle
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
            <PipelineStepDetail
              v-if="selectedStep"
              :step="selectedStep"
              :llm-calls="pipeline.llmCalls"
            />
          </ScrollArea>
        </div>
      </template>
    </DialogContent>
  </Dialog>
</template>
