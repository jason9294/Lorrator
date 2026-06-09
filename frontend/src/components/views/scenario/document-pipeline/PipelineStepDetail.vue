<script setup lang="ts">
import type { ProcessingStep } from '@/types/document-processing'
import { Separator } from '@/components/ui/separator'
import PrepareStepResult from './steps/PrepareStepResult.vue'
import ClearGraphStepResult from './steps/ClearGraphStepResult.vue'
import ChunkStepResult from './steps/ChunkStepResult.vue'
import EntityExtractionStepResult from './steps/EntityExtractionStepResult.vue'
import EntityEmbeddingStepResult from './steps/EntityEmbeddingStepResult.vue'
import EntityGroupingStepResult from './steps/EntityGroupingStepResult.vue'
import GraphBuildStepResult from './steps/GraphBuildStepResult.vue'

defineProps<{
  step: ProcessingStep
}>()
</script>

<template>
  <div class="p-6 space-y-6">
    <div class="space-y-2">
      <h3 class="text-base font-semibold">{{ step.title }}</h3>
      <p class="text-sm text-muted-foreground">{{ step.description }}</p>
      <p v-if="step.error" class="text-sm text-destructive whitespace-pre-wrap">
        {{ step.error }}
      </p>
    </div>

    <Separator />

    <p
      v-if="!step.result && step.status !== 'skipped'"
      class="text-sm text-muted-foreground"
    >
      此步驟尚無可顯示的結果。
    </p>
    <p v-else-if="step.status === 'skipped'" class="text-sm text-muted-foreground">
      此步驟已略過。
    </p>

    <PrepareStepResult v-else-if="step.id === 'prepare' && step.result" :result="step.result" />
    <ClearGraphStepResult
      v-else-if="step.id === 'clear_graph' && step.result"
      :result="step.result"
    />
    <ChunkStepResult v-else-if="step.id === 'chunk' && step.result" :result="step.result" />
    <EntityExtractionStepResult
      v-else-if="step.id === 'entity_extraction' && step.result"
      :result="step.result"
    />
    <EntityEmbeddingStepResult
      v-else-if="step.id === 'entity_embedding' && step.result"
      :result="step.result"
    />
    <EntityGroupingStepResult
      v-else-if="step.id === 'entity_grouping' && step.result"
      :result="step.result"
    />
    <GraphBuildStepResult
      v-else-if="step.id === 'graph_build' && step.result"
      :result="step.result"
    />
  </div>
</template>
