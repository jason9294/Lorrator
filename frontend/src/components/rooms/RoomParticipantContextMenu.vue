<script setup lang="ts">
import { useCopyFeedback } from '@/composables/useCopyFeedback'
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

const { copy, copied } = useCopyFeedback()

function copyUserId() {
  void copy(props.userId)
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
