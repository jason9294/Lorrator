<template>
  <div class="h-screen flex flex-col bg-background text-foreground overflow-hidden">

    <!-- 載入中 -->
    <div v-if="isLoading" class="flex-1 flex flex-col items-center justify-center gap-3 text-muted-foreground">
      <Spinner class="size-8" />
      <p class="text-sm">載入房間資料中…</p>
    </div>

    <!-- 錯誤 -->
    <div v-else-if="loadError" class="flex-1 flex flex-col items-center justify-center gap-4 p-8 text-center">
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
      <header class="shrink-0 flex items-center gap-3 px-5 h-13 border-b bg-card/80 backdrop-blur-sm z-30">
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
              {{ room.status === 'RUNNING' ? '跑團進行中' : room.status === 'COMPLETED' ? '已結束' : '準備中' }}
              · {{ room.participants.length }} 位參與者
            </span>
          </div>
        </div>

        <div class="flex items-center gap-2 shrink-0">
          <!-- 邀請碼（僅準備中顯示） -->
          <template v-if="room.status === 'PREPARING'">
            <div class="flex items-center gap-1.5 bg-muted rounded-md px-2.5 py-1.5">
              <span class="text-[10px] text-muted-foreground">邀請碼</span>
              <span class="font-mono text-sm font-semibold tracking-widest">{{ room.invite_code }}</span>
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
            <div
              v-for="p in room.participants"
              :key="p.user_id"
              class="flex items-center gap-3 px-4 py-3 border-b last:border-0"
            >
              <!-- 頭像 -->
              <div
                class="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold shrink-0"
                :style="{ backgroundColor: colorFromId(p.user_id) }"
              >
                {{ p.user_id.charAt(0).toUpperCase() }}
              </div>

              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-1.5">
                  <span class="text-sm font-medium truncate">{{ p.user_id === room.host_id ? '房主' : '玩家' }}</span>
                  <Badge variant="outline" class="text-[10px]">{{ p.role === 'gm' ? 'GM' : '玩家' }}</Badge>
                  <Badge
                    v-if="p.user_id === room.host_id"
                    class="text-[10px] bg-violet-500/15 text-violet-700 dark:text-violet-400 border-violet-500/30"
                    variant="outline"
                  >
                    房主
                  </Badge>
                </div>
                <p class="text-[10px] text-muted-foreground font-mono truncate">{{ p.user_id }}</p>
              </div>

              <!-- 就緒狀態 -->
              <div class="flex items-center gap-2 shrink-0">
                <span
                  class="flex items-center gap-1 text-xs font-medium"
                  :class="p.is_ready ? 'text-green-600 dark:text-green-400' : 'text-muted-foreground'"
                >
                  <CheckCircle2 v-if="p.is_ready" class="size-3.5" />
                  <Circle v-else class="size-3.5" />
                  {{ p.is_ready ? '已就緒' : '未就緒' }}
                </span>

                <!-- 踢出（房主操作其他人） -->
                <Button
                  v-if="isHost && p.user_id !== room.host_id"
                  variant="ghost"
                  size="icon-sm"
                  class="text-muted-foreground hover:text-destructive"
                  title="踢出"
                  :disabled="isKicking === p.user_id"
                  @click="handleKick(p.user_id)"
                >
                  <UserMinus class="size-3.5" />
                </Button>
              </div>
            </div>
          </div>

          <!-- 就緒按鈕（非房主） -->
          <div v-if="!isHost && myParticipant" class="flex justify-center">
            <Button
              :variant="myParticipant.is_ready ? 'outline' : 'default'"
              class="gap-2 min-w-32"
              :disabled="isSettingReady"
              @click="handleToggleReady"
            >
              <Spinner v-if="isSettingReady" class="size-4" />
              <CheckCircle2 v-else-if="myParticipant.is_ready" class="size-4" />
              <Circle v-else class="size-4" />
              {{ myParticipant.is_ready ? '取消就緒' : '我已就緒' }}
            </Button>
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
        <main ref="messageListRef" class="flex-1 overflow-y-auto px-4 py-4 space-y-4 scroll-smooth">

          <!-- 系統提示訊息 -->
          <div class="flex justify-center">
            <div class="bg-muted/50 text-muted-foreground text-xs px-3 py-1.5 rounded-full">
              跑團已開始，祝大家玩得愉快！
            </div>
          </div>

          <!-- 訊息氣泡 -->
          <template v-for="msg in messages" :key="msg.id">
            <!-- 系統訊息 -->
            <div v-if="msg.role === 'system'" class="flex justify-center">
              <div class="bg-muted/50 text-muted-foreground text-xs px-3 py-1.5 rounded-full">
                {{ msg.content }}
              </div>
            </div>

            <!-- AI 守門人訊息 -->
            <div v-else-if="msg.role === 'ai'" class="flex items-start gap-3 max-w-[85%]">
              <div class="w-8 h-8 rounded-full bg-linear-to-br from-violet-500 to-indigo-600 flex items-center justify-center shrink-0 shadow-sm mt-0.5">
                <svg class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C8.13 2 5 5.13 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26C17.81 13.47 19 11.38 19 9c0-3.87-3.13-7-7-7zm0 12c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/>
                </svg>
              </div>
              <div class="flex flex-col gap-1">
                <div class="flex items-center gap-2">
                  <span class="text-xs font-semibold">AI 守門人</span>
                  <span class="text-[10px] text-muted-foreground">{{ msg.time }}</span>
                </div>
                <div class="bg-muted/60 rounded-2xl rounded-tl-sm px-4 py-2.5 text-sm leading-relaxed max-w-prose whitespace-pre-wrap">
                  {{ msg.content }}
                </div>
              </div>
            </div>

            <!-- 玩家訊息 -->
            <div v-else class="flex items-start gap-3 max-w-[85%] ml-auto flex-row-reverse">
              <div
                class="w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-0.5 text-white text-xs font-bold"
                :style="{ backgroundColor: colorFromId(msg.sender_id ?? '') }"
              >
                {{ (msg.sender_id ?? '?').charAt(0).toUpperCase() }}
              </div>
              <div class="flex flex-col gap-1 items-end">
                <div class="flex items-center gap-2">
                  <span class="text-[10px] text-muted-foreground">{{ msg.time }}</span>
                  <span class="text-xs font-semibold">{{ msg.sender_id === currentUserId ? '你' : '玩家' }}</span>
                </div>
                <div
                  class="rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap"
                  :class="msg.sender_id === currentUserId ? 'bg-primary text-primary-foreground' : 'bg-muted/60'"
                >
                  {{ msg.content }}
                </div>
              </div>
            </div>
          </template>

          <!-- AI 輸入中 -->
          <div v-if="isAiTyping" class="flex items-start gap-3 max-w-[85%]">
            <div class="w-8 h-8 rounded-full bg-linear-to-br from-violet-500 to-indigo-600 flex items-center justify-center shrink-0 shadow-sm mt-0.5">
              <svg class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26C17.81 13.47 19 11.38 19 9c0-3.87-3.13-7-7-7zm0 12c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/>
              </svg>
            </div>
            <div class="flex flex-col gap-1">
              <span class="text-xs font-semibold">AI 守門人</span>
              <div class="bg-muted/60 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-muted-foreground/60 animate-bounce [animation-delay:0ms]" />
                <span class="w-1.5 h-1.5 rounded-full bg-muted-foreground/60 animate-bounce [animation-delay:150ms]" />
                <span class="w-1.5 h-1.5 rounded-full bg-muted-foreground/60 animate-bounce [animation-delay:300ms]" />
              </div>
            </div>
          </div>

          <div ref="bottomRef" />
        </main>

        <!-- 輸入區 -->
        <footer class="shrink-0 border-t bg-card/80 backdrop-blur-sm px-4 py-3">
          <div class="max-w-4xl mx-auto flex items-end gap-2">
            <div class="flex-1 relative">
              <Textarea
                v-model="inputText"
                placeholder="輸入你的行動或對話..."
                class="resize-none min-h-[44px] max-h-36 pr-2 py-2.5 text-sm"
                :rows="1"
                @keydown.enter.exact.prevent="sendMessage"
                @input="autoResize"
              />
            </div>
            <Button
              size="icon"
              class="h-11 w-11 shrink-0"
              :disabled="!inputText.trim() || isAiTyping"
              @click="sendMessage"
            >
              <SendHorizonal class="size-4" />
            </Button>
          </div>
          <p class="text-center text-[10px] text-muted-foreground/50 mt-2">Enter 發送 · Shift+Enter 換行</p>
        </footer>
      </template>

      <!-- 已結束 -->
      <div v-else class="flex-1 flex flex-col items-center justify-center gap-4 p-8 text-center text-muted-foreground">
        <p class="text-lg font-semibold">跑團已結束</p>
        <RouterLink to="/rooms"><Button variant="outline">返回房間列表</Button></RouterLink>
      </div>

    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, CheckCircle2, Circle, Copy, Play, RefreshCw, SendHorizonal, UserMinus } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Spinner } from '@/components/ui/spinner'
import { useAppWebSocket } from '@/composables/useAppWebSocket'
import { AuthService, RoomsService, type AppFeaturesRoomsSchemasResponsesRoomDetailResponse, type RoomParticipantResponse } from '@/services'

type RoomDetail = AppFeaturesRoomsSchemasResponsesRoomDetailResponse

interface UiMessage {
  id: string
  role: 'ai' | 'player' | 'system'
  content: string
  time: string
  sender_id?: string
}

const route = useRoute()
const roomId = String(route.params.room_id ?? '')

const isLoading = ref(true)
const loadError = ref<string | null>(null)
const room = ref<RoomDetail | null>(null)
const currentUserId = ref<string | null>(null)

const actionError = ref<string | null>(null)
const copiedToast = ref(false)
const isRegenerating = ref(false)
const isStarting = ref(false)
const isKicking = ref<string | null>(null)
const isSettingReady = ref(false)

// 聊天
const inputText = ref('')
const isAiTyping = ref(false)
const messageListRef = ref<HTMLElement | null>(null)
const bottomRef = ref<HTMLElement | null>(null)
const messages = ref<UiMessage[]>([])

const isHost = computed(() => room.value?.host_id === currentUserId.value)

const myParticipant = computed((): RoomParticipantResponse | undefined =>
  room.value?.participants.find((p) => p.user_id === currentUserId.value),
)

const allReady = computed(() =>
  (room.value?.participants.length ?? 0) > 0 &&
  room.value!.participants.every((p) => p.is_ready),
)

const notReadyCount = computed(() =>
  room.value?.participants.filter((p) => !p.is_ready).length ?? 0,
)

function colorFromId(id: string) {
  let hash = 0
  for (let i = 0; i < id.length; i++) hash = (hash * 31 + id.charCodeAt(i)) | 0
  const hue = Math.abs(hash) % 360
  return `hsl(${hue} 80% 45%)`
}

function now() {
  return new Date().toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
}

async function bootstrap() {
  isLoading.value = true
  loadError.value = null
  try {
    const [roomRes, meRes] = await Promise.all([
      RoomsService.getRoom({ path: { room_id: roomId } }),
      AuthService.me(),
    ])
    room.value = roomRes.data
    currentUserId.value = String(meRes.data.id)

    if (room.value.status === 'RUNNING') {
      await loadMessages()
    }
  } catch (e) {
    const status = (e as { response?: { status?: number } })?.response?.status
    const detail = (e as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
    loadError.value = status === 403
      ? '你不是此房間的參與者'
      : typeof detail === 'string'
        ? detail
        : '無法載入房間'
  } finally {
    isLoading.value = false
  }
}

async function loadMessages() {
  try {
    const res = await RoomsService.listRoomMessages({ path: { room_id: roomId } })
    messages.value = res.data.map((m) => ({
      id: m.id,
      role: 'player' as const,
      content: m.content,
      time: new Date(m.created_at).toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' }),
      sender_id: String(m.sender_id),
    }))
    await scrollToBottom()
  } catch {
    // ignore
  }
}

async function handleRegenerateInvite() {
  isRegenerating.value = true
  actionError.value = null
  try {
    const res = await RoomsService.regenerateInviteCode({ path: { room_id: roomId } })
    room.value = res.data
  } catch (e) {
    actionError.value = '重新生成邀請碼失敗'
  } finally {
    isRegenerating.value = false
  }
}

async function copyInviteCode() {
  if (!room.value) return
  try {
    await navigator.clipboard.writeText(room.value.invite_code)
    copiedToast.value = true
    setTimeout(() => { copiedToast.value = false }, 2000)
  } catch {
    // fallback: select text
  }
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

// WebSocket
const ws = useAppWebSocket()
let unsubscribeWs: (() => void) | null = null

onMounted(async () => {
  await bootstrap()
  await ws.connect()
  unsubscribeWs = ws.onType('rooms.test_message', (payload) => {
    if (String(payload.room_id ?? '') !== roomId) return
    const content = typeof payload.content === 'string' ? payload.content : ''
    if (!content) return
    isAiTyping.value = false
    messages.value.push({ id: `m${Date.now()}`, role: 'ai', content, time: now() })
    void scrollToBottom()
  })
})

onUnmounted(() => {
  unsubscribeWs?.()
})

async function sendMessage(e: Event) {
  const text = inputText.value.trim()
  if (!text || isAiTyping.value) return

  messages.value.push({
    id: `m${Date.now()}`,
    role: 'player',
    content: text,
    time: now(),
    sender_id: currentUserId.value ?? undefined,
  })
  inputText.value = ''
  await nextTick()
  autoResize(e)
  await scrollToBottom()

  isAiTyping.value = true
  await scrollToBottom()

  try {
    await RoomsService.sendRoomMessage({
      path: { room_id: roomId },
      body: { content: text },
    })
  } catch {
    isAiTyping.value = false
  }
}

async function scrollToBottom() {
  await nextTick()
  bottomRef.value?.scrollIntoView({ behavior: 'smooth' })
}

function autoResize(e: Event) {
  const el = e.target as HTMLTextAreaElement
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 144) + 'px'
}
</script>
