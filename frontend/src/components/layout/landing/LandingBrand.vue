<script setup lang="ts">
withDefaults(
  defineProps<{
    alwaysShowText?: boolean
  }>(),
  {
    alwaysShowText: false,
  },
)
</script>

<template>
  <RouterLink to="/" class="flex shrink-0 items-center gap-2">
    <img src="/logo.png" alt="Lorrator" class="size-7 rounded-lg object-contain" />
    <span
      class="font-mono text-label-md uppercase tracking-widest text-secondary"
      :class="alwaysShowText ? undefined : 'hidden sm:block'"
    >
      Lorrator
    </span>
  </RouterLink>
</template>
