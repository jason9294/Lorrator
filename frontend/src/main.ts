import { createApp } from 'vue'
import { createPinia } from 'pinia'

import { client } from '@/services/client.gen'
import { getStoredAccessToken } from '@/lib/accessToken'
import { showAxiosErrorToast } from '@/lib/toast/showAxiosErrorToast'

import './style.css'

import App from './App.vue'
import router from './router'
import type { AxiosError } from 'axios'

const app = createApp(App)

app.use(createPinia())
app.use(router)

client.setConfig({
  auth: () => getStoredAccessToken() ?? undefined,
})

// 攔截 http error code 並顯示錯誤訊息
client.instance.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    showAxiosErrorToast(error)
    return Promise.reject(error)
  }
)

app.mount('#app')
