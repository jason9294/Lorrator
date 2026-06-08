<template>
  <div class="min-h-screen flex flex-col bg-background text-foreground">
    <AppHeader>
      <template #actions>
        <Button size="sm" class="gap-2" @click="createDialogOpen = true">
          <UserPlus class="size-3.5" />
          建立角色
        </Button>
      </template>
    </AppHeader>

    <main class="flex-1 p-6">
      <div class="max-w-3xl mx-auto space-y-6">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-xl font-bold">我的角色卡</h2>
            <p class="text-sm text-muted-foreground mt-0.5">管理你的 TRPG 角色</p>
          </div>
          <Badge variant="secondary" class="gap-1">
            <User class="size-3" />
            {{ isLoading ? '載入中…' : `${characters.length} 個角色` }}
          </Badge>
        </div>

        <!-- 載入骨架 -->
        <div v-if="isLoading" class="grid gap-3">
          <div v-for="n in 3" :key="n" class="rounded-xl border bg-card p-5 animate-pulse">
            <div class="flex items-center gap-4">
              <div class="w-11 h-11 rounded-xl bg-muted shrink-0" />
              <div class="flex-1 space-y-2">
                <div class="h-4 w-32 bg-muted rounded" />
                <div class="h-3 w-20 bg-muted rounded" />
              </div>
            </div>
          </div>
        </div>

        <!-- 角色列表 -->
        <div v-else-if="characters.length > 0" class="grid gap-3">
          <CharacterCard
            v-for="character in characters"
            :key="character.id"
            :character="character"
            @click="router.push(`/characters/${character.id}`)"
          />
        </div>

        <!-- 空狀態 -->
        <div
          v-else
          class="flex flex-col items-center justify-center py-24 text-center border rounded-xl border-dashed"
        >
          <User class="size-12 text-muted-foreground/30 mb-4" />
          <p class="font-medium text-muted-foreground">還沒有角色</p>
          <p class="text-sm text-muted-foreground/60 mt-1 mb-4">建立你的第一個 COC 角色卡</p>
          <Button size="sm" class="gap-1.5" @click="createDialogOpen = true">
            <UserPlus class="size-3.5" />
            建立角色
          </Button>
        </div>
      </div>
    </main>

    <CreateCharacterDialog
      v-model:open="createDialogOpen"
      :is-submitting="isCreating"
      :error-message="createError"
      @submit="handleCreate"
    />
  </div>
</template>

<script setup lang="ts">
import { useAsyncState, useToggle } from '@vueuse/core'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { User, UserPlus } from 'lucide-vue-next'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import AppHeader from '@/components/layout/AppHeader.vue'
import { CharactersService } from '@/services'
import CharacterCard from '@/components/characters/CharacterCard.vue'
import CreateCharacterDialog from '@/components/characters/CreateCharacterDialog.vue'

const router = useRouter()

const { state: characters, isLoading } = useAsyncState(
  async () => (await CharactersService.listCharacters()).data ?? [],
  [],
  {
    immediate: true,
  },
)

const [createDialogOpen] = useToggle(false)
const isCreating = ref(false)
const createError = ref<string | null>(null)

async function handleCreate(payload: { name: string; game_system: 'COC' }) {
  isCreating.value = true
  createError.value = null
  try {
    const res = await CharactersService.createCharacter({
      body: { name: payload.name, game_system: payload.game_system },
    })
    createDialogOpen.value = false
    router.push(`/characters/${res.data.id}`)
  } catch {
    createError.value = '建立角色失敗，請稍後再試'
  } finally {
    isCreating.value = false
  }
}
</script>
