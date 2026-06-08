<template>
  <div class="min-h-screen flex flex-col bg-background text-foreground">
    <!-- 頂部導覽 -->
    <header
      class="shrink-0 flex items-center gap-3 px-5 h-13 border-b bg-card/80 backdrop-blur-sm z-30"
    >
      <RouterLink to="/characters">
        <Button variant="ghost" size="icon-sm">
          <ArrowLeft class="size-4" />
        </Button>
      </RouterLink>

      <div class="flex items-center gap-2 min-w-0">
        <span class="text-sm font-semibold truncate">
          {{ character?.name ?? '角色卡' }}
        </span>
        <Badge v-if="character" variant="secondary" class="text-[10px] shrink-0">
          {{ character.game_system === 'COC' ? 'COC 7e' : character.game_system }}
        </Badge>
      </div>

      <div class="ml-auto flex items-center gap-2 shrink-0">
        <template v-if="!isLoading && character">
          <Button
            v-if="!editMode"
            variant="outline"
            size="sm"
            class="gap-1.5"
            @click="editMode = true"
          >
            <Pencil class="size-3.5" />
            編輯
          </Button>
          <Button
            v-else
            variant="ghost"
            size="sm"
            class="gap-1.5 text-muted-foreground"
            :disabled="isSaving"
            @click="handleCancelEdit"
          >
            <X class="size-3.5" />
            取消編輯
          </Button>
        </template>

        <Button
          variant="ghost"
          size="icon-sm"
          class="text-destructive/60 hover:text-destructive"
          :disabled="isDeleting || editMode"
          title="刪除角色"
          @click="confirmDeleteOpen = true"
        >
          <Trash2 class="size-4" />
        </Button>
      </div>
    </header>

    <!-- 主體內容 -->
    <main class="flex-1 p-6">
      <div class="max-w-3xl mx-auto">
        <!-- 載入中 -->
        <div v-if="isLoading" class="space-y-4">
          <div v-for="n in 4" :key="n" class="rounded-xl border bg-card p-5 animate-pulse">
            <div class="h-4 w-1/3 bg-muted rounded mb-3" />
            <div class="h-16 bg-muted rounded" />
          </div>
        </div>

        <!-- 找不到 -->
        <div
          v-else-if="!character"
          class="flex flex-col items-center justify-center py-32 text-center"
        >
          <User class="size-12 text-muted-foreground/30 mb-4" />
          <p class="font-medium text-muted-foreground">找不到角色</p>
          <RouterLink to="/characters">
            <Button size="sm" variant="outline" class="mt-4">返回角色列表</Button>
          </RouterLink>
        </div>

        <!-- 檢視模式：COC 角色卡 -->
        <CoCCharacterSheet
          v-else-if="!editMode && cocData"
          :name="character.name"
          :data="cocData"
        />

        <!-- 編輯模式：COC 表單 -->
        <CoCCharacterForm
          v-else-if="editMode"
          :initial-data="cocData"
          :is-saving="isSaving"
          @submit="handleSave"
          @cancel="handleCancelEdit"
        />

        <!-- 無資料但非編輯模式 -->
        <div
          v-else
          class="flex flex-col items-center justify-center py-24 border rounded-xl border-dashed"
        >
          <p class="text-muted-foreground text-sm mb-4">尚未填寫角色卡資料</p>
          <Button size="sm" class="gap-1.5" @click="editMode = true">
            <Pencil class="size-3.5" />
            開始填寫
          </Button>
        </div>
      </div>
    </main>

    <!-- 刪除確認 Dialog -->
    <AlertDialog v-model:open="confirmDeleteOpen">
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>確定要刪除角色嗎？</AlertDialogTitle>
          <AlertDialogDescription>
            刪除「{{ character?.name }}」後將無法復原，角色卡資料也會一併刪除。
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel :disabled="isDeleting">取消</AlertDialogCancel>
          <AlertDialogAction
            class="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            :disabled="isDeleting"
            @click="handleDelete"
          >
            <Spinner v-if="isDeleting" class="size-4" />
            {{ isDeleting ? '刪除中…' : '確定刪除' }}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  </div>
</template>

<script setup lang="ts">
import { useAsyncState, useToggle } from '@vueuse/core'
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Pencil, Trash2, User, X } from 'lucide-vue-next'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Spinner } from '@/components/ui/spinner'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import {
  CharactersService,
  type CoCCharacterDataInput,
  type CoCCharacterDataOutput,
  type CharacterDetailResponse,
} from '@/services'
import CoCCharacterSheet from '@/components/characters/coc/CoCCharacterSheet.vue'
import CoCCharacterForm from '@/components/characters/coc/CoCCharacterForm.vue'

const route = useRoute()
const router = useRouter()
const characterId = route.params.character_id as string

const { state: character, isLoading } = useAsyncState(
  async () => {
    try {
      const res = await CharactersService.getCharacter({ path: { character_id: characterId } })
      return res.data
    } catch {
      return null
    }
  },
  null as CharacterDetailResponse | null,
  { immediate: true },
)

const editMode = ref(false)
const isSaving = ref(false)
const isDeleting = ref(false)
const [confirmDeleteOpen] = useToggle(false)

const cocData = computed<CoCCharacterDataOutput | null>(() => {
  const d = character.value?.data
  if (!d || typeof d !== 'object' || Array.isArray(d)) return null
  return d as CoCCharacterDataOutput
})

async function handleSave(data: CoCCharacterDataInput) {
  if (!character.value) return
  isSaving.value = true
  try {
    const res = await CharactersService.updateCharacter({
      path: { character_id: character.value.id },
      body: { data },
    })
    character.value = res.data
    editMode.value = false
  } finally {
    isSaving.value = false
  }
}

async function handleDelete() {
  if (!character.value) return
  isDeleting.value = true
  try {
    await CharactersService.deleteCharacter({ path: { character_id: character.value.id } })
    router.push('/characters')
  } finally {
    isDeleting.value = false
    confirmDeleteOpen.value = false
  }
}

function handleCancelEdit() {
  editMode.value = false
}
</script>
