<script setup lang="ts">
import { computed } from 'vue'
import { User } from 'lucide-vue-next'
import { colorFromId } from '@/utils/color'

const props = withDefaults(
  defineProps<{
    userId: string
    avatarUrl?: string | null
    nickname?: string | null
    username?: string | null
    size?: 'xs' | 'sm' | 'md' | 'lg'
  }>(),
  {
    avatarUrl: null,
    nickname: null,
    username: null,
    size: 'md',
  },
)

const sizeClass = computed(() => {
  switch (props.size) {
    case 'xs':
      return 'w-6 h-6 text-[10px]'
    case 'sm':
      return 'w-8 h-8 text-xs'
    case 'lg':
      return 'w-14 h-14 text-lg'
    default:
      return 'w-10 h-10 text-sm'
  }
})

const iconSize = computed(() => {
  switch (props.size) {
    case 'xs':
      return 'size-3'
    case 'sm':
      return 'size-3.5'
    case 'lg':
      return 'size-7'
    default:
      return 'size-5'
  }
})

const bgColor = computed(() => colorFromId(props.userId))

const initial = computed(() => {
  const name = props.nickname || props.username
  return name ? name.charAt(0).toUpperCase() : null
})

const fullAvatarUrl = computed(() => {
  return `${import.meta.env.VITE_API_URL}${props.avatarUrl}`
})
</script>

<template>
  <!-- 已有自訂圖片 -->
  <img
    v-if="avatarUrl"
    :src="fullAvatarUrl"
    :alt="nickname || username || 'avatar'"
    :class="[sizeClass, 'rounded-full object-cover shrink-0']"
  />

  <!-- 文字首字 -->
  <div
    v-else-if="initial"
    :class="[
      sizeClass,
      'rounded-full flex items-center justify-center text-white font-bold shrink-0',
    ]"
    :style="{ backgroundColor: bgColor }"
  >
    {{ initial }}
  </div>

  <!-- 預設 user icon -->
  <div
    v-else
    :class="[sizeClass, 'rounded-full flex items-center justify-center text-white shrink-0']"
    :style="{ backgroundColor: bgColor }"
  >
    <User :class="iconSize" />
  </div>
</template>
