<script setup lang="ts">
import { useLandingDrawer } from '@/composables/useLandingDrawer'
import LandingBrand from '@/components/layout/landing/LandingBrand.vue'
import LandingNav from '@/components/layout/landing/LandingNav.vue'

const { expanded } = useLandingDrawer()
</script>

<template>
  <aside
    class="fixed left-0 top-16 z-40 flex h-[calc(100vh-4rem)] flex-col overflow-hidden border-r border-outline-variant/30 bg-surface-container-low transition-[width] duration-300 ease-in-out"
    :class="expanded ? 'w-64' : 'w-0 border-r-0'"
  >
    <div v-show="expanded" class="flex h-full min-w-64 flex-col justify-between py-stack-md">
      <div class="flex flex-col gap-stack-lg px-margin-desktop">
        <LandingBrand always-show-text />

        <LandingNav variant="drawer" />
      </div>
    </div>
  </aside>
</template>
