<template>
  <div class="h-screen flex flex-col bg-background text-foreground overflow-hidden">

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
          :style="{ backgroundColor: scenario.color }"
        >
          {{ scenario.title.charAt(0) }}
        </div>
        <div class="flex flex-col leading-none min-w-0">
          <span class="text-sm font-semibold truncate">{{ scenario.title }}</span>
          <span class="text-[10px] text-muted-foreground">{{ scenario.system }}</span>
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
      <div v-show="activeTab === 'graph'" class="h-full">
        <KnowledgeGraph
          :graph="scenario.graph"
          :is-dark="isDark"
        />
      </div>

      <!-- Tab 2: 知識圖譜實體清單 -->
      <div v-show="activeTab === 'entities'" class="h-full overflow-y-auto">
        <div class="max-w-4xl mx-auto p-6 space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="font-semibold">實體清單</h3>
            <Badge variant="secondary">{{ scenario.graph.nodes.length }} 個實體</Badge>
          </div>

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
        </div>
      </div>

      <!-- Tab 3: 文件清單 -->
      <div v-show="activeTab === 'documents'" class="h-full overflow-y-auto">
        <div class="max-w-2xl mx-auto p-6 space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="font-semibold">文件清單</h3>
            <div class="flex items-center gap-2">
              <Badge variant="secondary">{{ documents.length }} 份文件</Badge>
              <Button size="sm" class="gap-1.5" @click="triggerUpload">
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

          <!-- 文件清單 -->
          <div v-if="documents.length > 0" class="border rounded-lg overflow-hidden">
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
                <p class="text-sm font-medium truncate">{{ doc.name }}</p>
                <p class="text-xs text-muted-foreground">{{ doc.size }} · {{ doc.uploadedAt }}</p>
              </div>
              <Button
                variant="ghost"
                size="icon-sm"
                class="text-muted-foreground shrink-0"
                @click="deleteDocument(doc.id)"
              >
                <Trash2 class="size-3.5" />
              </Button>
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

  </div>
</template>

<script setup lang="ts">
import { computed, ref, shallowRef } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, FileText, Network, List, Trash2, Upload } from 'lucide-vue-next'
import type { NodeType } from '@/types/graph'
import { NODE_COLORS, NODE_TYPE_LABELS } from '@/types/graph'
import { useColorMode } from '@/composables/useColorMode'
import KnowledgeGraph from '@/components/graph/KnowledgeGraph.vue'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Spinner } from '@/components/ui/spinner'

const route = useRoute()
const { isDark } = useColorMode()

const tabs = [
  { id: 'graph', label: '知識圖譜', icon: Network },
  { id: 'entities', label: '實體清單', icon: List },
  { id: 'documents', label: '文件清單', icon: FileText },
]
const activeTab = ref('graph')

const entityFilter = ref('')

// ─── Mock 劇本資料 ─────────────────────────────────────────────────────────────
const scenariosMap: Record<string, typeof scenario.value> = {
  s1: {
    id: 's1',
    title: '克蘇魯的呼喚',
    system: 'COC 7e',
    color: '#7c3aed',
    graph: {
      nodes: [
        { id: 'c1', type: 'character', label: '偵探 史密斯', description: '主角調查員，曾任警探，對超自然現象持懷疑態度。' },
        { id: 'c2', type: 'character', label: '教授 威廉斯', description: '米斯卡托尼克大學考古系教授，失蹤前留下大量研究筆記。' },
        { id: 'c3', type: 'character', label: '瑪格麗特', description: '威廉斯教授的助手，對某些事情諱莫如深。' },
        { id: 'l1', type: 'location', label: '阿卡姆鎮', description: '故事發生的核心地點，位於麻薩諸塞州。' },
        { id: 'l2', type: 'location', label: '米斯卡托尼克大學', description: '以龐大的禁忌書籍收藏聞名。' },
        { id: 'i1', type: 'item', label: '研究筆記', description: '威廉斯教授失蹤前留下的手稿。' },
        { id: 'o1', type: 'organization', label: '星際智慧教派', description: '在阿卡姆地下活動的神秘教派。' },
        { id: 'e1', type: 'event', label: '教授失蹤事件', description: '三週前，威廉斯教授在考古調查後失聯。' },
        { id: 'k1', type: 'concept', label: '克蘇魯神話', description: '描述超越人類理解的古老神靈與宇宙體系。' },
      ],
      edges: [
        { id: 'e1', source: 'c1', target: 'l1', type: '調查', directed: true },
        { id: 'e2', source: 'c2', target: 'l2', type: '任職於', directed: false },
        { id: 'e3', source: 'c2', target: 'i1', type: '撰寫', directed: true },
        { id: 'e4', source: 'c3', target: 'c2', type: '協助', directed: true },
        { id: 'e5', source: 'o1', target: 'e1', type: '涉嫌', directed: false },
        { id: 'e6', source: 'e1', target: 'c2', type: '當事人', directed: false },
        { id: 'e7', source: 'i1', target: 'k1', type: '記載', directed: true },
      ],
    },
  },
}

const scenario = shallowRef(
  scenariosMap[route.params.scenario_id as string] ?? {
    id: String(route.params.scenario_id),
    title: '未知劇本',
    system: '—',
    color: '#6b7280',
    graph: { nodes: [], edges: [] },
  }
)

const filteredNodes = computed(() =>
  entityFilter.value
    ? scenario.value.graph.nodes.filter((n) => n.type === entityFilter.value)
    : scenario.value.graph.nodes
)

// ─── 文件 ──────────────────────────────────────────────────────────────────────
const fileInputRef = ref<HTMLInputElement | null>(null)
const uploadingFiles = ref<{ name: string }[]>([])
const documents = ref([
  { id: 'd1', name: '克蘇魯的呼喚 - 規則手冊.pdf', size: '12.4 MB', uploadedAt: '2026/04/10' },
  { id: 'd2', name: '阿卡姆鎮地圖.png', size: '3.2 MB', uploadedAt: '2026/04/11' },
])

function triggerUpload() {
  fileInputRef.value?.click()
}

async function onFileChange(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (!files) return
  const toUpload = Array.from(files).map((f) => ({ name: f.name }))
  uploadingFiles.value = toUpload

  // TODO: 替換為實際上傳 API
  await new Promise((resolve) => setTimeout(resolve, 1500))

  for (const f of toUpload) {
    documents.value.unshift({
      id: `d-${Date.now()}-${f.name}`,
      name: f.name,
      size: '—',
      uploadedAt: new Date().toLocaleDateString('zh-TW'),
    })
  }
  uploadingFiles.value = []
  ;(e.target as HTMLInputElement).value = ''
}

function deleteDocument(id: string) {
  documents.value = documents.value.filter((d) => d.id !== id)
}
</script>
