<template>
  <div class="min-h-screen flex flex-col bg-background text-foreground">
    <!-- 頂部導覽列 -->
    <header
      class="shrink-0 flex items-center gap-3 px-5 h-13 border-b bg-card/80 backdrop-blur-sm z-30"
    >
      <div class="flex items-center gap-2.5">
        <div
          class="w-7 h-7 rounded-lg bg-linear-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-sm shrink-0"
        >
          <svg class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="currentColor">
            <path
              d="M12 2C8.13 2 5 5.13 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26C17.81 13.47 19 11.38 19 9c0-3.87-3.13-7-7-7zm0 12c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"
            />
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

    <CreateScenarioDialog
      v-model:open="createDialogOpen"
      v-model:name="newScenarioName"
      v-model:system="newScenarioSystem"
      v-model:description="newScenarioDescription"
      v-model:min-players="newScenarioMinPlayers"
      v-model:max-players="newScenarioMaxPlayers"
      v-model:min-hours="newScenarioMinHours"
      v-model:max-hours="newScenarioMaxHours"
      :is-submitting="isCreatingScenario"
      :error-message="createScenarioError"
      @submit="handleCreateScenario"
    />

    <!-- 主體 -->
    <main class="flex-1 p-6">
      <div class="max-w-4xl mx-auto space-y-6">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-bold">劇本列表</h2>
            <p class="text-sm text-muted-foreground mt-0.5">草稿僅自己可見，已發布可供所有人創建房間</p>
          </div>
          <Badge variant="secondary" class="gap-1">
            <BookOpen class="size-3" />
            {{ isLoadingScenarios ? '載入中…' : `${scenarios.length} 個劇本` }}
          </Badge>
        </div>

        <!-- 劇本清單 -->
        <div class="grid gap-4">
          <!-- 載入中 -->
          <template v-if="isLoadingScenarios">
            <Card v-for="n in 6" :key="`loading-${n}`" class="transition-shadow">
              <CardContent class="p-5">
                <div class="flex items-start justify-between gap-4">
                  <div class="flex items-start gap-4 flex-1 min-w-0">
                    <div class="w-10 h-10 rounded-lg shrink-0 bg-muted animate-pulse" />
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center gap-2 flex-wrap">
                        <div class="h-4 w-40 bg-muted rounded animate-pulse" />
                        <div class="h-4 w-14 bg-muted rounded animate-pulse" />
                      </div>
                      <div class="mt-2 space-y-2">
                        <div class="h-3 w-full bg-muted rounded animate-pulse" />
                        <div class="h-3 w-2/3 bg-muted rounded animate-pulse" />
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </template>

          <!-- 失敗 -->
          <Card v-else-if="scenariosLoadError" class="border-destructive/30">
            <CardContent class="p-5">
              <div class="flex items-start justify-between gap-4">
                <div class="space-y-1">
                  <div class="font-semibold text-sm">載入劇本清單失敗</div>
                  <div class="text-xs text-muted-foreground wrap-break-word">
                    {{ scenariosLoadError }}
                  </div>
                </div>
                <Button size="sm" class="gap-2" @click="fetchScenarios">
                  <Spinner v-if="isLoadingScenarios" class="size-3.5" />
                  重試
                </Button>
              </div>
            </CardContent>
          </Card>

          <!-- 空狀態 -->
          <Card v-else-if="scenarios.length === 0" class="border-dashed">
            <CardContent class="p-8">
              <div class="text-center space-y-2">
                <div class="text-sm font-semibold">目前還沒有劇本</div>
                <div class="text-xs text-muted-foreground">
                  建立第一個劇本草稿，完成後發布即可開始跑團。
                </div>
                <div class="pt-2">
                  <Button size="sm" class="gap-2" @click="createDialogOpen = true">
                    <Plus class="size-3.5" />
                    創建劇本
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- 成功 -->
          <Card
            v-else
            v-for="scenario in scenarios"
            :key="scenario.id"
            class="hover:shadow-md transition-shadow"
          >
            <CardContent class="p-5">
              <div class="flex items-start justify-between gap-4">
                <div class="flex items-start gap-4 flex-1 min-w-0">
                  <!-- 類型圖示 -->
                  <div
                    class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0 text-white text-sm font-bold"
                    :style="{ backgroundColor: colorFromId(scenario.id) }"
                  >
                    {{ scenario.name.charAt(0) }}
                  </div>

                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 flex-wrap">
                      <h3 class="font-semibold text-base">{{ scenario.name }}</h3>
                      <Badge variant="outline" class="text-[10px]">{{ scenario.system }}</Badge>
                      <!-- 狀態徽章 -->
                      <Badge
                        v-if="scenario.status === 'DRAFT'"
                        variant="secondary"
                        class="text-[10px] gap-1"
                      >
                        <PencilLine class="size-2.5" />
                        草稿
                      </Badge>
                      <Badge
                        v-else
                        class="text-[10px] gap-1 bg-green-500/15 text-green-700 dark:text-green-400 border-green-500/30"
                        variant="outline"
                      >
                        <Globe class="size-2.5" />
                        已發布
                      </Badge>
                    </div>
                    <p class="text-sm text-muted-foreground mt-1 line-clamp-2">
                      {{ scenario.description || '尚未新增簡介' }}
                    </p>
                    <div class="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                      <span class="flex items-center gap-1">
                        <Users class="size-3" />
                        {{ playerCountText(scenario) }}
                      </span>
                      <span class="flex items-center gap-1">
                        <Clock class="size-3" />
                        {{ durationText(scenario) }}
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
                    v-if="scenario.status === 'PUBLISHED'"
                    size="sm"
                    class="gap-1.5"
                    :disabled="creatingRoomId === scenario.id"
                    @click="createRoom(scenario.id)"
                  >
                    <Spinner v-if="creatingRoomId === scenario.id" class="size-3.5" />
                    <Plus v-else class="size-3.5" />
                    {{ creatingRoomId === scenario.id ? '建立中...' : '創建房間' }}
                  </Button>
                  <Button
                    v-else
                    variant="outline"
                    size="sm"
                    class="gap-1.5 text-muted-foreground"
                    disabled
                    title="請先發布劇本才能創建房間"
                  >
                    <Lock class="size-3.5" />
                    草稿中
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
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { BookOpen, Clock, DoorOpen, Globe, Info, Lock, PencilLine, Plus, Users } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Spinner } from '@/components/ui/spinner'
import CreateScenarioDialog from '@/components/dialogs/CreateScenarioDialog.vue'
import { ScenariosService, type ScenarioResponse } from '@/services'

const router = useRouter()

const creatingRoomId = ref<string | null>(null)
const createDialogOpen = ref(false)
const newScenarioName = ref('')
const newScenarioSystem = ref('')
const newScenarioDescription = ref('')
const newScenarioMinPlayers = ref('')
const newScenarioMaxPlayers = ref('')
const newScenarioMinHours = ref('')
const newScenarioMaxHours = ref('')
const isCreatingScenario = ref(false)
const createScenarioError = ref<string | null>(null)

const COLORS = ['#7c3aed', '#0891b2', '#b45309', '#be123c', '#10b981', '#f97316', '#6366f1']

function colorFromId(id: string) {
  let hash = 0
  for (let i = 0; i < id.length; i += 1) {
    hash = (hash * 31 + id.charCodeAt(i)) | 0
  }
  const idx = Math.abs(hash) % COLORS.length
  return COLORS[idx]
}

function playerCountText(s: ScenarioResponse) {
  if (s.min_players == null && s.max_players == null) return '— 人'
  if (s.min_players != null && s.max_players != null) return `${s.min_players}-${s.max_players} 人`
  if (s.min_players != null) return `${s.min_players}+ 人`
  return `≤ ${s.max_players} 人`
}

function durationText(s: ScenarioResponse) {
  if (s.min_hours == null && s.max_hours == null) return '—'
  if (s.min_hours != null && s.max_hours != null) return `${s.min_hours}-${s.max_hours} 小時`
  if (s.min_hours != null) return `${s.min_hours}+ 小時`
  return `≤ ${s.max_hours} 小時`
}

function toIntOrNull(raw: string): number | null {
  const t = raw.trim()
  if (!t) return null
  const n = Number.parseInt(t, 10)
  return Number.isFinite(n) ? n : null
}

function toFloatOrNull(raw: string): number | null {
  const t = raw.trim()
  if (!t) return null
  const n = Number.parseFloat(t)
  return Number.isFinite(n) ? n : null
}

async function handleCreateScenario() {
  if (!newScenarioName.value.trim()) return
  if (!newScenarioSystem.value.trim()) return
  isCreatingScenario.value = true
  createScenarioError.value = null
  try {
    const res = await ScenariosService.createScenario({
      body: {
        name: newScenarioName.value.trim(),
        system: newScenarioSystem.value.trim(),
        description: newScenarioDescription.value.trim()
          ? newScenarioDescription.value.trim()
          : null,
        min_players: toIntOrNull(newScenarioMinPlayers.value),
        max_players: toIntOrNull(newScenarioMaxPlayers.value),
        min_hours: toFloatOrNull(newScenarioMinHours.value),
        max_hours: toFloatOrNull(newScenarioMaxHours.value),
      },
    })
    const created = res.data
    scenarios.value = [created, ...scenarios.value.filter((s) => s.id !== created.id)]
    createDialogOpen.value = false
    newScenarioName.value = ''
    newScenarioSystem.value = ''
    newScenarioDescription.value = ''
    newScenarioMinPlayers.value = ''
    newScenarioMaxPlayers.value = ''
    newScenarioMinHours.value = ''
    newScenarioMaxHours.value = ''
    router.push(`/scenarios/${created.id}`)
  } catch (e) {
    const err = e as unknown
    const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
    if (Array.isArray(detail) && detail.length > 0) {
      createScenarioError.value = detail
        .map((d) => {
          const loc = (d as { loc?: unknown })?.loc
          const msg = (d as { msg?: unknown })?.msg
          const locText = Array.isArray(loc) ? loc.join('.') : 'body'
          const msgText = typeof msg === 'string' ? msg : 'invalid'
          return `${locText}: ${msgText}`
        })
        .join('\n')
      return
    }
    createScenarioError.value =
      typeof (err as { message?: unknown })?.message === 'string'
        ? (err as { message: string }).message
        : '建立失敗，請稍後再試'
  } finally {
    isCreatingScenario.value = false
  }
}

const scenarios = ref<ScenarioResponse[]>([])
const isLoadingScenarios = ref(false)
const scenariosLoadError = ref<string | null>(null)

async function fetchScenarios() {
  isLoadingScenarios.value = true
  scenariosLoadError.value = null
  try {
    const res = await ScenariosService.listScenarios()
    scenarios.value = res.data
  } catch (e) {
    const err = e as unknown
    scenariosLoadError.value =
      typeof (err as { message?: unknown })?.message === 'string'
        ? (err as { message: string }).message
        : '請稍後再試'
  } finally {
    isLoadingScenarios.value = false
  }
}

onMounted(fetchScenarios)

async function createRoom(scenarioId: string) {
  creatingRoomId.value = scenarioId
  try {
    const scenario = scenarios.value.find((item) => item.id === scenarioId)
    const res = await ScenariosService.createRoom({
      path: { scenario_id: scenarioId },
      body: {
        name: scenario?.name?.trim() || '新房間',
        description: scenario?.description ?? null,
      },
    })
    router.push(`/rooms/${res.data.id}`)
  } finally {
    creatingRoomId.value = null
  }
}
</script>
