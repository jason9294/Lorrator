<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Spinner } from '@/components/ui/spinner'

const open = defineModel<boolean>('open', { required: true })
const name = defineModel<string>('name', { required: true })
const system = defineModel<string>('system', { required: true })
const description = defineModel<string>('description', { required: true })

withDefaults(
  defineProps<{
    isEditing?: boolean
    error?: string | null
  }>(),
  {
    isEditing: false,
    error: null,
  },
)

const emit = defineEmits<{
  save: []
}>()
</script>

<template>
  <div
    v-if="open"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
    @click.self="open = false"
  >
    <div class="bg-card border rounded-xl shadow-xl w-full max-w-lg p-6 space-y-4">
      <h2 class="text-lg font-semibold">編輯劇本</h2>
      <div class="space-y-3">
        <div>
          <label class="text-xs font-medium text-muted-foreground mb-1 block">名稱</label>
          <input
            v-model="name"
            class="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-primary"
            placeholder="劇本名稱"
          />
        </div>
        <div>
          <label class="text-xs font-medium text-muted-foreground mb-1 block">規則系統</label>
          <input
            v-model="system"
            class="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-primary"
            placeholder="COC, DND, etc."
          />
        </div>
        <div>
          <label class="text-xs font-medium text-muted-foreground mb-1 block">簡介</label>
          <textarea
            v-model="description"
            rows="3"
            class="w-full rounded-md border bg-background px-3 py-2 text-sm outline-none focus:ring-1 focus:ring-primary resize-none"
            placeholder="劇本簡介（選填）"
          />
        </div>
      </div>
      <p v-if="error" class="text-xs text-destructive">{{ error }}</p>
      <div class="flex justify-end gap-2 pt-2">
        <Button variant="outline" size="sm" @click="open = false">取消</Button>
        <Button size="sm" :disabled="isEditing" @click="emit('save')">
          <Spinner v-if="isEditing" class="size-3.5 mr-1.5" />
          儲存
        </Button>
      </div>
    </div>
  </div>
</template>
