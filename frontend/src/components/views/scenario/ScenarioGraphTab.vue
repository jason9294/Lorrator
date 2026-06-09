<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { Filter, Network } from 'lucide-vue-next'

import type { Graph, NodeType } from '@/types/graph'
import { getNodeTypeColor, getNodeTypeLabel } from '@/types/graph'

import KnowledgeGraph from '@/components/graph/KnowledgeGraph.vue'

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

const ALL_TYPES = '__all__'

const props = defineProps<{
  graph: Graph
  scenarioId: string
  isDark: boolean
}>()

const selectedType = ref<string>(ALL_TYPES)

const typeOptions = computed(() => {
  const counts = new Map<NodeType, number>()
  for (const node of props.graph.nodes) {
    counts.set(node.type, (counts.get(node.type) ?? 0) + 1)
  }
  return [...counts.entries()]
    .sort(([a], [b]) => getNodeTypeLabel(a).localeCompare(getNodeTypeLabel(b), 'zh-TW'))
    .map(([type, count]) => ({
      type,
      label: `${getNodeTypeLabel(type)} (${count})`,
    }))
})

const highlightType = computed<NodeType | null>(() =>
  selectedType.value === ALL_TYPES ? null : (selectedType.value as NodeType),
)

watch(
  () => props.scenarioId,
  () => {
    selectedType.value = ALL_TYPES
  },
)
</script>

<template>
  <div class="h-full flex flex-col min-h-0">
    <div
      v-if="graph.nodes.length === 0"
      class="flex-1 flex flex-col items-center justify-center gap-2 p-8 text-center text-muted-foreground"
    >
      <Network class="size-10 opacity-40" />
      <p class="text-sm font-medium">尚無知識圖譜資料</p>
      <p class="text-xs opacity-80">後端圖譜功能就緒後，將顯示於此。</p>
    </div>
    <template v-else>
      <div class="shrink-0 flex items-center gap-2 px-4 py-2 border-b bg-muted/30">
        <Filter class="size-3.5 text-muted-foreground shrink-0" />
        <span class="text-xs text-muted-foreground shrink-0">節點類型</span>
        <Select v-model="selectedType">
          <SelectTrigger class="h-8 w-52 text-xs">
            <SelectValue placeholder="全部類型" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem :value="ALL_TYPES">全部類型</SelectItem>
            <SelectItem v-for="opt in typeOptions" :key="opt.type" :value="opt.type">
              <span class="flex items-center gap-2">
                <span
                  class="inline-block size-2 rounded-full shrink-0"
                  :style="{ backgroundColor: getNodeTypeColor(opt.type) }"
                />
                {{ opt.label }}
              </span>
            </SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div class="flex-1 min-h-0">
        <KnowledgeGraph
          :key="scenarioId"
          :graph="graph"
          :is-dark="isDark"
          :highlight-type="highlightType"
        />
      </div>
    </template>
  </div>
</template>
