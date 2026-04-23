<script setup lang="ts">
import { computed } from 'vue'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import type { CoCCharacterDataOutput, CharacterSkillOutput } from '@/services'

const props = defineProps<{
  name: string
  data: CoCCharacterDataOutput
}>()

const attrs = computed(() => [
  { key: 'strength',    label: 'STR', name: '力量' },
  { key: 'constitution', label: 'CON', name: '體質' },
  { key: 'size',        label: 'SIZ', name: '體型' },
  { key: 'dexterity',   label: 'DEX', name: '敏捷' },
  { key: 'appearance',  label: 'APP', name: '外表' },
  { key: 'intelligence', label: 'INT', name: '智力' },
  { key: 'power',       label: 'POW', name: '意志' },
  { key: 'education',   label: 'EDU', name: '教育' },
])

function attrValue(key: string): number {
  return (props.data as Record<string, unknown>)[key] as number ?? 0
}

function half(v: number) { return Math.floor(v / 2) }
function fifth(v: number) { return Math.floor(v / 5) }

const backgroundFields = computed(() => [
  { key: 'ideology_beliefs',    label: '思想與信念' },
  { key: 'significant_people',  label: '重要之人' },
  { key: 'meaningful_locations', label: '意義非凡之地' },
  { key: 'treasured_possessions', label: '寶貴之物' },
  { key: 'traits',              label: '特點' },
  { key: 'bonds',               label: '羈絆' },
])

function bgValue(key: string): string {
  return (props.data as Record<string, unknown>)[key] as string ?? ''
}

const skills = computed<CharacterSkillOutput[]>(() => props.data.skills ?? [])

const skillCategoryLabel: Record<string, string> = {
  NEGOTIATION: '溝通', INVESTIGATION: '調查', LANGUAGE: '語言',
  MEDICAL: '醫療', PILOT: '特殊駕駛', SURVIVAL: '生存',
  ART_AND_CRAFT: '藝術與工藝', SCIENCE: '科學', CUSTOM: '自訂',
}
</script>

<template>
  <div class="space-y-6">
    <!-- 基本資訊 -->
    <div class="rounded-xl border bg-card p-5 space-y-4">
      <div class="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h2 class="text-xl font-bold">{{ name }}</h2>
          <p v-if="data.occupation" class="text-sm text-muted-foreground mt-0.5">{{ data.occupation }}</p>
        </div>
        <Badge variant="outline" class="shrink-0">COC 7e</Badge>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
        <div v-if="data.age">
          <span class="text-xs text-muted-foreground block">年齡</span>
          <span class="font-medium">{{ data.age }} 歲</span>
        </div>
        <div v-if="data.gender">
          <span class="text-xs text-muted-foreground block">性別</span>
          <span class="font-medium">{{ data.gender }}</span>
        </div>
        <div v-if="data.residence">
          <span class="text-xs text-muted-foreground block">居住地</span>
          <span class="font-medium">{{ data.residence }}</span>
        </div>
        <div v-if="data.birthplace">
          <span class="text-xs text-muted-foreground block">出生地</span>
          <span class="font-medium">{{ data.birthplace }}</span>
        </div>
      </div>

      <p v-if="data.description" class="text-sm text-muted-foreground leading-relaxed border-t pt-3">
        {{ data.description }}
      </p>
    </div>

    <!-- 特徵值 -->
    <div class="rounded-xl border bg-card p-5">
      <h3 class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">特徵值</h3>
      <div class="grid grid-cols-4 sm:grid-cols-8 gap-2">
        <div
          v-for="attr in attrs"
          :key="attr.key"
          class="flex flex-col items-center rounded-lg bg-muted/40 p-2.5 gap-1"
        >
          <span class="text-[10px] text-muted-foreground font-medium">{{ attr.label }}</span>
          <span class="text-lg font-bold leading-none">{{ attrValue(attr.key) }}</span>
          <Separator class="w-full my-0.5" />
          <span class="text-[10px] text-muted-foreground">{{ half(attrValue(attr.key)) }}</span>
          <span class="text-[10px] text-muted-foreground/60">{{ fifth(attrValue(attr.key)) }}</span>
        </div>
      </div>
      <p class="text-[10px] text-muted-foreground/60 mt-2 text-center">值 / 半值 / 五分之一</p>
    </div>

    <!-- 狀態值 -->
    <div class="rounded-xl border bg-card p-5">
      <h3 class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">狀態</h3>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div class="flex flex-col items-center rounded-lg bg-red-500/10 border border-red-500/20 p-3">
          <span class="text-[10px] text-red-500/70 font-medium mb-1">HP 生命</span>
          <span class="text-2xl font-bold text-red-600 dark:text-red-400">{{ data.hp ?? 0 }}</span>
        </div>
        <div class="flex flex-col items-center rounded-lg bg-blue-500/10 border border-blue-500/20 p-3">
          <span class="text-[10px] text-blue-500/70 font-medium mb-1">MP 魔法</span>
          <span class="text-2xl font-bold text-blue-600 dark:text-blue-400">{{ data.mp ?? 0 }}</span>
        </div>
        <div class="flex flex-col items-center rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-3">
          <span class="text-[10px] text-emerald-500/70 font-medium mb-1">SAN 理智</span>
          <span class="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{{ data.san ?? 0 }}</span>
        </div>
        <div class="flex flex-col items-center rounded-lg bg-amber-500/10 border border-amber-500/20 p-3">
          <span class="text-[10px] text-amber-500/70 font-medium mb-1">LUCK 幸運</span>
          <span class="text-2xl font-bold text-amber-600 dark:text-amber-400">{{ data.luck ?? 0 }}</span>
        </div>
      </div>

      <div v-if="data.cthulhu_mythos || data.believer" class="flex items-center gap-3 mt-3 pt-3 border-t">
        <div v-if="data.cthulhu_mythos" class="text-sm">
          <span class="text-muted-foreground">克蘇魯神話：</span>
          <span class="font-medium">{{ data.cthulhu_mythos }}</span>
        </div>
        <Badge v-if="data.believer" variant="destructive" class="text-[10px]">神話相信者</Badge>
      </div>
    </div>

    <!-- 背景 -->
    <div
      v-if="backgroundFields.some(f => bgValue(f.key))"
      class="rounded-xl border bg-card p-5"
    >
      <h3 class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">背景故事</h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div v-for="field in backgroundFields" :key="field.key">
          <template v-if="bgValue(field.key)">
            <span class="text-xs font-medium text-muted-foreground block mb-1">{{ field.label }}</span>
            <p class="text-sm leading-relaxed">{{ bgValue(field.key) }}</p>
          </template>
        </div>
      </div>
    </div>

    <!-- 技能 -->
    <div v-if="skills.length > 0" class="rounded-xl border bg-card p-5">
      <h3 class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
        技能 <span class="ml-1 text-muted-foreground/60">({{ skills.length }})</span>
      </h3>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b">
              <th class="text-left text-xs text-muted-foreground font-medium pb-2 pr-3">技能名稱</th>
              <th class="text-left text-xs text-muted-foreground font-medium pb-2 pr-3">分類</th>
              <th class="text-right text-xs text-muted-foreground font-medium pb-2 pr-3">基礎</th>
              <th class="text-right text-xs text-muted-foreground font-medium pb-2 pr-3">職業</th>
              <th class="text-right text-xs text-muted-foreground font-medium pb-2 pr-3">興趣</th>
              <th class="text-right text-xs text-muted-foreground font-medium pb-2">合計</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="skill in skills"
              :key="skill.name"
              class="border-b border-border/40 last:border-0"
            >
              <td class="py-2 pr-3 font-medium">{{ skill.name }}</td>
              <td class="py-2 pr-3 text-xs text-muted-foreground">{{ skillCategoryLabel[skill.category] ?? skill.category }}</td>
              <td class="py-2 pr-3 text-right text-muted-foreground">{{ skill.base_value ?? 0 }}</td>
              <td class="py-2 pr-3 text-right text-muted-foreground">{{ skill.occupation_value ?? 0 }}</td>
              <td class="py-2 pr-3 text-right text-muted-foreground">{{ skill.interest_value ?? 0 }}</td>
              <td class="py-2 text-right font-bold">{{ skill.total_value }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div
      v-else
      class="rounded-xl border border-dashed p-8 text-center text-sm text-muted-foreground/60"
    >
      尚未填寫技能
    </div>
  </div>
</template>
