<template>
  <div class="h-screen flex flex-col bg-background text-foreground overflow-hidden">
    <!-- 載入中 -->
    <div
      v-if="isLoading"
      class="flex-1 flex flex-col items-center justify-center gap-3 text-muted-foreground"
    >
      <Spinner class="size-8" />
      <p class="text-sm">載入房間資料中…</p>
    </div>

    <!-- 錯誤 -->
    <div
      v-else-if="loadError"
      class="flex-1 flex flex-col items-center justify-center gap-4 p-8 text-center"
    >
      <p class="text-lg font-semibold">無法載入房間</p>
      <p class="text-sm text-muted-foreground">{{ loadError }}</p>
      <div class="flex gap-2">
        <Button @click="bootstrap">重試</Button>
        <RouterLink to="/rooms"><Button variant="outline">返回列表</Button></RouterLink>
      </div>
    </div>

    <!-- 主內容 -->
    <template v-else-if="room">
      <!-- ═══ 頂部導覽列 ═══ -->
      <header
        class="shrink-0 flex items-center gap-3 px-5 h-13 border-b bg-card/80 backdrop-blur-sm z-30"
      >
        <RouterLink to="/rooms">
          <Button variant="ghost" size="icon-sm" class="text-muted-foreground">
            <ArrowLeft class="size-4" />
          </Button>
        </RouterLink>
        <div class="w-px h-5 bg-border shrink-0" />

        <div class="flex items-center gap-2.5 flex-1 min-w-0">
          <div
            class="w-8 h-8 rounded-lg flex items-center justify-center text-white text-xs font-bold shadow-sm shrink-0"
            :style="{ backgroundColor: colorFromId(room.id) }"
          >
            {{ room.name.charAt(0) }}
          </div>
          <div class="flex flex-col leading-none min-w-0">
            <span class="text-sm font-semibold truncate">{{ room.name }}</span>
            <span class="text-[10px] text-muted-foreground">
              {{
                room.status === 'RUNNING'
                  ? '跑團進行中'
                  : room.status === 'COMPLETED'
                    ? '已結束'
                    : '準備中'
              }}
              · {{ room.participants.length }} 位參與者
            </span>
          </div>
        </div>

        <div class="flex items-center gap-2 shrink-0">
          <!-- 邀請碼（僅準備中顯示） -->
          <template v-if="room.status === 'PREPARING'">
            <div class="flex items-center gap-1.5 bg-muted rounded-md px-2.5 py-1.5">
              <span class="text-[10px] text-muted-foreground">邀請碼</span>
              <span class="font-mono text-sm font-semibold tracking-widest">{{
                room.invite_code
              }}</span>
              <button
                class="text-muted-foreground hover:text-foreground transition-colors ml-1"
                title="複製邀請碼"
                @click="copyInviteCode"
              >
                <Copy class="size-3.5" />
              </button>
            </div>
            <!-- 重新生成邀請碼（僅房主） -->
            <Button
              v-if="isHost"
              variant="outline"
              size="sm"
              class="gap-1.5"
              :disabled="isRegenerating"
              @click="handleRegenerateInvite"
              title="重新生成邀請碼"
            >
              <RefreshCw class="size-3.5" :class="isRegenerating ? 'animate-spin' : ''" />
            </Button>
          </template>

          <!-- 開始跑團（僅房主，準備中） -->
          <Button
            v-if="isHost && room.status === 'PREPARING'"
            size="sm"
            class="gap-1.5"
            :disabled="!allReady || isStarting"
            @click="handleStartSession"
          >
            <Spinner v-if="isStarting" class="size-3.5" />
            <Play v-else class="size-3.5" />
            {{ isStarting ? '啟動中...' : '開始跑團' }}
          </Button>

          <!-- 主題切換 -->
          <Button
            variant="outline"
            size="icon-sm"
            :title="isDark ? '切換為亮色模式' : '切換為暗色模式'"
            @click="toggle"
          >
            <Transition name="icon-swap" mode="out-in">
              <Moon v-if="!isDark" :key="'moon'" class="size-3.5" />
              <Sun v-else :key="'sun'" class="size-3.5" />
            </Transition>
          </Button>
        </div>
      </header>

      <!-- 複製成功提示 -->
      <div
        v-if="copiedToast"
        class="shrink-0 px-5 py-1.5 bg-green-500/15 text-green-700 dark:text-green-400 text-xs text-center"
      >
        邀請碼已複製到剪貼簿
      </div>

      <!-- 錯誤提示 -->
      <div
        v-if="actionError"
        class="shrink-0 px-5 py-1.5 bg-destructive/10 text-destructive text-xs flex items-center gap-2"
      >
        <span>{{ actionError }}</span>
        <button class="ml-auto" @click="actionError = null">✕</button>
      </div>

      <!-- ═══ 準備大廳 ═══ -->
      <main v-if="room.status === 'PREPARING'" class="flex-1 overflow-y-auto p-6">
        <div class="max-w-lg mx-auto space-y-6">
          <!-- 等待提示 -->
          <div class="text-center space-y-1 pt-4">
            <h2 class="text-xl font-bold">等待室</h2>
            <p class="text-sm text-muted-foreground">等待所有人就緒後，房主即可開始跑團</p>
          </div>

          <!-- 參與者列表 -->
          <div class="border rounded-xl overflow-hidden">
            <div class="bg-muted/40 px-4 py-2.5 border-b">
              <span class="text-xs font-semibold text-muted-foreground">參與者</span>
            </div>

            <RoomParticipantContextMenu
              v-for="p in room.participants"
              :key="p.user_id"
              :user-id="p.user_id"
              :can-kick="isHost && p.user_id !== room.host_id"
              :is-kicking="isKicking === p.user_id"
              @kick="handleKick(p.user_id)"
            >
              <RoomParticipantInfoCard :participant="p" :is-host="p.user_id === room.host_id">
                <div
                  class="flex items-center gap-3 px-4 py-3 border-b last:border-0 cursor-pointer hover:bg-muted/30 transition-colors select-none"
                >
                  <!-- 頭像 -->
                  <UserAvatar
                    :user-id="p.user_id"
                    :avatar-url="p.avatar_url"
                    :nickname="p.nickname"
                    :username="p.username"
                    size="sm"
                  />

                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-1.5">
                      <span class="text-sm font-medium truncate">
                        {{ p.nickname || p.username }}
                      </span>
                      <Badge
                        v-if="p.user_id === room.host_id"
                        class="text-[10px] bg-violet-500/15 text-violet-700 dark:text-violet-400 border-violet-500/30"
                        variant="outline"
                      >
                        房主
                      </Badge>
                    </div>
                    <!-- 角色卡名稱 -->
                    <div class="flex items-center gap-1 mt-0.5">
                      <Scroll class="size-3 text-muted-foreground/60 shrink-0" />
                      <p class="text-[10px] text-muted-foreground truncate">
                        {{ p.character_name || '未選擇角色' }}
                      </p>
                    </div>
                  </div>

                  <!-- 就緒狀態 -->
                  <div class="flex items-center gap-2 shrink-0">
                    <span
                      class="flex items-center gap-1 text-xs font-medium"
                      :class="
                        p.is_ready ? 'text-green-600 dark:text-green-400' : 'text-muted-foreground'
                      "
                    >
                      <CheckCircle2 v-if="p.is_ready" class="size-3.5" />
                      <Circle v-else class="size-3.5" />
                      {{ p.is_ready ? '已就緒' : '未就緒' }}
                    </span>
                  </div>
                </div>
              </RoomParticipantInfoCard>
            </RoomParticipantContextMenu>
          </div>

          <!-- 角色卡選擇（自己，僅準備中且未就緒可操作） -->
          <div v-if="myParticipant" class="border rounded-xl overflow-hidden">
            <div class="bg-muted/40 px-4 py-2.5 border-b">
              <span class="text-xs font-semibold text-muted-foreground">我的角色卡</span>
            </div>
            <div class="px-4 py-3 space-y-2">
              <!-- 尚無角色卡 -->
              <template v-if="characters.length === 0">
                <p class="text-sm text-muted-foreground">你還沒有任何角色卡。</p>
                <RouterLink to="/characters">
                  <Button variant="outline" size="sm" class="gap-1.5 w-full">
                    <Scroll class="size-3.5" />
                    前往建立角色卡
                  </Button>
                </RouterLink>
              </template>

              <!-- 有角色卡可選 -->
              <template v-else>
                <div class="flex items-center gap-2">
                  <Select
                    :model-value="myParticipant.character_id ?? ''"
                    :disabled="myParticipant.is_ready || isSelectingCharacter"
                    @update:model-value="(val) => handleSelectCharacter((val as string) || null)"
                  >
                    <SelectTrigger class="flex-1 h-8 text-sm">
                      <SelectValue placeholder="選擇角色卡…" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem v-for="c in characters" :key="c.id" :value="c.id">
                        {{ c.name }}
                      </SelectItem>
                    </SelectContent>
                  </Select>
                  <Button
                    v-if="myParticipant.character_id"
                    variant="ghost"
                    size="icon-sm"
                    :disabled="myParticipant.is_ready || isSelectingCharacter"
                    title="取消選擇角色卡"
                    @click="handleSelectCharacter(null)"
                  >
                    <X class="size-3.5" />
                  </Button>
                </div>
                <p v-if="myParticipant.is_ready" class="text-[10px] text-muted-foreground">
                  取消就緒後方可更換角色卡
                </p>
              </template>
            </div>
          </div>

          <!-- 就緒按鈕（非房主） -->
          <div v-if="myParticipant" class="flex flex-col items-center gap-1.5">
            <Button
              :variant="myParticipant.is_ready ? 'outline' : 'default'"
              class="gap-2 min-w-32"
              :disabled="isSettingReady || (!myParticipant.is_ready && !myParticipant.character_id)"
              @click="handleToggleReady"
            >
              <Spinner v-if="isSettingReady" class="size-4" />
              <CheckCircle2 v-else-if="myParticipant.is_ready" class="size-4" />
              <Circle v-else class="size-4" />
              {{ myParticipant.is_ready ? '取消就緒' : '我已就緒' }}
            </Button>
            <p
              v-if="!myParticipant.is_ready && !myParticipant.character_id && characters.length > 0"
              class="text-[10px] text-amber-600 dark:text-amber-400"
            >
              請先選擇角色卡才能就緒
            </p>
          </div>

          <!-- 房主就緒提示 -->
          <div v-if="isHost" class="text-center">
            <p class="text-xs text-muted-foreground">
              <template v-if="allReady">所有人已就緒，可以開始跑團了！</template>
              <template v-else>等待 {{ notReadyCount }} 位參與者就緒中…</template>
            </p>
          </div>
        </div>
      </main>

      <!-- ═══ 聊天介面（跑團進行中） ═══ -->
      <template v-else-if="room.status === 'RUNNING'">
        <main ref="messageListRef" class="flex-1 overflow-y-auto px-4 py-4 scroll-smooth">
          <!-- 系統提示訊息 -->
          <div class="flex justify-center">
            <div class="bg-muted/50 text-muted-foreground text-xs px-3 py-1.5 rounded-full">
              跑團已開始，祝大家玩得愉快！
            </div>
          </div>

          <!-- 訊息氣泡 -->
          <MessageRenderer
            v-for="(msg, index) in messages"
            :key="msg.id"
            :data="msg"
            :participants="room.participants"
            :show-author="shouldShowMessageAuthor(messages, index)"
          />

          <TypingIndicator v-if="isAiTyping" />

          <div ref="bottomRef" />
        </main>

        <!-- 輸入區 -->
        <footer class="shrink-0 border-t bg-card/80 backdrop-blur-sm px-4 py-3">
          <div class="max-w-4xl mx-auto flex items-end gap-2">
            <DiceRollerDialog :room-id="roomId" :disabled="isAiTyping" @rolled="handleDiceRolled" />
            <div class="flex-1 min-w-0">
              <RoomMessageComposer
                v-model="inputText"
                :disabled="isAiTyping"
                :loading="isSending"
                @send="sendMessage"
              />
            </div>
          </div>

          <p class="text-center text-[10px] text-muted-foreground/50 mt-2">
            Enter 發送 · Shift+Enter 換行
          </p>
        </footer>
      </template>

      <!-- 已結束 -->
      <div
        v-else
        class="flex-1 flex flex-col items-center justify-center gap-4 p-8 text-center text-muted-foreground"
      >
        <p class="text-lg font-semibold">跑團已結束</p>
        <RouterLink to="/rooms"><Button variant="outline">返回房間列表</Button></RouterLink>
      </div>
    </template>

    <RoomKickedDialog v-model:open="kickedDialogOpen" @confirm="handleKickedConfirm" />
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { useAsyncState, useToggle } from '@vueuse/core'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowLeft,
  CheckCircle2,
  Circle,
  Copy,
  Moon,
  Play,
  RefreshCw,
  Scroll,
  Sun,
  X,
} from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { useColorMode } from '@/composables/useColorMode'
import { useCopyFeedback } from '@/composables/useCopyFeedback'

const { isDark, toggle } = useColorMode()
const { copy, copied: copiedToast } = useCopyFeedback()
import { Badge } from '@/components/ui/badge'
import { Spinner } from '@/components/ui/spinner'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useSocketOnType, useSocketTopic } from '@/composables/websocket'
import {
  CharactersService,
  RoomsService,
  type CharacterResponse,
  type RoomMessageResponse,
  type RoomDetailResponse,
  type RoomParticipantResponse,
} from '@/services'
import { useMeStore } from '@/stores/me'

import MessageRenderer from '@/components/rooms/messages/MessageRenderer.vue'
import TypingIndicator from '@/components/rooms/messages/TypingIndicator.vue'
import DiceRollerDialog from '@/components/rooms/DiceRollerDialog.vue'
import RoomMessageComposer from '@/components/rooms/RoomMessageComposer.vue'
import RoomKickedDialog from '@/components/rooms/RoomKickedDialog.vue'
import RoomParticipantInfoCard from '@/components/rooms/RoomParticipantInfoCard.vue'
import RoomParticipantContextMenu from '@/components/rooms/RoomParticipantContextMenu.vue'
import UserAvatar from '@/components/user/UserAvatar.vue'
import { colorFromId } from '@/utils/color'
import { shouldShowMessageAuthor } from '@/utils/messageGrouping'

import {
  roomsAiThinkingPayloadSchema,
  roomsCreateMessagePayloadSchema,
  roomsJoinRoomPayloadSchema,
  roomsKickPayloadSchema,
  roomsSelectCharacterPayloadSchema,
  roomsSetReadyPayloadSchema,
} from '@/types/socket-schemas'

type RoomDetail = RoomDetailResponse

const route = useRoute()
const router = useRouter()
const roomId = String(route.params.room_id ?? '')

const meStore = useMeStore()

const actionError = ref<string | null>(null)
const isRegenerating = ref(false)
const isStarting = ref(false)
const isKicking = ref<string | null>(null)
const isSettingReady = ref(false)
const isSending = ref(false)
const [kickedDialogOpen] = useToggle(false)

// 角色卡
const characters = ref<CharacterResponse[]>([])
const isSelectingCharacter = ref(false)

// 聊天
const inputText = ref('')
const isAiTyping = ref(false)
const bottomRef = ref<HTMLElement | null>(null)
const messages = ref<RoomMessageResponse[]>([])

async function scrollToBottom() {
  await nextTick()
  bottomRef.value?.scrollIntoView({ behavior: 'smooth' })
}

async function loadCharacters() {
  try {
    const res = await CharactersService.listCharacters()
    characters.value = res.data
  } catch {
    // ignore
  }
}

async function loadMessages() {
  try {
    const res = await RoomsService.listRoomMessages({ path: { room_id: roomId } })
    messages.value = res.data
    await scrollToBottom()
  } catch {
    // ignore
  }
}

const {
  state: room,
  isLoading,
  error: bootstrapError,
  execute: bootstrap,
} = useAsyncState(
  async () => {
    const [roomRes] = await Promise.all([
      RoomsService.getRoom({ path: { room_id: roomId } }),
      meStore.ensureMe(),
    ])
    const data = roomRes.data
    if (data.status === 'RUNNING') {
      await loadMessages()
    } else if (data.status === 'PREPARING') {
      await loadCharacters()
    }
    return data
  },
  null as RoomDetail | null,
  { immediate: false },
)

const loadError = computed(() => {
  if (!bootstrapError.value) return null
  const e = bootstrapError.value as {
    response?: { status?: number; data?: { detail?: unknown } }
  }
  const status = e.response?.status
  const detail = e.response?.data?.detail
  return status === 403
    ? '你不是此房間的參與者'
    : typeof detail === 'string'
      ? detail
      : '無法載入房間'
})

const isHost = computed(() => room.value?.host_id === meStore.id)

const myParticipant = computed((): RoomParticipantResponse | undefined =>
  room.value?.participants.find((p) => p.user_id === meStore.id),
)

const allReady = computed(
  () =>
    (room.value?.participants.length ?? 0) > 0 && room.value!.participants.every((p) => p.is_ready),
)

const notReadyCount = computed(
  () => room.value?.participants.filter((p) => !p.is_ready).length ?? 0,
)

function handleKickedConfirm() {
  void router.push('/rooms')
}

async function handleRegenerateInvite() {
  isRegenerating.value = true
  actionError.value = null
  try {
    const res = await RoomsService.regenerateInviteCode({ path: { room_id: roomId } })
    room.value = res.data
  } catch {
    actionError.value = '重新生成邀請碼失敗'
  } finally {
    isRegenerating.value = false
  }
}

function copyInviteCode() {
  if (!room.value) return
  void copy(room.value.invite_code)
}

async function handleKick(userId: string) {
  isKicking.value = userId
  actionError.value = null
  try {
    const res = await RoomsService.kickParticipant({
      path: { room_id: roomId, user_id: userId },
    })
    room.value = res.data
  } catch (e) {
    const detail = (e as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
    actionError.value = typeof detail === 'string' ? detail : '踢出失敗'
  } finally {
    isKicking.value = null
  }
}

async function handleSelectCharacter(characterId: string | null) {
  isSelectingCharacter.value = true
  actionError.value = null
  try {
    const res = await RoomsService.selectCharacter({
      path: { room_id: roomId },
      body: { character_id: characterId ?? null },
    })
    room.value = res.data
  } catch (e) {
    const detail = (e as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
    actionError.value = typeof detail === 'string' ? detail : '選擇角色卡失敗'
  } finally {
    isSelectingCharacter.value = false
  }
}

async function handleToggleReady() {
  if (!myParticipant.value) return
  isSettingReady.value = true
  actionError.value = null
  try {
    const res = await RoomsService.setReady({
      path: { room_id: roomId },
      query: { is_ready: !myParticipant.value.is_ready },
    })
    room.value = res.data
  } catch (e) {
    const detail = (e as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
    actionError.value = typeof detail === 'string' ? detail : '更新就緒狀態失敗'
  } finally {
    isSettingReady.value = false
  }
}

async function handleStartSession() {
  isStarting.value = true
  actionError.value = null
  try {
    const res = await RoomsService.startSession({ path: { room_id: roomId } })
    room.value = res.data
    await loadMessages()
  } catch (e) {
    const detail = (e as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
    actionError.value = typeof detail === 'string' ? detail : '無法開始跑團'
  } finally {
    isStarting.value = false
  }
}

async function sendMessage(text: string) {
  const trimmed = text.trim()
  if (!trimmed) return

  const tempId = `temp-${Date.now()}`
  const tempMessage: RoomMessageResponse = {
    id: tempId,
    room_id: roomId,
    sender_id: meStore.id,
    role: 'PLAYER',
    type: 'CHAT',
    content: trimmed,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }
  messages.value.push(tempMessage)
  inputText.value = ''
  await nextTick()
  await scrollToBottom()

  isSending.value = true
  try {
    const res = await RoomsService.sendRoomMessage({
      path: { room_id: roomId },
      body: { content: trimmed },
    })
    const idx = messages.value.findIndex((m) => m.id === tempId)
    if (idx !== -1) {
      messages.value[idx] = res.data
    }
  } catch {
    const idx = messages.value.findIndex((m) => m.id === tempId)
    if (idx !== -1) {
      messages.value.splice(idx, 1)
    }
  }

  isSending.value = false
  await nextTick()
  await scrollToBottom()
}

async function handleDiceRolled(message: RoomMessageResponse) {
  messages.value.push(message)
  await nextTick()
  await scrollToBottom()
}

// WebSocket
useSocketTopic(() => `rooms:${roomId}`)

useSocketOnType('rooms.join_room', async (payload) => {
  console.log('join room', payload)
  const parsed = roomsJoinRoomPayloadSchema.safeParse(payload)
  if (!parsed.success) {
    console.error('Invalid payload', payload)
    return
  }
  const data = parsed.data

  console.log(data.room_id, roomId)
  if (data.room_id !== roomId) {
    return
  }

  // add participant to ui (full profile will be fetched on next room reload)
  room.value?.participants.push({
    user_id: data.user_id,
    username: data.user_id,
    nickname: null,
    avatar_url: null,
    role: data.role,
    is_ready: data.is_ready,
    joined_at: data.joined_at,
  })
  console.log('joined room', data)
})

useSocketOnType('rooms.create_message', (payload) => {
  const parsed = roomsCreateMessagePayloadSchema.safeParse(payload)
  if (!parsed.success) {
    console.error('Invalid payload for rooms.create_message', payload)
    console.error(parsed.error)
    return
  }

  const data = parsed.data

  // 自己發的玩家訊息已透過 HTTP 回應加入，跳過避免重複
  if (data.sender_id === meStore.id) {
    return
  }

  messages.value.push({
    id: data.id,
    room_id: data.room_id,
    sender_id: data.sender_id,
    role: data.role,
    type: data.type,
    content: data.content,
    detail: data.detail ?? null,
    created_at: data.created_at,
    updated_at: data.updated_at,
  })
  void scrollToBottom()
})

useSocketOnType('rooms.ai_thinking', (payload) => {
  const parsed = roomsAiThinkingPayloadSchema.safeParse(payload)
  if (!parsed.success) return
  if (parsed.data.room_id !== roomId) return

  isAiTyping.value = parsed.data.active
  if (parsed.data.active) {
    void scrollToBottom()
  }
})

useSocketOnType('rooms.set_ready', (payload) => {
  const parsed = roomsSetReadyPayloadSchema.safeParse(payload)
  if (!parsed.success) {
    console.error('Invalid payload', payload)
    return
  }
  const data = parsed.data

  // validate room id
  if (data.room_id !== roomId) {
    console.error('Invalid room id', data.room_id)
    return
  }

  // turn to ui
  const idx = room.value!.participants.findIndex((p) => p.user_id === data.user_id)
  if (idx === -1) return // not found participant

  const existing = room.value?.participants[idx]
  if (!existing) return

  const updated = { ...existing, is_ready: data.is_ready } as RoomParticipantResponse
  room.value?.participants.splice(idx, 1, updated)
})

useSocketOnType('rooms.select_character', (payload) => {
  const parsed = roomsSelectCharacterPayloadSchema.safeParse(payload)
  if (!parsed.success) {
    console.error('Invalid payload', payload)
    return
  }
  const data = parsed.data

  if (data.room_id !== roomId) return

  const idx = room.value?.participants.findIndex((p) => p.user_id === data.user_id) ?? -1
  if (idx === -1) return

  const existing = room.value?.participants[idx]
  if (!existing) return

  const updated = {
    ...existing,
    character_id: data.character_id,
    character_name: data.character_name,
  } as RoomParticipantResponse
  room.value?.participants.splice(idx, 1, updated)
})

useSocketOnType('rooms.kick', (payload) => {
  const parsed = roomsKickPayloadSchema.safeParse(payload)
  if (!parsed.success) {
    console.error('Invalid payload', payload)
    return
  }
  const data = parsed.data

  if (data.room_id !== roomId) {
    return
  }

  if (data.user_id === meStore.id) {
    kickedDialogOpen.value = true
    return
  }

  if (!room.value) return

  const idx = room.value.participants.findIndex((p) => p.user_id === data.user_id)
  if (idx === -1) return

  room.value.participants.splice(idx, 1)
})

onMounted(async () => {
  await bootstrap()
})
</script>

<style scoped>
.agent-markdown :deep(p) {
  margin-bottom: 0.5em;
}
.agent-markdown :deep(p:last-child) {
  margin-bottom: 0;
}
.agent-markdown :deep(h1),
.agent-markdown :deep(h2),
.agent-markdown :deep(h3),
.agent-markdown :deep(h4) {
  font-weight: 700;
  line-height: 1.3;
  margin-top: 0.75em;
  margin-bottom: 0.4em;
}
.agent-markdown :deep(h1) {
  font-size: 1.15em;
}
.agent-markdown :deep(h2) {
  font-size: 1.05em;
}
.agent-markdown :deep(h3) {
  font-size: 0.97em;
}
.agent-markdown :deep(ul),
.agent-markdown :deep(ol) {
  padding-left: 1.4em;
  margin-bottom: 0.5em;
}
.agent-markdown :deep(li) {
  margin-bottom: 0.2em;
}
.agent-markdown :deep(strong) {
  font-weight: 700;
}
.agent-markdown :deep(em) {
  font-style: italic;
}
.agent-markdown :deep(code) {
  font-family: ui-monospace, monospace;
  font-size: 0.85em;
  background-color: hsl(var(--muted));
  border-radius: 0.25em;
  padding: 0.1em 0.35em;
}
.agent-markdown :deep(pre) {
  background-color: hsl(var(--muted));
  border-radius: 0.5em;
  padding: 0.75em 1em;
  overflow-x: auto;
  margin-bottom: 0.5em;
}
.agent-markdown :deep(pre code) {
  background: none;
  padding: 0;
  font-size: 0.85em;
}
.agent-markdown :deep(blockquote) {
  border-left: 3px solid hsl(var(--border));
  padding-left: 0.75em;
  color: hsl(var(--muted-foreground));
  margin-bottom: 0.5em;
}
.agent-markdown :deep(a) {
  color: hsl(var(--primary));
  text-decoration: underline;
}
.agent-markdown :deep(hr) {
  border: none;
  border-top: 1px solid hsl(var(--border));
  margin: 0.75em 0;
}
</style>
