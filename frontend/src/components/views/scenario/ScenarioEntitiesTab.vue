<script setup lang="ts">
import { computed, ref } from 'vue'
import { List } from 'lucide-vue-next'
import type { Graph, NodeType } from '@/types/graph'
import { NODE_COLORS, NODE_TYPE_LABELS } from '@/types/graph'
import { Badge } from '@/components/ui/badge'

const props = defineProps<{
  graph: Graph
}>()

const entityFilter = ref('')

const filteredNodes = computed(() =>
  entityFilter.value
    ? props.graph.nodes.filter((n) => n.type === entityFilter.value)
    : props.graph.nodes,
)
</script>

<template>
  <div class="h-full overflow-y-auto">
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
        <div class="flex items-center gap-2 flex-wrap">
          <button
            class="inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border transition-colors"
            :class="
              entityFilter === ''
                ? 'bg-primary text-primary-foreground border-primary'
                : 'border-border text-muted-foreground hover:text-foreground'
            "
            @click="entityFilter = ''"
          >
            全部
          </button>
          <button
            v-for="(label, type) in NODE_TYPE_LABELS"
            :key="type"
            class="inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border transition-colors"
            :class="
              entityFilter === type
                ? 'bg-primary text-primary-foreground border-primary'
                : 'border-border text-muted-foreground hover:text-foreground'
            "
            @click="entityFilter = entityFilter === type ? '' : type"
          >
            <span
              class="w-1.5 h-1.5 rounded-full"
              :style="{ backgroundColor: NODE_COLORS[type as NodeType] }"
            />
            {{ label }}
          </button>
        </div>

        <div class="border rounded-lg overflow-hidden">
          <table class="w-full text-sm">
            <thead>
              <tr class="bg-muted/50 border-b">
                <th class="text-left px-4 py-2.5 text-xs text-muted-foreground font-medium w-28">
                  類型
                </th>
                <th class="text-left px-4 py-2.5 text-xs text-muted-foreground font-medium w-36">
                  名稱
                </th>
                <th class="text-left px-4 py-2.5 text-xs text-muted-foreground font-medium">
                  描述
                </th>
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
                    <span
                      class="w-2 h-2 rounded-full shrink-0"
                      :style="{ backgroundColor: NODE_COLORS[node.type] }"
                    />
                    {{ NODE_TYPE_LABELS[node.type] }}
                  </span>
                </td>
                <td class="px-4 py-3 font-medium">{{ node.label }}</td>
                <td class="px-4 py-3 text-muted-foreground text-xs">
                  {{ node.description }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>
  </div>
</template>
