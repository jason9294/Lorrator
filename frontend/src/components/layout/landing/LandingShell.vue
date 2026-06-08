<script setup lang="ts">
import { computed, watch } from 'vue'
import { provideLandingDrawer } from '@/composables/useLandingDrawer'
import LandingDrawer from '@/components/layout/landing/LandingDrawer.vue'
import LandingHeader from '@/components/layout/landing/LandingHeader.vue'
import { useMeStore } from '@/stores/me'

const props = withDefaults(defineProps<{
  defaultDrawerExpanded?: boolean
}>(), {
  defaultDrawerExpanded: true,
})

const meStore = useMeStore()
const isLoggedIn = computed(() => meStore.me !== null)

const { expanded } = provideLandingDrawer(false)

watch(
  isLoggedIn,
  (loggedIn) => {
    if (!loggedIn) {
      expanded.value = false
      return
    }
    if (props.defaultDrawerExpanded) {
      expanded.value = true
    }
  },
  { immediate: true },
)

const mainOffsetClass = computed(() =>
  isLoggedIn.value && expanded.value ? 'md:ml-64' : 'md:ml-0',
)
</script>

<template>
  <div class="flex min-h-screen flex-col bg-background text-on-background antialiased">
    <LandingHeader />

    <button
      v-if="isLoggedIn && expanded"
      type="button"
      class="fixed inset-x-0 top-16 bottom-0 z-30 bg-inverse-surface/20 md:hidden"
      aria-label="關閉側欄"
      @click="expanded = false"
    />

    <div class="relative flex flex-1">
      <LandingDrawer v-if="isLoggedIn" />

      <main
        class="flex w-full flex-1 flex-col transition-[margin] duration-300 ease-in-out"
        :class="mainOffsetClass"
      >
        <slot />
      </main>
    </div>
  </div>
</template>
