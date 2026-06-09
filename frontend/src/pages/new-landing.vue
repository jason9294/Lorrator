<script setup lang="ts">
import { LogIn } from 'lucide-vue-next'
import LandingShell from '@/components/layout/landing/LandingShell.vue'
</script>

<template>
  <LandingShell>
    <section
      class="relative flex min-h-[819px] w-full flex-col items-center justify-center overflow-hidden border-outline-variant/20 px-margin-mobile pb-margin-desktop pt-stack-lg md:px-margin-desktop"
    >
      <div
        class="absolute inset-0 z-0 bg-cover bg-center opacity-20"
        :style="{ backgroundImage: `url('/hero-bg.png')` }"
      />
      <div class="absolute inset-0 z-0 bg-linear-to-b from-surface/50 to-surface" />

      <div
        class="relative z-10 mt-stack-lg flex max-w-[800px] flex-col items-center gap-stack-md text-center"
      >
        <h2
          class="mx-auto max-w-[600px] font-serif text-headline-lg-mobile leading-tight text-primary md:text-headline-lg"
        >
          由 LLM 驅動的 TRPG 平台
        </h2>

        <p class="mx-auto max-w-[500px] font-sans text-body-lg text-on-surface-variant">
          在流暢、現代的環境中管理劇本與角色卡，體驗由 LLM 進行的 TRPG。
        </p>

        <div class="mt-stack-sm flex items-center gap-stack-sm">
          <!-- Login Button -->
          <RouterLink to="/login">
            <button
              type="button"
              class="flex items-center gap-2 rounded bg-primary-container px-6 py-3 font-mono text-label-md text-primary-foreground transition-colors hover:bg-primary"
            >
              登入
              <LogIn class="size-4" />
            </button>
          </RouterLink>

          <!-- Register Button -->
          <RouterLink to="/register">
            <button
              type="button"
              class="rounded border border-secondary px-6 py-3 font-mono text-label-md text-secondary transition-colors hover:bg-secondary-fixed/10"
            >
              註冊
            </button>
          </RouterLink>
        </div>
      </div>
    </section>
  </LandingShell>
</template>

<style scoped>
.shadow-ambient {
  box-shadow: 0 0 20px 0 rgba(44, 44, 44, 0.05);
}
</style>
