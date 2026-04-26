<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import SvgTooltip from '@/components/shared/SvgTooltip.vue'
import { formatMonthDay } from '@/utils/date'
import type { VisitTrend } from '@/types'

const props = defineProps<{ data: VisitTrend[] }>()

const hoverPointIdx = ref(-1)

const W = 700, H = 300, PAD = 50

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

const maxVal = computed(() => Math.max(1, ...props.data.map(d => d.pv)))

function px(i: number) {
  return props.data.length <= 1 ? PAD : PAD + i * (W - PAD * 2) / (props.data.length - 1)
}
function py(val: number) {
  return H - PAD - (val / maxVal.value) * (H - PAD * 2)
}

interface Point { x: number; y: number }

/** Catmull-Rom → Cubic Bezier 平滑路径转换 */
function smoothPath(points: Point[], closed = false): string {
  if (points.length < 2) return points.length === 1 ? `M ${points[0].x} ${points[0].y}` : ''
  const tension = 6
  const minY = PAD
  const maxY = H - PAD
  const d: string[] = [`M ${points[0].x} ${points[0].y}`]

  for (let i = 0; i < points.length - 1; i++) {
    const p0 = points[Math.max(0, i - 1)]
    const p1 = points[i]
    const p2 = points[i + 1]
    const p3 = points[Math.min(points.length - 1, i + 2)]

    const cp1x = p1.x + (p2.x - p0.x) / tension
    const cp1y = Math.max(minY, Math.min(maxY, p1.y + (p2.y - p0.y) / tension))
    const cp2x = p2.x - (p3.x - p1.x) / tension
    const cp2y = Math.max(minY, Math.min(maxY, p2.y + (p3.y - p1.y) / tension))

    d.push(`C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`)
  }

  if (closed) d.push('Z')
  return d.join(' ')
}

// ── PV 系列 ──
const points = computed<Point[]>(() =>
  props.data.map((d, i) => ({ x: px(i), y: py(d.pv) }))
)
const pathD = computed(() => smoothPath(points.value))
const areaD = computed(() => {
  if (!points.value.length) return ''
  const lastX = points.value[points.value.length - 1].x
  const firstX = points.value[0].x
  const baseY = H - PAD
  return `${pathD.value} L ${lastX} ${baseY} L ${firstX} ${baseY} Z`
})

// ── UV 系列 ──
const uvPoints = computed<Point[]>(() =>
  props.data.map((d, i) => ({ x: px(i), y: py(d.uv) }))
)
const uvPathD = computed(() => smoothPath(uvPoints.value))
const uvAreaD = computed(() => {
  if (!uvPoints.value.length) return ''
  const lastX = uvPoints.value[uvPoints.value.length - 1].x
  const firstX = uvPoints.value[0].x
  const baseY = H - PAD
  return `${uvPathD.value} L ${lastX} ${baseY} L ${firstX} ${baseY} Z`
})

// ── 网格线 & Y 轴刻度 ──
const gridLines = computed(() => {
  const lines: number[] = []
  for (let i = 1; i <= 4; i++) {
    lines.push(H - PAD - (i / 4) * (H - PAD * 2))
  }
  return lines
})

const yTickLabels = computed(() => {
  return gridLines.value.map(y => {
    const ratio = (y - (H - PAD)) / -(H - PAD * 2)
    return Math.round(ratio * maxVal.value)
  })
})

// ── X 轴标签 ──
const visibleLabelIndices = computed(() => {
  if (props.data.length <= 10) return props.data.map((_, i) => i)
  const step = Math.ceil(props.data.length / 10)
  return props.data.map((_, i) => i).filter(i => i % step === 0)
})

function showTooltip(e: MouseEvent, _d: VisitTrend, _i: number) {
  const rect = containerEl.value!.getBoundingClientRect()
  const d = _d
  tooltip.value = {
    visible: true,
    x: e.clientX - rect.left,
    y: e.clientY - rect.top,
    content: `${d.date}\nPV: ${d.pv}  UV: ${d.uv}`,
  }
}
function hideTooltip() {
  tooltip.value.visible = false
}
</script>

<template>
  <div ref="containerEl" class="relative">
    <div class="flex items-center mb-4">
      <h3 class="text-base font-semibold text-neutral-800">访问趋势</h3>
      <div class="flex items-center gap-4 ml-auto text-xs text-neutral-500">
        <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-[#6366F1]"></span>PV</span>
        <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full bg-[#F97316]"></span>UV</span>
      </div>
    </div>
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full">
      <defs>
        <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#6366F1" stop-opacity="0.25" />
          <stop offset="100%" stop-color="#6366F1" stop-opacity="0.02" />
        </linearGradient>
        <linearGradient id="uvAreaGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#F97316" stop-opacity="0.2" />
          <stop offset="100%" stop-color="#F97316" stop-opacity="0.02" />
        </linearGradient>
      </defs>

      <!-- 水平网格线 -->
      <line
        v-for="(y, i) in gridLines" :key="'g'+i"
        :x1="PAD" :y1="y" :x2="W-PAD" :y2="y"
        stroke="#f1f5f9" stroke-width="1"
      />

      <!-- Y 轴刻度标签 -->
      <text
        v-for="(label, i) in yTickLabels" :key="'yt'+i"
        :x="PAD - 8" :y="gridLines[i] + 3.5"
        text-anchor="end"
        class="text-[9px] fill-neutral-400"
      >{{ label }}</text>

      <!-- 轴 -->
      <line :x1="PAD" :y1="H-PAD" :x2="W-PAD" :y2="H-PAD" stroke="#e2e8f0" stroke-width="1" />
      <line :x1="PAD" :y1="PAD" :x2="PAD" :y2="H-PAD" stroke="#e2e8f0" stroke-width="1" />

      <!-- UV 渐变填充区域 -->
      <path v-if="data.length" :d="uvAreaD" fill="url(#uvAreaGrad)" />

      <!-- UV 折线 -->
      <path
        v-if="data.length"
        :d="uvPathD"
        fill="none"
        stroke="#F97316"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="uv-line-animate"
      />

      <!-- PV 渐变填充区域 -->
      <path v-if="data.length" :d="areaD" fill="url(#areaGrad)" />

      <!-- PV 折线（带动画） -->
      <path
        v-if="data.length"
        :d="pathD"
        fill="none"
        stroke="#6366F1"
        stroke-width="2.5"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="visit-line-animate"
      />

      <!-- UV 数据点 -->
      <circle
        v-for="(d, i) in data" :key="'uv'+i"
        :cx="px(i)" :cy="py(d.uv)"
        :r="hoverPointIdx === i ? 6 : 4"
        fill="#F97316"
        stroke="white"
        stroke-width="2"
        class="cursor-pointer"
        style="transition: r 0.15s ease"
        @mouseenter="hoverPointIdx = i; showTooltip($event, d, i)"
        @mouseleave="hoverPointIdx = -1; hideTooltip()"
      />

      <!-- PV 数据点 -->
      <circle
        v-for="(d, i) in data" :key="'pv'+i"
        :cx="px(i)" :cy="py(d.pv)"
        :r="hoverPointIdx === i ? 6 : 4"
        fill="#6366F1"
        stroke="white"
        stroke-width="2"
        class="cursor-pointer"
        style="transition: r 0.15s ease"
        @mouseenter="hoverPointIdx = i; showTooltip($event, d, i)"
        @mouseleave="hoverPointIdx = -1; hideTooltip()"
      />

      <!-- X轴标签 -->
      <text
        v-for="i in visibleLabelIndices" :key="'l'+i"
        :x="px(i)" :y="H-PAD+20"
        text-anchor="middle"
        class="text-[10px] fill-neutral-400"
      >{{ formatMonthDay(data[i].date) }}</text>
    </svg>
    <SvgTooltip v-bind="tooltip" :container-width="containerWidth" />
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

.uv-line-animate {
  stroke-dasharray: 2000;
  stroke-dashoffset: 2000;
  animation: lineDrawIn 1.2s cubic-bezier(0.16, 1, 0.3, 1) 0.4s forwards;
}
</style>
