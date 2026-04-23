<script setup lang="ts">
import { ref } from 'vue'
import { adminApi } from '@/api/admin'

const emit = defineEmits<{ close: []; imported: [] }>()
const file = ref<File | null>(null)
const uploading = ref(false)
const result = ref('')
const isError = ref(false)

async function handleUpload() {
  if (!file.value) return
  uploading.value = true
  isError.value = false
  try {
    const res = await adminApi.importExcel(file.value)
    result.value = res.data.message
    setTimeout(() => emit('imported'), 1500)
  } catch (e) {
    result.value = '导入失败'
    isError.value = true
  } finally {
    uploading.value = false
  }
}

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  file.value = input.files?.[0] || null
}
</script>

<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="emit('close')">
    <div class="bg-white rounded-xl shadow-lg w-full max-w-md p-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-6">Excel 批量导入</h2>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">选择 Excel 文件</label>
          <input type="file" accept=".xlsx,.xls" @change="onFileChange" class="w-full text-sm" />
        </div>
        <p class="text-xs text-gray-500">支持 .xlsx 格式，需包含中文列名：客户名称、客户所在省、客户所在市、标准行业、企业简介、用友建设内容</p>
        <div v-if="result" class="text-sm" :class="isError ? 'text-red-600' : 'text-green-600'">{{ result }}</div>
        <div class="flex justify-end gap-3 pt-4">
          <button class="px-4 py-2 border rounded-lg text-sm" @click="emit('close')">取消</button>
          <button :disabled="!file || uploading" class="px-4 py-2 bg-green-600 text-white rounded-lg text-sm disabled:opacity-50" @click="handleUpload">
            {{ uploading ? '导入中...' : '开始导入' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
