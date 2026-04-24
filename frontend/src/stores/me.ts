import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { AuthService, type MeResponse, type UpdateProfileRequest } from '@/services'

export const useMeStore = defineStore('me', () => {
  const me = ref<MeResponse | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const id = computed(() => me.value?.id ?? null)
  const username = computed(() => me.value?.username ?? null)
  const nickname = computed(() => me.value?.nickname ?? null)
  const avatarUrl = computed(() => me.value?.avatar_url ?? null)
  const displayName = computed(() => me.value?.nickname || me.value?.username || null)

  async function fetchMe() {
    console.log('[me-store] fetchMe')
    isLoading.value = true
    error.value = null
    try {
      const res = await AuthService.me()
      me.value = res.data
      return res.data
    } catch (e) {
      const detail = (e as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
      error.value = typeof detail === 'string' ? detail : '無法取得使用者資訊'
      me.value = null
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function ensureMe() {
    if (me.value) return me.value
    return await fetchMe()
  }

  async function updateProfile(body: UpdateProfileRequest) {
    const res = await AuthService.updateMe({ body })
    me.value = res.data
    return res.data
  }

  async function uploadAvatar(file: File) {
    const res = await AuthService.uploadAvatar({ body: { file } })
    me.value = res.data
    return res.data
  }

  function clear() {
    me.value = null
    error.value = null
    isLoading.value = false
  }

  return {
    me,
    id,
    username,
    nickname,
    avatarUrl,
    displayName,
    isLoading,
    error,
    fetchMe,
    ensureMe,
    updateProfile,
    uploadAvatar,
    clear,
  }
})

