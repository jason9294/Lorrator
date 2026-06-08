<script setup lang="ts">
import type { RoomMessageResponse } from '@/services'

defineProps<{
  data: RoomMessageResponse
}>()
</script>

<template>
  <div class="flex justify-center mt-4">
    <div class="bg-muted/50 text-muted-foreground text-xs px-3 py-1.5 rounded-full">
      {{ data.content }}
    </div>
  </div>
</template>
