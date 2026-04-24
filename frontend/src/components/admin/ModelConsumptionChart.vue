<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import SvgTooltip from '@/components/shared/SvgTooltip.vue'
import { Inbox } from 'lucide-vue-next'

const COLORS = [
  '#6366F1', // 靛蓝
  '#06B6D4', // 青碧
  '#10B981', // 翡翠
  '#F59E0B', // 琥珀
  '#EF4444', // 玫瑰
  '#8B5CF6', // 紫罗兰
  '#EC4899', // 玫瑰粉
  '#14B8A6', // 青绿
]

const props = defineProps<{ data: { model: string; total_tokens: number; calls: number }[] }>()

const CX = 200, CY = 200, R = 140
const INNER_R = R * 0.55

function formatTokenNumber(val: number): string {
  if (val >= 1_000_000) return (val / 1_000_000).toFixed(1) + 'M'
  if (val >= 1_000) return (val / 1_000).toFixed(1) + 'K'
  return val.toLocaleString('zh-CN')
}

interface Slice {
  path: string
  color: string
  model: string
  tokens: number
  calls: number
  pct: string
  lx: number
  ly: number
  tx: number
  ty: number
}

const total = computed(() => props.data.reduce((s, d) => s + d.total_tokens, 0))

const slices = computed<Slice[]>(() => {
  if (!props.data.length || total.value <= 0) return []
  let angle = -Math.PI / 2
  return props.data.map((d, i) => {
    const sweep = (d.total_tokens / total.value) * Math.PI * 2
    const startAngle = angle
    angle += sweep
    const largeArc = sweep > Math.PI ? 1 : 0

    // 外弧
    const x1 = CX + R * Math.cos(startAngle)
    const y1 = CY + R * Math.sin(startAngle)
    const x2 = CX + R * Math.cos(angle)
    const y2 = CY + R * Math.sin(angle)

    // 内弧
    const ix1 = CX + INNER_R * Math.cos(startAngle)
    const iy1 = CY + INNER_R * Math.sin(startAngle)
    const ix2 = CX + INNER_R * Math.cos(angle)
    const iy2 = CY + INNER_R * Math.sin(angle)

    // 环形路径
    const path = `M ${x1} ${y1} A ${R} ${R} 0 ${largeArc} 1 ${x2} ${y2} L ${ix2} ${iy2} A ${INNER_R} ${INNER_R} 0 ${largeArc} 0 ${ix1} ${iy1} Z`

    const midAngle = startAngle + sweep / 2
    const lx = CX + (R * 0.78) * Math.cos(midAngle)
    const ly = CY + (R * 0.78) * Math.sin(midAngle)
    const pct = ((d.total_tokens / total.value) * 100).toFixed(1)

    // hover offset for pop-out effect
    const tx = hoverIdx.value === i ? 6 * Math.cos(midAngle) : 0
    const ty = hoverIdx.value === i ? 6 * Math.sin(midAngle) : 0

    return { path, color: COLORS[i % COLORS.length], model: d.model, tokens: d.total_tokens, calls: d.calls, pct, lx, ly, tx, ty }
  })
})

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

function showTooltip(e: MouseEvent, s: { model: string; tokens: number; calls: number; pct: string }) {
  const rect = containerEl.value!.getBoundingClientRect()
  tooltip.value = { visible: true, x: e.clientX - rect.left, y: e.clientY - rect.top, content: `${s.model}: ${s.tokens.toLocaleString()} Token · ${s.calls.toLocaleString()} 次 (${s.pct}%)` }
}
</script>

<template>
  <div ref="containerEl" class="relative">
    <h3 class="text-base font-semibold text-neutral-800 mb-4">模型消耗分布</h3>
    <template v-if="slices.length > 0">
      <svg viewBox="0 0 400 400" class="w-full max-w-sm mx-auto">
        <defs>
          <filter id="donutShadow">
            <feDropShadow dx="0" dy="1" stdDeviation="2" flood-opacity="0.12" />
          </filter>
        </defs>

        <!-- 环形扇区 -->
        <path
          v-for="(s, i) in slices" :key="i"
          :d="s.path"
          :fill="hoverIdx === i ? '#4338CA' : s.color"
          :transform="`translate(${s.tx}, ${s.ty})`"
          :filter="hoverIdx === i ? 'url(#donutShadow)' : 'none'"
          class="cursor-pointer"
          style="transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), fill 0.15s ease, filter 0.15s ease"
          @mouseenter="hoverIdx = i; showTooltip($event, s)"
          @mouseleave="hoverIdx = -1; tooltip.visible = false"
        />

        <!-- 中心文字 -->
        <text :x="CX" :y="CY - 6" text-anchor="middle" class="text-[18px] fill-neutral-900 font-bold">{{ formatTokenNumber(total) }}</text>
        <text :x="CX" :y="CY + 14" text-anchor="middle" class="text-[11px] fill-neutral-400">总计</text>

        <!-- 百分比标签（仅显示较大的） -->
        <text
          v-for="(s, i) in slices" :key="'t'+i"
          :x="s.lx" :y="s.ly"
          text-anchor="middle" dominant-baseline="middle"
          class="text-[9px] fill-white font-medium pointer-events-none"
        >{{ parseFloat(s.pct) > 5 ? s.pct + '%' : '' }}</text>
      </svg>

      <!-- 图例 -->
      <div class="flex flex-wrap gap-x-4 gap-y-2 mt-4 justify-center">
        <div
          v-for="(s, i) in slices" :key="'l'+i"
          class="flex items-center gap-1.5 text-xs text-neutral-600"
        >
          <div class="w-2.5 h-2.5 rounded-full" :style="{ backgroundColor: s.color }" />
          <span class="truncate max-w-[100px]">{{ s.model }}</span>
          <span class="text-neutral-400 tabular-nums">{{ s.pct }}%</span>
        </div>
      </div>
      <SvgTooltip v-bind="tooltip" :container-width="containerWidth" />
    </template>
    <div v-else class="flex flex-col items-center justify-center h-64 text-neutral-400">
      <Inbox :size="32" />
      <span class="mt-2 text-sm">暂无消耗数据</span>
    </div>
  </div>
</template>
