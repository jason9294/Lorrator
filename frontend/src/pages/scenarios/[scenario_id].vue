<template>
  <div class="h-screen flex flex-col bg-background text-foreground overflow-hidden">
    <!-- 載入中 -->
    <div
      v-if="isInitialLoading"
      class="flex-1 flex flex-col items-center justify-center gap-3 text-muted-foreground"
    >
      <Spinner class="size-8" />
      <p class="text-sm">載入劇本資料中…</p>
    </div>

    <!-- 找不到劇本 -->
    <div
      v-else-if="pageError === 'not_found'"
      class="flex-1 flex flex-col items-center justify-center gap-4 p-8 text-center"
    >
      <p class="text-lg font-semibold">找不到這個劇本</p>
      <p class="text-sm text-muted-foreground">可能已被刪除，或連結不正確。</p>
      <RouterLink to="/scenarios">
        <Button>返回劇本列表</Button>
      </RouterLink>
    </div>

    <!-- 載入失敗 -->
    <div
      v-else-if="pageError === 'load_failed'"
      class="flex-1 flex flex-col items-center justify-center gap-4 p-8 text-center"
    >
      <p class="text-lg font-semibold">無法載入劇本</p>
      <p class="text-sm text-muted-foreground">請確認後端服務已啟動，並稍後再試。</p>
      <Button @click="bootstrap">重試</Button>
    </div>

    <!-- 主內容 -->
    <template v-else-if="scenarioDetail">
      <!-- 頂部導覽列 -->
      <header
        class="shrink-0 flex items-center gap-3 px-5 h-13 border-b bg-card/80 backdrop-blur-sm z-30"
      >
        <RouterLink to="/scenarios">
          <Button variant="ghost" size="icon-sm" class="text-muted-foreground">
            <ArrowLeft class="size-4" />
          </Button>
        </RouterLink>

        <div class="w-px h-5 bg-border shrink-0" />

        <div class="flex items-center gap-2.5 flex-1 min-w-0">
          <div
            class="w-7 h-7 rounded-lg flex items-center justify-center shadow-sm shrink-0 text-white text-xs font-bold"
            :style="{ backgroundColor: colorFromId(scenarioDetail.id) }"
          >
            {{ scenarioDetail.name.charAt(0) }}
          </div>
          <div class="flex flex-col leading-none min-w-0">
            <span class="text-sm font-semibold truncate">{{ scenarioDetail.name }}</span>
            <span class="text-[10px] text-muted-foreground">{{ scenarioDetail.system }}</span>
          </div>
          <!-- 狀態徽章 -->
          <Badge
            v-if="scenarioDetail.status === 'DRAFT'"
            variant="secondary"
            class="text-[10px] gap-1 ml-1"
          >
            <PencilLine class="size-2.5" />
            草稿
          </Badge>
          <Badge
            v-else
            class="text-[10px] gap-1 ml-1 bg-green-500/15 text-green-700 dark:text-green-400 border-green-500/30"
            variant="outline"
          >
            <Globe class="size-2.5" />
            已發布
          </Badge>
        </div>

        <!-- 右側操作按鈕 -->
        <div class="flex items-center gap-2 shrink-0">
          <!-- 草稿操作：編輯 / 發布 -->
          <template v-if="scenarioDetail.status === 'DRAFT'">
            <Button variant="outline" size="sm" class="gap-1.5" @click="editDialogOpen = true">
              <Pencil class="size-3.5" />
              編輯
            </Button>
            <Button
              size="sm"
              class="gap-1.5"
              :disabled="isPublishing || !canPublish"
              :title="!canPublish ? '請先上傳文件並確認所有文件皆處理完成' : undefined"
              @click="confirmPublishOpen = true"
            >
              <Spinner v-if="isPublishing" class="size-3.5" />
              <Globe v-else class="size-3.5" />
              {{ isPublishing ? '發布中...' : '發布劇本' }}
            </Button>
          </template>

          <!-- 已發布操作：創建房間 -->
          <Button
            v-else
            size="sm"
            class="gap-1.5"
            :disabled="isCreatingRoom"
            @click="handleCreateRoom"
          >
            <Spinner v-if="isCreatingRoom" class="size-3.5" />
            <Plus v-else class="size-3.5" />
            {{ isCreatingRoom ? '建立中...' : '創建房間' }}
          </Button>

          <!-- 主題切換 -->
          <Button
            variant="outline"
            size="icon-sm"
            :title="isDark ? '切換為亮色模式' : '切換為暗色模式'"
            @click="toggle"
          >
            <Transition name="icon-swap" mode="out-in">
              <Moon v-if="!isDark" :key="'moon'" class="size-3.5" />
              <Sun v-else :key="'sun'" class="size-3.5" />
            </Transition>
          </Button>
        </div>

        <!-- Tab 切換器 -->
        <nav class="hidden md:flex items-center gap-1 bg-muted rounded-lg p-1 ml-2">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-colors"
            :class="
              activeTab === tab.id
                ? 'bg-background text-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground'
            "
            @click="activeTab = tab.id"
          >
            <component :is="tab.icon" class="size-3.5" />
            {{ tab.label }}
          </button>
        </nav>

        <!-- 行動裝置 Tab 下拉 -->
        <div class="md:hidden">
          <select
            v-model="activeTab"
            class="text-xs bg-muted border-0 rounded-md px-2 py-1.5 text-foreground outline-none"
          >
            <option v-for="tab in tabs" :key="tab.id" :value="tab.id">{{ tab.label }}</option>
          </select>
        </div>
      </header>

      <ConfirmPublishScenarioDialog
        v-model:open="confirmPublishOpen"
        :is-publishing="isPublishing"
        @confirm="handlePublish"
      />

      <!-- 發布錯誤提示 -->
      <div
        v-if="publishError"
        class="shrink-0 px-5 py-2 bg-destructive/10 text-destructive text-xs flex items-center gap-2"
      >
        <span>{{ publishError }}</span>
        <button class="ml-auto" @click="publishError = null">✕</button>
      </div>

      <!-- Tab 內容 -->
      <main class="flex-1 min-h-0 overflow-hidden">
        <ScenarioGraphTab
          v-show="activeTab === 'graph'"
          :graph="graph"
          :scenario-id="scenarioDetail.id"
          :is-dark="isDark"
        />
        <ScenarioEntitiesTab v-show="activeTab === 'entities'" :graph="graph" />
        <ScenarioDocumentsTab
          v-show="activeTab === 'documents'"
          :documents="documents"
          :documents-loading="documentsLoading"
          :documents-error="documentsError"
          :upload-error="uploadError"
          :process-error="processError"
          :uploading-files="uploadingFiles"
          :processing-document-id="processingDocumentId"
          @file-change="onFileChange"
          @process-document="handleProcessDocument"
          @reprocess-document="handleReprocessDocument"
        />
      </main>
    </template>

    <EditScenarioDialog
      v-model:open="editDialogOpen"
      v-model:name="editName"
      v-model:system="editSystem"
      v-model:description="editDescription"
      :is-editing="isEditing"
      :error="editError"
      @save="handleEdit"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { useAsyncState, useToggle, whenever } from '@vueuse/core'

// Icons
import {
  ArrowLeft,
  FileText,
  Globe,
  List,
  Moon,
  Network,
  Pencil,
  PencilLine,
  Plus,
  Sun,
} from 'lucide-vue-next'

// Types
import type { NodeType } from '@/types/graph'
import { NODE_TYPE_LABELS } from '@/types/graph'
import type { Graph } from '@/types/graph'

// Composables
import { useColorMode } from '@/composables/useColorMode'
import { useAppWebSocket } from '@/composables/useAppWebSocket'

// Low-level Components
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Spinner } from '@/components/ui/spinner'

// High-level Components
import ConfirmPublishScenarioDialog from '@/components/scenarios/ConfirmPublishScenarioDialog.vue'
import EditScenarioDialog from '@/components/scenarios/EditScenarioDialog.vue'
import ScenarioGraphTab from '@/components/views/scenario/ScenarioGraphTab.vue'
import ScenarioEntitiesTab from '@/components/views/scenario/ScenarioEntitiesTab.vue'
import ScenarioDocumentsTab from '@/components/views/scenario/ScenarioDocumentsTab.vue'

// API services
import {
  DocumentsService,
  ScenariosService,
  type DocumentResponse,
  type ScenarioResponse,
} from '@/services'

const route = useRoute()
const router = useRouter()
const { isDark, toggle } = useColorMode()

const COLORS = ['#7c3aed', '#0891b2', '#b45309', '#be123c', '#10b981', '#f97316', '#6366f1']

function colorFromId(id: string) {
  let hash = 0
  for (let i = 0; i < id.length; i += 1) {
    hash = (hash * 31 + id.charCodeAt(i)) | 0
  }
  const idx = Math.abs(hash) % COLORS.length
  return COLORS[idx]
}

const scenarioId = computed(() => {
  const p = route.params.scenario_id
  return Array.isArray(p) ? p[0] : p
})

const tabs = [
  { id: 'graph', label: '知識圖譜', icon: Network },
  { id: 'entities', label: '實體清單', icon: List },
  { id: 'documents', label: '文件清單', icon: FileText },
]
const activeTab = ref('graph')

const graph = ref<Graph>({ nodes: [], edges: [] })
const documents = ref<DocumentResponse[]>([])
const documentsLoading = ref(false)
const documentsError = ref<string | null>(null)

const uploadingFiles = ref<{ name: string }[]>([])
const uploadError = ref<string | null>(null)
const processingDocumentId = ref<string | null>(null)
const processError = ref<string | null>(null)

// 發布
const isPublishing = ref(false)
const publishError = ref<string | null>(null)
const [confirmPublishOpen] = useToggle(false)

const canPublish = computed(() => {
  if (!documents.value.length) return false
  return documents.value.every((d) => d.status === 'COMPLETED')
})

// 創建房間
const isCreatingRoom = ref(false)

// 編輯
const [editDialogOpen] = useToggle(false)
const editName = ref('')
const editSystem = ref('')
const editDescription = ref('')
const isEditing = ref(false)
const editError = ref<string | null>(null)

function normalizeGraphPayload(data: unknown): Graph {
  if (!data || typeof data !== 'object') return { nodes: [], edges: [] }
  const o = data as Record<string, unknown>
  const nodesRaw = o.nodes
  const edgesRaw = o.edges
  if (!Array.isArray(nodesRaw) || !Array.isArray(edgesRaw)) return { nodes: [], edges: [] }

  const nodes = nodesRaw
    .map((n) => {
      if (!n || typeof n !== 'object') {
        console.error('Invalid node:', n)
        return null
      }
      const x = n as Record<string, unknown>
      const id = typeof x.id === 'string' ? x.id : null
      const type = typeof x.type === 'string' ? x.type : null
      const label = typeof x.label === 'string' ? x.label : null
      const description = typeof x.description === 'string' ? x.description : ''
      if (!id || !type || !label) {
        console.error('Invalid node:', n)
        return null
      }
      if (!NODE_TYPE_LABELS[type as NodeType]) {
        return { id, type: 'UNKNOWN' as NodeType, label, description }
      }
      return { id, type: type as NodeType, label, description }
    })
    .filter((n): n is NonNullable<typeof n> => n !== null)

  const edges = edgesRaw
    .map((e) => {
      if (!e || typeof e !== 'object') return null
      const x = e as Record<string, unknown>
      const id = typeof x.id === 'string' ? x.id : null
      const source = typeof x.source === 'string' ? x.source : null
      const target = typeof x.target === 'string' ? x.target : null
      const type = typeof x.type === 'string' ? x.type : ''
      const directed = typeof x.directed === 'boolean' ? x.directed : false
      if (!id || !source || !target) return null
      return { id, source, target, type, directed }
    })
    .filter((e): e is NonNullable<typeof e> => e !== null)

  return { nodes, edges }
}

async function loadGraph() {
  console.log('loadGraph() called with id:', scenarioId.value)
  const id = scenarioId.value
  if (!id) return
  try {
    const res = await ScenariosService.getScenarioGraph({ path: { scenario_id: id } })
    graph.value = normalizeGraphPayload(res.data)
    console.log('Graph loaded successfully:', graph.value)
  } catch (error) {
    console.error('Error loading graph:', error)
    graph.value = { nodes: [], edges: [] }
  }
}

async function loadDocuments() {
  const id = scenarioId.value
  if (!id) return
  documentsLoading.value = true
  documentsError.value = null
  try {
    const res = await ScenariosService.listScenarioDocuments({ path: { scenario_id: id } })
    documents.value = res.data
  } catch (e) {
    documents.value = []
    const err = e as { response?: { data?: { detail?: unknown } }; message?: string }
    const detail = err.response?.data?.detail
    documentsError.value = typeof detail === 'string' ? detail : (err.message ?? '無法載入文件清單')
  } finally {
    documentsLoading.value = false
  }
}

async function handleProcessDocument(documentId: string) {
  processingDocumentId.value = documentId
  processError.value = null
  try {
    await DocumentsService.processDocument({ path: { document_id: documentId } })
    await loadDocuments()
  } catch (err) {
    const e = err as { response?: { data?: { detail?: unknown } }; message?: string }
    const detail = e.response?.data?.detail
    processError.value = typeof detail === 'string' ? detail : (e.message ?? '處理失敗，請稍後再試')
  } finally {
    processingDocumentId.value = null
  }
}

async function handleReprocessDocument(documentId: string) {
  processingDocumentId.value = documentId
  processError.value = null
  try {
    await DocumentsService.reprocessDocument({ path: { document_id: documentId } })
    await loadDocuments()
  } catch (err) {
    const e = err as { response?: { data?: { detail?: unknown } }; message?: string }
    const detail = e.response?.data?.detail
    processError.value =
      typeof detail === 'string' ? detail : (e.message ?? '重新處理失敗，請稍後再試')
  } finally {
    processingDocumentId.value = null
  }
}

const {
  state: scenarioDetail,
  isLoading: isInitialLoading,
  error: bootstrapError,
  execute: bootstrap,
} = useAsyncState(
  async () => {
    const id = scenarioId.value
    if (!id) throw Object.assign(new Error('not_found'), { response: { status: 404 } })

    graph.value = { nodes: [], edges: [] }
    documents.value = []

    const res = await ScenariosService.getScenario({ path: { scenario_id: id } })
    await Promise.all([loadGraph(), loadDocuments()])
    return res.data
  },
  null as ScenarioResponse | null,
  { immediate: true },
)

const pageError = computed<'not_found' | 'load_failed' | null>(() => {
  if (!scenarioId.value) return 'not_found'
  if (!bootstrapError.value) return null
  const status = (bootstrapError.value as { response?: { status?: number } })?.response?.status
  return status === 404 || status === 403 ? 'not_found' : 'load_failed'
})

watch(scenarioId, () => {
  void bootstrap()
})

async function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  const files = input.files
  const id = scenarioId.value
  if (!files?.length || !id) return

  uploadError.value = null
  uploadingFiles.value = Array.from(files).map((f) => ({ name: f.name }))

  try {
    for (const file of Array.from(files)) {
      await ScenariosService.uploadScenarioDocument({ path: { scenario_id: id }, body: { file } })
    }
    await loadDocuments()
    activeTab.value = 'documents'
  } catch (err) {
    const e = err as { response?: { data?: { detail?: unknown } }; message?: string }
    const detail = e.response?.data?.detail
    if (Array.isArray(detail) && detail.length > 0) {
      uploadError.value = detail
        .map((d) => {
          const loc = (d as { loc?: unknown })?.loc
          const msg = (d as { msg?: unknown })?.msg
          return `${Array.isArray(loc) ? loc.join('.') : 'body'}: ${typeof msg === 'string' ? msg : 'invalid'}`
        })
        .join('\n')
    } else {
      uploadError.value =
        typeof detail === 'string' ? detail : (e.message ?? '上傳失敗，請稍後再試')
    }
  } finally {
    uploadingFiles.value = []
    input.value = ''
  }
}

// WebSocket：文件處理完成後刷新文件與圖譜
const ws = useAppWebSocket()
let unsubscribeWs: (() => void) | null = null

onMounted(async () => {
  try {
    await ws.connect()
  } catch {
    // ignore
  }
  unsubscribeWs = ws.onType('documents.process_updated', (payload) => {
    const sid = String(payload.scenario_id ?? '')
    if (!sid || sid !== String(scenarioId.value ?? '')) return
    void loadDocuments()
    const st = String(payload.status ?? '')
    if (st === 'COMPLETED') {
      void loadGraph()
      toast.success('文件處理完成', { description: '知識圖譜已更新。' })
    } else if (st === 'FAILED') {
      const errMsg = typeof payload.error === 'string' ? payload.error : '請重新嘗試處理。'
      toast.error('文件處理失敗', { description: errMsg })
    }
  })
})

onUnmounted(() => {
  unsubscribeWs?.()
})

async function handlePublish() {
  const id = scenarioId.value
  if (!id) return
  isPublishing.value = true
  publishError.value = null
  try {
    const res = await ScenariosService.publishScenario({ path: { scenario_id: id } })
    scenarioDetail.value = res.data
  } catch (e) {
    const detail = (e as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
    publishError.value = typeof detail === 'string' ? detail : '發布失敗，請稍後再試'
  } finally {
    isPublishing.value = false
  }
}

async function handleCreateRoom() {
  const id = scenarioId.value
  if (!id || !scenarioDetail.value) return
  isCreatingRoom.value = true
  try {
    const res = await ScenariosService.createRoom({
      path: { scenario_id: id },
      body: {
        name: scenarioDetail.value.name.trim(),
        description: scenarioDetail.value.description ?? null,
      },
    })
    router.push(`/rooms/${res.data.id}`)
  } finally {
    isCreatingRoom.value = false
  }
}

function openEditDialog() {
  if (!scenarioDetail.value) return
  editName.value = scenarioDetail.value.name
  editSystem.value = scenarioDetail.value.system
  editDescription.value = scenarioDetail.value.description ?? ''
  editError.value = null
  editDialogOpen.value = true
}

whenever(editDialogOpen, (open) => {
  if (open) openEditDialog()
})

async function handleEdit() {
  const id = scenarioId.value
  if (!id) return
  isEditing.value = true
  editError.value = null
  try {
    const res = await ScenariosService.updateScenario({
      path: { scenario_id: id },
      body: {
        name: editName.value.trim() || undefined,
        system: editSystem.value.trim() || undefined,
        description: editDescription.value.trim() || null,
      },
    })
    scenarioDetail.value = res.data
    editDialogOpen.value = false
  } catch (e) {
    const detail = (e as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
    editError.value = typeof detail === 'string' ? detail : '儲存失敗，請稍後再試'
  } finally {
    isEditing.value = false
  }
}
</script>
