<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { Save, X } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Separator } from '@/components/ui/separator'
import { Spinner } from '@/components/ui/spinner'
import CoCSkillsEditor from './CoCSkillsEditor.vue'
import type { CoCCharacterDataInput } from '@/services'

const props = withDefaults(
  defineProps<{
    initialData?: CoCCharacterDataInput | null
    isSaving?: boolean
  }>(),
  {
    initialData: null,
    isSaving: false,
  },
)

const emit = defineEmits<{
  submit: [data: CoCCharacterDataInput]
  cancel: []
}>()

type Tab = 'basic' | 'attributes' | 'background' | 'skills'
const activeTab = ref<Tab>('basic')

const tabs: { key: Tab; label: string }[] = [
  { key: 'basic', label: '基本資訊' },
  { key: 'attributes', label: '能力值' },
  { key: 'background', label: '背景故事' },
  { key: 'skills', label: '技能' },
]

function makeForm(d?: CoCCharacterDataInput | null): CoCCharacterDataInput {
  return {
    occupation: d?.occupation ?? '',
    age: d?.age ?? 0,
    gender: d?.gender ?? '',
    residence: d?.residence ?? '',
    birthplace: d?.birthplace ?? '',
    description: d?.description ?? '',
    hp: d?.hp ?? 0,
    mp: d?.mp ?? 0,
    san: d?.san ?? 0,
    luck: d?.luck ?? 0,
    strength: d?.strength ?? 0,
    constitution: d?.constitution ?? 0,
    size: d?.size ?? 0,
    dexterity: d?.dexterity ?? 0,
    appearance: d?.appearance ?? 0,
    intelligence: d?.intelligence ?? 0,
    power: d?.power ?? 0,
    education: d?.education ?? 0,
    believer: d?.believer ?? false,
    cthulhu_mythos: d?.cthulhu_mythos ?? 0,
    ideology_beliefs: d?.ideology_beliefs ?? '',
    significant_people: d?.significant_people ?? '',
    meaningful_locations: d?.meaningful_locations ?? '',
    treasured_possessions: d?.treasured_possessions ?? '',
    traits: d?.traits ?? '',
    bonds: d?.bonds ?? '',
    skills: d?.skills ?? [],
    skill_adjustments: d?.skill_adjustments ?? [],
  }
}

const form = reactive<CoCCharacterDataInput>(makeForm(props.initialData))

watch(
  () => props.initialData,
  (v) => {
    Object.assign(form, makeForm(v))
  },
  { immediate: false },
)

const attributeFields: { key: keyof CoCCharacterDataInput; label: string; abbr: string }[] = [
  { key: 'strength', label: '力量', abbr: 'STR' },
  { key: 'constitution', label: '體質', abbr: 'CON' },
  { key: 'size', label: '體型', abbr: 'SIZ' },
  { key: 'dexterity', label: '敏捷', abbr: 'DEX' },
  { key: 'appearance', label: '外表', abbr: 'APP' },
  { key: 'intelligence', label: '智力', abbr: 'INT' },
  { key: 'power', label: '意志', abbr: 'POW' },
  { key: 'education', label: '教育', abbr: 'EDU' },
]

const statusFields: { key: keyof CoCCharacterDataInput; label: string; color: string }[] = [
  { key: 'hp', label: 'HP 生命', color: 'text-red-500' },
  { key: 'mp', label: 'MP 魔法', color: 'text-blue-500' },
  { key: 'san', label: 'SAN 理智', color: 'text-emerald-500' },
  { key: 'luck', label: 'LUCK 幸運', color: 'text-amber-500' },
]

const backgroundFields: { key: keyof CoCCharacterDataInput; label: string; placeholder: string }[] =
  [
    { key: 'ideology_beliefs', label: '思想與信念', placeholder: '角色的信仰、價值觀…' },
    {
      key: 'significant_people',
      label: '重要之人',
      placeholder: '對角色而言最重要的人是誰，以及原因…',
    },
    { key: 'meaningful_locations', label: '意義非凡之地', placeholder: '對角色而言最重要的地方…' },
    { key: 'treasured_possessions', label: '寶貴之物', placeholder: '角色最珍視的物品…' },
    { key: 'traits', label: '特點', placeholder: '角色的個性特徵…' },
    { key: 'bonds', label: '羈絆', placeholder: '與角色有深厚關聯的人事物…' },
  ]

function handleSubmit() {
  if (props.isSaving) return
  emit('submit', { ...form })
}
</script>

<template>
  <div class="space-y-5">
    <!-- Tab 切換 -->
    <div class="flex gap-1 p-1 rounded-lg bg-muted/50 border w-fit">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="px-3 py-1.5 rounded-md text-sm font-medium transition-all"
        :class="
          activeTab === tab.key
            ? 'bg-background text-foreground shadow-sm'
            : 'text-muted-foreground hover:text-foreground'
        "
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- 基本資訊 -->
    <div v-show="activeTab === 'basic'" class="space-y-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="space-y-1.5">
          <Label>職業</Label>
          <Input v-model="form.occupation" placeholder="例如：私家偵探" />
        </div>
        <div class="space-y-1.5">
          <Label>年齡</Label>
          <Input v-model.number="form.age" type="number" min="1" max="99" placeholder="0" />
        </div>
        <div class="space-y-1.5">
          <Label>性別</Label>
          <Input v-model="form.gender" placeholder="例如：男" />
        </div>
        <div class="space-y-1.5">
          <Label>居住地</Label>
          <Input v-model="form.residence" placeholder="例如：阿卡姆" />
        </div>
        <div class="space-y-1.5">
          <Label>出生地</Label>
          <Input v-model="form.birthplace" placeholder="例如：麻省波士頓" />
        </div>
      </div>
      <div class="space-y-1.5">
        <Label>角色描述</Label>
        <Textarea v-model="form.description" placeholder="簡短描述角色的外貌或個性…" :rows="3" />
      </div>
    </div>

    <!-- 能力值 -->
    <div v-show="activeTab === 'attributes'" class="space-y-5">
      <div>
        <h4 class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
          特徵值
        </h4>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div v-for="attr in attributeFields" :key="attr.key" class="space-y-1.5">
            <Label class="text-xs">
              <span class="font-bold">{{ attr.abbr }}</span>
              <span class="text-muted-foreground ml-1">{{ attr.label }}</span>
            </Label>
            <Input
              :model-value="(form[attr.key] as number) ?? 0"
              type="number"
              min="0"
              max="99"
              class="text-center"
              @update:model-value="(v) => ((form[attr.key] as number) = Number(v))"
            />
          </div>
        </div>
      </div>

      <Separator />

      <div>
        <h4 class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
          狀態值
        </h4>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div v-for="stat in statusFields" :key="stat.key" class="space-y-1.5">
            <Label class="text-xs" :class="stat.color">{{ stat.label }}</Label>
            <Input
              :model-value="(form[stat.key] as number) ?? 0"
              type="number"
              min="0"
              class="text-center"
              @update:model-value="(v) => ((form[stat.key] as number) = Number(v))"
            />
          </div>
        </div>
      </div>

      <Separator />

      <div>
        <h4 class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
          神話相關
        </h4>
        <div class="flex items-center gap-4 flex-wrap">
          <div class="space-y-1.5">
            <Label class="text-xs">克蘇魯神話</Label>
            <Input
              v-model.number="form.cthulhu_mythos"
              type="number"
              min="0"
              max="99"
              class="w-24 text-center"
            />
          </div>
          <label class="flex items-center gap-2 cursor-pointer select-none mt-4">
            <input
              v-model="form.believer"
              type="checkbox"
              class="w-4 h-4 rounded accent-destructive cursor-pointer"
            />
            <span class="text-sm">神話相信者</span>
          </label>
        </div>
      </div>
    </div>

    <!-- 背景故事 -->
    <div v-show="activeTab === 'background'" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div v-for="field in backgroundFields" :key="field.key" class="space-y-1.5">
        <Label>{{ field.label }}</Label>
        <Textarea
          :model-value="(form[field.key] as string) ?? ''"
          :placeholder="field.placeholder"
          :rows="3"
          @update:model-value="(v) => ((form[field.key] as string) = v)"
        />
      </div>
    </div>

    <!-- 技能 -->
    <div v-show="activeTab === 'skills'">
      <CoCSkillsEditor v-model="form.skills!" />
    </div>

    <!-- 操作列 -->
    <Separator />
    <div class="flex justify-end gap-2">
      <Button variant="outline" :disabled="isSaving" @click="emit('cancel')">
        <X class="size-4" />
        取消
      </Button>
      <Button :disabled="isSaving" @click="handleSubmit">
        <Spinner v-if="isSaving" class="size-4" />
        <Save v-else class="size-4" />
        {{ isSaving ? '儲存中…' : '儲存角色卡' }}
      </Button>
    </div>
  </div>
</template>
