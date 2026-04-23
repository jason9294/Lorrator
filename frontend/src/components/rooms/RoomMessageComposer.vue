<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import { Loader2, SendHorizonal } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

const text = defineModel<string>({ default: '' })

const props = withDefaults(
  defineProps<{
    disabled?: boolean
    placeholder?: string
    loading?: boolean
  }>(),
  {
    disabled: false,
    placeholder: '輸入你的行動或對話...',
    loading: false,
  },
)

const emit = defineEmits<{
  send: [text: string]
}>()

const lastTextareaEl = ref<HTMLTextAreaElement | null>(null)

function resizeTextarea(el: HTMLTextAreaElement) {
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 144) + 'px'
}

function handleInput(e: Event) {
  const el = e.target as HTMLTextAreaElement | null
  if (!el) return
  lastTextareaEl.value = el
  resizeTextarea(el)
}

function handleSend() {
  if (props.disabled) return
  emit('send', text.value)
}

watch(
  () => text.value,
  async (v) => {
    if (v !== '') return
    await nextTick()
    if (!lastTextareaEl.value) return
    lastTextareaEl.value.style.height = 'auto'
    lastTextareaEl.value.style.height = '44px'
  },
)
</script>

<template>
  <div class="max-w-4xl mx-auto flex items-end gap-2">
    <div class="flex-1 relative">
      <Textarea
        v-model="text"
        :placeholder="props.placeholder"
        class="resize-none min-h-[44px] max-h-36 pr-2 py-2.5 text-sm"
        :rows="1"
        :disabled="props.disabled"
        @keydown.enter.exact.prevent="handleSend"
        @input="handleInput"
      />
    </div>
    <Button
      size="icon"
      class="h-11 w-11 shrink-0"
      :disabled="props.disabled || !text.trim() || props.loading"
      @click="handleSend"
    >
      <Loader2 v-if="props.loading" class="size-4 animate-spin" />
      <SendHorizonal v-else class="size-4" />
    </Button>
  </div>
</template>
