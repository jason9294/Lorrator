<script setup lang="ts">
import { Dices } from 'lucide-vue-next'
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

const { participant, senderLabel } = useMessageAuthor(
  toRef(props, 'data'),
  toRef(props, 'participants'),
)

type ParsedDice =
  | {
      kind: 'skill'
      skillName: string
      skillValue: number
      roll: number
      result: string
    }
  | {
      kind: 'normal'
      count: number
      faces: number
      results: string
      total: number
    }

const parsed = computed((): ParsedDice | null => {
  const raw = props.data.content.replace(/^🎲\s*/, '')

  const skillMatch = raw.match(/^進行【(.+?) (\d+)%】技能檢定：擲出 (\d+) → (.+)$/)
  if (skillMatch) {
    return {
      kind: 'skill',
      skillName: skillMatch[1]!,
      skillValue: Number(skillMatch[2]),
      roll: Number(skillMatch[3]),
      result: skillMatch[4]!,
    }
  }

  const normalMatch = raw.match(/^擲出了 (\d+)d(\d+)：\[([^\]]+)\] = (\d+)$/)
  if (normalMatch) {
    return {
      kind: 'normal',
      count: Number(normalMatch[1]),
      faces: Number(normalMatch[2]),
      results: normalMatch[3]!,
      total: Number(normalMatch[4]),
    }
  }

  return null
})

const headline = computed(() => {
  const p = parsed.value
  if (!p) return props.data.content.replace(/^🎲\s*/, '')
  if (p.kind === 'skill') return `${p.skillName}: ${p.roll} / ${p.skillValue}`
  return `${p.count}d${p.faces}: [${p.results}] = ${p.total}`
})

const resultLabel = computed(() => {
  const p = parsed.value
  if (!p || p.kind !== 'skill') return null
  return p.result
})

const rootClass = computed(() => (props.showAuthor ? 'mt-4' : 'mt-0.5'))
</script>

<template>
  <div class="flex items-start gap-3 max-w-[75%] ml-auto flex-row-reverse" :class="rootClass">
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

    <div class="flex flex-col items-end gap-1 min-w-0">
      <div v-if="showAuthor" class="flex items-center gap-2">
        <span class="text-xs font-semibold">{{ senderLabel }}</span>
      </div>
      <div
        class="border-2 border-tertiary bg-surface-container-lowest text-tertiary px-stack-md py-stack-sm rounded -rotate-1 shadow-sm flex flex-col items-end"
      >
        <div class="text-[16px] font-bold flex items-center gap-2">
          <Dices class="size-4 shrink-0" />
          {{ headline }}
        </div>
        <div v-if="resultLabel" class="text-[14px] font-bold mt-1 uppercase tracking-wider">
          {{ resultLabel }}
        </div>
      </div>
    </div>
  </div>
</template>
