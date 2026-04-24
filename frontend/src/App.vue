<template>
  <main>
    <RouterView />
    <Toaster />
  </main>
</template>

<script setup lang="ts">
import 'vue-sonner/style.css'
import { Toaster } from '@/components/ui/sonner'
import { useColorMode } from '@/composables/useColorMode'
import { useMeStore } from '@/stores/me'
import { onMounted } from 'vue'

const meStore = useMeStore()

useColorMode()

onMounted(async () => {
  await meStore.fetchMe()
})
</script>

<style scoped>
/*  */
</style>
