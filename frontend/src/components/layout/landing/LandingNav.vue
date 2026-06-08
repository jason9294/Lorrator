<script setup lang="ts">
import { BookOpen, DoorOpen, IdCard } from 'lucide-vue-next'
import { useRoute } from 'vue-router'
import { cn } from '@/lib/utils'

const props = withDefaults(defineProps<{
  variant?: 'drawer' | 'header'
}>(), {
  variant: 'drawer',
})

const route = useRoute()

const navLinks = [
  { label: '角色卡', to: '/characters', icon: IdCard },
  { label: '劇本', to: '/scenarios', icon: BookOpen },
  { label: '房間', to: '/rooms', icon: DoorOpen },
] as const

function isActive(path: string) {
  return route.path.startsWith(path)
}
</script>

<template>
  <nav
    :class="cn(
      props.variant === 'drawer'
        ? 'flex flex-col gap-2 -mx-margin-desktop'
        : 'flex items-center gap-1 p-1 rounded-lg bg-surface-container border border-outline-variant/30',
    )"
  >
    <RouterLink
      v-for="link in navLinks"
      :key="link.to"
      :to="link.to"
      :class="cn(
        'font-mono text-label-md transition-colors duration-200',
        props.variant === 'drawer'
          ? cn(
              'flex items-center gap-stack-sm px-stack-md py-stack-sm',
              isActive(link.to)
                ? 'text-primary font-bold bg-surface-container-highest border-r-2 border-secondary opacity-90'
                : 'text-on-surface-variant hover:text-primary hover:bg-secondary-fixed/10',
            )
          : cn(
              'flex items-center gap-1.5 px-3.5 py-1.5 rounded-md text-sm font-medium',
              isActive(link.to)
                ? 'bg-surface text-primary shadow-sm'
                : 'text-on-surface-variant hover:text-primary',
            ),
      )"
    >
      <component :is="link.icon" :class="props.variant === 'drawer' ? 'size-[18px]' : 'size-3.5'" />
      <span>{{ link.label }}</span>
    </RouterLink>
  </nav>
</template>
