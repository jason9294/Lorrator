<script setup lang="ts">
import type { GraphNode, NodeType } from '@/types/graph'
import { NODE_TYPE_LABELS, NODE_COLORS } from '@/types/graph'
import { ref, watch } from 'vue'
import { X, Save, RotateCcw, Tag, Type, AlignLeft } from 'lucide-vue-next'

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
        <div class="flex-shrink-0 px-4 pt-4 pb-3 border-b">
          <div class="flex items-start gap-2">
            <!-- 類型色點 + 標題 -->
            <div class="flex flex-col gap-2 flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span
                  class="inline-block w-2.5 h-2.5 rounded-full flex-shrink-0 mt-0.5"
                  :style="{ backgroundColor: nodeColor(draft.type) }"
                />
                <span class="text-xs font-medium text-muted-foreground">
                  {{ NODE_TYPE_LABELS[draft.type] ?? draft.type }}
                </span>
              </div>
              <h3 class="text-sm font-semibold leading-tight truncate">{{ draft.label }}</h3>
            </div>
            <!-- 關閉按鈕 -->
            <button
              class="flex-shrink-0 w-7 h-7 rounded-md flex items-center justify-center text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
              @click="emit('close')"
            >
              <X :size="14" />
            </button>
          </div>
        </div>

        <!-- 修改提示 Banner -->
        <Transition name="fade">
          <div
            v-if="isDirty"
            class="flex-shrink-0 flex items-center gap-2 px-4 py-2 bg-amber-500/10 border-b border-amber-500/20 text-xs text-amber-600 dark:text-amber-400"
          >
            <span class="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
            尚未儲存的修改
          </div>
        </Transition>

        <!-- Form 區域（可滾動） ──────────────────────────────────────────── -->
        <div class="flex-1 overflow-y-auto px-4 py-4 space-y-5">

          <!-- 名稱 -->
          <div class="space-y-1.5">
            <label class="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
              <Type :size="11" />
              名稱
            </label>
            <input
              v-model="draft.label"
              class="w-full border-input bg-background/50 border rounded-lg px-3 py-2 text-sm outline-none focus-visible:ring-2 ring-ring/50 transition placeholder:text-muted-foreground/50"
              placeholder="節點名稱"
            />
          </div>

          <!-- 類型 -->
          <div class="space-y-1.5">
            <label class="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
              <Tag :size="11" />
              類型
            </label>
            <div class="relative">
              <select
                v-model="draft.type"
                class="w-full border-input bg-background/50 border rounded-lg px-3 py-2 text-sm outline-none focus-visible:ring-2 ring-ring/50 transition cursor-pointer appearance-none"
              >
                <option
                  v-for="(label, val) in NODE_TYPE_LABELS"
                  :key="val"
                  :value="val"
                >
                  {{ label }}
                </option>
              </select>
              <!-- 自訂 select 箭頭 -->
              <div class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2">
                <svg class="w-3.5 h-3.5 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
            <!-- 顏色預覽 -->
            <div class="flex items-center gap-2 px-1">
              <span
                class="inline-block w-3 h-3 rounded-full"
                :style="{ backgroundColor: nodeColor(draft.type as NodeType) }"
              />
              <span class="text-xs text-muted-foreground">節點顏色預覽</span>
            </div>
          </div>

          <!-- 描述 -->
          <div class="space-y-1.5">
            <label class="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
              <AlignLeft :size="11" />
              描述
            </label>
            <textarea
              v-model="draft.description"
              rows="6"
              class="w-full border-input bg-background/50 border rounded-lg px-3 py-2 text-sm outline-none focus-visible:ring-2 ring-ring/50 transition resize-none placeholder:text-muted-foreground/50"
              placeholder="輸入節點描述..."
            />
          </div>

        </div>

        <!-- Footer 按鈕 ──────────────────────────────────────────────────── -->
        <div class="flex-shrink-0 flex gap-2 px-4 py-3 border-t bg-muted/30">
          <button
            :disabled="!isDirty"
            class="flex-1 inline-flex items-center justify-center gap-1.5 bg-primary text-primary-foreground rounded-lg px-3 py-2 text-xs font-medium hover:opacity-90 active:scale-95 transition-all disabled:opacity-35 disabled:cursor-not-allowed disabled:active:scale-100"
            @click="save"
          >
            <Save :size="12" />
            儲存
          </button>
          <button
            :disabled="!isDirty"
            class="inline-flex items-center justify-center gap-1.5 border bg-background rounded-lg px-3 py-2 text-xs font-medium hover:bg-muted active:scale-95 transition-all disabled:opacity-35 disabled:cursor-not-allowed disabled:active:scale-100"
            @click="reset"
          >
            <RotateCcw :size="12" />
            還原
          </button>
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
