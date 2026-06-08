<script setup lang="ts">
import { computed } from 'vue'

import type { RoomMessageResponse, RoomParticipantResponse } from '@/services'

import { useMeStore } from '@/stores/me'

const props = defineProps<{
  data: RoomMessageResponse
  participants: RoomParticipantResponse[]
}>()

const meStore = useMeStore()

const senderLabel = computed(() => {
  const id = props.data.sender_id
  if (id === meStore.id) return '你'
  const p = props.participants.find((x) => x.user_id === id)
  return p?.nickname || p?.username || '玩家'
})
</script>

<template>
  <div class="flex justify-center">
    <div
      class="flex items-start gap-2.5 bg-amber-500/10 border border-amber-500/25 text-amber-800 dark:text-amber-300 text-sm px-4 py-2.5 rounded-xl max-w-sm w-full"
    >
      <span class="text-lg leading-none shrink-0">🎲</span>
      <div class="flex-1 min-w-0">
        <p class="text-[10px] font-medium text-amber-600 dark:text-amber-400 mb-0.5">
          {{ senderLabel }}
        </p>
        <p class="leading-snug">{{ data.content.replace(/^🎲\s*/, '') }}</p>
      </div>
    </div>
  </div>
</template>
