<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api/admin'
import type { Enterprise } from '@/types'

const props = defineProps<{ item: Enterprise | null }>()
const emit = defineEmits<{ close: []; saved: [] }>()

const form = ref({
  customer_name: props.item?.customer_name || '',
  province: props.item?.province || '',
  city: props.item?.city || '',
  industry: props.item?.industry || '',
  company_intro: props.item?.company_intro || '',
  yonyou_content: props.item?.yonyou_content || '',
})

const saving = ref(false)

async function handleSave() {
  saving.value = true
  try {
    if (props.item) {
      await adminApi.updateEnterprise(props.item.id, form.value)
    } else {
      await adminApi.createEnterprise(form.value)
    }
    emit('saved')
  } catch (e) {
    alert('保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="emit('close')">
    <div class="bg-white rounded-xl shadow-lg w-full max-w-lg p-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-6">{{ item ? '编辑企业' : '新增企业' }}</h2>
      <form @submit.prevent="handleSave" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">客户名称</label>
          <input v-model="form.customer_name" required class="w-full px-3 py-2 border rounded-lg text-sm" />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">省份</label>
            <input v-model="form.province" required class="w-full px-3 py-2 border rounded-lg text-sm" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">城市</label>
            <input v-model="form.city" required class="w-full px-3 py-2 border rounded-lg text-sm" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">行业</label>
          <input v-model="form.industry" required class="w-full px-3 py-2 border rounded-lg text-sm" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">企业简介</label>
          <textarea v-model="form.company_intro" rows="3" class="w-full px-3 py-2 border rounded-lg text-sm" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">用友建设内容</label>
          <textarea v-model="form.yonyou_content" rows="3" class="w-full px-3 py-2 border rounded-lg text-sm" />
        </div>
        <div class="flex justify-end gap-3 pt-4">
          <button type="button" class="px-4 py-2 border rounded-lg text-sm" @click="emit('close')">取消</button>
          <button type="submit" :disabled="saving" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm disabled:opacity-50">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
