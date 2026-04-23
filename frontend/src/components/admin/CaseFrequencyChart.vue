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
  <div>
    <h3 class="text-base font-semibold text-neutral-800 mb-4">案例使用频次 Top 20</h3>
    <svg :viewBox="`0 0 ${W} ${Math.max(H, 20 + data.length * ROW_H)}`" class="w-full">
      <defs>
        <linearGradient id="freqBarGrad" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stop-color="#10b981" />
          <stop offset="100%" stop-color="#6ee7b7" />
        </linearGradient>
        <linearGradient id="freqBarGradHover" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stop-color="#059669" />
          <stop offset="100%" stop-color="#34d399" />
        </linearGradient>
      </defs>

      <g v-for="(d, i) in data" :key="i">
        <!-- 排名序号 -->
        <text
          :x="8"
          :y="20 + i * ROW_H"
          text-anchor="start"
          class="text-[10px] font-semibold"
          :class="i < 3 ? 'fill-primary-500' : 'fill-neutral-400'"
        >{{ i + 1 }}</text>

        <!-- 企业名称 -->
        <text
          :x="PAD - 8"
          :y="20 + i * ROW_H"
          text-anchor="end"
          class="text-[11px]"
          :class="hoverIdx === i ? 'fill-neutral-900 font-medium' : 'fill-neutral-600'"
        >{{ d.enterprise.slice(0, 12) }}</text>

        <!-- 条形 -->
        <rect
          :x="PAD"
          :y="10 + i * ROW_H"
          :width="(d.count / maxVal) * chartW"
          :height="ROW_H - 4"
          :fill="hoverIdx === i ? 'url(#freqBarGradHover)' : 'url(#freqBarGrad)'"
          :rx="3"
          class="cursor-pointer transition-all duration-150"
          :style="{
            filter: hoverIdx === i ? 'drop-shadow(0 1px 4px rgba(16,185,129,0.3))' : 'none',
          }"
          @mouseenter="hoverIdx = i; showTooltip($event, d)"
          @mouseleave="hoverIdx = -1; tooltip.visible = false"
        />

        <!-- 计数标签 -->
        <text
          :x="PAD + (d.count / maxVal) * chartW + 6"
          :y="20 + i * ROW_H"
          class="text-[10px] fill-neutral-400"
        >{{ d.count }}</text>
      </g>
    </svg>
    <SvgTooltip v-bind="tooltip" />
  </div>
</template>
