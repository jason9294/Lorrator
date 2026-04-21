<template>
  <div class="min-h-screen flex items-center justify-center bg-background text-foreground p-4">
    <div class="w-full max-w-sm space-y-6">
      <!-- Logo -->
      <div class="flex flex-col items-center gap-3 text-center">
        <div
          class="w-12 h-12 rounded-2xl bg-linear-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-lg"
        >
          <svg class="w-6 h-6 text-white" viewBox="0 0 24 24" fill="currentColor">
            <path
              d="M12 2C8.13 2 5 5.13 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26C17.81 13.47 19 11.38 19 9c0-3.87-3.13-7-7-7zm0 12c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"
            />
          </svg>
        </div>
        <div>
          <h1 class="text-2xl font-bold">歡迎回來</h1>
          <p class="text-sm text-muted-foreground mt-1">登入你的跑團帳號</p>
        </div>
      </div>

      <!-- 登入表單 -->
      <Card>
        <CardContent class="pt-6 space-y-4">
          <div class="space-y-2">
            <Label for="username">帳號</Label>
            <Input
              id="username"
              v-model="form.username"
              type="text"
              placeholder="輸入帳號"
              :disabled="isLoading"
              @keydown.enter="handleLogin"
            />
          </div>

          <div class="space-y-2">
            <Label for="password">密碼</Label>
            <Input
              id="password"
              v-model="form.password"
              type="password"
              placeholder="輸入密碼"
              :disabled="isLoading"
              @keydown.enter="handleLogin"
            />
          </div>

          <div
            v-if="errorMessage"
            class="flex items-center gap-2 text-sm text-destructive bg-destructive/10 rounded-md px-3 py-2"
          >
            <AlertCircle class="size-4 shrink-0" />
            {{ errorMessage }}
          </div>

          <Button class="w-full" :disabled="isLoading" @click="handleLogin">
            <Spinner v-if="isLoading" class="size-4" />
            <LogIn v-else class="size-4" />
            {{ isLoading ? '登入中...' : '登入' }}
          </Button>
        </CardContent>
      </Card>

      <!-- 前往註冊 -->
      <p class="text-center text-sm text-muted-foreground">
        還沒有帳號？
        <RouterLink to="/register" class="text-primary hover:underline font-medium">
          立即註冊
        </RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { AlertCircle, LogIn } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import { Spinner } from '@/components/ui/spinner'
import { setStoredAccessToken } from '@/lib/accessToken'
import { AuthService } from '@/services'

const router = useRouter()

const form = ref({ username: '', password: '' })
const isLoading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  if (!form.value.username || !form.value.password) {
    errorMessage.value = '請填寫帳號與密碼'
    return
  }
  errorMessage.value = ''
  isLoading.value = true
  try {
    const { data } = await AuthService.login({
      body: {
        username: form.value.username.trim(),
        password: form.value.password,
      },
    })
    setStoredAccessToken(data.access_token)
    toast.success('登入成功', { description: '歡迎回來' })
    await router.push('/scenarios')
  } catch {
    // 錯誤訊息由 axios response interceptor（showAxiosErrorToast）顯示
  } finally {
    isLoading.value = false
  }
}
</script>
