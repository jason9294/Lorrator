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
      <header class="shrink-0 flex items-center gap-3 px-5 h-13 border-b bg-card/80 backdrop-blur-sm z-30">
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
        </div>

        <!-- Tab 切換器 -->
        <nav class="hidden md:flex items-center gap-1 bg-muted rounded-lg p-1">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-colors"
            :class="activeTab === tab.id
              ? 'bg-background text-foreground shadow-sm'
              : 'text-muted-foreground hover:text-foreground'"
            @click="activeTab = tab.id"
          >
            <component :is="tab.icon" class="size-3.5" />
            {{ tab.label }}
          </button>
        </nav>

        <!-- 行動裝置 Tab 下拉 -->
        <div class="md:hidden ml-auto">
          <select
            v-model="activeTab"
            class="text-xs bg-muted border-0 rounded-md px-2 py-1.5 text-foreground outline-none"
          >
            <option v-for="tab in tabs" :key="tab.id" :value="tab.id">{{ tab.label }}</option>
          </select>
        </div>
      </header>

      <!-- Tab 內容 -->
      <main class="flex-1 min-h-0 overflow-hidden">
        <!-- Tab 1: 劇本知識圖譜 -->
        <div v-show="activeTab === 'graph'" class="h-full flex flex-col min-h-0">
          <div
            v-if="graph.nodes.length === 0"
            class="flex-1 flex flex-col items-center justify-center gap-2 p-8 text-center text-muted-foreground"
          >
            <Network class="size-10 opacity-40" />
            <p class="text-sm font-medium">尚無知識圖譜資料</p>
            <p class="text-xs opacity-80">後端圖譜功能就緒後，將顯示於此。</p>
          </div>
          <KnowledgeGraph
            v-else
            :key="scenarioDetail.id"
            :graph="graph"
            :is-dark="isDark"
          />
        </div>

        <!-- Tab 2: 知識圖譜實體清單 -->
        <div v-show="activeTab === 'entities'" class="h-full overflow-y-auto">
          <div class="max-w-4xl mx-auto p-6 space-y-4">
            <div class="flex items-center justify-between">
              <h3 class="font-semibold">實體清單</h3>
              <Badge variant="secondary">{{ graph.nodes.length }} 個實體</Badge>
            </div>

            <div
              v-if="graph.nodes.length === 0"
              class="flex flex-col items-center justify-center py-16 text-center border rounded-lg border-dashed text-muted-foreground"
            >
              <List class="size-10 opacity-40 mb-3" />
              <p class="text-sm font-medium">尚無實體</p>
            </div>

            <template v-else>
              <!-- 篩選 -->
              <div class="flex items-center gap-2 flex-wrap">
                <button
                  class="inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border transition-colors"
                  :class="entityFilter === '' ? 'bg-primary text-primary-foreground border-primary' : 'border-border text-muted-foreground hover:text-foreground'"
                  @click="entityFilter = ''"
                >
                  全部
                </button>
                <button
                  v-for="(label, type) in NODE_TYPE_LABELS"
                  :key="type"
                  class="inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border transition-colors"
                  :class="entityFilter === type ? 'bg-primary text-primary-foreground border-primary' : 'border-border text-muted-foreground hover:text-foreground'"
                  @click="entityFilter = entityFilter === type ? '' : type"
                >
                  <span class="w-1.5 h-1.5 rounded-full" :style="{ backgroundColor: NODE_COLORS[type as NodeType] }" />
                  {{ label }}
                </button>
              </div>

              <!-- 實體表格 -->
              <div class="border rounded-lg overflow-hidden">
                <table class="w-full text-sm">
                  <thead>
                    <tr class="bg-muted/50 border-b">
                      <th class="text-left px-4 py-2.5 text-xs text-muted-foreground font-medium w-28">類型</th>
                      <th class="text-left px-4 py-2.5 text-xs text-muted-foreground font-medium w-36">名稱</th>
                      <th class="text-left px-4 py-2.5 text-xs text-muted-foreground font-medium">描述</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="node in filteredNodes"
                      :key="node.id"
                      class="border-b last:border-0 hover:bg-muted/30 transition-colors"
                    >
                      <td class="px-4 py-3">
                        <span class="inline-flex items-center gap-1.5 text-xs">
                          <span class="w-2 h-2 rounded-full shrink-0" :style="{ backgroundColor: NODE_COLORS[node.type] }" />
                          {{ NODE_TYPE_LABELS[node.type] }}
                        </span>
                      </td>
                      <td class="px-4 py-3 font-medium">{{ node.label }}</td>
                      <td class="px-4 py-3 text-muted-foreground text-xs">{{ node.description }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </template>
          </div>
        </div>

        <!-- Tab 3: 文件清單 -->
        <div v-show="activeTab === 'documents'" class="h-full overflow-y-auto">
          <div class="max-w-2xl mx-auto p-6 space-y-4">
            <div class="flex items-center justify-between">
              <h3 class="font-semibold">文件清單</h3>
              <div class="flex items-center gap-2">
                <Badge variant="secondary">{{ documents.length }} 份文件</Badge>
                <Button size="sm" class="gap-1.5" :disabled="documentsLoading" @click="triggerUpload">
                  <Upload class="size-3.5" />
                  上傳文件
                </Button>
                <input
                  ref="fileInputRef"
                  type="file"
                  class="hidden"
                  multiple
                  accept=".pdf,.txt,.md,.docx"
                  @change="onFileChange"
                />
              </div>
            </div>

            <p v-if="documentsError" class="text-sm text-destructive whitespace-pre-wrap">
              {{ documentsError }}
            </p>
            <p v-if="uploadError" class="text-sm text-destructive whitespace-pre-wrap">
              {{ uploadError }}
            </p>

            <!-- 上傳進度 -->
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

            <div v-if="documentsLoading" class="flex items-center gap-2 text-sm text-muted-foreground py-4">
              <Spinner class="size-4" />
              載入文件清單中…
            </div>

            <!-- 文件清單 -->
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
                  </p>
                </div>
              </div>
            </div>

            <!-- 空狀態 -->
            <div
              v-else-if="uploadingFiles.length === 0"
              class="flex flex-col items-center justify-center py-16 text-center border rounded-lg border-dashed"
            >
              <FileText class="size-10 text-muted-foreground/40 mb-3" />
              <p class="text-sm font-medium text-muted-foreground">尚無文件</p>
              <p class="text-xs text-muted-foreground/60 mt-1">點擊「上傳文件」新增劇本相關文件</p>
            </div>
          </div>
        </div>
      </main>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, FileText, Network, List, Upload } from 'lucide-vue-next'
import type { NodeType } from '@/types/graph'
import { NODE_COLORS, NODE_TYPE_LABELS } from '@/types/graph'
import type { Graph } from '@/types/graph'
import { useColorMode } from '@/composables/useColorMode'
import KnowledgeGraph from '@/components/graph/KnowledgeGraph.vue'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Spinner } from '@/components/ui/spinner'
import { ScenariosService, type DocumentResponse, type ScenarioResponse } from '@/services'

const route = useRoute()
const { isDark } = useColorMode()

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

const entityFilter = ref('')

const isInitialLoading = ref(true)
const pageError = ref<'not_found' | 'load_failed' | null>(null)
const scenarioDetail = ref<ScenarioResponse | null>(null)

const graph = ref<Graph>({ nodes: [], edges: [] })

const documents = ref<DocumentResponse[]>([])
const documentsLoading = ref(false)
const documentsError = ref<string | null>(null)

const fileInputRef = ref<HTMLInputElement | null>(null)
const uploadingFiles = ref<{ name: string }[]>([])
const uploadError = ref<string | null>(null)

const filteredNodes = computed(() =>
  entityFilter.value
    ? graph.value.nodes.filter((n) => n.type === entityFilter.value)
    : graph.value.nodes,
)

function normalizeGraphPayload(data: unknown): Graph {
  if (!data || typeof data !== 'object') return { nodes: [], edges: [] }
  const o = data as Record<string, unknown>
  const nodesRaw = o.nodes
  const edgesRaw = o.edges
  if (!Array.isArray(nodesRaw) || !Array.isArray(edgesRaw)) return { nodes: [], edges: [] }

  const nodes = nodesRaw
    .map((n) => {
      if (!n || typeof n !== 'object') return null
      const x = n as Record<string, unknown>
      const id = typeof x.id === 'string' ? x.id : null
      const type = typeof x.type === 'string' ? x.type : null
      const label = typeof x.label === 'string' ? x.label : null
      const description = typeof x.description === 'string' ? x.description : ''
      if (!id || !type || !label) return null
      if (!NODE_TYPE_LABELS[type as NodeType]) return null
      return {
        id,
        type: type as NodeType,
        label,
        description,
      }
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
  const id = scenarioId.value
  if (!id) return
  try {
    const res = await ScenariosService.getScenarioGraph({
      path: { scenario_id: id },
    })
    graph.value = normalizeGraphPayload(res.data)
  } catch {
    graph.value = { nodes: [], edges: [] }
  }
}

async function loadDocuments() {
  const id = scenarioId.value
  if (!id) return
  documentsLoading.value = true
  documentsError.value = null
  try {
    const res = await ScenariosService.listScenarioDocuments({
      path: { scenario_id: id },
    })
    documents.value = res.data
  } catch (e) {
    documents.value = []
    const err = e as { response?: { data?: { detail?: unknown } }; message?: string }
    const detail = err.response?.data?.detail
    if (typeof detail === 'string') {
      documentsError.value = detail
    } else {
      documentsError.value = err.message ?? '無法載入文件清單'
    }
  } finally {
    documentsLoading.value = false
  }
}

async function bootstrap() {
  const id = scenarioId.value
  if (!id) {
    pageError.value = 'not_found'
    isInitialLoading.value = false
    return
  }

  isInitialLoading.value = true
  pageError.value = null
  scenarioDetail.value = null
  graph.value = { nodes: [], edges: [] }
  documents.value = []
  documentsError.value = null

  try {
    const listRes = await ScenariosService.listScenarios()
    const found = listRes.data.find((s) => s.id === id)
    if (!found) {
      pageError.value = 'not_found'
      return
    }
    scenarioDetail.value = found
    await Promise.all([loadGraph(), loadDocuments()])
  } catch {
    pageError.value = 'load_failed'
  } finally {
    isInitialLoading.value = false
  }
}

onMounted(bootstrap)

watch(scenarioId, () => {
  void bootstrap()
})

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
  if (ct) return `${ct} · ${when}`
  return when
}

function triggerUpload() {
  fileInputRef.value?.click()
}

async function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  const files = input.files
  const id = scenarioId.value
  if (!files?.length || !id) return

  uploadError.value = null
  uploadingFiles.value = Array.from(files).map((f) => ({ name: f.name }))

  try {
    for (const file of Array.from(files)) {
      await ScenariosService.uploadScenarioDocument({
        path: { scenario_id: id },
        body: { file },
      })
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
          const locText = Array.isArray(loc) ? loc.join('.') : 'body'
          const msgText = typeof msg === 'string' ? msg : 'invalid'
          return `${locText}: ${msgText}`
        })
        .join('\n')
    } else if (typeof detail === 'string') {
      uploadError.value = detail
    } else {
      uploadError.value = e.message ?? '上傳失敗，請稍後再試'
    }
  } finally {
    uploadingFiles.value = []
    input.value = ''
  }
}
</script>
