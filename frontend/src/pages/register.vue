<template>
  <div class="min-h-screen flex items-center justify-center bg-background text-foreground p-4">
    <div class="w-full max-w-sm space-y-6">

      <!-- Logo -->
      <div class="flex flex-col items-center gap-3 text-center">
        <div class="w-12 h-12 rounded-2xl bg-linear-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-lg">
          <svg class="w-6 h-6 text-white" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26C17.81 13.47 19 11.38 19 9c0-3.87-3.13-7-7-7zm0 12c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/>
          </svg>
        </div>
        <div>
          <h1 class="text-2xl font-bold">建立帳號</h1>
          <p class="text-sm text-muted-foreground mt-1">開始你的跑團旅程</p>
        </div>
      </div>

      <!-- 註冊表單 -->
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
            />
          </div>

          <div class="space-y-2">
            <Label for="confirm-password">確認密碼</Label>
            <Input
              id="confirm-password"
              v-model="form.confirmPassword"
              type="password"
              placeholder="再次輸入密碼"
              :disabled="isLoading"
              @keydown.enter="handleRegister"
            />
          </div>

          <div v-if="errorMessage" class="flex items-center gap-2 text-sm text-destructive bg-destructive/10 rounded-md px-3 py-2">
            <AlertCircle class="size-4 shrink-0" />
            {{ errorMessage }}
          </div>

          <Button class="w-full" :disabled="isLoading" @click="handleRegister">
            <Spinner v-if="isLoading" class="size-4" />
            <UserPlus v-else class="size-4" />
            {{ isLoading ? '建立中...' : '建立帳號' }}
          </Button>
        </CardContent>
      </Card>

      <!-- 前往登入 -->
      <p class="text-center text-sm text-muted-foreground">
        已有帳號？
        <RouterLink to="/login" class="text-primary hover:underline font-medium">
          立即登入
        </RouterLink>
      </p>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { AlertCircle, UserPlus } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import { Spinner } from '@/components/ui/spinner'
import { setStoredAccessToken } from '@/lib/accessToken'
import { AuthService } from '@/services'

const router = useRouter()

const form = ref({ username: '', password: '', confirmPassword: '' })
const isLoading = ref(false)
const errorMessage = ref('')

async function handleRegister() {
  errorMessage.value = ''
  if (!form.value.username || !form.value.password || !form.value.confirmPassword) {
    errorMessage.value = '請填寫所有欄位'
    return
  }
  if (form.value.password !== form.value.confirmPassword) {
    errorMessage.value = '兩次輸入的密碼不一致'
    return
  }
  if (form.value.password.length < 6) {
    errorMessage.value = '密碼長度至少需要 6 個字元'
    return
  }
  isLoading.value = true
  try {
    const { data } = await AuthService.register({
      body: {
        username: form.value.username.trim(),
        password: form.value.password,
      },
    })
    setStoredAccessToken(data.access_token)
    toast.success('註冊成功', { description: '已自動登入' })
    await router.push('/scenarios')
  } catch {
    // 錯誤訊息由 axios response interceptor（showAxiosErrorToast）顯示
  } finally {
    isLoading.value = false
  }
}
</script>
