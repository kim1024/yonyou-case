<script setup lang="ts">
import { ref, computed } from 'vue'
import SvgTooltip from '@/components/shared/SvgTooltip.vue'
import type { CaseFrequency } from '@/types'

const props = defineProps<{ data: CaseFrequency[] }>()

const W = 700, H = 400, PAD = 180, ROW_H = 16
const maxVal = computed(() => Math.max(1, ...props.data.map(d => d.count)))
const chartW = W - PAD - 40

const tooltip = ref({ visible: false, x: 0, y: 0, content: '' })
const hoverIdx = ref(-1)

function showTooltip(e: MouseEvent, d: CaseFrequency) {
  const rect = (e.target as SVGElement).closest('svg')!.getBoundingClientRect()
  tooltip.value = { visible: true, x: e.clientX - rect.left, y: e.clientY - rect.top, content: `${d.enterprise}: ${d.count} 次 (${d.industry})` }
}
</script>

<template>
  <div class="bg-white rounded-xl shadow-sm p-6 relative">
    <h3 class="text-lg font-semibold text-gray-800 mb-4">案例使用频次 Top 20</h3>
    <svg :viewBox="`0 0 ${W} ${Math.max(H, 20 + data.length * ROW_H)}`" class="w-full">
      <g v-for="(d, i) in data" :key="i">
        <text :x="PAD - 8" :y="20 + i * ROW_H" text-anchor="end" class="text-[11px] fill-gray-600">{{ d.enterprise.slice(0, 12) }}</text>
        <rect
          :x="PAD"
          :y="10 + i * ROW_H"
          :width="(d.count / maxVal) * chartW"
          :height="ROW_H - 4"
          :fill="hoverIdx === i ? '#059669' : '#10b981'"
          rx="2"
          class="cursor-pointer transition-colors"
          @mouseenter="hoverIdx = i; showTooltip($event, d)"
          @mouseleave="hoverIdx = -1; tooltip.visible = false"
        />
        <text :x="PAD + (d.count / maxVal) * chartW + 6" :y="20 + i * ROW_H" class="text-[10px] fill-gray-500">{{ d.count }}</text>
      </g>
    </svg>
    <SvgTooltip v-bind="tooltip" />
  </div>
</template>
