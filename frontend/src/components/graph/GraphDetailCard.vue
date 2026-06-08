<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { GraphNode, GraphSelection, NodeType } from '@/types/graph'
import { NODE_TYPE_LABELS, NODE_COLORS } from '@/types/graph'

// Icons
import {
  X,
  Save,
  RotateCcw,
  Tag,
  Type,
  AlignLeft,
  ArrowRight,
  ArrowLeftRight,
  Link2,
} from 'lucide-vue-next'

// low-level components
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

// Props / Emits
const props = defineProps<{
  selection: GraphSelection | null
}>()

const emit = defineEmits<{
  (e: 'update', node: GraphNode): void
  (e: 'close'): void
}>()

const draft = ref<GraphNode | null>(null)

// 是否 dirty
const isDirty = ref(false)

const isNode = computed(() => props.selection?.kind === 'node')
const isEdge = computed(() => props.selection?.kind === 'edge')
const edge = computed(() => (props.selection?.kind === 'edge' ? props.selection.data : null))

watch(
  () => props.selection,
  (sel) => {
    draft.value = sel?.kind === 'node' ? { ...sel.data } : null
    isDirty.value = false
  },
  { immediate: true },
)

watch(
  draft,
  (newVal) => {
    if (!newVal || props.selection?.kind !== 'node') return
    const node = props.selection.data
    isDirty.value =
      newVal.label !== node.label ||
      newVal.type !== node.type ||
      newVal.description !== node.description
  },
  { deep: true },
)

function save() {
  if (!draft.value) return
  emit('update', { ...draft.value })
  isDirty.value = false
}

function reset() {
  if (props.selection?.kind !== 'node') return
  draft.value = { ...props.selection.data }
  isDirty.value = false
}

function nodeColor(type: NodeType): string {
  return NODE_COLORS[type] ?? '#6b7280'
}
</script>

<template>
  <Transition name="slide-right">
    <div
      v-if="selection"
      class="absolute right-0 top-0 bottom-0 w-72 flex flex-col z-20 pointer-events-auto"
    >
      <div
        class="flex-1 flex flex-col overflow-hidden bg-card/95 backdrop-blur-md border-l shadow-2xl"
      >
        <!-- Node header -->
        <div v-if="isNode && draft" class="shrink-0 px-4 pt-4 pb-3 border-b">
          <div class="flex items-start gap-2">
            <div class="flex flex-col gap-2 flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span
                  class="inline-block w-2.5 h-2.5 rounded-full shrink-0 mt-0.5"
                  :style="{ backgroundColor: nodeColor(draft.type) }"
                />
                <span class="text-xs font-medium text-muted-foreground">
                  {{ NODE_TYPE_LABELS[draft.type] ?? draft.type }}
                </span>
              </div>
              <h3 class="text-sm font-semibold leading-tight truncate">{{ draft.label }}</h3>
            </div>
            <!-- 關閉按鈕 -->
            <Button
              variant="ghost"
              size="icon-sm"
              class="shrink-0 text-muted-foreground"
              @click="emit('close')"
            >
              <X class="size-3.5" />
            </Button>
          </div>
        </div>

        <!-- Edge header -->
        <div v-else-if="isEdge && edge" class="shrink-0 px-4 pt-4 pb-3 border-b">
          <div class="flex items-start gap-2">
            <div class="flex flex-col gap-2 flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <Link2 class="size-3 text-muted-foreground shrink-0" />
                <span class="text-xs font-medium text-muted-foreground">關係</span>
              </div>
              <h3 class="text-sm font-semibold leading-tight truncate">
                {{ edge.type || '未命名關係' }}
              </h3>
            </div>
            <Button
              variant="ghost"
              size="icon-sm"
              class="shrink-0 text-muted-foreground"
              @click="emit('close')"
            >
              <X class="size-3.5" />
            </Button>
          </div>
        </div>

        <!-- Dirty banner (node only) -->
        <Transition name="fade">
          <div
            v-if="isNode && isDirty"
            class="shrink-0 flex items-center gap-2 px-4 py-2 bg-amber-500/10 border-b border-amber-500/20 text-xs text-amber-600 dark:text-amber-400"
          >
            <span class="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
            尚未儲存的修改
          </div>
        </Transition>

        <!-- Node form -->
        <div v-if="isNode && draft" class="flex-1 overflow-y-auto px-4 py-4 space-y-5">
          <div class="space-y-1.5">
            <Label class="text-xs text-muted-foreground">
              <Type class="size-3" />
              名稱
            </Label>
            <Input v-model="draft.label" placeholder="節點名稱" />
          </div>

          <div class="space-y-1.5">
            <Label class="text-xs text-muted-foreground">
              <Tag class="size-3" />
              類型
            </Label>
            <Select v-model="draft.type">
              <SelectTrigger class="w-full">
                <SelectValue placeholder="選擇類型" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="(typeLabel, val) in NODE_TYPE_LABELS" :key="val" :value="val">
                  <span class="flex items-center gap-2">
                    <span
                      class="inline-block size-2 rounded-full shrink-0"
                      :style="{ backgroundColor: nodeColor(val as NodeType) }"
                    />
                    {{ typeLabel }}
                  </span>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="space-y-1.5">
            <Label class="text-xs text-muted-foreground">
              <AlignLeft class="size-3" />
              描述
            </Label>
            <Textarea
              v-model="draft.description"
              placeholder="輸入節點描述..."
              class="resize-none min-h-32"
            />
          </div>
        </div>

        <!-- Edge details (read-only) -->
        <div v-else-if="isEdge && edge" class="flex-1 overflow-y-auto px-4 py-4 space-y-5">
          <div class="space-y-1.5">
            <Label class="text-xs text-muted-foreground">
              <Tag class="size-3" />
              關係類型
            </Label>
            <p class="text-sm px-3 py-2 rounded-md bg-muted/50 border">
              {{ edge.type || '—' }}
            </p>
          </div>

          <div class="space-y-1.5">
            <Label class="text-xs text-muted-foreground">
              <ArrowRight class="size-3" />
              來源節點
            </Label>
            <p class="text-sm px-3 py-2 rounded-md bg-muted/50 border truncate">
              {{ edge.sourceLabel }}
            </p>
          </div>

          <div class="space-y-1.5">
            <Label class="text-xs text-muted-foreground">
              <ArrowRight class="size-3" />
              目標節點
            </Label>
            <p class="text-sm px-3 py-2 rounded-md bg-muted/50 border truncate">
              {{ edge.targetLabel }}
            </p>
          </div>

          <div class="space-y-1.5">
            <Label class="text-xs text-muted-foreground">
              <ArrowLeftRight class="size-3" />
              方向
            </Label>
            <p class="text-sm px-3 py-2 rounded-md bg-muted/50 border">
              {{ edge.directed ? '有向' : '無向' }}
            </p>
          </div>
        </div>

        <!-- Node footer -->
        <div v-if="isNode && draft" class="shrink-0 flex gap-2 px-4 py-3 border-t bg-muted/30">
          <Button class="flex-1" size="sm" :disabled="!isDirty" @click="save">
            <Save class="size-3.5" />
            儲存
          </Button>
          <Button variant="outline" size="sm" :disabled="!isDirty" @click="reset">
            <RotateCcw class="size-3.5" />
            還原
          </Button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.slide-right-enter-active,
.slide-right-leave-active {
  transition:
    transform 0.22s cubic-bezier(0.4, 0, 0.2, 1),
    opacity 0.22s ease;
}
.slide-right-enter-from,
.slide-right-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition:
    opacity 0.2s ease,
    max-height 0.2s ease;
  overflow: hidden;
  max-height: 40px;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  max-height: 0;
}
</style>
