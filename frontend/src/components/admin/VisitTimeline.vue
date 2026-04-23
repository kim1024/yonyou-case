<script setup lang="ts">
import { ref, computed } from 'vue'
import SvgTooltip from '@/components/shared/SvgTooltip.vue'
import type { VisitTrend } from '@/types'

const props = defineProps<{ data: VisitTrend[] }>()

const hoverPointIdx = ref(-1)

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

const areaD = computed(() => {
  if (!props.data.length) return ''
  const line = props.data.map((d, i) => `${i === 0 ? 'M' : 'L'} ${px(i)} ${py(d.count)}`).join(' ')
  const lastX = px(props.data.length - 1)
  const firstX = px(0)
  const baseY = H - PAD
  return `${line} L ${lastX} ${baseY} L ${firstX} ${baseY} Z`
})

const gridLines = computed(() => {
  const lines: number[] = []
  for (let i = 1; i <= 4; i++) {
    lines.push(H - PAD - (i / 4) * (H - PAD * 2))
  }
  return lines
})

function showTooltip(e: MouseEvent, d: VisitTrend, _i: number) {
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
  <div>
    <h3 class="text-base font-semibold text-neutral-800 mb-4">访问趋势</h3>
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full">
      <defs>
        <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#007AFF" stop-opacity="0.25" />
          <stop offset="100%" stop-color="#007AFF" stop-opacity="0.02" />
        </linearGradient>
      </defs>

      <!-- 水平网格线 -->
      <line
        v-for="(y, i) in gridLines" :key="'g'+i"
        :x1="PAD" :y1="y" :x2="W-PAD" :y2="y"
        stroke="#f1f5f9" stroke-width="1"
      />

      <!-- 轴 -->
      <line :x1="PAD" :y1="H-PAD" :x2="W-PAD" :y2="H-PAD" stroke="#e2e8f0" stroke-width="1" />
      <line :x1="PAD" :y1="PAD" :x2="PAD" :y2="H-PAD" stroke="#e2e8f0" stroke-width="1" />

      <!-- 渐变填充区域 -->
      <path v-if="data.length" :d="areaD" fill="url(#areaGrad)" />

      <!-- 折线（带动画） -->
      <path
        v-if="data.length"
        :d="pathD"
        fill="none"
        stroke="#007AFF"
        stroke-width="2.5"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="visit-line-animate"
      />

      <!-- 数据点 -->
      <circle
        v-for="(d, i) in data" :key="i"
        :cx="px(i)" :cy="py(d.count)"
        :r="hoverPointIdx === i ? 6 : 4"
        fill="#007AFF"
        stroke="white"
        stroke-width="2"
        class="cursor-pointer"
        style="transition: r 0.15s ease"
        @mouseenter="hoverPointIdx = i; showTooltip($event, d, i)"
        @mouseleave="hoverPointIdx = -1; hideTooltip"
      />

      <!-- X轴标签 -->
      <text
        v-for="(d, i) in data" :key="'l'+i"
        :x="px(i)" :y="H-PAD+20"
        text-anchor="middle"
        class="text-[10px] fill-neutral-400"
      >{{ d.date.slice(5) }}</text>
    </svg>
    <SvgTooltip v-bind="tooltip" />
  </div>
</template>

<style scoped>
@keyframes lineDrawIn {
  from {
    stroke-dashoffset: 2000;
  }
  to {
    stroke-dashoffset: 0;
  }
}

.visit-line-animate {
  stroke-dasharray: 2000;
  stroke-dashoffset: 2000;
  animation: lineDrawIn 1.2s cubic-bezier(0.16, 1, 0.3, 1) 0.2s forwards;
}
</style>
