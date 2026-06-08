import { computed, type Ref } from 'vue'

import type { RoomMessageResponse, RoomParticipantResponse } from '@/services'
import { useMeStore } from '@/stores/me'

export function useMessageAuthor(
  data: Ref<RoomMessageResponse>,
  participants: Ref<RoomParticipantResponse[]>,
) {
  const meStore = useMeStore()

  const participant = computed(() =>
    participants.value.find((x) => x.user_id === data.value.sender_id),
  )

  const senderLabel = computed(() => {
    const id = data.value.sender_id
    if (id === meStore.id) return '你'
    const p = participant.value
    return p?.nickname || p?.username || '玩家'
  })

  const isSelf = computed(() => data.value.sender_id === meStore.id)

  return { participant, senderLabel, isSelf }
}
