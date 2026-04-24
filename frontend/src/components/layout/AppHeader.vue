<script setup lang="ts">
import { ref } from 'vue'
import { Moon, Sun, LogOut, Settings } from 'lucide-vue-next'
import { useRoute, useRouter } from 'vue-router'
import { onClickOutside } from '@vueuse/core'
import { Button } from '@/components/ui/button'
import { useColorMode } from '@/composables/useColorMode'
import { useMeStore } from '@/stores/me'
import { clearStoredAccessToken } from '@/lib/accessToken'
import UserAvatar from '@/components/user/UserAvatar.vue'
import EditProfileDialog from '@/components/user/EditProfileDialog.vue'

const route = useRoute()
const router = useRouter()
const { isDark, toggle } = useColorMode()
const meStore = useMeStore()

const navLinks = [
  { label: '角色', to: '/characters' },
  { label: '劇本', to: '/scenarios' },
  { label: '房間', to: '/rooms' },
]

function isActive(path: string) {
  return route.path.startsWith(path)
}

// User dropdown
const dropdownOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)
const editProfileOpen = ref(false)

onClickOutside(dropdownRef, () => {
  dropdownOpen.value = false
})

async function handleLogout() {
  dropdownOpen.value = false
  clearStoredAccessToken()
  meStore.clear()
  await router.push('/')
}

function openEditProfile() {
  dropdownOpen.value = false
  editProfileOpen.value = true
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

    <!-- 右側：頁面自訂操作 + 使用者選單 + 主題切換 -->
    <div class="flex items-center gap-2">
      <slot name="actions" />

      <!-- 主題切換 -->
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

      <!-- 使用者頭像 / 選單 -->
      <div v-if="meStore.me" ref="dropdownRef" class="relative">
        <button
          class="flex items-center gap-2 rounded-lg px-2 py-1 hover:bg-muted/60 transition-colors"
          @click="dropdownOpen = !dropdownOpen"
        >
          <UserAvatar
            :user-id="String(meStore.id)"
            :avatar-url="meStore.avatarUrl"
            :nickname="meStore.nickname"
            :username="meStore.username"
            size="sm"
          />
          <span class="text-sm font-medium hidden sm:block max-w-24 truncate">
            {{ meStore.displayName }}
          </span>
        </button>

        <!-- 下拉選單 -->
        <Transition
          enter-active-class="transition-all duration-150 ease-out"
          enter-from-class="opacity-0 scale-95 -translate-y-1"
          enter-to-class="opacity-100 scale-100 translate-y-0"
          leave-active-class="transition-all duration-100 ease-in"
          leave-from-class="opacity-100 scale-100 translate-y-0"
          leave-to-class="opacity-0 scale-95 -translate-y-1"
        >
          <div
            v-if="dropdownOpen"
            class="absolute right-0 top-full mt-2 w-52 rounded-xl border bg-card shadow-lg z-50 overflow-hidden"
          >
            <!-- 使用者資訊 -->
            <div class="px-4 py-3 border-b bg-muted/30">
              <div class="flex items-center gap-3">
                <UserAvatar
                  :user-id="String(meStore.id)"
                  :avatar-url="meStore.avatarUrl"
                  :nickname="meStore.nickname"
                  :username="meStore.username"
                  size="md"
                />
                <div class="min-w-0">
                  <p class="text-sm font-semibold truncate">{{ meStore.displayName }}</p>
                  <p v-if="meStore.nickname" class="text-xs text-muted-foreground truncate">@{{ meStore.username }}</p>
                </div>
              </div>
            </div>

            <!-- 操作項目 -->
            <div class="p-1">
              <button
                class="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm hover:bg-muted transition-colors text-left"
                @click="openEditProfile"
              >
                <Settings class="size-3.5 text-muted-foreground" />
                編輯個人資料
              </button>
              <button
                class="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm hover:bg-destructive/10 hover:text-destructive transition-colors text-left"
                @click="handleLogout"
              >
                <LogOut class="size-3.5" />
                登出
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </header>

  <EditProfileDialog v-model:open="editProfileOpen" />
</template>
