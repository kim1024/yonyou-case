<script setup lang="ts">
import EnterpriseInfoPanel from '@/components/wizard/EnterpriseInfoPanel.vue'
import type { Enterprise } from '@/types'

defineProps<{
  enterprises: string[]
  loading: boolean
  enterpriseInfo: Enterprise | null
}>()
const emit = defineEmits<{ select: [name: string] }>()
</script>

<template>
  <div>
    <h2 class="text-xl font-semibold text-gray-800 mb-6">选择企业</h2>
    <div v-if="loading" class="text-gray-500">加载中...</div>
    <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div>
        <div class="max-h-96 overflow-y-auto space-y-2">
          <button
            v-for="name in enterprises"
            :key="name"
            class="w-full p-3 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition text-left"
            @click="emit('select', name)"
          >
            <div class="text-sm font-medium text-gray-700">{{ name }}</div>
          </button>
        </div>
      </div>
      <EnterpriseInfoPanel :info="enterpriseInfo" />
    </div>
  </div>
</template>
