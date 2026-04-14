<template>
  <div class="h-screen flex flex-col bg-background text-foreground overflow-hidden">

    <!-- 頂部導覽列 -->
    <header class="shrink-0 flex items-center gap-3 px-5 h-13 border-b bg-card/80 backdrop-blur-sm z-30">
      <RouterLink to="/rooms">
        <Button variant="ghost" size="icon-sm" class="text-muted-foreground">
          <ArrowLeft class="size-4" />
        </Button>
      </RouterLink>

      <div class="w-px h-5 bg-border shrink-0" />

      <div class="flex items-center gap-2.5 flex-1 min-w-0">
        <div class="relative shrink-0">
          <div class="w-8 h-8 rounded-lg bg-linear-to-br from-violet-500 to-indigo-600 flex items-center justify-center text-white text-xs font-bold shadow-sm">
            失
          </div>
          <span class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-green-500 border-2 border-background" />
        </div>
        <div class="flex flex-col leading-none min-w-0">
          <span class="text-sm font-semibold truncate">{{ roomName }}</span>
          <span class="text-[10px] text-muted-foreground">克蘇魯的呼喚 · COC 7e</span>
        </div>
      </div>

      <div class="flex items-center gap-2 shrink-0">
        <Badge variant="outline" class="gap-1 text-green-600 border-green-500/30 bg-green-500/10">
          <span class="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
          AI 守門人在線
        </Badge>
      </div>
    </header>

    <!-- 訊息列表 -->
    <main ref="messageListRef" class="flex-1 overflow-y-auto px-4 py-4 space-y-4 scroll-smooth">

      <!-- 日期分隔 -->
      <div class="flex items-center gap-3 py-1">
        <div class="flex-1 h-px bg-border" />
        <span class="text-[10px] text-muted-foreground px-2">2026年4月14日</span>
        <div class="flex-1 h-px bg-border" />
      </div>

      <!-- 系統提示訊息 -->
      <div class="flex justify-center">
        <div class="bg-muted/50 text-muted-foreground text-xs px-3 py-1.5 rounded-full">
          跑團房間已建立，AI 守門人正在等待你的行動...
        </div>
      </div>

      <!-- 訊息氣泡 -->
      <template v-for="msg in messages" :key="msg.id">

        <!-- AI 訊息 -->
        <div v-if="msg.role === 'ai'" class="flex items-start gap-3 max-w-[85%]">
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
          <div class="w-8 h-8 rounded-full bg-muted flex items-center justify-center shrink-0 mt-0.5">
            <User class="size-4 text-muted-foreground" />
          </div>
          <div class="flex flex-col gap-1 items-end">
            <div class="flex items-center gap-2">
              <span class="text-[10px] text-muted-foreground">{{ msg.time }}</span>
              <span class="text-xs font-semibold">你</span>
            </div>
            <div class="bg-primary text-primary-foreground rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap">
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

      <!-- 底部錨點 -->
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
            @keydown.enter.shift.exact="inputText += '\n'"
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
      <p class="text-center text-[10px] text-muted-foreground/50 mt-2">
        Enter 發送 · Shift+Enter 換行
      </p>
    </footer>

  </div>
</template>

<script setup lang="ts">
import { nextTick, ref } from 'vue'
import { ArrowLeft, SendHorizonal, User } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'

interface Message {
  id: string
  role: 'ai' | 'player'
  content: string
  time: string
}

const roomName = ref('失落的藝術家')
const inputText = ref('')
const isAiTyping = ref(false)
const messageListRef = ref<HTMLElement | null>(null)
const bottomRef = ref<HTMLElement | null>(null)

function now() {
  return new Date().toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
}

const messages = ref<Message[]>([
  {
    id: 'm0',
    role: 'ai',
    content: `歡迎來到「失落的藝術家」。\n\n今夜的阿卡姆瀰漫著濃霧，碼頭的燈光在霧中若隱若現。你剛剛收到了一封來自老友瑪格麗特的信，信中她語氣焦急，提到教授威廉斯已失蹤三週，警方不願深究……\n\n你打算怎麼做？`,
    time: '20:00',
  },
])

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || isAiTyping.value) return

  messages.value.push({
    id: `m${Date.now()}`,
    role: 'player',
    content: text,
    time: now(),
  })
  inputText.value = ''
  await scrollToBottom()

  isAiTyping.value = true
  await scrollToBottom()

  // TODO: 替換為實際 AI API 呼叫
  await new Promise((resolve) => setTimeout(resolve, 1200 + Math.random() * 800))

  const replies = [
    '你穿上外套，走出公寓。阿卡姆的街道在雨夜中顯得格外陰森，你的腳步聲在石板路上迴響……\n\n前往教授的辦公室，你需要進行一次【偵查】技能檢定。請告訴我你的偵查技能值。',
    '瑪格麗特焦急地看著你，她的眼眶微微泛紅，「教授最後一次聯繫是在三週前……他說發現了什麼東西，在那座廢棄倉庫附近。」\n\n她遞給你一個皺巴巴的信封，「這是他寄給我的最後一封信。」',
    '你打開信封，裡面是幾頁潦草的筆記，充斥著奇異的符號和碎片化的描述。有一行字被重重劃了底線：\n\n「它們在星光下甦醒，不可名狀，不可言說……」\n\n你的理智受到衝擊。請進行【心理學】檢定。',
  ]

  isAiTyping.value = false
  messages.value.push({
    id: `m${Date.now()}`,
    role: 'ai',
    content: replies[Math.floor(Math.random() * replies.length)],
    time: now(),
  })
  await scrollToBottom()
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
