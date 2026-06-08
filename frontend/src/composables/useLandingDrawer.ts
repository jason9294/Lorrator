import { inject, provide, ref, type InjectionKey, type Ref } from 'vue'

export interface LandingDrawerContext {
  expanded: Ref<boolean>
  toggle: () => void
}

const landingDrawerKey: InjectionKey<LandingDrawerContext> = Symbol('landing-drawer')

export function provideLandingDrawer(defaultExpanded = true) {
  const expanded = ref(defaultExpanded)

  function toggle() {
    expanded.value = !expanded.value
  }

  const context: LandingDrawerContext = { expanded, toggle }
  provide(landingDrawerKey, context)

  return context
}

export function useLandingDrawer() {
  const context = inject(landingDrawerKey)
  if (!context) {
    throw new Error('useLandingDrawer must be used within a component that called provideLandingDrawer')
  }
  return context
}
