<template>
  <div class="min-h-screen flex flex-col bg-background text-foreground">
    <AppHeader>
      <template #actions>
        <Button variant="outline" size="sm" class="gap-2" @click="joinDialogOpen = true">
          <LogIn class="size-3.5" />
          加入房間
        </Button>
      </template>
    </AppHeader>

    <!-- 加入房間 Dialog -->
    <div
      v-if="joinDialogOpen"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
      @click.self="joinDialogOpen = false"
    >
      <div class="bg-card border rounded-xl shadow-xl w-full max-w-sm p-6 space-y-4">
        <h2 class="text-lg font-semibold">透過邀請碼加入房間</h2>
        <div>
          <label class="text-xs font-medium text-muted-foreground mb-1.5 block">邀請碼</label>
          <input
            v-model="joinCode"
            class="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-primary uppercase tracking-widest font-mono"
            placeholder="輸入 8 位邀請碼"
            maxlength="16"
            @keydown.enter="handleJoinRoom"
          />
        </div>
        <p v-if="joinError" class="text-xs text-destructive">{{ joinError }}</p>
        <div class="flex justify-end gap-2 pt-1">
          <Button variant="outline" size="sm" @click="joinDialogOpen = false">取消</Button>
          <Button size="sm" :disabled="isJoining || !joinCode.trim()" @click="handleJoinRoom">
            <Spinner v-if="isJoining" class="size-3.5 mr-1.5" />
            加入
          </Button>
        </div>
      </div>
    </div>

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
            {{ isLoading ? '載入中…' : `${rooms.length} 個房間` }}
          </Badge>
        </div>

        <!-- 載入中 -->
        <div v-if="isLoading" class="grid gap-4">
          <Card v-for="n in 3" :key="n">
            <CardContent class="p-5">
              <div class="flex items-center gap-4">
                <div class="w-10 h-10 rounded-lg bg-muted animate-pulse shrink-0" />
                <div class="flex-1 space-y-2">
                  <div class="h-4 w-32 bg-muted rounded animate-pulse" />
                  <div class="h-3 w-48 bg-muted rounded animate-pulse" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- 房間清單 -->
        <div v-else-if="rooms.length > 0" class="grid gap-4">
          <Card v-for="room in rooms" :key="room.id" class="hover:shadow-md transition-shadow">
            <CardContent class="p-5">
              <div class="flex items-center gap-4">
                <!-- 狀態色點 -->
                <div class="relative shrink-0">
                  <div
                    class="w-10 h-10 rounded-lg flex items-center justify-center text-white text-sm font-bold"
                    :style="{ backgroundColor: colorFromId(room.id) }"
                  >
                    {{ room.name.charAt(0) }}
                  </div>
                  <span
                    class="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-background"
                    :class="
                      room.status === 'RUNNING'
                        ? 'bg-green-500'
                        : room.status === 'COMPLETED'
                          ? 'bg-muted-foreground/40'
                          : 'bg-yellow-500'
                    "
                  />
                </div>

                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 flex-wrap">
                    <h3 class="font-semibold text-sm">{{ room.name }}</h3>
                    <Badge
                      :variant="room.status === 'RUNNING' ? 'default' : 'secondary'"
                      class="text-[10px]"
                    >
                      {{ statusLabel(room.status) }}
                    </Badge>
                  </div>
                  <p class="text-xs text-muted-foreground mt-0.5">
                    {{ room.description || '無簡介' }}
                  </p>
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
          <p class="text-sm text-muted-foreground/60 mt-1 mb-4">
            可以從劇本列表創建房間，或透過邀請碼加入
          </p>
          <div class="flex items-center gap-2">
            <Button size="sm" class="gap-1.5" variant="outline" @click="joinDialogOpen = true">
              <LogIn class="size-3.5" />
              加入房間
            </Button>
            <RouterLink to="/scenarios">
              <Button size="sm" class="gap-1.5">
                <BookOpen class="size-3.5" />
                瀏覽劇本
              </Button>
            </RouterLink>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useAsyncState, useToggle } from '@vueuse/core'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { DoorOpen, LogIn } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import AppHeader from '@/components/layout/AppHeader.vue'
import { Card, CardContent } from '@/components/ui/card'
import { Spinner } from '@/components/ui/spinner'
import { MeService, RoomsService, type RoomStatus } from '@/services'
import { colorFromId } from '@/utils/color'

const router = useRouter()

const { state: rooms, isLoading } = useAsyncState(
  async () => (await MeService.listMyRooms()).data ?? [],
  [],
  {
    immediate: true,
  },
)

const [joinDialogOpen] = useToggle(false)
const joinCode = ref('')
const isJoining = ref(false)
const joinError = ref<string | null>(null)

function statusLabel(status: RoomStatus) {
  if (status === 'RUNNING') return '跑團中'
  if (status === 'COMPLETED') return '已結束'
  return '準備中'
}

async function handleJoinRoom() {
  const code = joinCode.value.trim().toUpperCase()
  if (!code) return
  isJoining.value = true
  joinError.value = null
  try {
    const res = await RoomsService.joinRoom({ body: { invite_code: code } })
    joinDialogOpen.value = false
    joinCode.value = ''
    router.push(`/rooms/${res.data.id}`)
  } catch (e) {
    const detail = (e as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
    joinError.value = typeof detail === 'string' ? detail : '邀請碼無效或房間不存在'
  } finally {
    isJoining.value = false
  }
}
</script>
