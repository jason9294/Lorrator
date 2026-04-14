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
        <span class="text-sm font-semibold">我的房間</span>
      </div>

      <div class="ml-auto flex items-center gap-2 shrink-0">
        <RouterLink to="/scenarios">
          <Button variant="outline" size="sm" class="gap-2">
            <BookOpen class="size-3.5" />
            劇本列表
          </Button>
        </RouterLink>
      </div>
    </header>

    <!-- 主體 -->
    <main class="flex-1 p-6">
      <div class="max-w-4xl mx-auto space-y-6">

        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-bold">我的跑團房間</h2>
            <p class="text-sm text-muted-foreground mt-0.5">在這裡繼續你的冒險</p>
          </div>
          <Badge variant="secondary" class="gap-1">
            <DoorOpen class="size-3" />
            {{ rooms.length }} 個房間
          </Badge>
        </div>

        <!-- 房間清單 -->
        <div v-if="rooms.length > 0" class="grid gap-4">
          <Card v-for="room in rooms" :key="room.id" class="hover:shadow-md transition-shadow">
            <CardContent class="p-5">
              <div class="flex items-center gap-4">
                <!-- 狀態色點 -->
                <div class="relative shrink-0">
                  <div
                    class="w-10 h-10 rounded-lg flex items-center justify-center text-white text-sm font-bold"
                    :style="{ backgroundColor: room.color }"
                  >
                    {{ room.scenarioTitle.charAt(0) }}
                  </div>
                  <span
                    class="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-background"
                    :class="room.status === 'active' ? 'bg-green-500' : 'bg-muted-foreground/40'"
                  />
                </div>

                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 flex-wrap">
                    <h3 class="font-semibold text-sm">{{ room.name }}</h3>
                    <Badge
                      :variant="room.status === 'active' ? 'default' : 'secondary'"
                      class="text-[10px]"
                    >
                      {{ room.status === 'active' ? '進行中' : '已結束' }}
                    </Badge>
                  </div>
                  <p class="text-xs text-muted-foreground mt-0.5">{{ room.scenarioTitle }} · {{ room.system }}</p>
                  <div class="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                    <span class="flex items-center gap-1">
                      <Clock class="size-3" />
                      最後活動：{{ room.lastActive }}
                    </span>
                    <span class="flex items-center gap-1">
                      <MessageSquare class="size-3" />
                      {{ room.messageCount }} 則訊息
                    </span>
                  </div>
                </div>

                <!-- 進入按鈕 -->
                <RouterLink :to="`/rooms/${room.id}`" class="shrink-0">
                  <Button size="sm" class="gap-1.5">
                    <DoorOpen class="size-3.5" />
                    進入房間
                  </Button>
                </RouterLink>
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- 空狀態 -->
        <div
          v-else
          class="flex flex-col items-center justify-center py-24 text-center border rounded-xl border-dashed"
        >
          <DoorOpen class="size-12 text-muted-foreground/30 mb-4" />
          <p class="font-medium text-muted-foreground">還沒有房間</p>
          <p class="text-sm text-muted-foreground/60 mt-1 mb-4">前往劇本列表，創建你的第一個跑團房間</p>
          <RouterLink to="/scenarios">
            <Button size="sm" class="gap-1.5">
              <BookOpen class="size-3.5" />
              瀏覽劇本
            </Button>
          </RouterLink>
        </div>

      </div>
    </main>

  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { BookOpen, Clock, DoorOpen, MessageSquare } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'

const rooms = ref([
  {
    id: 'room-001',
    name: '失落的藝術家',
    scenarioTitle: '克蘇魯的呼喚',
    system: 'COC 7e',
    status: 'active',
    lastActive: '10 分鐘前',
    messageCount: 42,
    color: '#7c3aed',
  },
  {
    id: 'room-002',
    name: '新上海滲透行動',
    scenarioTitle: '暗影奔馳：新上海',
    system: 'Shadowrun 6e',
    status: 'active',
    lastActive: '2 小時前',
    messageCount: 128,
    color: '#0891b2',
  },
  {
    id: 'room-003',
    name: '矮人礦坑探險',
    scenarioTitle: '龍與地下城：迷失礦坑',
    system: 'D&D 5e',
    status: 'ended',
    lastActive: '3 天前',
    messageCount: 87,
    color: '#b45309',
  },
])
</script>
