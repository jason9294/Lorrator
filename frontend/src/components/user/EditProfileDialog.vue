<script setup lang="ts">
import { ref, watch } from 'vue'
import { Camera, Loader2 } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import UserAvatar from './UserAvatar.vue'
import { useMeStore } from '@/stores/me'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ 'update:open': [value: boolean] }>()

const meStore = useMeStore()

const nicknameInput = ref('')
const avatarPreview = ref<string | null>(null)
const pendingFile = ref<File | null>(null)
const isSaving = ref(false)
const errorMsg = ref<string | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

watch(
  () => props.open,
  (val) => {
    if (val) {
      nicknameInput.value = meStore.nickname ?? ''
      avatarPreview.value = null
      pendingFile.value = null
      errorMsg.value = null
    }
  },
)

function onFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  pendingFile.value = file
  avatarPreview.value = URL.createObjectURL(file)
}

async function save() {
  isSaving.value = true
  errorMsg.value = null
  try {
    if (pendingFile.value) {
      await meStore.uploadAvatar(pendingFile.value)
    }
    await meStore.updateProfile({
      nickname: nicknameInput.value.trim() || null,
      avatar_url: meStore.avatarUrl ?? null,
    })
    emit('update:open', false)
  } catch {
    errorMsg.value = '儲存失敗，請稍後再試'
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="emit('update:open', $event)">
    <DialogContent class="max-w-sm">
      <DialogHeader>
        <DialogTitle>編輯個人資料</DialogTitle>
      </DialogHeader>

      <div class="space-y-5 py-2">
        <!-- Avatar -->
        <div class="flex flex-col items-center gap-3">
          <div class="relative group cursor-pointer" @click="fileInputRef?.click()">
            <UserAvatar
              :user-id="meStore.id ?? ''"
              :avatar-url="avatarPreview ?? meStore.avatarUrl"
              :nickname="meStore.nickname"
              :username="meStore.username"
              size="lg"
            />
            <div
              class="absolute inset-0 rounded-full bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <Camera class="size-5 text-white" />
            </div>
          </div>
          <p class="text-xs text-muted-foreground">點擊更換頭像（JPG / PNG / WebP，最大 5 MB）</p>
          <input
            ref="fileInputRef"
            type="file"
            accept="image/jpeg,image/png,image/webp,image/gif"
            class="hidden"
            @change="onFileChange"
          />
        </div>

        <!-- Nickname -->
        <div class="space-y-1.5">
          <Label for="nickname">暱稱</Label>
          <Input
            id="nickname"
            v-model="nicknameInput"
            placeholder="輸入暱稱（留空則顯示帳號）"
            maxlength="50"
          />
          <p class="text-xs text-muted-foreground">帳號：{{ meStore.username }}</p>
        </div>

        <p v-if="errorMsg" class="text-xs text-destructive">{{ errorMsg }}</p>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="emit('update:open', false)">取消</Button>
        <Button :disabled="isSaving" @click="save">
          <Loader2 v-if="isSaving" class="size-3.5 mr-1.5 animate-spin" />
          儲存
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
