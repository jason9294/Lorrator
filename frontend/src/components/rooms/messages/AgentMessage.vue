<script setup lang="ts">
import MarkdownIt from 'markdown-it'
import { computed } from 'vue'

import type { RoomMessageResponse } from '@/services'

const props = withDefaults(
  defineProps<{
    data: RoomMessageResponse
    showAuthor?: boolean
  }>(),
  { showAuthor: true },
)

const md = new MarkdownIt({ breaks: true, linkify: true })

const html = computed(() => md.render(props.data.content))

const rootClass = computed(() => (props.showAuthor ? 'mt-4' : 'mt-0.5'))
</script>

<template>
  <div class="flex items-start gap-3" :class="rootClass">
    <img
      v-if="showAuthor"
      src="/logo.png"
      alt="Lorrator"
      class="w-8 h-8 rounded-lg object-contain shrink-0 mt-0.5"
    />
    <div v-else class="w-8 shrink-0" aria-hidden="true" />

    <div class="flex flex-col gap-0.5 w-fit max-w-[50vw] min-w-0">
      <div v-if="showAuthor" class="flex items-center gap-2">
        <span class="text-xs font-semibold">Lorrator</span>
      </div>
      <div
        class="agent-markdown w-fit max-w-full bg-muted/60 rounded-2xl rounded-tl-sm px-4 py-2.5 text-sm leading-relaxed wrap-break-word"
        v-html="html"
      />
    </div>
  </div>
</template>
