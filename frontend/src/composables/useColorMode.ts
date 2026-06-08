import { computed } from 'vue'
import { useColorMode as useVueColorMode, usePreferredDark } from '@vueuse/core'

const STORAGE_KEY = 'lorrator-color-mode'

const mode = useVueColorMode({
  storageKey: STORAGE_KEY,
  initialValue: 'auto',
})

const preferredDark = usePreferredDark()

export function useColorMode() {
  const isDark = computed(
    () => mode.value === 'dark' || (mode.value === 'auto' && preferredDark.value),
  )

  function toggle() {
    mode.value = isDark.value ? 'light' : 'dark'
  }

  return { mode, isDark, toggle }
}
