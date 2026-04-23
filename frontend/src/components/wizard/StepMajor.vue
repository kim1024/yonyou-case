<script setup lang="ts">
import { ref } from 'vue'
import { Calculator, Building2, TrendingUp } from 'lucide-vue-next'

defineProps<{ majors: string[]; loading: boolean }>()
const emit = defineEmits<{ select: [major: string] }>()

const poppedKey = ref<string | null>(null)

const majorMeta: Record<string, { icon: typeof Calculator; desc: string }> = {
  '大数据与会计': { icon: Calculator, desc: '涵盖智能财务、数据分析与审计实务' },
  '工商企业管理': { icon: Building2, desc: '聚焦企业战略、运营管理与组织发展' },
  '市场营销': { icon: TrendingUp, desc: '深入品牌管理、数字营销与市场策略' },
}

function getMeta(name: string) {
  return majorMeta[name] ?? { icon: Building2, desc: '' }
}

function handleSelect(major: string) {
  poppedKey.value = major
  setTimeout(() => {
    emit('select', major)
    poppedKey.value = null
  }, 250)
}
</script>

<template>
  <div>
    <div class="mb-8">
      <span class="text-sm font-bold text-indigo-500 tracking-wide uppercase">01</span>
      <h2 class="mt-1 text-2xl font-bold text-gray-900">选择专业方向</h2>
      <p class="mt-1 text-sm text-gray-500">请选择您的教学专业，我们将为您定制专属课程方案</p>
    </div>

    <!-- 骨架屏 -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div
        v-for="i in 3"
        :key="i"
        class="bg-white border border-gray-200 rounded-[10px] p-6 shadow-xs"
      >
        <div class="skeleton w-12 h-12 rounded-full mx-auto mb-4" />
        <div class="skeleton h-5 w-32 mx-auto mb-3" />
        <div class="skeleton h-4 w-48 mx-auto" />
      </div>
    </div>

    <!-- 专业卡片 -->
    <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <button
        v-for="major in majors"
        :key="major"
        :class="[
          'bg-white border border-gray-200 rounded-[10px] p-6 shadow-xs',
          'hover:border-indigo-400 hover:shadow-md hover:-translate-y-0.5',
          'transition-all duration-200 text-center cursor-pointer',
          poppedKey === major ? 'animate-select-pop' : '',
        ]"
        @click="handleSelect(major)"
      >
        <div class="w-12 h-12 rounded-full bg-indigo-50 flex items-center justify-center mx-auto mb-4">
          <component :is="getMeta(major).icon" class="w-6 h-6 text-indigo-500" :stroke-width="1.5" />
        </div>
        <div class="text-lg font-semibold text-gray-900">{{ major }}</div>
        <p class="text-sm text-gray-500 mt-2">{{ getMeta(major).desc }}</p>
      </button>
    </div>
  </div>
</template>
