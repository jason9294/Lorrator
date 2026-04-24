<script setup lang="ts">
import { ref } from 'vue'
import { Dices } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Spinner } from '@/components/ui/spinner'
import { RoomsService, type RoomMessageResponse } from '@/services'

const props = defineProps<{
  roomId: string
  disabled?: boolean
}>()

const emit = defineEmits<{
  rolled: [message: RoomMessageResponse]
}>()

const open = ref(false)
const mode = ref<'normal' | 'skill'>('normal')
const isRolling = ref(false)
const error = ref<string | null>(null)

// 普通擲骰
const diceCount = ref(1)
const diceFaces = ref(100)

// 技能檢定
const skillName = ref('')
const skillValue = ref<number | null>(null)

const PRESET_FACES = [4, 6, 8, 10, 12, 20, 100]

async function handleRoll() {
  error.value = null
  isRolling.value = true
  try {
    let res: Awaited<ReturnType<typeof RoomsService.rollDice>>
    if (mode.value === 'normal') {
      res = await RoomsService.rollDice({
        path: { room_id: props.roomId },
        body: { count: diceCount.value, faces: diceFaces.value },
      })
    } else {
      if (!skillName.value.trim()) {
        error.value = '請輸入技能名稱'
        return
      }
      if (!skillValue.value || skillValue.value < 1 || skillValue.value > 100) {
        error.value = '技能數值需介於 1–100'
        return
      }
      res = await RoomsService.skillCheck({
        path: { room_id: props.roomId },
        body: { skill_name: skillName.value.trim(), skill_value: skillValue.value },
      })
    }
    open.value = false
    emit('rolled', res.data)
  } catch (e) {
    const detail = (e as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
    error.value = typeof detail === 'string' ? detail : '擲骰失敗，請稍後再試'
  } finally {
    isRolling.value = false
  }
}

function switchMode(m: 'normal' | 'skill') {
  mode.value = m
  error.value = null
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogTrigger as-child>
      <Button
        variant="outline"
        size="icon"
        class="h-11 w-11 shrink-0"
        :disabled="props.disabled"
        title="擲骰"
      >
        <Dices class="size-4" />
      </Button>
    </DialogTrigger>

    <DialogContent class="sm:max-w-sm">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          <Dices class="size-4" />
          擲骰
        </DialogTitle>
      </DialogHeader>

      <!-- 模式切換 -->
      <div class="flex rounded-lg border overflow-hidden text-sm">
        <button
          class="flex-1 py-2 font-medium transition-colors"
          :class="
            mode === 'normal'
              ? 'bg-primary text-primary-foreground'
              : 'bg-transparent text-muted-foreground hover:text-foreground'
          "
          @click="switchMode('normal')"
        >
          普通擲骰
        </button>
        <button
          class="flex-1 py-2 font-medium transition-colors"
          :class="
            mode === 'skill'
              ? 'bg-primary text-primary-foreground'
              : 'bg-transparent text-muted-foreground hover:text-foreground'
          "
          @click="switchMode('skill')"
        >
          技能檢定
        </button>
      </div>

      <!-- 普通擲骰 -->
      <div v-if="mode === 'normal'" class="space-y-4">
        <div class="flex items-center gap-3">
          <div class="flex-1 space-y-1.5">
            <Label>數量</Label>
            <Input
              v-model.number="diceCount"
              type="number"
              min="1"
              max="100"
              class="text-center"
            />
          </div>
          <span class="text-xl font-bold text-muted-foreground mt-5">d</span>
          <div class="flex-1 space-y-1.5">
            <Label>面數</Label>
            <Select
              :model-value="String(diceFaces)"
              @update:model-value="(v) => (diceFaces = Number(v))"
            >
              <SelectTrigger class="text-center">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem v-for="f in PRESET_FACES" :key="f" :value="String(f)">
                  d{{ f }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <p class="text-center text-sm text-muted-foreground">
          即將擲出
          <span class="font-bold text-foreground">{{ diceCount }}d{{ diceFaces }}</span>
        </p>
      </div>

      <!-- 技能檢定 -->
      <div v-else class="space-y-4">
        <div class="space-y-1.5">
          <Label>技能名稱</Label>
          <Input v-model="skillName" placeholder="例：偵查、說服、潛行…" />
        </div>
        <div class="space-y-1.5">
          <Label>技能數值（1–100）</Label>
          <Input
            v-model.number="skillValue"
            type="number"
            min="1"
            max="100"
            placeholder="60"
          />
        </div>
        <p class="text-xs text-muted-foreground leading-relaxed">
          系統將擲 1d100，依結果判定：<br />
          大成功 ≤ 數值÷5 ／ 困難成功 ≤ 數值÷2 ／ 成功 ≤ 數值 ／ 失敗 ／ 大失敗 ≥ 96
        </p>
      </div>

      <!-- 錯誤 -->
      <p v-if="error" class="text-sm text-destructive">{{ error }}</p>

      <!-- 確認按鈕 -->
      <Button class="w-full gap-2" :disabled="isRolling" @click="handleRoll">
        <Spinner v-if="isRolling" class="size-4" />
        <Dices v-else class="size-4" />
        {{ isRolling ? '擲骰中…' : '擲！' }}
      </Button>
    </DialogContent>
  </Dialog>
</template>
