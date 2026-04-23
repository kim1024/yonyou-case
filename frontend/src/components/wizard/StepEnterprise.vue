<script setup lang="ts">
import { ref, computed } from 'vue'
import { Search } from 'lucide-vue-next'
import EnterpriseInfoPanel from '@/components/wizard/EnterpriseInfoPanel.vue'
import type { MajorEnterpriseInfo } from '@/types'

const props = defineProps<{
  enterprises: string[]
  loading: boolean
  enterpriseInfo: MajorEnterpriseInfo | null
  selectedEnterprise: string | null
  infoLoading: boolean
}>()
const emit = defineEmits<{ select: [name: string] }>()

const searchQuery = ref('')

const filteredEnterprises = computed(() => {
  if (!searchQuery.value.trim()) return props.enterprises
  const q = searchQuery.value.trim().toLowerCase()
  return props.enterprises.filter((n) => n.toLowerCase().includes(q))
})

const skeletonCount = 6
</script>

<template>
  <div>
    <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
      <!-- 左栏：企业列表 -->
      <div class="lg:col-span-2">
        <!-- 搜索框 -->
        <div class="relative mb-4">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400 pointer-events-none" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索企业..."
            class="input-macos pl-10 w-full"
          />
        </div>

        <!-- 总数 -->
        <div class="text-xs text-neutral-400 mb-3">
          共 {{ enterprises.length }} 家企业
        </div>

        <!-- 加载骨架屏 -->
        <div v-if="loading" class="space-y-1.5">
          <div
            v-for="i in skeletonCount"
            :key="i"
            class="h-[44px] rounded-xl bg-neutral-100 animate-pulse"
          />
        </div>

        <!-- 企业列表 -->
        <div v-else class="max-h-[420px] overflow-y-auto space-y-1 pr-1 custom-scrollbar">
          <button
            v-for="name in filteredEnterprises"
            :key="name"
            class="w-full px-4 py-3 rounded-xl border text-left transition-all cursor-pointer"
            :class="
              selectedEnterprise === name
                ? 'bg-primary-50 border-primary-400 text-primary-700 font-semibold shadow-sm'
                : 'border-neutral-200 text-neutral-700 hover:bg-neutral-50'
            "
            @click="emit('select', name)"
          >
            <span class="text-sm">{{ name }}</span>
          </button>

          <!-- 空搜索 -->
          <div
            v-if="filteredEnterprises.length === 0 && !loading && enterprises.length > 0"
            class="text-center py-6 text-neutral-400 text-sm"
          >
            未找到匹配的企业
          </div>
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
  background-color: var(--color-neutral-200);
  border-radius: 9999px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: var(--color-neutral-300);
}
</style>
