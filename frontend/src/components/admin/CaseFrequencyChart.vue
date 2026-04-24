<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
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

// 20 组渐变色 [stop-0, stop-1, hover-0, hover-1]
const barGradients: [string, string, string, string][] = [
  ['#F59E0B', '#FBBF24', '#D97706', '#F59E0B'], // #1  金黄
  ['#F97316', '#FB923C', '#EA580C', '#F97316'], // #2  橙色
  ['#EF4444', '#F87171', '#DC2626', '#EF4444'], // #3  红色
  ['#EC4899', '#F472B6', '#DB2777', '#EC4899'], // #4  粉红
  ['#D946EF', '#E879F9', '#C026D3', '#D946EF'], // #5  品红
  ['#A855F7', '#C084FC', '#9333EA', '#A855F7'], // #6  紫色
  ['#8B5CF6', '#A78BFA', '#7C3AED', '#8B5CF6'], // #7  靛紫
  ['#7C3AED', '#A78BFA', '#6D28D9', '#7C3AED'], // #8  深紫
  ['#6366F1', '#818CF8', '#4F46E5', '#6366F1'], // #9  靛蓝
  ['#4F46E5', '#6366F1', '#4338CA', '#4F46E5'], // #10 深靛蓝
  ['#4338CA', '#6366F1', '#3730A3', '#4338CA'], // #11 靛蓝-700
  ['#3B82F6', '#60A5FA', '#2563EB', '#3B82F6'], // #12 蓝色
  ['#0EA5E9', '#38BDF8', '#0284C7', '#0EA5E9'], // #13 天蓝
  ['#06B6D4', '#22D3EE', '#0891B2', '#06B6D4'], // #14 青色
  ['#14B8A6', '#2DD4BF', '#0D9488', '#14B8A6'], // #15 蓝绿
  ['#10B981', '#34D399', '#059669', '#10B981'], // #16 翡翠
  ['#6B7280', '#9CA3AF', '#4B5563', '#6B7280'], // #17 中灰
  ['#78716C', '#A8A29E', '#57534E', '#78716C'], // #18 暖灰
  ['#A8A29E', '#D6D3D1', '#78716C', '#A8A29E'], // #19 浅暖灰
  ['#D6D3D1', '#E7E5E4', '#A8A29E', '#D6D3D1'], // #20 最淡灰
]

const containerEl = ref<HTMLElement | null>(null)
const containerWidth = ref(0)
let resizeObs: ResizeObserver | null = null

onMounted(() => {
  if (containerEl.value) {
    containerWidth.value = containerEl.value.offsetWidth
    resizeObs = new ResizeObserver(([entry]) => {
      containerWidth.value = entry.contentRect.width
    })
    resizeObs.observe(containerEl.value)
  }
})
onBeforeUnmount(() => { resizeObs?.disconnect() })

const tooltip = ref({ visible: false, x: 0, y: 0, content: '' })
const hoverIdx = ref(-1)

function showTooltip(e: MouseEvent, d: CaseFrequency) {
  const rect = containerEl.value!.getBoundingClientRect()
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
  <div ref="containerEl" class="relative">
    <h3 class="text-base font-semibold text-neutral-800 mb-4">案例使用频次 Top 20</h3>
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full">
      <defs>
        <linearGradient
          v-for="(g, i) in barGradients"
          :key="'grad-' + i"
          :id="'freqBarGrad' + i"
          x1="0" y1="0" x2="0" y2="1"
        >
          <stop offset="0%" :stop-color="g[0]" />
          <stop offset="100%" :stop-color="g[1]" />
        </linearGradient>
        <linearGradient
          v-for="(g, i) in barGradients"
          :key="'gradH-' + i"
          :id="'freqBarGradHover' + i"
          x1="0" y1="0" x2="0" y2="1"
        >
          <stop offset="0%" :stop-color="g[2]" />
          <stop offset="100%" :stop-color="g[3]" />
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
          :fill="hoverIdx === i ? `url(#freqBarGradHover${i})` : `url(#freqBarGrad${i})`"
          :rx="hoverIdx === i ? 4 : 2"
          class="cursor-pointer transition-all duration-150"
          :style="{
            transformOrigin: `${barX(i) + barW / 2}px ${PAD_TOP + CHART_H}px`,
            transform: hoverIdx === i ? 'scaleY(1.03)' : 'scaleY(1)',
            filter: hoverIdx === i
              ? `drop-shadow(0 2px 6px ${barGradients[i][2]}59)`
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
          class="text-[13px]"
          :class="hoverIdx === i ? 'fill-neutral-900 font-medium' : 'fill-neutral-600'"
        >{{ d.enterprise }}</text>

        <!-- 排名序号（Top 1/2/3） -->
        <text
          v-if="i < 3"
          :x="barX(i) + barW / 2"
          :y="PAD_TOP + CHART_H + 14 + 22"
          text-anchor="end"
          :transform="`rotate(-45, ${barX(i) + barW / 2}, ${PAD_TOP + CHART_H + 14 + 22})`"
          class="text-[10px] fill-primary-500 font-semibold"
        >Top {{ i + 1 }}</text>
      </g>
    </svg>
    <SvgTooltip v-bind="tooltip" :container-width="containerWidth" />
  </div>
</template>
