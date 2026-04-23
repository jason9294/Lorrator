<script setup lang="ts">
import { Moon, Sun } from 'lucide-vue-next'
import { useRoute } from 'vue-router'
import { Button } from '@/components/ui/button'
import { useColorMode } from '@/composables/useColorMode'

const route = useRoute()
const { isDark, toggle } = useColorMode()

const navLinks = [
  { label: '角色', to: '/characters' },
  { label: '劇本', to: '/scenarios' },
  { label: '房間', to: '/rooms' },
]

function isActive(path: string) {
  return route.path.startsWith(path)
}
</script>

<template>
  <header class="shrink-0 grid grid-cols-[auto_1fr_auto] items-center gap-3 px-5 h-13 border-b bg-card/80 backdrop-blur-sm z-30">
    <!-- 左側：Logo -->
    <RouterLink to="/" class="flex items-center gap-2.5">
      <div class="w-7 h-7 rounded-lg bg-linear-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-sm shrink-0">
        <svg class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C8.13 2 5 5.13 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26C17.81 13.47 19 11.38 19 9c0-3.87-3.13-7-7-7zm0 12c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z" />
        </svg>
      </div>
      <span class="text-sm font-semibold hidden sm:block">Lorrator</span>
    </RouterLink>

    <!-- 中間：導航 tabs -->
    <nav class="flex justify-center">
      <div class="flex items-center gap-0.5 p-1 rounded-lg bg-muted/50 border">
        <RouterLink
          v-for="link in navLinks"
          :key="link.to"
          :to="link.to"
          class="px-3.5 py-1 rounded-md text-sm font-medium transition-all"
          :class="isActive(link.to)
            ? 'bg-background text-foreground shadow-sm'
            : 'text-muted-foreground hover:text-foreground'"
        >
          {{ link.label }}
        </RouterLink>
      </div>
    </nav>

    <!-- 右側：頁面自訂操作 + 主題切換 -->
    <div class="flex items-center gap-2">
      <slot name="actions" />
      <Button
        variant="outline"
        size="icon-sm"
        :title="isDark ? '切換為亮色模式' : '切換為暗色模式'"
        @click="toggle"
      >
        <Transition name="icon-swap" mode="out-in">
          <Moon v-if="!isDark" :key="'moon'" class="size-3.5" />
          <Sun v-else :key="'sun'" class="size-3.5" />
        </Transition>
      </Button>
    </div>
  </header>
</template>
