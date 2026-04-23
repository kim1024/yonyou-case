<script setup lang="ts">
import { ref, computed } from 'vue'
import SvgTooltip from '@/components/shared/SvgTooltip.vue'
import type { VisitTrend } from '@/types'

const props = defineProps<{ data: VisitTrend[] }>()

const W = 700, H = 300, PAD = 50

const tooltip = ref({ visible: false, x: 0, y: 0, content: '' })

const maxVal = computed(() => Math.max(1, ...props.data.map(d => d.count)))

function px(i: number) {
  return props.data.length <= 1 ? PAD : PAD + i * (W - PAD * 2) / (props.data.length - 1)
}
function py(val: number) {
  return H - PAD - (val / maxVal.value) * (H - PAD * 2)
}

const pathD = computed(() => {
  return props.data.map((d, i) => `${i === 0 ? 'M' : 'L'} ${px(i)} ${py(d.count)}`).join(' ')
})

function showTooltip(e: MouseEvent, d: VisitTrend, i: number) {
  const rect = (e.target as SVGElement).closest('svg')!.getBoundingClientRect()
  tooltip.value = {
    visible: true,
    x: e.clientX - rect.left,
    y: e.clientY - rect.top,
    content: `${d.date}: ${d.count} 次`,
  }
}
function hideTooltip() {
  tooltip.value.visible = false
}
</script>

<template>
  <div class="bg-white rounded-xl shadow-sm p-6 relative">
    <h3 class="text-lg font-semibold text-gray-800 mb-4">访问趋势</h3>
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full">
      <!-- 轴 -->
      <line :x1="PAD" :y1="H-PAD" :x2="W-PAD" :y2="H-PAD" stroke="#e5e7eb" />
      <line :x1="PAD" :y1="PAD" :x2="PAD" :y2="H-PAD" stroke="#e5e7eb" />
      <!-- 折线 -->
      <path v-if="data.length" :d="pathD" fill="none" stroke="#3b82f6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
      <!-- 数据点 -->
      <circle v-for="(d, i) in data" :key="i" :cx="px(i)" :cy="py(d.count)" r="4" fill="#3b82f6" class="cursor-pointer" @mouseenter="showTooltip($event, d, i)" @mouseleave="hideTooltip" />
      <!-- X轴标签 -->
      <text v-for="(d, i) in data" :key="'l'+i" :x="px(i)" :y="H-PAD+20" text-anchor="middle" class="text-[10px] fill-gray-400">{{ d.date.slice(5) }}</text>
    </svg>
    <SvgTooltip v-bind="tooltip" />
  </div>
</template>
