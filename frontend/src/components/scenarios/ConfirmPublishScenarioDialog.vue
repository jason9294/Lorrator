<script setup lang="ts">
import { Spinner } from '@/components/ui/spinner'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'

const open = defineModel<boolean>('open', { required: true })

withDefaults(
  defineProps<{
    isPublishing?: boolean
  }>(),
  {
    isPublishing: false,
  },
)

const emit = defineEmits<{
  confirm: []
}>()

function onConfirm() {
  emit('confirm')
}
</script>

<template>
  <AlertDialog v-model:open="open">
    <AlertDialogContent>
      <AlertDialogHeader>
        <AlertDialogTitle>確認發布劇本？</AlertDialogTitle>
        <AlertDialogDescription>
          發布後無法撤回，也無法再編輯劇本內容。請確認劇本與所有文件均已就緒。
        </AlertDialogDescription>
      </AlertDialogHeader>
      <AlertDialogFooter>
        <AlertDialogCancel :disabled="isPublishing">取消</AlertDialogCancel>
        <AlertDialogAction :disabled="isPublishing" @click="onConfirm">
          <Spinner v-if="isPublishing" class="size-3.5 mr-1.5" />
          {{ isPublishing ? '發布中...' : '確認發布' }}
        </AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
</template>
