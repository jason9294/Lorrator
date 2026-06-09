<script setup lang="ts">
import { Bug } from 'lucide-vue-next'
import { computed, ref } from 'vue'

import type { RoomMessageResponse } from '@/services'
import { mapLlmCallResponse } from '@/types/llm-call'

import PipelineLlmCallButton from '@/components/views/scenario/document-pipeline/PipelineLlmCallButton.vue'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

const props = defineProps<{
  data: RoomMessageResponse
}>()

const open = ref(false)

const hasDetail = computed(() => Boolean(props.data.detail?.trim()))

const llmCalls = computed(() =>
  (props.data.llm_calls ?? []).map((call) => mapLlmCallResponse(call)),
)
</script>

<template>
  <div class="mt-4 flex max-w-[85%] items-start gap-2 border-l-2 border-muted-foreground/20 pl-3">
    <Bug class="mt-px size-3.5 shrink-0 text-muted-foreground/50" aria-hidden="true" />

    <div class="min-w-0 text-xs leading-relaxed text-muted-foreground">
      <p>
        <span class="font-medium text-muted-foreground/80">Debug</span>
        <span class="text-muted-foreground/30"> · </span>
        <span>{{ data.content }}</span>
        <button
          v-if="hasDetail"
          type="button"
          class="ml-1.5 text-muted-foreground/70 underline-offset-2 hover:text-foreground hover:underline"
          @click="open = true"
        >
          查看詳情
        </button>
        <span v-for="call in llmCalls" :key="call.id" class="ml-1.5 inline-flex">
          <PipelineLlmCallButton :call="call" :label="call.label" />
        </span>
      </p>
    </div>

    <Dialog v-model:open="open">
      <DialogContent class="flex max-h-[80vh] max-w-2xl flex-col">
        <DialogHeader>
          <DialogTitle class="flex items-center gap-2 text-sm font-medium">
            <Bug class="size-4 text-muted-foreground/60" aria-hidden="true" />
            <span>Debug · {{ data.content }}</span>
          </DialogTitle>
        </DialogHeader>
        <pre
          class="overflow-x-auto rounded-md bg-muted/40 p-4 font-mono text-xs leading-relaxed whitespace-pre-wrap text-muted-foreground"
        >{{ data.detail }}</pre>
      </DialogContent>
    </Dialog>
  </div>
</template>
