<template>
  <div class="h-screen flex flex-col bg-background text-foreground overflow-hidden">

    <!-- ── 頂部導覽列 ──────────────────────────────────────────────────────── -->
    <header class="shrink-0 flex items-center gap-3 px-5 h-13 border-b bg-card/80 backdrop-blur-sm z-30">

      <!-- Logo + 標題 -->
      <div class="flex items-center gap-2.5">
        <div class="w-7 h-7 rounded-lg bg-linear-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-sm shrink-0">
          <svg class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26C17.81 13.47 19 11.38 19 9c0-3.87-3.13-7-7-7zm0 12c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/>
          </svg>
        </div>
        <div class="flex flex-col leading-none">
          <span class="text-sm font-semibold">知識圖譜</span>
          <span class="text-[10px] text-muted-foreground">克蘇魯的呼喚 · COC</span>
        </div>
      </div>

      <div class="w-px h-5 bg-border mx-1 shrink-0" />

      <!-- 統計 Pills -->
      <div class="flex items-center gap-2 shrink-0">
        <span class="inline-flex items-center gap-1.5 text-xs text-muted-foreground bg-muted px-2.5 py-1 rounded-full">
          <span class="w-1.5 h-1.5 rounded-full bg-primary" />
          {{ visibleNodeCount }} / {{ graph.nodes.length }} 節點
        </span>
        <span class="inline-flex items-center gap-1.5 text-xs text-muted-foreground bg-muted px-2.5 py-1 rounded-full">
          <span class="w-1.5 h-1.5 rounded-full bg-primary/50" />
          {{ graph.edges.length }} 關係
        </span>
      </div>

      <div class="w-px h-5 bg-border mx-1 shrink-0" />

      <!-- 節點類型篩選 ToggleGroup -->
      <div class="hidden lg:flex items-center">
        <ToggleGroup
          type="multiple"
          variant="outline"
          :model-value="visibleTypes"
          class="gap-1"
          @update:model-value="onVisibleTypesChange"
        >
          <ToggleGroupItem
            v-for="(label, type) in NODE_TYPE_LABELS"
            :key="type"
            :value="type"
            class="h-7 px-2.5 text-xs gap-1.5"
          >
            <span
              class="inline-block size-2 rounded-full shrink-0"
              :style="{ backgroundColor: NODE_COLORS[type as NodeType] }"
            />
            {{ label }}
          </ToggleGroupItem>
        </ToggleGroup>
      </div>

      <!-- 右側工具 -->
      <div class="ml-auto flex items-center gap-2 shrink-0">
        <!-- 搜尋按鈕 -->
        <Button
          variant="outline"
          size="sm"
          class="gap-2 text-muted-foreground hidden sm:inline-flex"
          @click="searchOpen = true"
        >
          <Search class="size-3.5" />
          <span class="text-xs">搜尋節點</span>
          <Kbd class="ml-1">
            <KbdGroup>
              <span>⌘K</span>
            </KbdGroup>
          </Kbd>
        </Button>
        <Button
          variant="outline"
          size="icon-sm"
          class="sm:hidden"
          @click="searchOpen = true"
        >
          <Search class="size-3.5" />
        </Button>

        <!-- 暗色 / 亮色切換 -->
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
    </header>

    <!-- ── 主體 ────────────────────────────────────────────────────────────── -->
    <main class="flex-1 p-4 min-h-0">
      <KnowledgeGraph
        ref="graphRef"
        :graph="graph"
        :is-dark="isDark"
        :hidden-types="hiddenTypes"
        @node-updated="onNodeUpdated"
      />
    </main>

    <!-- ── Command 搜尋 Palette ─────────────────────────────────────────── -->
    <CommandDialog v-model:open="searchOpen" title="搜尋節點" description="輸入節點名稱進行搜尋">
      <CommandInput placeholder="搜尋節點名稱..." />
      <CommandList>
        <CommandEmpty>找不到符合的節點</CommandEmpty>
        <CommandGroup
          v-for="(label, type) in NODE_TYPE_LABELS"
          :key="type"
          :heading="label"
        >
          <CommandItem
            v-for="node in nodesByType[type as NodeType]"
            :key="node.id"
            :value="`${node.label} ${node.description}`"
            class="gap-2.5"
            @select="onSearchSelect(node.id)"
          >
            <span
              class="inline-block size-2.5 rounded-full shrink-0"
              :style="{ backgroundColor: NODE_COLORS[type as NodeType] }"
            />
            <span class="font-medium">{{ node.label }}</span>
            <span class="text-muted-foreground text-xs truncate">{{ node.description }}</span>
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>

  </div>
</template>

<script setup lang="ts">
import type { Graph, GraphNode, NodeType } from '@/types/graph'
import { NODE_COLORS, NODE_TYPE_LABELS } from '@/types/graph'
import KnowledgeGraph from '@/components/graph/KnowledgeGraph.vue'
import { useColorMode } from '@/composables/useColorMode'
import { Moon, Sun, Search } from 'lucide-vue-next'
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Kbd, KbdGroup } from '@/components/ui/kbd'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command'

// ─── 主題 ─────────────────────────────────────────────────────────────────────
const { isDark, toggle } = useColorMode()

// ─── Graph Ref（用於 focusNode）─────────────────────────────────────────────
const graphRef = ref<InstanceType<typeof KnowledgeGraph> | null>(null)

// ─── 搜尋 Palette ─────────────────────────────────────────────────────────────
const searchOpen = ref(false)

function onSearchSelect(nodeId: string) {
  searchOpen.value = false
  setTimeout(() => graphRef.value?.focusNode(nodeId), 100)
}

// Cmd+K 快捷鍵
function onKeydown(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    searchOpen.value = !searchOpen.value
  }
}
onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))

// ─── 節點類型篩選 ─────────────────────────────────────────────────────────────
const allTypes = Object.keys(NODE_TYPE_LABELS) as NodeType[]
const visibleTypes = ref<string[]>([...allTypes])

const hiddenTypes = computed<NodeType[]>(() =>
  allTypes.filter((t) => !visibleTypes.value.includes(t)),
)

function onVisibleTypesChange(val: unknown) {
  const arr = Array.isArray(val) ? (val as string[]) : []
  visibleTypes.value = arr.length ? arr : [...allTypes]
}

const visibleNodeCount = computed(
  () => graph.value.nodes.filter((n) => !hiddenTypes.value.includes(n.type)).length,
)

// 按類型分組（Command palette 用）
const nodesByType = computed(() => {
  const map: Partial<Record<NodeType, GraphNode[]>> = {}
  for (const node of graph.value.nodes) {
    if (!map[node.type]) map[node.type] = []
    map[node.type]!.push(node)
  }
  return map
})

// ─── 示範資料：COC「失落的藝術家」劇本片段 ─────────────────────────────────────
const graph = ref<Graph>({
  nodes: [
    {
      id: 'c1',
      type: 'character',
      label: '偵探 史密斯',
      description: '主角調查員，曾任警探，對超自然現象持懷疑態度。擁有高尚的正直感，卻在調查阿卡姆事件後開始動搖。',
    },
    {
      id: 'c2',
      type: 'character',
      label: '教授 威廉斯',
      description: '米斯卡托尼克大學考古系教授，失蹤前留下大量研究筆記，據說已接觸到某件「超乎理解之物」。',
    },
    {
      id: 'c3',
      type: 'character',
      label: '瑪格麗特',
      description: '威廉斯教授的助手，性格謹慎內向。調查員發現她似乎對某些事情諱莫如深。',
    },
    {
      id: 'c4',
      type: 'character',
      label: '神秘老人',
      description: '常在碼頭一帶出沒的怪異老人，能說出調查員不可能知道的事，身份不明。',
    },
    {
      id: 'l1',
      type: 'location',
      label: '阿卡姆鎮',
      description: '故事發生的核心地點，位於麻薩諸塞州。此地長年瀰漫著超自然傳說，居民習以為常。',
    },
    {
      id: 'l2',
      type: 'location',
      label: '米斯卡托尼克大學',
      description: '以龐大的禁忌書籍收藏聞名，其圖書館地下室封存著數卷《死靈之書》副本。',
    },
    {
      id: 'l3',
      type: 'location',
      label: '廢棄倉庫',
      description: '碼頭附近的廢棄倉庫，牆上刻有奇異符文。據說是某個祕密儀式的場所。',
    },
    {
      id: 'i1',
      type: 'item',
      label: '研究筆記',
      description: '威廉斯教授失蹤前留下的手稿，記載著他對古代文明與異世界存在的研究推論，部分頁面被撕去。',
    },
    {
      id: 'i2',
      type: 'item',
      label: '石板碎片',
      description: '在廢棄倉庫中發現的古老石板碎片，上面的文字與任何已知語言都不相符。',
    },
    {
      id: 'o1',
      type: 'organization',
      label: '星際智慧教派',
      description: '在阿卡姆地下活動的神秘教派，崇拜來自外太空的古神實體，疑似與多起失蹤事件有關。',
    },
    {
      id: 'e1',
      type: 'event',
      label: '教授失蹤事件',
      description: '三週前，威廉斯教授在完成一次考古實地調查後失聯。警方結案為自願失蹤，但助手瑪格麗特不信。',
    },
    {
      id: 'k1',
      type: 'concept',
      label: '克蘇魯神話',
      description: '一套描述超越人類理解的古老神靈與宇宙體系的神話框架，閱讀相關典籍可能導致理智崩潰。',
    },
  ],
  edges: [
    { id: 'e-c1-l1',  source: 'c1', target: 'l1', type: '調查',    directed: true  },
    { id: 'e-c1-c2',  source: 'c1', target: 'c2', type: '尋找',    directed: true  },
    { id: 'e-c2-l2',  source: 'c2', target: 'l2', type: '任職於',  directed: false },
    { id: 'e-c2-i1',  source: 'c2', target: 'i1', type: '撰寫',    directed: true  },
    { id: 'e-c3-c2',  source: 'c3', target: 'c2', type: '協助',    directed: true  },
    { id: 'e-c3-i1',  source: 'c3', target: 'i1', type: '持有',    directed: false },
    { id: 'e-c4-l3',  source: 'c4', target: 'l3', type: '出沒',    directed: false },
    { id: 'e-i1-k1',  source: 'i1', target: 'k1', type: '記載',    directed: true  },
    { id: 'e-i2-l3',  source: 'i2', target: 'l3', type: '發現於',  directed: false },
    { id: 'e-i2-k1',  source: 'i2', target: 'k1', type: '關聯',    directed: false },
    { id: 'e-o1-e1',  source: 'o1', target: 'e1', type: '涉嫌',    directed: false },
    { id: 'e-o1-l3',  source: 'o1', target: 'l3', type: '使用',    directed: true  },
    { id: 'e-e1-c2',  source: 'e1', target: 'c2', type: '當事人',  directed: false },
    { id: 'e-c1-e1',  source: 'c1', target: 'e1', type: '調查',    directed: true  },
    { id: 'e-l2-k1',  source: 'l2', target: 'k1', type: '收藏典籍', directed: true },
  ],
})

function onNodeUpdated(node: GraphNode) {
  const idx = graph.value.nodes.findIndex((n) => n.id === node.id)
  if (idx !== -1) {
    graph.value.nodes[idx] = { ...node }
  }
}
</script>

<style scoped>
.icon-swap-enter-active,
.icon-swap-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.icon-swap-enter-from {
  opacity: 0;
  transform: rotate(-30deg) scale(0.7);
}
.icon-swap-leave-to {
  opacity: 0;
  transform: rotate(30deg) scale(0.7);
}
</style>
