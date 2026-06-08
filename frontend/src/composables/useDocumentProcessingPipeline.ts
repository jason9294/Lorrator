import { ref } from 'vue'
import { DocumentsService } from '@/services'
import type { DocumentProcessingPipeline } from '@/types/document-processing'
import { mapDocumentProcessingPipeline } from '@/composables/mapDocumentProcessingPipeline'

export function useDocumentProcessingPipeline() {
  const pipeline = ref<DocumentProcessingPipeline | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchPipeline(documentId: string) {
    loading.value = true
    error.value = null
    pipeline.value = null
    try {
      const response = await DocumentsService.getDocumentProcessingPipeline({
        path: { document_id: documentId },
      })
      pipeline.value = mapDocumentProcessingPipeline(response.data)
    } catch (e) {
      const detail = (e as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
      error.value =
        typeof detail === 'string' ? detail : '無法載入文件處理流程，請稍後再試'
      throw e
    } finally {
      loading.value = false
    }
  }

  function reset() {
    pipeline.value = null
    loading.value = false
    error.value = null
  }

  return {
    pipeline,
    loading,
    error,
    fetchPipeline,
    reset,
  }
}
