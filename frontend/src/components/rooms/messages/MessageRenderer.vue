<script setup lang="ts">
import type { Component } from 'vue'
import { computed } from 'vue'

import type { RoomParticipantResponse, RoomMessageResponse } from '@/services'

import AgentMessage from './AgentMessage.vue'
import DebugMessage from './DebugMessage.vue'
// import DiceMessage from './DiceMessage.vue'
import NewDiceMessage from './NewDiceMessage.vue'
import PlayerMessage from './PlayerMessage.vue'
import SystemMessage from './SystemMessage.vue'

const props = defineProps<{
  data: RoomMessageResponse
  participants: RoomParticipantResponse[]
  showAuthor?: boolean
}>()

const messageComponent = computed((): Component => {
  const { type, role } = props.data
  if (type === 'DEBUG') return DebugMessage
  if (type === 'DICE') return NewDiceMessage
  if (role === 'SYSTEM') return SystemMessage
  if (role === 'AGENT') return AgentMessage
  return PlayerMessage
})
</script>

<template>
  <component
    :is="messageComponent"
    :data="data"
    :participants="participants"
    :show-author="showAuthor ?? true"
  />
</template>
