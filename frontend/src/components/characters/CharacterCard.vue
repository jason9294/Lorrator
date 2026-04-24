<script setup lang="ts">
import { User } from 'lucide-vue-next'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import type { CharacterResponse } from '@/services'
import { colorFromId } from '@/utils/color'

defineProps<{
  character: CharacterResponse
}>()

const emit = defineEmits<{
  click: [id: string]
}>()

function systemLabel(system: string) {
  if (system === 'COC') return 'COC 7e'
  if (system === 'DND') return 'D&D 5e'
  return system
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-TW', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}
</script>

<template>
  <Card
    class="hover:shadow-md transition-all cursor-pointer hover:border-primary/40 active:scale-[0.99]"
    @click="emit('click', character.id)"
  >
    <CardContent class="p-5">
      <div class="flex items-center gap-4">
        <div
          class="w-11 h-11 rounded-xl flex items-center justify-center text-white text-base font-bold shrink-0 shadow-sm"
          :style="{ backgroundColor: colorFromId(character.id) }"
        >
          {{ character.name.charAt(0).toUpperCase() }}
        </div>

        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="font-semibold text-sm truncate">{{ character.name }}</span>
            <Badge variant="secondary" class="text-[10px] shrink-0">
              {{ systemLabel(character.game_system) }}
            </Badge>
          </div>
          <p class="text-xs text-muted-foreground mt-0.5">
            建立於 {{ formatDate(character.created_at) }}
          </p>
        </div>

        <User class="size-4 text-muted-foreground/40 shrink-0" />
      </div>
    </CardContent>
  </Card>
</template>
