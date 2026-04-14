<script setup lang="ts">
import type { GraphNode, NodeType } from '@/types/graph'
import { NODE_TYPE_LABELS, NODE_COLORS } from '@/types/graph'
import { ref, watch } from 'vue'
import { X, Save, RotateCcw, Tag, Type, AlignLeft } from 'lucide-vue-next'
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

// ─── Props / Emits ────────────────────────────────────────────────────────────
const props = defineProps<{
  node: GraphNode | null
}>()

const emit = defineEmits<{
  (e: 'update', node: GraphNode): void
  (e: 'close'): void
}>()

// ─── 草稿狀態 ─────────────────────────────────────────────────────────────────
const draft = ref<GraphNode | null>(null)
const isDirty = ref(false)

watch(
  () => props.node,
  (node) => {
    draft.value = node ? { ...node } : null
    isDirty.value = false
  },
  { immediate: true },
)

watch(
  draft,
  (newVal) => {
    if (!newVal || !props.node) return
    isDirty.value =
      newVal.label !== props.node.label ||
      newVal.type !== props.node.type ||
      newVal.description !== props.node.description
  },
  { deep: true },
)

// ─── Methods ──────────────────────────────────────────────────────────────────
function save() {
  if (!draft.value) return
  emit('update', { ...draft.value })
  isDirty.value = false
}

function reset() {
  if (!props.node) return
  draft.value = { ...props.node }
  isDirty.value = false
}

function nodeColor(type: NodeType): string {
  return NODE_COLORS[type] ?? '#6b7280'
}
</script>

<template>
  <Transition name="slide-right">
    <div
      v-if="draft"
      class="absolute right-0 top-0 bottom-0 w-72 flex flex-col z-20 pointer-events-auto"
    >
      <!-- 毛玻璃卡片 -->
      <div class="flex-1 flex flex-col overflow-hidden bg-card/95 backdrop-blur-md border-l shadow-2xl">

        <!-- Header ──────────────────────────────────────────────────────── -->
        <div class="shrink-0 px-4 pt-4 pb-3 border-b">
          <div class="flex items-start gap-2">
            <!-- 類型色點 + 標題 -->
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

        <!-- 修改提示 Banner -->
        <Transition name="fade">
          <div
            v-if="isDirty"
            class="shrink-0 flex items-center gap-2 px-4 py-2 bg-amber-500/10 border-b border-amber-500/20 text-xs text-amber-600 dark:text-amber-400"
          >
            <span class="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
            尚未儲存的修改
          </div>
        </Transition>

        <!-- Form 區域（可滾動） ──────────────────────────────────────────── -->
        <div class="flex-1 overflow-y-auto px-4 py-4 space-y-5">

          <!-- 名稱 -->
          <div class="space-y-1.5">
            <Label class="text-xs text-muted-foreground">
              <Type class="size-3" />
              名稱
            </Label>
            <Input
              v-model="draft.label"
              placeholder="節點名稱"
            />
          </div>

          <!-- 類型 -->
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
                <SelectItem
                  v-for="(typeLabel, val) in NODE_TYPE_LABELS"
                  :key="val"
                  :value="val"
                >
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

          <!-- 描述 -->
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

        <!-- Footer 按鈕 ──────────────────────────────────────────────────── -->
        <div class="shrink-0 flex gap-2 px-4 py-3 border-t bg-muted/30">
          <Button
            class="flex-1"
            size="sm"
            :disabled="!isDirty"
            @click="save"
          >
            <Save class="size-3.5" />
            儲存
          </Button>
          <Button
            variant="outline"
            size="sm"
            :disabled="!isDirty"
            @click="reset"
          >
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
  transition: transform 0.22s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.22s ease;
}
.slide-right-enter-from,
.slide-right-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, max-height 0.2s ease;
  overflow: hidden;
  max-height: 40px;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  max-height: 0;
}
</style>
