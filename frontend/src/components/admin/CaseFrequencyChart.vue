<script setup lang="ts">
import { ref, computed } from 'vue'
import SvgTooltip from '@/components/shared/SvgTooltip.vue'
import type { CaseFrequency } from '@/types'

const props = defineProps<{ data: CaseFrequency[] }>()

const W = 800
const PAD_TOP = 30
const PAD_BOTTOM = 130
const PAD_LEFT = 50
const PAD_RIGHT = 20
const H = 420
const CHART_H = H - PAD_TOP - PAD_BOTTOM
const CHART_W = W - PAD_LEFT - PAD_RIGHT

const maxVal = computed(() => Math.max(1, ...props.data.map(d => d.count)))
const barW = computed(() =>
  props.data.length ? (CHART_W / props.data.length) * 0.6 : 20,
)
const barGap = computed(() =>
  props.data.length ? (CHART_W / props.data.length) * 0.4 : 8,
)

const yTicks = computed(() => {
  const m = maxVal.value
  const step = Math.ceil(m / 4) || 1
  const ticks: number[] = []
  for (let v = 0; v <= m; v += step) {
    ticks.push(v)
  }
  if (ticks[ticks.length - 1] < m) ticks.push(m)
  return ticks
})

const gridLines = computed(() =>
  yTicks.value
    .filter((v) => v > 0)
    .map((v) => ({
      y: PAD_TOP + CHART_H - (v / maxVal.value) * CHART_H,
      label: v,
    })),
)

const tooltip = ref({ visible: false, x: 0, y: 0, content: '' })
const hoverIdx = ref(-1)

function showTooltip(e: MouseEvent, d: CaseFrequency) {
  const rect = (e.target as SVGElement).closest('svg')!.getBoundingClientRect()
  tooltip.value = {
    visible: true,
    x: e.clientX - rect.left,
    y: e.clientY - rect.top,
    content: `${d.enterprise}: ${d.count} 次 (${d.industry})`,
  }
}

function barX(i: number): number {
  return PAD_LEFT + i * (barW.value + barGap.value) + barGap.value / 2
}
function barY(d: CaseFrequency): number {
  return PAD_TOP + CHART_H - (d.count / maxVal.value) * CHART_H
}
function barH(d: CaseFrequency): number {
  return (d.count / maxVal.value) * CHART_H
}
</script>

<template>
  <div>
    <h3 class="text-base font-semibold text-neutral-800 mb-4">案例使用频次 Top 20</h3>
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full">
      <defs>
        <linearGradient id="freqBarGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#8B5CF6" />
          <stop offset="100%" stop-color="#C4B5FD" />
        </linearGradient>
        <linearGradient id="freqBarGradHover" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#7C3AED" />
          <stop offset="100%" stop-color="#A78BFA" />
        </linearGradient>
      </defs>

      <!-- 水平网格线 -->
      <g v-for="(g, i) in gridLines" :key="'grid-' + i">
        <line
          :x1="PAD_LEFT"
          :y1="g.y"
          :x2="W - PAD_RIGHT"
          :y2="g.y"
          stroke="#f1f5f9"
          stroke-width="1"
        />
        <text
          :x="PAD_LEFT - 8"
          :y="g.y + 4"
          text-anchor="end"
          class="text-[10px] fill-neutral-400"
        >{{ g.label }}</text>
      </g>

      <!-- Y 轴 0 刻度 -->
      <text
        :x="PAD_LEFT - 8"
        :y="PAD_TOP + CHART_H + 4"
        text-anchor="end"
        class="text-[10px] fill-neutral-400"
      >0</text>

      <!-- 底轴 -->
      <line
        :x1="PAD_LEFT"
        :y1="PAD_TOP + CHART_H"
        :x2="W - PAD_RIGHT"
        :y2="PAD_TOP + CHART_H"
        stroke="#e2e8f0"
        stroke-width="1"
      />

      <!-- 柱体 & 标签 -->
      <g v-for="(d, i) in data" :key="i">
        <!-- 柱子 -->
        <rect
          :x="barX(i)"
          :y="barY(d)"
          :width="barW"
          :height="barH(d)"
          :fill="hoverIdx === i ? 'url(#freqBarGradHover)' : 'url(#freqBarGrad)'"
          :rx="hoverIdx === i ? 4 : 2"
          class="cursor-pointer transition-all duration-150"
          :style="{
            transformOrigin: `${barX(i) + barW / 2}px ${PAD_TOP + CHART_H}px`,
            transform: hoverIdx === i ? 'scaleY(1.03)' : 'scaleY(1)',
            filter: hoverIdx === i
              ? 'drop-shadow(0 2px 6px rgba(139,92,246,0.35))'
              : 'none',
          }"
          @mouseenter="hoverIdx = i; showTooltip($event, d)"
          @mouseleave="hoverIdx = -1; tooltip.visible = false"
        />

        <!-- 顶部计数 -->
        <text
          :x="barX(i) + barW / 2"
          :y="barY(d) - 6"
          text-anchor="middle"
          class="text-[10px] fill-neutral-400"
        >{{ d.count }}</text>

        <!-- X 轴旋转标签（完整企业名称） -->
        <text
          :x="barX(i) + barW / 2"
          :y="PAD_TOP + CHART_H + 14"
          text-anchor="end"
          :transform="`rotate(-45, ${barX(i) + barW / 2}, ${PAD_TOP + CHART_H + 14})`"
          class="text-[11px]"
          :class="hoverIdx === i ? 'fill-neutral-900 font-medium' : 'fill-neutral-600'"
        >{{ d.enterprise }}</text>

        <!-- 排名序号（Top 1/2/3） -->
        <text
          v-if="i < 3"
          :x="barX(i) + barW / 2"
          :y="PAD_TOP + CHART_H + 14 + 22"
          text-anchor="end"
          :transform="`rotate(-45, ${barX(i) + barW / 2}, ${PAD_TOP + CHART_H + 14 + 22})`"
          class="text-[9px] fill-primary-500 font-semibold"
        >Top {{ i + 1 }}</text>
      </g>
    </svg>
    <SvgTooltip v-bind="tooltip" />
  </div>
</template>
