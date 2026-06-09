<script setup lang="ts">
defineProps<{
  label: string
  class?: string
}>()
</script>

<template>
  <div class="rounded-lg border bg-muted/30 px-4 py-3" :class="class">
    <p class="text-xs text-muted-foreground">{{ label }}</p>
    <div class="mt-1">
      <slot />
    </div>
  </div>
</template>
