<script setup lang="ts">
import { computed, ref } from 'vue'
import { LogOut, PanelLeftClose, PanelLeftOpen, Settings } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { onClickOutside } from '@vueuse/core'
import { useLandingDrawer } from '@/composables/useLandingDrawer'
import LandingBrand from '@/components/layout/landing/LandingBrand.vue'
import LandingNav from '@/components/layout/landing/LandingNav.vue'
import { Button } from '@/components/ui/button'
import UserAvatar from '@/components/user/UserAvatar.vue'
import EditProfileDialog from '@/components/user/EditProfileDialog.vue'
import { clearStoredAccessToken } from '@/lib/accessToken'
import { useMeStore } from '@/stores/me'

const meStore = useMeStore()
const router = useRouter()
const { expanded, toggle } = useLandingDrawer()

const isLoggedIn = computed(() => meStore.me !== null)
const showBrand = computed(() => !isLoggedIn.value || !expanded.value)

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
  await router.push('/new-landing')
}

function openEditProfile() {
  dropdownOpen.value = false
  editProfileOpen.value = true
}
</script>

<template>
  <header
    class="sticky top-0 z-50 flex h-16 w-full shrink-0 items-center justify-between border-b border-outline-variant/20 bg-surface px-margin-mobile md:px-margin-desktop"
  >
    <div class="flex min-w-0 items-center gap-stack-md">
      <button
        v-if="isLoggedIn"
        type="button"
        class="shrink-0 text-on-surface-variant transition-colors hover:text-secondary"
        :title="expanded ? '收合側欄' : '展開側欄'"
        @click="toggle"
      >
        <PanelLeftClose v-if="expanded" class="size-5" />
        <PanelLeftOpen v-else class="size-5" />
      </button>

      <Transition name="landing-brand-fade">
        <div v-if="showBrand" key="brand" class="shrink-0">
          <LandingBrand />
        </div>
      </Transition>

      <LandingNav
        v-if="isLoggedIn && !expanded"
        variant="header"
        class="hidden min-w-0 overflow-x-auto sm:flex"
      />
    </div>

    <div class="flex items-center gap-stack-sm">
      <template v-if="isLoggedIn">
        <div ref="dropdownRef" class="relative">
          <button
            type="button"
            class="flex items-center gap-2 rounded-lg px-2 py-1 transition-colors hover:bg-surface-container-highest"
            @click="dropdownOpen = !dropdownOpen"
          >
            <UserAvatar
              :user-id="String(meStore.id)"
              :avatar-url="meStore.avatarUrl"
              :nickname="meStore.nickname"
              :username="meStore.username"
              size="sm"
            />
            <span class="hidden max-w-24 truncate text-sm font-medium sm:block">
              {{ meStore.displayName }}
            </span>
          </button>

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
              class="absolute right-0 top-full z-50 mt-2 w-52 overflow-hidden rounded-xl border border-outline-variant/30 bg-surface shadow-lg"
            >
              <div class="border-b border-outline-variant/30 bg-surface-container-low px-4 py-3">
                <div class="flex items-center gap-3">
                  <UserAvatar
                    :user-id="String(meStore.id)"
                    :avatar-url="meStore.avatarUrl"
                    :nickname="meStore.nickname"
                    :username="meStore.username"
                    size="md"
                  />
                  <div class="min-w-0">
                    <p class="truncate text-sm font-semibold">{{ meStore.displayName }}</p>
                    <p v-if="meStore.nickname" class="truncate text-xs text-on-surface-variant">
                      @{{ meStore.username }}
                    </p>
                  </div>
                </div>
              </div>

              <div class="p-1">
                <button
                  type="button"
                  class="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-left text-sm transition-colors hover:bg-surface-container-highest"
                  @click="openEditProfile"
                >
                  <Settings class="size-3.5 text-on-surface-variant" />
                  編輯個人資料
                </button>
                <button
                  type="button"
                  class="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-left text-sm text-error transition-colors hover:bg-error-container/30"
                  @click="handleLogout"
                >
                  <LogOut class="size-3.5" />
                  登出
                </button>
              </div>
            </div>
          </Transition>
        </div>
      </template>

      <template v-else>
        <RouterLink to="/login">
          <Button variant="outline" size="sm" class="font-mono text-label-sm"> 登入 </Button>
        </RouterLink>
        <RouterLink to="/register">
          <Button size="sm" class="font-mono text-label-sm text-white"> 註冊 </Button>
        </RouterLink>
      </template>
    </div>
  </header>

  <EditProfileDialog v-model:open="editProfileOpen" />
</template>

<style scoped>
.landing-brand-fade-enter-active,
.landing-brand-fade-leave-active {
  transition: opacity 0.25s ease;
}

.landing-brand-fade-enter-from,
.landing-brand-fade-leave-to {
  opacity: 0;
}
</style>
