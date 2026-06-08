<script setup lang="ts">
import { useCopyFeedback } from '@/composables/useCopyFeedback'
import { Check, Copy } from 'lucide-vue-next'
import { PopoverArrow, PopoverContent, PopoverPortal, PopoverRoot, PopoverTrigger } from 'reka-ui'
import UserAvatar from '@/components/user/UserAvatar.vue'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import type { RoomParticipantResponse } from '@/services'

const props = defineProps<{
  participant: RoomParticipantResponse
  isHost?: boolean
}>()

const { copy, copied } = useCopyFeedback()

function copyId() {
  void copy(props.participant.user_id)
}
</script>

<template>
  <PopoverRoot>
    <PopoverTrigger as-child>
      <slot />
    </PopoverTrigger>

    <PopoverPortal>
      <PopoverContent
        :side-offset="6"
        class="z-50 w-72 rounded-xl border bg-popover p-4 text-popover-foreground shadow-lg outline-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=top]:slide-in-from-bottom-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2"
        @open-auto-focus.prevent
      >
        <!-- 頭像 + 基本資訊 -->
        <div class="flex items-start gap-3">
          <UserAvatar
            :user-id="participant.user_id"
            :avatar-url="participant.avatar_url"
            :nickname="participant.nickname"
            :username="participant.username"
            size="lg"
          />

          <div class="flex-1 min-w-0 pt-0.5">
            <div class="flex flex-wrap items-center gap-1.5">
              <span class="text-sm font-semibold leading-none">
                {{ participant.nickname || participant.username }}
              </span>
              <Badge
                v-if="isHost"
                class="text-[10px] bg-violet-500/15 text-violet-700 dark:text-violet-400 border-violet-500/30"
                variant="outline"
              >
                房主
              </Badge>
            </div>
            <p class="mt-1 text-xs text-muted-foreground">@{{ participant.username }}</p>
          </div>
        </div>

        <!-- 使用者 ID 區塊 -->
        <div class="mt-3 rounded-lg bg-muted/50 px-3 py-2.5">
          <p class="text-[10px] text-muted-foreground mb-1">使用者 ID</p>
          <div class="flex items-center gap-2">
            <code class="flex-1 text-[11px] font-mono text-foreground/80 truncate select-all">
              {{ participant.user_id }}
            </code>
            <Button
              size="icon-sm"
              variant="ghost"
              class="shrink-0 text-muted-foreground hover:text-foreground"
              :title="copied ? '已複製' : '複製 ID'"
              @click.stop="copyId"
            >
              <Check v-if="copied" class="size-3.5 text-green-500" />
              <Copy v-else class="size-3.5" />
            </Button>
          </div>
        </div>

        <PopoverArrow class="fill-border" />
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
</template>
