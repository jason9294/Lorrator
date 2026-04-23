import { computed, onMounted, ref, watch } from 'vue'

type ColorMode = 'light' | 'dark'

const STORAGE_KEY = 'lorrator-color-mode'

const mode = ref<ColorMode>('dark')
const isDark = computed(() => mode.value === 'dark')

function applyMode(m: ColorMode) {
  if (m === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

watch(mode, (m) => {
  applyMode(m)
  localStorage.setItem(STORAGE_KEY, m)
})

export function useColorMode() {
  onMounted(() => {
    const stored = localStorage.getItem(STORAGE_KEY) as ColorMode | null
    if (stored) {
      mode.value = stored
    } else {
      mode.value = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    applyMode(mode.value)
  })

  function toggle() {
    mode.value = mode.value === 'dark' ? 'light' : 'dark'
  }

  return { mode, isDark, toggle }
}
