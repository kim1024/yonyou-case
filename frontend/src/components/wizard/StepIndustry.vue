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
  type Component,
} from 'lucide-vue-next'

const props = defineProps<{
  industries: string[]
  loading: boolean
  selectedIndustry: string | null
}>()
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
    <!-- 骨架屏 -->
    <div v-if="loading" class="flex flex-wrap gap-3">
      <div
        v-for="i in 10"
        :key="i"
        class="h-10 w-24 rounded-full bg-neutral-100 animate-pulse"
      />
    </div>

    <!-- Pill 按钮组 -->
    <div v-else class="flex flex-wrap gap-3">
      <button
        v-for="industry in industries"
        :key="industry"
        :class="[
          'inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-medium',
          'transition-all duration-200 cursor-pointer',
          'border',
          selectedIndustry === industry
            ? 'bg-primary-500 text-white border-primary-500 shadow-md shadow-primary-500/25 -translate-y-0.5'
            : 'bg-white text-neutral-600 border-neutral-200 hover:border-primary-300 hover:text-primary-600 hover:-translate-y-0.5',
          poppedKey === industry ? 'animate-select-pop' : '',
        ]"
        @click="handleSelect(industry)"
      >
        <component
          :is="getIndustryIcon(industry)"
          class="w-4 h-4"
          :stroke-width="1.5"
        />
        <span>{{ industry }}</span>
      </button>
    </div>
  </div>
</template>
