<script setup lang="ts">
import { ref } from 'vue'
import { Eye, FileText, Network, RefreshCw, Upload } from 'lucide-vue-next'
import type { DocumentResponse } from '@/services'
import { useDocumentProcessingPipeline } from '@/composables/useDocumentProcessingPipeline'
import DocumentProcessingPipelineDialog from '@/components/views/scenario/DocumentProcessingPipelineDialog.vue'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Spinner } from '@/components/ui/spinner'

defineProps<{
  documents: DocumentResponse[]
  documentsLoading: boolean
  documentsError: string | null
  uploadError: string | null
  processError: string | null
  uploadingFiles: { name: string }[]
  processingDocumentId: string | null
}>()

const emit = defineEmits<{
  'file-change': [event: Event]
  'process-document': [documentId: string]
  'reprocess-document': [documentId: string]
}>()

const fileInputRef = ref<HTMLInputElement | null>(null)
const pipelineDialogOpen = ref(false)
const viewingPipelineDocumentId = ref<string | null>(null)

const {
  pipeline: selectedPipeline,
  loading: pipelineLoading,
  error: pipelineError,
  fetchPipeline,
  reset: resetPipeline,
} = useDocumentProcessingPipeline()

function triggerUpload() {
  fileInputRef.value?.click()
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
  })
}

function documentMetaLine(doc: DocumentResponse) {
  const ct = doc.content_type?.trim()
  const when = formatDateTime(doc.created_at)
  return ct ? `${ct} · ${when}` : when
}

function documentStatusLabel(status: string) {
  if (status === 'READY') return '待處理'
  if (status === 'PROCESSING') return '處理中'
  if (status === 'COMPLETED') return '已完成'
  if (status === 'FAILED') return '失敗'
  return status
}

function canProcessDocument(status: string) {
  return status === 'READY'
}

function canReprocessDocument(status: string) {
  return status === 'COMPLETED' || status === 'FAILED'
}

function canViewProcessingPipeline(status: string) {
  return status === 'COMPLETED' || status === 'FAILED'
}

async function openProcessingPipeline(doc: DocumentResponse) {
  viewingPipelineDocumentId.value = doc.id
  pipelineDialogOpen.value = true
  try {
    await fetchPipeline(doc.id)
  } catch {
    // error state is shown in the dialog
  }
}

function onPipelineDialogOpenChange(open: boolean) {
  pipelineDialogOpen.value = open
  if (!open) {
    viewingPipelineDocumentId.value = null
    resetPipeline()
  }
}
</script>

<template>
  <div class="h-full overflow-y-auto">
    <div class="max-w-2xl mx-auto p-6 space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="font-semibold">文件清單</h3>
        <div class="flex items-center gap-2">
          <Badge variant="secondary">{{ documents.length }} 份文件</Badge>
          <Button
            v-if="documents.length === 0"
            size="sm"
            class="gap-1.5"
            :disabled="documentsLoading"
            @click="triggerUpload"
          >
            <Upload class="size-3.5" />
            上傳文件
          </Button>
          <input
            v-if="documents.length === 0"
            ref="fileInputRef"
            type="file"
            class="hidden"
            multiple
            accept=".pdf,.txt,.md,.docx"
            @change="emit('file-change', $event)"
          />
        </div>
      </div>

      <p v-if="documentsError" class="text-sm text-destructive whitespace-pre-wrap">
        {{ documentsError }}
      </p>
      <p v-if="uploadError" class="text-sm text-destructive whitespace-pre-wrap">
        {{ uploadError }}
      </p>
      <p v-if="processError" class="text-sm text-destructive whitespace-pre-wrap">
        {{ processError }}
      </p>

      <div v-if="uploadingFiles.length > 0" class="space-y-2">
        <div
          v-for="f in uploadingFiles"
          :key="f.name"
          class="flex items-center gap-3 bg-muted/50 rounded-lg px-3 py-2"
        >
          <Spinner class="size-4 shrink-0" />
          <div class="flex-1 min-w-0">
            <p class="text-xs font-medium truncate">{{ f.name }}</p>
            <p class="text-[10px] text-muted-foreground">上傳中...</p>
          </div>
        </div>
      </div>

      <div
        v-if="documentsLoading"
        class="flex items-center gap-2 text-sm text-muted-foreground py-4"
      >
        <Spinner class="size-4" />
        載入文件清單中…
      </div>

      <div v-else-if="documents.length > 0" class="border rounded-lg overflow-hidden">
        <div
          v-for="(doc, idx) in documents"
          :key="doc.id"
          class="flex items-center gap-3 px-4 py-3 hover:bg-muted/30 transition-colors"
          :class="idx < documents.length - 1 ? 'border-b' : ''"
        >
          <div class="w-8 h-8 rounded-md bg-muted flex items-center justify-center shrink-0">
            <FileText class="size-4 text-muted-foreground" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium truncate">{{ doc.filename }}</p>
            <p class="text-xs text-muted-foreground">
              {{ documentMetaLine(doc) }}
              <span class="mx-1">·</span>
              <span>{{ documentStatusLabel(doc.status) }}</span>
            </p>
          </div>
          <div class="shrink-0 flex items-center gap-2">
            <Button
              v-if="canProcessDocument(doc.status)"
              size="sm"
              variant="outline"
              class="gap-1.5"
              :disabled="processingDocumentId === doc.id"
              @click="emit('process-document', doc.id)"
            >
              <Spinner v-if="processingDocumentId === doc.id" class="size-3.5" />
              <Network v-else class="size-3.5" />
              處理文件
            </Button>
            <template v-else-if="canReprocessDocument(doc.status)">
              <Button
                v-if="canViewProcessingPipeline(doc.status)"
                size="sm"
                variant="outline"
                class="gap-1.5"
                :disabled="pipelineLoading && viewingPipelineDocumentId === doc.id"
                @click="openProcessingPipeline(doc)"
              >
                <Spinner
                  v-if="pipelineLoading && viewingPipelineDocumentId === doc.id"
                  class="size-3.5"
                />
                <Eye v-else class="size-3.5" />
                查看過程
              </Button>
              <Button
                size="sm"
                variant="outline"
                class="gap-1.5"
                :disabled="processingDocumentId === doc.id"
                @click="emit('reprocess-document', doc.id)"
              >
                <Spinner v-if="processingDocumentId === doc.id" class="size-3.5" />
                <RefreshCw v-else class="size-3.5" />
                重新處理
              </Button>
            </template>
            <Button v-else size="sm" variant="outline" disabled>
              {{ doc.status === 'PROCESSING' ? '處理中…' : '已處理' }}
            </Button>
          </div>
        </div>
      </div>

      <div
        v-else-if="uploadingFiles.length === 0"
        class="flex flex-col items-center justify-center py-16 text-center border rounded-lg border-dashed"
      >
        <FileText class="size-10 text-muted-foreground/40 mb-3" />
        <p class="text-sm font-medium text-muted-foreground">尚無文件</p>
        <p class="text-xs text-muted-foreground/60 mt-1">點擊「上傳文件」新增劇本相關文件</p>
      </div>
    </div>

    <DocumentProcessingPipelineDialog
      :open="pipelineDialogOpen"
      :pipeline="selectedPipeline"
      :loading="pipelineLoading"
      :error="pipelineError"
      @update:open="onPipelineDialogOpenChange"
    />
  </div>
</template>
