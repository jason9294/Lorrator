<script setup lang="ts">
import { computed, toRef } from 'vue'

import type { RoomMessageResponse, RoomParticipantResponse } from '@/services'

import UserAvatar from '@/components/user/UserAvatar.vue'
import { useMessageAuthor } from '@/composables/useMessageAuthor'

const props = withDefaults(
  defineProps<{
    data: RoomMessageResponse
    participants: RoomParticipantResponse[]
    showAuthor?: boolean
  }>(),
  { showAuthor: true },
)

const { participant, senderLabel, isSelf } = useMessageAuthor(
  toRef(props, 'data'),
  toRef(props, 'participants'),
)

const rootClass = computed(() => (props.showAuthor ? 'mt-4' : 'mt-0.5'))
</script>

<template>
  <div class="flex items-start gap-3 max-w-[85%] ml-auto flex-row-reverse" :class="rootClass">
    <UserAvatar
      v-if="showAuthor"
      :user-id="data.sender_id ?? ''"
      :avatar-url="participant?.avatar_url"
      :nickname="participant?.nickname"
      :username="participant?.username"
      size="sm"
      class="mt-0.5 shrink-0"
    />
    <div v-else class="w-8 shrink-0" aria-hidden="true" />

    <div class="flex flex-col gap-1 items-end min-w-0">
      <div v-if="showAuthor" class="flex items-center gap-2">
        <span class="text-xs font-semibold">{{ senderLabel }}</span>
      </div>
      <div
        class="rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap"
        :class="isSelf ? 'bg-primary text-primary-foreground' : 'bg-muted/60'"
      >
        {{ data.content }}
      </div>
    </div>
  </div>
</template>
