<template>
  <div class="min-h-screen flex flex-col bg-background text-foreground">
    <AppHeader />

    <main class="flex-1 p-6">
      <div class="max-w-4xl mx-auto space-y-10">

        <!-- 歡迎區塊 -->
        <div class="pt-6 space-y-2">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-linear-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-sm shrink-0">
              <svg class="w-5 h-5 text-white" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26C17.81 13.47 19 11.38 19 9c0-3.87-3.13-7-7-7zm0 12c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z" />
              </svg>
            </div>
            <div>
              <h1 class="text-2xl font-bold tracking-tight">歡迎來到 Lorrator</h1>
              <p class="text-sm text-muted-foreground">你的 TRPG 跑團助手</p>
            </div>
          </div>
        </div>

        <!-- 快速入口 -->
        <section class="space-y-3">
          <h2 class="text-sm font-semibold text-muted-foreground uppercase tracking-wider">快速入口</h2>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">

            <!-- 我的房間 -->
            <RouterLink to="/rooms" class="group">
              <Card class="h-full hover:shadow-md hover:border-primary/30 transition-all cursor-pointer">
                <CardContent class="p-5 space-y-3">
                  <div class="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                    <DoorOpen class="size-5 text-green-600 dark:text-green-400" />
                  </div>
                  <div>
                    <div class="font-semibold text-sm group-hover:text-primary transition-colors">我的房間</div>
                    <p class="text-xs text-muted-foreground mt-0.5">進入正在進行的跑團</p>
                  </div>
                  <div class="flex items-center gap-1 text-xs text-muted-foreground">
                    <ArrowRight class="size-3" />
                    <span>查看房間</span>
                  </div>
                </CardContent>
              </Card>
            </RouterLink>

            <!-- 劇本庫 -->
            <RouterLink to="/scenarios" class="group">
              <Card class="h-full hover:shadow-md hover:border-primary/30 transition-all cursor-pointer">
                <CardContent class="p-5 space-y-3">
                  <div class="w-10 h-10 rounded-lg bg-violet-500/10 flex items-center justify-center">
                    <BookOpen class="size-5 text-violet-600 dark:text-violet-400" />
                  </div>
                  <div>
                    <div class="font-semibold text-sm group-hover:text-primary transition-colors">劇本庫</div>
                    <p class="text-xs text-muted-foreground mt-0.5">瀏覽與建立跑團劇本</p>
                  </div>
                  <div class="flex items-center gap-1 text-xs text-muted-foreground">
                    <ArrowRight class="size-3" />
                    <span>查看劇本</span>
                  </div>
                </CardContent>
              </Card>
            </RouterLink>

            <!-- 角色卡 -->
            <RouterLink to="/characters" class="group">
              <Card class="h-full hover:shadow-md hover:border-primary/30 transition-all cursor-pointer">
                <CardContent class="p-5 space-y-3">
                  <div class="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
                    <User class="size-5 text-amber-600 dark:text-amber-400" />
                  </div>
                  <div>
                    <div class="font-semibold text-sm group-hover:text-primary transition-colors">角色卡</div>
                    <p class="text-xs text-muted-foreground mt-0.5">管理你的 TRPG 角色</p>
                  </div>
                  <div class="flex items-center gap-1 text-xs text-muted-foreground">
                    <ArrowRight class="size-3" />
                    <span>查看角色</span>
                  </div>
                </CardContent>
              </Card>
            </RouterLink>

          </div>
        </section>

        <!-- 統計數字 -->
        <section class="space-y-3">
          <h2 class="text-sm font-semibold text-muted-foreground uppercase tracking-wider">總覽</h2>
          <div class="grid grid-cols-3 gap-4">
            <Card>
              <CardContent class="p-5">
                <div class="text-2xl font-bold">
                  <span v-if="isLoadingStats" class="inline-block w-8 h-6 bg-muted rounded animate-pulse" />
                  <span v-else>{{ stats.rooms }}</span>
                </div>
                <div class="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                  <DoorOpen class="size-3" />
                  個房間
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent class="p-5">
                <div class="text-2xl font-bold">
                  <span v-if="isLoadingStats" class="inline-block w-8 h-6 bg-muted rounded animate-pulse" />
                  <span v-else>{{ stats.scenarios }}</span>
                </div>
                <div class="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                  <BookOpen class="size-3" />
                  個劇本
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent class="p-5">
                <div class="text-2xl font-bold">
                  <span v-if="isLoadingStats" class="inline-block w-8 h-6 bg-muted rounded animate-pulse" />
                  <span v-else>{{ stats.characters }}</span>
                </div>
                <div class="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                  <User class="size-3" />
                  個角色
                </div>
              </CardContent>
            </Card>
          </div>
        </section>

        <!-- 進行中的房間 -->
        <section class="space-y-3">
          <div class="flex items-center justify-between">
            <h2 class="text-sm font-semibold text-muted-foreground uppercase tracking-wider">進行中的跑團</h2>
            <RouterLink to="/rooms" class="text-xs text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1">
              查看全部
              <ArrowRight class="size-3" />
            </RouterLink>
          </div>

          <!-- 載入中 -->
          <div v-if="isLoadingRooms" class="grid gap-3">
            <Card v-for="n in 2" :key="n">
              <CardContent class="p-4">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-lg bg-muted animate-pulse shrink-0" />
                  <div class="flex-1 space-y-1.5">
                    <div class="h-3.5 w-32 bg-muted rounded animate-pulse" />
                    <div class="h-3 w-48 bg-muted rounded animate-pulse" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <!-- 有資料 -->
          <div v-else-if="runningRooms.length > 0" class="grid gap-3">
            <Card
              v-for="room in runningRooms"
              :key="room.id"
              class="hover:shadow-md transition-shadow cursor-pointer"
              @click="router.push(`/rooms/${room.id}`)"
            >
              <CardContent class="p-4">
                <div class="flex items-center gap-3">
                  <div
                    class="w-9 h-9 rounded-lg flex items-center justify-center text-white text-xs font-bold shrink-0"
                    :style="{ backgroundColor: colorFromId(room.id) }"
                  >
                    {{ room.name.charAt(0) }}
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2">
                      <span class="font-semibold text-sm">{{ room.name }}</span>
                      <span class="w-2 h-2 rounded-full bg-green-500 shrink-0" />
                      <span class="text-[10px] text-green-600 dark:text-green-400 font-medium">跑團中</span>
                    </div>
                    <p class="text-xs text-muted-foreground truncate mt-0.5">{{ room.description || '無簡介' }}</p>
                  </div>
                  <Button variant="outline" size="sm" class="shrink-0 gap-1.5">
                    <DoorOpen class="size-3.5" />
                    進入
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          <!-- 空狀態 -->
          <Card v-else class="border-dashed">
            <CardContent class="p-8 text-center space-y-2">
              <DoorOpen class="size-8 text-muted-foreground/30 mx-auto" />
              <p class="text-sm text-muted-foreground">目前沒有進行中的跑團</p>
              <RouterLink to="/scenarios">
                <Button size="sm" variant="outline" class="gap-1.5 mt-1">
                  <BookOpen class="size-3.5" />
                  瀏覽劇本來開始
                </Button>
              </RouterLink>
            </CardContent>
          </Card>
        </section>

      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, BookOpen, DoorOpen, User } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import AppHeader from '@/components/layout/AppHeader.vue'
import { CharactersService, MeService, ScenariosService, type RoomResponse } from '@/services'
import { colorFromId } from '@/utils/color'

const router = useRouter()

const isLoadingRooms = ref(false)
const rooms = ref<RoomResponse[]>([])

const isLoadingStats = ref(false)
const stats = ref({ rooms: 0, scenarios: 0, characters: 0 })

const runningRooms = computed(() =>
  rooms.value.filter((r) => r.status === 'RUNNING').slice(0, 3),
)

async function loadData() {
  isLoadingRooms.value = true
  isLoadingStats.value = true
  try {
    const [roomsRes, scenariosRes, charactersRes] = await Promise.allSettled([
      MeService.listMyRooms(),
      ScenariosService.listScenarios(),
      CharactersService.listCharacters(),
    ])

    if (roomsRes.status === 'fulfilled') {
      rooms.value = roomsRes.value.data ?? []
    }

    stats.value = {
      rooms: roomsRes.status === 'fulfilled' ? (roomsRes.value.data?.length ?? 0) : 0,
      scenarios: scenariosRes.status === 'fulfilled' ? (scenariosRes.value.data?.length ?? 0) : 0,
      characters: charactersRes.status === 'fulfilled' ? (charactersRes.value.data?.length ?? 0) : 0,
    }
  } finally {
    isLoadingRooms.value = false
    isLoadingStats.value = false
  }
}

onMounted(loadData)
</script>
