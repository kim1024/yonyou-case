<script setup lang="ts">
import { ref } from 'vue'
import {
  Factory,
  ShoppingBag,
  Landmark,
  HeartPulse,
  GraduationCap,
  Building,
  UtensilsCrossed,
  Cpu,
  Leaf,
  Building2,
} from 'lucide-vue-next'
import type { Component } from 'vue'

defineProps<{ industries: string[]; loading: boolean }>()
const emit = defineEmits<{ select: [industry: string] }>()

const poppedKey = ref<string | null>(null)

const iconMap: Array<[string, Component]> = [
  ['制造', Factory],
  ['零售', ShoppingBag],
  ['商贸', ShoppingBag],
  ['金融', Landmark],
  ['医疗', HeartPulse],
  ['健康', HeartPulse],
  ['教育', GraduationCap],
  ['房地产', Building],
  ['地产', Building],
  ['餐饮', UtensilsCrossed],
  ['科技', Cpu],
  ['信息', Cpu],
  ['农业', Leaf],
]

function getIndustryIcon(name: string): Component {
  for (const [keyword, icon] of iconMap) {
    if (name.includes(keyword)) return icon
  }
  return Building2
}

function handleSelect(industry: string) {
  poppedKey.value = industry
  setTimeout(() => {
    emit('select', industry)
    poppedKey.value = null
  }, 250)
}
</script>

<template>
  <div>
    <div class="mb-8">
      <span class="text-sm font-bold text-indigo-500 tracking-wide uppercase">02</span>
      <h2 class="mt-1 text-2xl font-bold text-gray-900">选择行业</h2>
      <p class="mt-1 text-sm text-gray-500">选择案例所属行业，系统将匹配该行业的标杆企业</p>
    </div>

    <!-- 骨架屏 -->
    <div v-if="loading" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
      <div
        v-for="i in 10"
        :key="i"
        class="bg-white border border-gray-200 rounded-[10px] p-4 shadow-xs"
      >
        <div class="skeleton w-9 h-9 rounded-full mx-auto mb-3" />
        <div class="skeleton h-4 w-20 mx-auto" />
      </div>
    </div>

    <!-- 行业卡片 -->
    <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
      <button
        v-for="industry in industries"
        :key="industry"
        :class="[
          'bg-white border border-gray-200 rounded-[10px] p-4 shadow-xs',
          'hover:border-indigo-400 hover:shadow-md hover:-translate-y-0.5',
          'transition-all duration-200 text-center cursor-pointer',
          poppedKey === industry ? 'animate-select-pop' : '',
        ]"
        @click="handleSelect(industry)"
      >
        <div class="w-9 h-9 rounded-full bg-indigo-50 flex items-center justify-center mx-auto mb-3">
          <component
            :is="getIndustryIcon(industry)"
            class="w-5 h-5 text-indigo-500"
            :stroke-width="1.5"
          />
        </div>
        <div class="text-sm font-medium text-gray-700">{{ industry }}</div>
      </button>
    </div>
  </div>
</template>
