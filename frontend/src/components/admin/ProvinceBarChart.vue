<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import SvgTooltip from '@/components/shared/SvgTooltip.vue'
import type { ProvinceCount } from '@/types'

const props = defineProps<{ data: ProvinceCount[] }>()

const W = 700, H = 300, PAD = 50
const maxVal = computed(() => Math.max(1, ...props.data.map(d => d.count)))
const barW = computed(() => props.data.length ? (W - PAD * 2) / props.data.length - 4 : 30)

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

// 每个省份独立的渐变色板 —— 亮色(柱顶) → 深色(柱底)
// 悬停色版整体向深偏移一档，形成 hover 加深效果
const BAR_PALETTES: Array<{ base: [string, string]; hover: [string, string]; shadow: string }> = [
  { base: ['#818cf8', '#4f46e5'], hover: ['#6366f1', '#4338ca'], shadow: 'rgba(99,102,241,0.4)' },   // indigo
  { base: ['#22d3ee', '#0891b2'], hover: ['#06b6d4', '#0e7490'], shadow: 'rgba(6,182,212,0.4)' },    // cyan
  { base: ['#34d399', '#059669'], hover: ['#10b981', '#047857'], shadow: 'rgba(16,185,129,0.4)' },    // emerald
  { base: ['#fbbf24', '#d97706'], hover: ['#f59e0b', '#b45309'], shadow: 'rgba(245,158,11,0.4)' },    // amber
  { base: ['#fb7185', '#e11d48'], hover: ['#f43f5e', '#be123c'], shadow: 'rgba(244,63,94,0.4)' },     // rose
  { base: ['#a78bfa', '#7c3aed'], hover: ['#8b5cf6', '#6d28d9'], shadow: 'rgba(139,92,246,0.4)' },    // violet
  { base: ['#38bdf8', '#0284c7'], hover: ['#0ea5e9', '#0369a1'], shadow: 'rgba(14,165,233,0.4)' },    // sky
  { base: ['#2dd4bf', '#0d9488'], hover: ['#14b8a6', '#0f766e'], shadow: 'rgba(20,184,166,0.4)' },    // teal
  { base: ['#fb923c', '#ea580c'], hover: ['#f97316', '#c2410c'], shadow: 'rgba(249,115,22,0.4)' },    // orange
  { base: ['#e879f9', '#a21caf'], hover: ['#d946ef', '#86198f'], shadow: 'rgba(217,70,239,0.4)' },    // fuchsia
  { base: ['#60a5fa', '#2563eb'], hover: ['#3b82f6', '#1d4ed8'], shadow: 'rgba(59,130,246,0.4)' },    // blue
  { base: ['#a3e635', '#65a30d'], hover: ['#84cc16', '#4d7c0f'], shadow: 'rgba(132,204,22,0.4)' },    // lime
  { base: ['#f87171', '#dc2626'], hover: ['#ef4444', '#b91c1c'], shadow: 'rgba(239,68,68,0.4)' },     // red
  { base: ['#c084fc', '#9333ea'], hover: ['#a855f7', '#7e22ce'], shadow: 'rgba(168,85,247,0.4)' },    // purple
  { base: ['#fca5a5', '#b91c1c'], hover: ['#f87171', '#991b1b'], shadow: 'rgba(248,113,113,0.4)' },   // red-soft
]

function getBarGradId(i: number, hovered: boolean): string {
  const suffix = hovered ? 'h' : 'b'
  return `provBar-${suffix}-${i}`
}

const gridLines = computed(() => {
  const lines: number[] = []
  for (let i = 1; i <= 4; i++) {
    lines.push(H - PAD - (i / 4) * (H - PAD * 2))
  }
  return lines
})

function showTooltip(e: MouseEvent, d: ProvinceCount) {
  const rect = containerEl.value!.getBoundingClientRect()
  tooltip.value = { visible: true, x: e.clientX - rect.left, y: e.clientY - rect.top, content: `${d.province}: ${d.count} 次` }
}
</script>

<template>
  <div ref="containerEl" class="relative">
    <h3 class="text-base font-semibold text-neutral-800 mb-4">省份分布</h3>
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full">
      <defs>
        <!-- 为每个省份生成独立的线性渐变（正常 + 悬停） -->
        <linearGradient
          v-for="(_, i) in data" :key="'grad-'+i"
          :id="getBarGradId(i, false)"
          x1="0" y1="0" x2="0" y2="1"
        >
          <stop offset="0%" :stop-color="BAR_PALETTES[i % BAR_PALETTES.length].base[0]" />
          <stop offset="100%" :stop-color="BAR_PALETTES[i % BAR_PALETTES.length].base[1]" />
        </linearGradient>
        <linearGradient
          v-for="(_, i) in data" :key="'gradH-'+i"
          :id="getBarGradId(i, true)"
          x1="0" y1="0" x2="0" y2="1"
        >
          <stop offset="0%" :stop-color="BAR_PALETTES[i % BAR_PALETTES.length].hover[0]" />
          <stop offset="100%" :stop-color="BAR_PALETTES[i % BAR_PALETTES.length].hover[1]" />
        </linearGradient>
      </defs>

      <!-- 水平网格线 -->
      <line
        v-for="(y, i) in gridLines" :key="'g'+i"
        :x1="PAD" :y1="y" :x2="W-PAD" :y2="y"
        stroke="#f1f5f9" stroke-width="1"
      />

      <!-- 底轴 -->
      <line :x1="PAD" :y1="H-PAD" :x2="W-PAD" :y2="H-PAD" stroke="#e2e8f0" stroke-width="1" />

      <g v-for="(d, i) in data" :key="i">
        <!-- 柱体 -->
        <rect
          :x="PAD + i * (barW + 4)"
          :y="H - PAD - (d.count / maxVal) * (H - PAD * 2)"
          :width="barW"
          :height="(d.count / maxVal) * (H - PAD * 2)"
          :fill="hoverIdx === i ? `url(#${getBarGradId(i, true)})` : `url(#${getBarGradId(i, false)})`"
          :rx="hoverIdx === i ? 4 : 2"
          class="cursor-pointer"
          :style="{
            transform: hoverIdx === i ? 'scaleY(1.03)' : 'scaleY(1)',
            transformOrigin: 'bottom center',
            filter: hoverIdx === i
              ? `drop-shadow(0 2px 6px ${BAR_PALETTES[i % BAR_PALETTES.length].shadow})`
              : 'none',
            transition: 'transform 0.15s cubic-bezier(0.16, 1, 0.3, 1), filter 0.15s ease',
            animation: `growUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) ${i * 40}ms both`,
          }"
          @mouseenter="hoverIdx = i; showTooltip($event, d)"
          @mouseleave="hoverIdx = -1; tooltip.visible = false"
        />
        <!-- X轴标签 -->
        <text
          :x="PAD + i * (barW + 4) + barW / 2"
          :y="H - PAD + 18"
          text-anchor="middle"
          class="text-[10px] fill-neutral-400"
        >{{ d.province.slice(0, 2) }}</text>
      </g>
    </svg>
    <SvgTooltip v-bind="tooltip" :container-width="containerWidth" />
  </div>
</template>

<style scoped>
@keyframes growUp {
  from { transform: scaleY(0); }
  to   { transform: scaleY(1); }
}
</style>
