<script setup lang="ts">
import { ref } from 'vue'
import { Check, Copy, UserMinus } from 'lucide-vue-next'
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuLabel,
  ContextMenuSeparator,
  ContextMenuTrigger,
} from '@/components/ui/context-menu'

const props = defineProps<{
  userId: string
  canKick?: boolean
  isKicking?: boolean
}>()

const emit = defineEmits<{
  kick: []
}>()

const copied = ref(false)

async function copyUserId() {
  try {
    await navigator.clipboard.writeText(props.userId)
  } catch {
    const ta = document.createElement('textarea')
    ta.value = props.userId
    ta.style.position = 'fixed'
    ta.style.opacity = '0'
    document.body.appendChild(ta)
    ta.focus()
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
  }
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 2000)
}
</script>

<template>
  <ContextMenu>
    <ContextMenuTrigger class="block">
      <slot />
    </ContextMenuTrigger>

    <ContextMenuContent class="w-52">
      <ContextMenuLabel class="text-xs text-muted-foreground font-normal">
        使用者操作
      </ContextMenuLabel>
      <ContextMenuSeparator />

      <ContextMenuItem @click="copyUserId">
        <Check v-if="copied" class="size-3.5 text-green-500" />
        <Copy v-else class="size-3.5" />
        {{ copied ? 'ID 已複製！' : '複製使用者 ID' }}
      </ContextMenuItem>

      <template v-if="canKick">
        <ContextMenuSeparator />
        <ContextMenuItem
          variant="destructive"
          :disabled="isKicking"
          @click="emit('kick')"
        >
          <UserMinus class="size-3.5" />
          踢出使用者
        </ContextMenuItem>
      </template>
    </ContextMenuContent>
  </ContextMenu>
</template>
