<script setup lang="ts">
import { ref } from 'vue'
import { Plus, Trash2 } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { CharacterSkillInput, CoCSkillCategory, CoCSkillType } from '@/services'

const skills = defineModel<CharacterSkillInput[]>({ required: true })

const showAddForm = ref(false)

const emptySkill = (): CharacterSkillInput => ({
  type: 'STANDARD',
  category: 'CUSTOM',
  name: '',
  base_value: 0,
  occupation_value: 0,
  interest_value: 0,
  adjustments: [],
})

const newSkill = ref<CharacterSkillInput>(emptySkill())

const categoryOptions: { value: CoCSkillCategory; label: string }[] = [
  { value: 'NEGOTIATION', label: '溝通' },
  { value: 'INVESTIGATION', label: '調查' },
  { value: 'LANGUAGE', label: '語言' },
  { value: 'MEDICAL', label: '醫療' },
  { value: 'PILOT', label: '特殊駕駛' },
  { value: 'SURVIVAL', label: '生存' },
  { value: 'ART_AND_CRAFT', label: '藝術與工藝' },
  { value: 'SCIENCE', label: '科學' },
  { value: 'CUSTOM', label: '自訂' },
]

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const typeOptions: { value: CoCSkillType; label: string }[] = [
  { value: 'STANDARD', label: '標準' },
  { value: 'DERIVED', label: '衍生' },
  { value: 'CUSTOM', label: '自訂' },
]

const categoryLabel = Object.fromEntries(categoryOptions.map((o) => [o.value, o.label]))

function skillTotal(s: CharacterSkillInput): number {
  return (s.base_value ?? 0) + (s.occupation_value ?? 0) + (s.interest_value ?? 0)
}

function addSkill() {
  if (!newSkill.value.name.trim()) return
  skills.value = [...skills.value, { ...newSkill.value, name: newSkill.value.name.trim() }]
  newSkill.value = emptySkill()
  showAddForm.value = false
}

function removeSkill(index: number) {
  skills.value = skills.value.filter((_, i) => i !== index)
}

function cancelAdd() {
  newSkill.value = emptySkill()
  showAddForm.value = false
}
</script>

<template>
  <div class="space-y-3">
    <!-- 技能列表 -->
    <div v-if="skills.length > 0" class="overflow-x-auto rounded-lg border">
      <table class="w-full text-sm">
        <thead>
          <tr class="bg-muted/40 border-b">
            <th class="text-left text-xs text-muted-foreground font-medium px-3 py-2">技能名稱</th>
            <th class="text-left text-xs text-muted-foreground font-medium px-3 py-2">分類</th>
            <th class="text-right text-xs text-muted-foreground font-medium px-3 py-2">基礎</th>
            <th class="text-right text-xs text-muted-foreground font-medium px-3 py-2">職業</th>
            <th class="text-right text-xs text-muted-foreground font-medium px-3 py-2">興趣</th>
            <th class="text-right text-xs text-muted-foreground font-medium px-3 py-2">合計</th>
            <th class="px-3 py-2" />
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(skill, i) in skills"
            :key="i"
            class="border-b border-border/40 last:border-0 hover:bg-muted/20"
          >
            <td class="px-3 py-2 font-medium">{{ skill.name }}</td>
            <td class="px-3 py-2 text-xs text-muted-foreground">
              {{ categoryLabel[skill.category] ?? skill.category }}
            </td>
            <td class="px-3 py-2 text-right">
              <Input
                type="number"
                class="w-16 h-7 text-center text-xs px-1"
                :model-value="skill.base_value ?? 0"
                @update:model-value="(v) => (skills[i] = { ...skills[i], base_value: Number(v) })"
              />
            </td>
            <td class="px-3 py-2 text-right">
              <Input
                type="number"
                class="w-16 h-7 text-center text-xs px-1"
                :model-value="skill.occupation_value ?? 0"
                @update:model-value="
                  (v) => (skills[i] = { ...skills[i], occupation_value: Number(v) })
                "
              />
            </td>
            <td class="px-3 py-2 text-right">
              <Input
                type="number"
                class="w-16 h-7 text-center text-xs px-1"
                :model-value="skill.interest_value ?? 0"
                @update:model-value="
                  (v) => (skills[i] = { ...skills[i], interest_value: Number(v) })
                "
              />
            </td>
            <td class="px-3 py-2 text-right font-bold">{{ skillTotal(skill) }}</td>
            <td class="px-3 py-2">
              <Button
                variant="ghost"
                size="icon-sm"
                class="text-destructive/60 hover:text-destructive"
                @click="removeSkill(i)"
              >
                <Trash2 class="size-3.5" />
              </Button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div
      v-else-if="!showAddForm"
      class="rounded-lg border border-dashed p-6 text-center text-sm text-muted-foreground/60"
    >
      尚未新增任何技能
    </div>

    <!-- 新增技能表單 -->
    <div v-if="showAddForm" class="rounded-lg border bg-muted/20 p-4 space-y-3">
      <p class="text-xs font-semibold text-muted-foreground">新增技能</p>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div class="space-y-1.5">
          <Label class="text-xs">技能名稱</Label>
          <Input v-model="newSkill.name" placeholder="例如：圖書館使用" class="h-8 text-sm" />
        </div>
        <div class="space-y-1.5">
          <Label class="text-xs">分類</Label>
          <Select v-model="newSkill.category">
            <SelectTrigger class="h-8 text-sm">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="opt in categoryOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <div class="grid grid-cols-3 gap-3">
        <div class="space-y-1.5">
          <Label class="text-xs">基礎值</Label>
          <Input
            v-model.number="newSkill.base_value"
            type="number"
            min="0"
            max="99"
            class="h-8 text-sm text-center"
          />
        </div>
        <div class="space-y-1.5">
          <Label class="text-xs">職業點數</Label>
          <Input
            v-model.number="newSkill.occupation_value"
            type="number"
            min="0"
            max="99"
            class="h-8 text-sm text-center"
          />
        </div>
        <div class="space-y-1.5">
          <Label class="text-xs">興趣點數</Label>
          <Input
            v-model.number="newSkill.interest_value"
            type="number"
            min="0"
            max="99"
            class="h-8 text-sm text-center"
          />
        </div>
      </div>
      <div class="flex justify-end gap-2">
        <Button variant="outline" size="sm" @click="cancelAdd">取消</Button>
        <Button size="sm" :disabled="!newSkill.name.trim()" @click="addSkill">
          <Plus class="size-3.5" />
          加入
        </Button>
      </div>
    </div>

    <Button
      v-if="!showAddForm"
      variant="outline"
      size="sm"
      class="gap-1.5 w-full"
      @click="showAddForm = true"
    >
      <Plus class="size-3.5" />
      新增技能
    </Button>
  </div>
</template>
