<script setup lang="ts">
import { ref, computed } from 'vue'
import SvgTooltip from '@/components/shared/SvgTooltip.vue'
import type { ProvinceCount } from '@/types'

const props = defineProps<{ data: ProvinceCount[] }>()

const W = 700, H = 300, PAD = 50
const maxVal = computed(() => Math.max(1, ...props.data.map(d => d.count)))
const barW = computed(() => props.data.length ? (W - PAD * 2) / props.data.length - 4 : 30)

const tooltip = ref({ visible: false, x: 0, y: 0, content: '' })
const hoverIdx = ref(-1)

function showTooltip(e: MouseEvent, d: ProvinceCount) {
  const rect = (e.target as SVGElement).closest('svg')!.getBoundingClientRect()
  tooltip.value = { visible: true, x: e.clientX - rect.left, y: e.clientY - rect.top, content: `${d.province}: ${d.count} 次` }
}
</script>

<template>
  <div class="bg-white rounded-xl shadow-sm p-6 relative">
    <h3 class="text-lg font-semibold text-gray-800 mb-4">省份分布</h3>
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full">
      <line :x1="PAD" :y1="H-PAD" :x2="W-PAD" :y2="H-PAD" stroke="#e5e7eb" />
      <rect
        v-for="(d, i) in data" :key="i"
        :x="PAD + i * (barW + 4)"
        :y="H - PAD - (d.count / maxVal) * (H - PAD * 2)"
        :width="barW"
        :height="(d.count / maxVal) * (H - PAD * 2)"
        :fill="hoverIdx === i ? '#0891b2' : '#06b6d4'"
        rx="2"
        class="cursor-pointer transition-colors"
        @mouseenter="hoverIdx = i; showTooltip($event, d)"
        @mouseleave="hoverIdx = -1; tooltip.visible = false"
      />
      <text v-for="(d, i) in data" :key="'l'+i" :x="PAD + i * (barW + 4) + barW/2" :y="H-PAD+18" text-anchor="middle" class="text-[10px] fill-gray-400">{{ d.province.slice(0, 2) }}</text>
    </svg>
    <SvgTooltip v-bind="tooltip" />
  </div>
</template>
