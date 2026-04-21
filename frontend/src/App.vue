<template>
  <main>
    <RouterView />
    <Toaster />
  </main>
</template>

<script setup lang="ts">
import 'vue-sonner/style.css'
import { Toaster } from '@/components/ui/sonner'
</script>

<style scoped>
/*  */
</style>
