<script setup lang="ts">
import { Plus } from 'lucide-vue-next'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Spinner } from '@/components/ui/spinner'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

const open = defineModel<boolean>('open', { required: true })
const name = defineModel<string>('name', { default: '' })
const system = defineModel<string>('system', { default: '' })
const description = defineModel<string>('description', { default: '' })
const minPlayers = defineModel<string>('minPlayers', { default: '' })
const maxPlayers = defineModel<string>('maxPlayers', { default: '' })
const minHours = defineModel<string>('minHours', { default: '' })
const maxHours = defineModel<string>('maxHours', { default: '' })

const props = withDefaults(defineProps<{
  isSubmitting?: boolean
  errorMessage?: string | null
}>(), {
  isSubmitting: false,
  errorMessage: null,
})

const emit = defineEmits<{
  submit: []
}>()

function handleSubmit() {
  if (props.isSubmitting) return
  if (!name.value.trim()) return
  if (!system.value.trim()) return
  emit('submit')
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent class="sm:max-w-sm">
      <DialogHeader>
        <DialogTitle>創建新劇本</DialogTitle>
        <DialogDescription>輸入劇本名稱後即可建立，建立後可在詳情頁繼續編輯。</DialogDescription>
      </DialogHeader>
      <div class="space-y-3 py-2">
        <div class="space-y-2">
          <Label for="new-scenario-name">劇本名稱</Label>
          <Input
            id="new-scenario-name"
            v-model="name"
            placeholder="例如：克蘇魯的呼喚"
            :disabled="props.isSubmitting"
            @keydown.enter="handleSubmit"
          />
        </div>

        <div class="space-y-2">
          <Label for="new-scenario-system">系統</Label>
          <Input
            id="new-scenario-system"
            v-model="system"
            placeholder="例如：COC 7e / D&D 5e"
            :disabled="props.isSubmitting"
            @keydown.enter="handleSubmit"
          />
        </div>

        <div class="space-y-2">
          <Label for="new-scenario-description">簡介（選填）</Label>
          <Textarea
            id="new-scenario-description"
            v-model="description"
            placeholder="一句話描述這個劇本的基調或主題"
            :disabled="props.isSubmitting"
          />
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div class="space-y-2">
            <Label for="new-scenario-min-players">最少人數（選填）</Label>
            <Input
              id="new-scenario-min-players"
              v-model="minPlayers"
              inputmode="numeric"
              placeholder="例如：2"
              :disabled="props.isSubmitting"
            />
          </div>
          <div class="space-y-2">
            <Label for="new-scenario-max-players">最多人數（選填）</Label>
            <Input
              id="new-scenario-max-players"
              v-model="maxPlayers"
              inputmode="numeric"
              placeholder="例如：5"
              :disabled="props.isSubmitting"
            />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div class="space-y-2">
            <Label for="new-scenario-min-hours">最短時數（選填）</Label>
            <Input
              id="new-scenario-min-hours"
              v-model="minHours"
              inputmode="decimal"
              placeholder="例如：4"
              :disabled="props.isSubmitting"
            />
          </div>
          <div class="space-y-2">
            <Label for="new-scenario-max-hours">最長時數（選填）</Label>
            <Input
              id="new-scenario-max-hours"
              v-model="maxHours"
              inputmode="decimal"
              placeholder="例如：6"
              :disabled="props.isSubmitting"
            />
          </div>
        </div>

        <p v-if="props.errorMessage" class="text-sm text-destructive">
          {{ props.errorMessage }}
        </p>
      </div>
      <DialogFooter>
        <Button variant="outline" :disabled="props.isSubmitting" @click="open = false">
          取消
        </Button>
        <Button :disabled="!name.trim() || !system.trim() || props.isSubmitting" @click="handleSubmit">
          <Spinner v-if="props.isSubmitting" class="size-4" />
          <Plus v-else class="size-4" />
          {{ props.isSubmitting ? '建立中...' : '建立' }}
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>

