<script setup lang="ts">
import { ref } from 'vue'
import { MessageSquareText } from 'lucide-vue-next'
import type { DocumentProcessingLlmCall } from '@/types/document-processing'
import { Button } from '@/components/ui/button'
import PipelineLlmCallDialog from './PipelineLlmCallDialog.vue'

const props = defineProps<{
  call: DocumentProcessingLlmCall | null | undefined
  label?: string
}>()

const open = ref(false)

function showDialog() {
  if (!props.call) return
  open.value = true
}
</script>

<template>
  <Button
    v-if="call"
    type="button"
    variant="outline"
    size="sm"
    class="h-7 gap-1.5 text-xs"
    @click="showDialog"
  >
    <MessageSquareText class="size-3.5" />
    {{ label ?? '查看 LLM' }}
  </Button>

  <PipelineLlmCallDialog v-model:open="open" :call="call ?? null" />
</template>
