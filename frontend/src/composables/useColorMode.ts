import { onMounted, ref, watch } from 'vue'

type ColorMode = 'light' | 'dark'

const STORAGE_KEY = 'lorrator-color-mode'

// 單例：整個 App 共享同一個狀態
const mode = ref<ColorMode>('dark')

function applyMode(m: ColorMode) {
  const html = document.documentElement
  if (m === 'dark') {
    html.classList.add('dark')
  } else {
    html.classList.remove('dark')
  }
}

export function useColorMode() {
  onMounted(() => {
    // 讀取 localStorage，若無則偵測系統偏好
    const stored = localStorage.getItem(STORAGE_KEY) as ColorMode | null
    if (stored) {
      mode.value = stored
    } else {
      mode.value = window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light'
    }
    applyMode(mode.value)
  })

  watch(mode, (m) => {
    applyMode(m)
    localStorage.setItem(STORAGE_KEY, m)
  })

  function toggle() {
    mode.value = mode.value === 'dark' ? 'light' : 'dark'
  }

  const isDark = ref(false)
  watch(mode, (m) => { isDark.value = m === 'dark' }, { immediate: true })

  return { mode, isDark, toggle }
}
