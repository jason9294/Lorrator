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

useColorMode()
</script>

<style scoped>
/*  */
</style>
