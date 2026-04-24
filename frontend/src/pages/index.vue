<template>
  <div class="min-h-screen flex flex-col bg-background text-foreground overflow-x-hidden">
    <!-- 頂部導覽 -->
    <header
      class="shrink-0 flex items-center justify-between px-6 h-14 border-b bg-card/80 backdrop-blur-sm sticky top-0 z-30"
    >
      <div class="flex items-center gap-2.5">
        <div
          class="w-7 h-7 rounded-lg bg-linear-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-sm shrink-0"
        >
          <svg class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="currentColor">
            <path
              d="M12 2C8.13 2 5 5.13 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26C17.81 13.47 19 11.38 19 9c0-3.87-3.13-7-7-7zm0 12c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"
            />
          </svg>
        </div>
        <span class="text-sm font-semibold">Lorrator</span>
      </div>

      <div class="flex items-center gap-2">
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
        <RouterLink to="/login">
          <Button variant="outline" size="sm">登入</Button>
        </RouterLink>
        <RouterLink to="/register">
          <Button size="sm">免費註冊</Button>
        </RouterLink>
      </div>
    </header>

    <main class="flex-1">
      <!-- Hero 區塊 -->
      <section
        class="relative flex flex-col items-center justify-center text-center px-6 py-24 sm:py-32 overflow-hidden"
      >
        <!-- 背景裝飾 -->
        <div class="absolute inset-0 -z-10 overflow-hidden">
          <div
            class="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-violet-500/8 blur-3xl"
          />
          <div
            class="absolute top-2/3 right-1/4 w-[300px] h-[300px] rounded-full bg-indigo-500/6 blur-3xl"
          />
        </div>

        <div class="max-w-3xl mx-auto space-y-6">
          <!-- Badge -->
          <div
            class="inline-flex items-center gap-2 rounded-full border bg-muted/50 px-3 py-1 text-xs font-medium text-muted-foreground"
          >
            <span class="w-1.5 h-1.5 rounded-full bg-green-500" />
            為 TRPG 玩家打造的智慧跑團助手
          </div>

          <h1 class="text-4xl sm:text-5xl font-bold tracking-tight leading-tight">
            讓每次跑團<br />
            <span
              class="bg-linear-to-r from-violet-600 to-indigo-600 bg-clip-text text-transparent"
            >
              更有沉浸感
            </span>
          </h1>

          <p class="text-base sm:text-lg text-muted-foreground max-w-xl mx-auto leading-relaxed">
            Lorrator 結合 AI 守門人，讓你專注於劇情創作。<br class="hidden sm:block" />
            管理角色卡、建立劇本、即時跑團，一站搞定。
          </p>

          <div class="flex items-center justify-center gap-3 pt-2">
            <RouterLink to="/register">
              <Button size="lg" class="gap-2 px-6">
                <Sparkles class="size-4" />
                免費開始
              </Button>
            </RouterLink>
            <RouterLink to="/login">
              <Button variant="outline" size="lg" class="px-6"> 登入 </Button>
            </RouterLink>
          </div>
        </div>
      </section>

      <!-- 功能特色 -->
      <section class="px-6 pb-24">
        <div class="max-w-4xl mx-auto">
          <div class="text-center mb-10 space-y-2">
            <h2 class="text-2xl font-bold">一切你跑團需要的功能</h2>
            <p class="text-sm text-muted-foreground">從角色創建到跑團結束，全程陪伴</p>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-5">
            <div class="rounded-xl border bg-card p-5 space-y-3">
              <div class="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center">
                <User class="size-5 text-amber-600 dark:text-amber-400" />
              </div>
              <div>
                <h3 class="font-semibold text-sm">角色卡系統</h3>
                <p class="text-xs text-muted-foreground mt-1 leading-relaxed">
                  支援 COC 7e 完整角色卡，自動計算屬性，隨時查閱與更新。
                </p>
              </div>
            </div>

            <div class="rounded-xl border bg-card p-5 space-y-3">
              <div class="w-10 h-10 rounded-lg bg-violet-500/10 flex items-center justify-center">
                <BookOpen class="size-5 text-violet-600 dark:text-violet-400" />
              </div>
              <div>
                <h3 class="font-semibold text-sm">劇本知識庫</h3>
                <p class="text-xs text-muted-foreground mt-1 leading-relaxed">
                  上傳劇本文件，AI 自動解析並建立知識圖譜，讓 KP 輕鬆掌握全局。
                </p>
              </div>
            </div>

            <div class="rounded-xl border bg-card p-5 space-y-3">
              <div class="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                <MessageCircle class="size-5 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <h3 class="font-semibold text-sm">AI 守門人</h3>
                <p class="text-xs text-muted-foreground mt-1 leading-relaxed">
                  即時 AI 輔助敘事，根據劇本內容回應玩家行動，提升沉浸體驗。
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- CTA -->
      <section class="px-6 pb-24">
        <div
          class="max-w-2xl mx-auto rounded-2xl border bg-linear-to-br from-violet-500/5 to-indigo-500/5 p-10 text-center space-y-5"
        >
          <h2 class="text-2xl font-bold">準備好開始你的冒險了嗎？</h2>
          <p class="text-sm text-muted-foreground">免費建立帳號，立即體驗 AI 跑團的樂趣。</p>
          <RouterLink to="/register">
            <Button size="lg" class="gap-2 px-8">
              <Sparkles class="size-4" />
              立即免費註冊
            </Button>
          </RouterLink>
        </div>
      </section>
    </main>

    <!-- 頁尾 -->
    <footer class="border-t px-6 py-5 text-center text-xs text-muted-foreground">
      © 2026 Lorrator · 為 TRPG 玩家打造
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { BookOpen, MessageCircle, Moon, Sparkles, Sun, User } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { useColorMode } from '@/composables/useColorMode'
import { getStoredAccessToken } from '@/lib/accessToken'
import { AuthService } from '@/services'

const router = useRouter()
const { isDark, toggle } = useColorMode()

onMounted(async () => {
  const token = getStoredAccessToken()
  if (!token) return
  try {
    await AuthService.me()
    await router.replace('/dashboard')
  } catch {
    // token 失效，留在 landing page
  }
})
</script>
