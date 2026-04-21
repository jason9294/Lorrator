<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps<{
  title: string
  description?: string
  status?: number
  method?: string
  url?: string
  durationMs: number
  onCloseToast: () => void
  isPaused: boolean
}>()

const remainingMs = ref(props.durationMs)
const startedAt = ref<number>(0)
const lastTickAt = ref<number>(0)
let raf: number | null = null

const progress = computed(() => {
  if (props.durationMs <= 0) return 0
  return Math.max(0, Math.min(1, remainingMs.value / props.durationMs))
})

const metaLine = computed(() => {
  const parts: string[] = []
  if (props.status) parts.push(`HTTP ${props.status}`)
  if (props.method) parts.push(props.method.toUpperCase())
  if (props.url) parts.push(props.url)
  return parts.join(' · ')
})

function loop(now: number) {
  if (!startedAt.value) {
    startedAt.value = now
    lastTickAt.value = now
  }

  if (!props.isPaused) {
    const delta = Math.max(0, now - lastTickAt.value)
    remainingMs.value = Math.max(0, remainingMs.value - delta)
  }

  lastTickAt.value = now
  raf = requestAnimationFrame(loop)
}

watch(
  () => props.isPaused,
  (paused) => {
    if (!paused) {
      lastTickAt.value = performance.now()
    }
  },
)

onMounted(() => {
  raf = requestAnimationFrame(loop)
})

onBeforeUnmount(() => {
  if (raf) cancelAnimationFrame(raf)
})
</script>

<template>
  <div
    class="w-[360px] overflow-hidden rounded-xl border bg-popover text-popover-foreground shadow-lg"
    role="status"
    aria-live="polite"
  >
    <div class="flex gap-3 px-4 pb-3 pt-4">
      <div
        class="mt-0.5 grid size-9 place-items-center rounded-lg bg-destructive/10 text-destructive"
        aria-hidden="true"
      >
        <span class="text-base font-semibold">!</span>
      </div>

      <div class="min-w-0 flex-1">
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <div class="truncate text-sm font-semibold leading-5">
              {{ title }}
            </div>
            <div v-if="metaLine" class="mt-0.5 truncate text-xs text-muted-foreground">
              {{ metaLine }}
            </div>
          </div>

          <button
            type="button"
            class="shrink-0 rounded-md p-1 text-muted-foreground transition hover:bg-muted hover:text-foreground"
            @click="onCloseToast"
            aria-label="關閉"
          >
            <span aria-hidden="true">×</span>
          </button>
        </div>

        <div v-if="description" class="mt-2 line-clamp-3 text-sm text-muted-foreground">
          {{ description }}
        </div>
      </div>
    </div>

    <div class="h-1 bg-muted">
      <div
        class="h-full bg-destructive transition-[width]"
        :style="{ width: `${progress * 100}%` }"
      />
    </div>
  </div>
</template>

