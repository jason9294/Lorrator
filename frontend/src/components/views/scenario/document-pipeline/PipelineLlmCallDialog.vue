<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Braces } from 'lucide-vue-next'
import type { DocumentProcessingLlmCall } from '@/types/document-processing'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { cn } from '@/lib/utils'

const open = defineModel<boolean>('open', { required: true })

const props = defineProps<{
  call: DocumentProcessingLlmCall | null
}>()

const showRequestJson = ref(false)
const showResponseJson = ref(false)

watch(
  () => props.call?.id,
  () => {
    showRequestJson.value = false
    showResponseJson.value = false
  },
)

type LlmMessage = {
  role: string
  content: string
}

const requestMessages = computed((): LlmMessage[] => {
  if (!props.call) return []
  return props.call.request
    .map((item) => {
      const role = typeof item.role === 'string' ? item.role : 'unknown'
      const content = normalizeContent(item.content)
      return { role, content }
    })
    .filter((message) => message.content.length > 0)
})

const formattedRequestJson = computed(() =>
  props.call ? JSON.stringify(props.call.request, null, 2) : '',
)

const formattedResponseJson = computed(() => {
  if (!props.call) return ''
  if (typeof props.call.response === 'string') {
    return props.call.response
  }
  return JSON.stringify(props.call.response, null, 2)
})

const responseObject = computed(() => {
  if (!props.call || typeof props.call.response !== 'object' || props.call.response === null) {
    return null
  }
  return props.call.response
})

const entityGroups = computed(() => {
  const groups = responseObject.value?.entity_groups
  if (!Array.isArray(groups)) return null
  return groups.filter((group): group is string[] => Array.isArray(group))
})

const extractedEntities = computed(() => {
  const entities = responseObject.value?.entities
  if (!Array.isArray(entities)) return null
  return entities as Array<Record<string, unknown>>
})

const extractedRelationships = computed(() => {
  const relationships = responseObject.value?.relationships
  if (!Array.isArray(relationships)) return null
  return relationships as Array<Record<string, unknown>>
})

function normalizeContent(value: unknown): string {
  if (typeof value === 'string') return value
  if (value === null || value === undefined) return ''
  if (Array.isArray(value)) {
    return value
      .map((part) => {
        if (typeof part === 'string') return part
        if (part && typeof part === 'object' && 'text' in part) {
          return String((part as { text?: unknown }).text ?? '')
        }
        return JSON.stringify(part)
      })
      .join('\n')
  }
  if (typeof value === 'object' && 'text' in value) {
    return String((value as { text?: unknown }).text ?? '')
  }
  return JSON.stringify(value)
}

function roleLabel(role: string) {
  if (role === 'system') return 'System'
  if (role === 'user') return 'User'
  if (role === 'assistant') return 'Assistant'
  return role
}

function roleBadgeClass(role: string) {
  if (role === 'system') return 'bg-muted text-muted-foreground'
  if (role === 'user') return 'bg-primary/10 text-primary'
  if (role === 'assistant') return 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400'
  return 'bg-muted text-muted-foreground'
}

function fieldText(value: unknown) {
  return typeof value === 'string' ? value : String(value ?? '')
}
</script>

<template>
  <Dialog v-model:open="open">
    <DialogContent
      class="flex flex-col gap-0 p-0 sm:max-w-3xl w-[calc(100vw-2rem)] h-[min(85vh,900px)] max-h-[min(85vh,900px)] overflow-hidden"
    >
      <DialogHeader class="shrink-0 px-6 pt-6 pb-4 border-b space-y-2">
        <DialogTitle class="text-base">{{ call?.label ?? 'LLM 呼叫紀錄' }}</DialogTitle>
        <DialogDescription v-if="call" class="flex flex-wrap items-center gap-2">
          <Badge variant="outline" class="font-mono text-xs">{{ call.model }}</Badge>
          <span class="text-xs text-muted-foreground">{{ call.callKey }}</span>
        </DialogDescription>
      </DialogHeader>

      <ScrollArea v-if="call" class="flex-1 min-h-0">
        <div class="p-6 space-y-6">
          <section class="space-y-3">
            <div class="flex items-center justify-between gap-2">
              <h4 class="text-sm font-medium">請求（Request）</h4>
              <Button
                type="button"
                variant="outline"
                size="sm"
                class="h-7 gap-1.5 text-xs"
                :class="showRequestJson && 'bg-muted'"
                @click="showRequestJson = !showRequestJson"
              >
                <Braces class="size-3.5" />
                JSON 檢視
              </Button>
            </div>

            <pre
              v-if="showRequestJson"
              class="text-xs leading-relaxed whitespace-pre-wrap rounded-lg border bg-muted/30 p-4 font-mono overflow-x-auto"
            >{{ formattedRequestJson }}</pre>
            <div v-else class="space-y-3">
              <div
                v-for="(message, index) in requestMessages"
                :key="`${message.role}-${index}`"
                class="rounded-lg border overflow-hidden"
              >
                <div class="px-3 py-2 border-b bg-muted/30 flex items-center gap-2">
                  <Badge :class="cn('text-[10px] uppercase tracking-wide', roleBadgeClass(message.role))">
                    {{ roleLabel(message.role) }}
                  </Badge>
                </div>
                <pre class="text-sm leading-relaxed whitespace-pre-wrap p-4 font-sans">{{ message.content }}</pre>
              </div>
              <p v-if="requestMessages.length === 0" class="text-sm text-muted-foreground">
                無可顯示的訊息內容
              </p>
            </div>
          </section>

          <section class="space-y-3">
            <div class="flex items-center justify-between gap-2">
              <h4 class="text-sm font-medium">回應（Response）</h4>
              <Button
                type="button"
                variant="outline"
                size="sm"
                class="h-7 gap-1.5 text-xs"
                :class="showResponseJson && 'bg-muted'"
                @click="showResponseJson = !showResponseJson"
              >
                <Braces class="size-3.5" />
                JSON 檢視
              </Button>
            </div>

            <pre
              v-if="showResponseJson"
              class="text-xs leading-relaxed whitespace-pre-wrap rounded-lg border bg-muted/30 p-4 font-mono overflow-x-auto"
            >{{ formattedResponseJson }}</pre>
            <div v-else class="space-y-4">
              <template v-if="entityGroups">
                <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                  分群結果
                </p>
                <div class="flex flex-wrap gap-2">
                  <div
                    v-for="(group, groupIndex) in entityGroups"
                    :key="`group-${groupIndex}`"
                    class="rounded-lg border px-3 py-2 text-sm"
                  >
                    <span class="text-xs text-muted-foreground">群 {{ groupIndex + 1 }}：</span>
                    <span class="font-mono">{{ group.join(', ') }}</span>
                  </div>
                </div>
              </template>

              <template v-if="extractedEntities">
                <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                  實體 ({{ extractedEntities.length }})
                </p>
                <div class="border rounded-lg overflow-hidden">
                  <table class="w-full text-sm">
                    <thead>
                      <tr class="bg-muted/50 border-b">
                        <th class="text-left px-3 py-2 text-xs text-muted-foreground font-medium w-24">
                          類型
                        </th>
                        <th class="text-left px-3 py-2 text-xs text-muted-foreground font-medium w-32">
                          名稱
                        </th>
                        <th class="text-left px-3 py-2 text-xs text-muted-foreground font-medium">
                          描述
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="(entity, entityIndex) in extractedEntities"
                        :key="`entity-${entityIndex}`"
                        class="border-b last:border-b-0"
                      >
                        <td class="px-3 py-2 text-xs">{{ fieldText(entity.type) }}</td>
                        <td class="px-3 py-2 font-medium">{{ fieldText(entity.name) }}</td>
                        <td class="px-3 py-2 text-muted-foreground">{{ fieldText(entity.description) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </template>

              <template v-if="extractedRelationships">
                <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                  關係 ({{ extractedRelationships.length }})
                </p>
                <div
                  v-if="extractedRelationships.length === 0"
                  class="text-sm text-muted-foreground border rounded-lg px-3 py-4 text-center"
                >
                  無關係資料
                </div>
                <div v-else class="border rounded-lg overflow-hidden">
                  <table class="w-full text-sm">
                    <thead>
                      <tr class="bg-muted/50 border-b">
                        <th class="text-left px-3 py-2 text-xs text-muted-foreground font-medium w-28">
                          來源
                        </th>
                        <th class="text-left px-3 py-2 text-xs text-muted-foreground font-medium w-24">
                          類型
                        </th>
                        <th class="text-left px-3 py-2 text-xs text-muted-foreground font-medium w-28">
                          目標
                        </th>
                        <th class="text-left px-3 py-2 text-xs text-muted-foreground font-medium">
                          描述
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="(rel, relIndex) in extractedRelationships"
                        :key="`rel-${relIndex}`"
                        class="border-b last:border-b-0"
                      >
                        <td class="px-3 py-2">{{ fieldText(rel.source_name) }}</td>
                        <td class="px-3 py-2 font-mono text-xs">{{ fieldText(rel.type) }}</td>
                        <td class="px-3 py-2">{{ fieldText(rel.target_name) }}</td>
                        <td class="px-3 py-2 text-muted-foreground">{{ fieldText(rel.description) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </template>

              <p
                v-if="!entityGroups && !extractedEntities && !extractedRelationships"
                class="text-sm text-muted-foreground whitespace-pre-wrap rounded-lg border bg-muted/20 p-4"
              >
                {{ typeof call.response === 'string' ? call.response : '無法以結構化方式顯示，請使用 JSON 檢視。' }}
              </p>
            </div>
          </section>
        </div>
      </ScrollArea>
    </DialogContent>
  </Dialog>
</template>
