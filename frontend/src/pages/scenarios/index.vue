<template>
  <div class="min-h-screen flex flex-col bg-background text-foreground">

    <!-- 頂部導覽列 -->
    <header class="shrink-0 flex items-center gap-3 px-5 h-13 border-b bg-card/80 backdrop-blur-sm z-30">
      <div class="flex items-center gap-2.5">
        <div class="w-7 h-7 rounded-lg bg-linear-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-sm shrink-0">
          <svg class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26C17.81 13.47 19 11.38 19 9c0-3.87-3.13-7-7-7zm0 12c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/>
          </svg>
        </div>
        <span class="text-sm font-semibold">劇本列表</span>
      </div>

      <div class="ml-auto flex items-center gap-2 shrink-0">
        <RouterLink to="/rooms">
          <Button variant="outline" size="sm" class="gap-2">
            <DoorOpen class="size-3.5" />
            我的房間
          </Button>
        </RouterLink>
        <Button size="sm" class="gap-2" @click="createDialogOpen = true">
          <Plus class="size-3.5" />
          創建劇本
        </Button>
      </div>
    </header>

    <!-- 創建劇本 Modal -->
    <Dialog v-model:open="createDialogOpen">
      <DialogContent class="sm:max-w-sm">
        <DialogHeader>
          <DialogTitle>創建新劇本</DialogTitle>
          <DialogDescription>輸入劇本名稱後即可建立，建立後可在詳情頁繼續編輯。</DialogDescription>
        </DialogHeader>
        <div class="space-y-2 py-2">
          <Label for="new-scenario-name">劇本名稱</Label>
          <Input
            id="new-scenario-name"
            v-model="newScenarioName"
            placeholder="例如：克蘇魯的呼喚"
            :disabled="isCreatingScenario"
            @keydown.enter="handleCreateScenario"
          />
        </div>
        <DialogFooter>
          <Button variant="outline" :disabled="isCreatingScenario" @click="createDialogOpen = false">
            取消
          </Button>
          <Button :disabled="!newScenarioName.trim() || isCreatingScenario" @click="handleCreateScenario">
            <Spinner v-if="isCreatingScenario" class="size-4" />
            <Plus v-else class="size-4" />
            {{ isCreatingScenario ? '建立中...' : '建立' }}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    <!-- 主體 -->
    <main class="flex-1 p-6">
      <div class="max-w-4xl mx-auto space-y-6">

        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-bold">所有劇本</h2>
            <p class="text-sm text-muted-foreground mt-0.5">選擇一個劇本開始你的冒險</p>
          </div>
          <Badge variant="secondary" class="gap-1">
            <BookOpen class="size-3" />
            {{ scenarios.length }} 個劇本
          </Badge>
        </div>

        <!-- 劇本清單 -->
        <div class="grid gap-4">
          <Card v-for="scenario in scenarios" :key="scenario.id" class="hover:shadow-md transition-shadow">
            <CardContent class="p-5">
              <div class="flex items-start justify-between gap-4">
                <div class="flex items-start gap-4 flex-1 min-w-0">
                  <!-- 類型圖示 -->
                  <div
                    class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0 text-white text-sm font-bold"
                    :style="{ backgroundColor: scenario.color }"
                  >
                    {{ scenario.title.charAt(0) }}
                  </div>

                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 flex-wrap">
                      <h3 class="font-semibold text-base">{{ scenario.title }}</h3>
                      <Badge variant="outline" class="text-[10px]">{{ scenario.system }}</Badge>
                    </div>
                    <p class="text-sm text-muted-foreground mt-1 line-clamp-2">{{ scenario.description }}</p>
                    <div class="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                      <span class="flex items-center gap-1">
                        <Users class="size-3" />
                        {{ scenario.playerCount }} 人
                      </span>
                      <span class="flex items-center gap-1">
                        <Clock class="size-3" />
                        {{ scenario.duration }}
                      </span>
                    </div>
                  </div>
                </div>

                <!-- 操作按鈕 -->
                <div class="flex items-center gap-2 shrink-0">
                  <RouterLink :to="`/scenarios/${scenario.id}`">
                    <Button variant="outline" size="sm" class="gap-1.5">
                      <Info class="size-3.5" />
                      詳情
                    </Button>
                  </RouterLink>
                  <Button
                    size="sm"
                    class="gap-1.5"
                    :disabled="creatingRoomId === scenario.id"
                    @click="createRoom(scenario.id)"
                  >
                    <Spinner v-if="creatingRoomId === scenario.id" class="size-3.5" />
                    <Plus v-else class="size-3.5" />
                    {{ creatingRoomId === scenario.id ? '建立中...' : '創建房間' }}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

      </div>
    </main>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { BookOpen, Clock, DoorOpen, Info, Plus, Users } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Spinner } from '@/components/ui/spinner'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

const router = useRouter()

const creatingRoomId = ref<string | null>(null)
const createDialogOpen = ref(false)
const newScenarioName = ref('')
const isCreatingScenario = ref(false)

const COLORS = ['#7c3aed', '#0891b2', '#b45309', '#be123c', '#10b981', '#f97316', '#6366f1']

async function handleCreateScenario() {
  if (!newScenarioName.value.trim()) return
  isCreatingScenario.value = true
  try {
    // TODO: 替換為實際 API 呼叫
    await new Promise((resolve) => setTimeout(resolve, 800))
    const scenarioId = `s-${Date.now()}`
    scenarios.value.unshift({
      id: scenarioId,
      title: newScenarioName.value.trim(),
      system: '—',
      description: '劇本尚未新增簡介，請至詳情頁編輯。',
      playerCount: '—',
      duration: '—',
      color: COLORS[Math.floor(Math.random() * COLORS.length)],
    })
    createDialogOpen.value = false
    newScenarioName.value = ''
    router.push(`/scenarios/${scenarioId}`)
  } finally {
    isCreatingScenario.value = false
  }
}

const scenarios = ref([
  {
    id: 's1',
    title: '克蘇魯的呼喚',
    system: 'COC 7e',
    description: '在阿卡姆的黑暗深處，古老的存在正在甦醒。調查員們必須面對超越人類理解的恐懼，揭開隱藏在小鎮背後的可怕秘密。',
    playerCount: '2-5',
    duration: '4-6 小時',
    color: '#7c3aed',
  },
  {
    id: 's2',
    title: '暗影奔馳：新上海',
    system: 'Shadowrun 6e',
    description: '2080年的新上海，企業與黑市之間的界線早已模糊。一支影子傭兵小隊接下了一個看似簡單的滲透任務，卻發現背後牽涉到城市最大的陰謀。',
    playerCount: '3-5',
    duration: '6-8 小時',
    color: '#0891b2',
  },
  {
    id: 's3',
    title: '龍與地下城：迷失礦坑',
    system: 'D&D 5e',
    description: '一座廢棄的矮人礦坑中藏有傳說中的寶藏，但同時也住著未知的危險。英雄們能否在黑暗中找到財富，並活著離開？',
    playerCount: '4-6',
    duration: '3-4 小時',
    color: '#b45309',
  },
  {
    id: 's4',
    title: '吸血鬼：假面舞會',
    system: 'VtM 5e',
    description: '在上海的地下夜場，古老的吸血鬼氏族正進行著隱秘的權力鬥爭。作為剛覺醒的新生血族，你必須在各方勢力之間找到生存之道。',
    playerCount: '3-5',
    duration: '5-7 小時',
    color: '#be123c',
  },
])

async function createRoom(scenarioId: string) {
  creatingRoomId.value = scenarioId
  try {
    // TODO: 替換為實際 API 呼叫
    await new Promise((resolve) => setTimeout(resolve, 800))
    const roomId = `room-${Date.now()}`
    router.push(`/rooms/${roomId}`)
  } finally {
    creatingRoomId.value = null
  }
}
</script>
