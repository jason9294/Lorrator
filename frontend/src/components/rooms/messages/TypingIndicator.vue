<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    name?: string
    avatarSrc?: string
    side?: 'left' | 'right'
  }>(),
  {
    name: 'Lorrator',
    avatarSrc: '/logo.png',
    side: 'left',
  },
)

const isRight = computed(() => props.side === 'right')

const rootClass = computed(() =>
  isRight.value
    ? 'flex items-start gap-3 ml-auto flex-row-reverse'
    : 'flex items-start gap-3',
)

const contentClass = computed(() =>
  isRight.value
    ? 'flex flex-col gap-1 items-end w-fit max-w-[50vw] min-w-0'
    : 'flex flex-col gap-0.5 w-fit max-w-[50vw] min-w-0',
)

const bubbleClass = computed(() =>
  isRight.value
    ? 'w-fit bg-muted/60 rounded-2xl rounded-tr-sm px-4 py-3 flex items-center gap-1'
    : 'w-fit bg-muted/60 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-1',
)
</script>

<template>
  <div :class="rootClass">
    <slot name="avatar">
      <img
        :src="avatarSrc"
        :alt="name"
        class="w-8 h-8 rounded-lg object-contain shrink-0 mt-0.5"
      />
    </slot>

    <div :class="contentClass">
      <span class="text-xs font-semibold">{{ name }}</span>
      <div :class="bubbleClass">
        <span
          class="w-1.5 h-1.5 rounded-full bg-muted-foreground/60 animate-bounce [animation-delay:0ms]"
        />
        <span
          class="w-1.5 h-1.5 rounded-full bg-muted-foreground/60 animate-bounce [animation-delay:150ms]"
        />
        <span
          class="w-1.5 h-1.5 rounded-full bg-muted-foreground/60 animate-bounce [animation-delay:300ms]"
        />
      </div>
    </div>
  </div>
</template>
