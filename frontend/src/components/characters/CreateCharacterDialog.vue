<script setup lang="ts">
import { ref } from 'vue'
import { UserPlus } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Spinner } from '@/components/ui/spinner'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

const open = defineModel<boolean>('open', { required: true })

const props = withDefaults(defineProps<{
  isSubmitting?: boolean
  errorMessage?: string | null
}>(), {
  isSubmitting: false,
  errorMessage: null,
})

const emit = defineEmits<{
  submit: [{ name: string; game_system: 'COC' }]
}>()

const name = ref('')

function handleSubmit() {
  const trimmed = name.value.trim()
  if (!trimmed || props.isSubmitting) return
  emit('submit', { name: trimmed, game_system: 'COC' })
}

function handleClose() {
  open.value = false
  name.value = ''
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent class="sm:max-w-sm">
      <DialogHeader>
        <DialogTitle>建立新角色</DialogTitle>
        <DialogDescription>輸入角色名稱即可建立，建立後可在角色卡頁面填寫詳細資料。</DialogDescription>
      </DialogHeader>

      <div class="space-y-3 py-2">
        <div class="space-y-2">
          <Label for="create-char-name">角色名稱</Label>
          <Input
            id="create-char-name"
            v-model="name"
            placeholder="例如：田中一郎"
            :disabled="isSubmitting"
            autofocus
            @keydown.enter="handleSubmit"
          />
        </div>

        <div class="space-y-2">
          <Label>遊戲系統</Label>
          <div class="flex items-center gap-2 px-3 py-2 rounded-md border bg-muted/40 text-sm text-muted-foreground">
            <span class="font-medium text-foreground">COC 7e</span>
            <span class="text-xs">（克蘇魯的呼喚 第七版）</span>
          </div>
        </div>

        <p v-if="errorMessage" class="text-sm text-destructive">{{ errorMessage }}</p>
      </div>

      <DialogFooter>
        <Button variant="outline" :disabled="isSubmitting" @click="handleClose">取消</Button>
        <Button :disabled="!name.trim() || isSubmitting" @click="handleSubmit">
          <Spinner v-if="isSubmitting" class="size-4" />
          <UserPlus v-else class="size-4" />
          {{ isSubmitting ? '建立中…' : '建立角色' }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
