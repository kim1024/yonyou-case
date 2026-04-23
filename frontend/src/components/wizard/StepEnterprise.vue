<script setup lang="ts">
import EnterpriseInfoPanel from '@/components/wizard/EnterpriseInfoPanel.vue'
import type { Enterprise } from '@/types'

defineProps<{
  enterprises: string[]
  loading: boolean
  enterpriseInfo: Enterprise | null
  selectedEnterprise: string | null
  infoLoading: boolean
}>()
const emit = defineEmits<{ select: [name: string] }>()

const skeletonCount = 6
</script>

<template>
  <div>
    <!-- 标题区域 -->
    <div class="mb-8">
      <div class="text-sm font-bold text-indigo-500 tracking-wide mb-1">04</div>
      <h2 class="text-2xl font-bold text-gray-900 mb-1.5">选择企业</h2>
      <p class="text-sm text-gray-500">选择一家企业，查看其详细信息和用友可提供的内容</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
      <!-- 左栏：企业列表 -->
      <div class="lg:col-span-2">
        <!-- 总数 -->
        <div class="text-sm text-gray-400 mb-3">
          共 {{ enterprises.length }} 家企业
        </div>

        <!-- 加载骨架屏 -->
        <div v-if="loading" class="space-y-1.5">
          <div
            v-for="i in skeletonCount"
            :key="i"
            class="h-[52px] rounded-[10px] bg-gray-100 animate-pulse"
          />
        </div>

        <!-- 企业列表 -->
        <div v-else class="max-h-[480px] overflow-y-auto space-y-1.5 pr-1 custom-scrollbar">
          <button
            v-for="name in enterprises"
            :key="name"
            class="w-full p-3.5 rounded-[10px] border transition-all cursor-pointer text-left"
            :class="
              selectedEnterprise === name
                ? 'bg-indigo-50 border-l-[3px] border-indigo-500 border-t-0 border-r-0 border-b-0'
                : 'border-gray-200 hover:bg-gray-50'
            "
            @click="emit('select', name)"
          >
            <span
              class="text-sm"
              :class="
                selectedEnterprise === name
                  ? 'text-indigo-700 font-semibold'
                  : 'font-medium text-gray-800'
              "
            >
              {{ name }}
            </span>
          </button>
        </div>
      </div>

      <!-- 右栏：企业详情面板 -->
      <div class="lg:col-span-3">
        <EnterpriseInfoPanel
          :info="enterpriseInfo"
          :loading="infoLoading"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #e5e7eb;
  border-radius: 9999px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: #d1d5db;
}
</style>
