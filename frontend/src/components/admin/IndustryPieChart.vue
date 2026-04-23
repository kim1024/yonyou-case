<script setup lang="ts">
import { ref, computed } from 'vue'
import SvgTooltip from '@/components/shared/SvgTooltip.vue'
import type { IndustryCount } from '@/types'

const COLORS = ['#3b82f6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#6366f1']

const props = defineProps<{ data: IndustryCount[] }>()

const CX = 200, CY = 200, R = 140

const total = computed(() => props.data.reduce((s, d) => s + d.count, 0))

const slices = computed(() => {
  let angle = -Math.PI / 2
  return props.data.map((d, i) => {
    const sweep = (d.count / total.value) * Math.PI * 2
    const startAngle = angle
    angle += sweep
    const largeArc = sweep > Math.PI ? 1 : 0
    const x1 = CX + R * Math.cos(startAngle)
    const y1 = CY + R * Math.sin(startAngle)
    const x2 = CX + R * Math.cos(angle)
    const y2 = CY + R * Math.sin(angle)
    const path = `M ${CX} ${CY} L ${x1} ${y1} A ${R} ${R} 0 ${largeArc} 1 ${x2} ${y2} Z`
    const midAngle = startAngle + sweep / 2
    const lx = CX + (R * 0.65) * Math.cos(midAngle)
    const ly = CY + (R * 0.65) * Math.sin(midAngle)
    const pct = ((d.count / total.value) * 100).toFixed(1)
    return { path, color: COLORS[i % COLORS.length], industry: d.industry, count: d.count, pct, lx, ly }
  })
})

const tooltip = ref({ visible: false, x: 0, y: 0, content: '' })
const hoverIdx = ref(-1)

function showTooltip(e: MouseEvent, s: any) {
  const rect = (e.target as SVGElement).closest('svg')!.getBoundingClientRect()
  tooltip.value = { visible: true, x: e.clientX - rect.left, y: e.clientY - rect.top, content: `${s.industry}: ${s.count} 次 (${s.pct}%)` }
}
</script>

<template>
  <div class="bg-white rounded-xl shadow-sm p-6 relative">
    <h3 class="text-lg font-semibold text-gray-800 mb-4">行业分布</h3>
    <svg viewBox="0 0 400 400" class="w-full max-w-sm mx-auto">
      <path
        v-for="(s, i) in slices" :key="i"
        :d="s.path"
        :fill="hoverIdx === i ? '#1e40af' : s.color"
        class="cursor-pointer transition-colors"
        @mouseenter="hoverIdx = i; showTooltip($event, s)"
        @mouseleave="hoverIdx = -1; tooltip.visible = false"
      />
      <text v-for="(s, i) in slices" :key="'t'+i" :x="s.lx" :y="s.ly" text-anchor="middle" dominant-baseline="middle" class="text-[10px] fill-white font-medium pointer-events-none">{{ s.pct }}%</text>
    </svg>
    <!-- 图例 -->
    <div class="flex flex-wrap gap-3 mt-4 justify-center">
      <div v-for="(s, i) in slices" :key="'l'+i" class="flex items-center gap-1 text-xs text-gray-600">
        <div class="w-3 h-3 rounded-sm" :style="{ backgroundColor: s.color }" />
        {{ s.industry }}
      </div>
    </div>
    <SvgTooltip v-bind="tooltip" />
  </div>
</template>
