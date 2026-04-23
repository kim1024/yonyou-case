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

const gridLines = computed(() => {
  const lines: number[] = []
  for (let i = 1; i <= 4; i++) {
    lines.push(H - PAD - (i / 4) * (H - PAD * 2))
  }
  return lines
})

function showTooltip(e: MouseEvent, d: ProvinceCount) {
  const rect = (e.target as SVGElement).closest('svg')!.getBoundingClientRect()
  tooltip.value = { visible: true, x: e.clientX - rect.left, y: e.clientY - rect.top, content: `${d.province}: ${d.count} 次` }
}
</script>

<template>
  <div>
    <h3 class="text-base font-semibold text-neutral-800 mb-4">省份分布</h3>
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full">
      <defs>
        <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#06b6d4" />
          <stop offset="100%" stop-color="#67e8f9" />
        </linearGradient>
        <linearGradient id="barGradHover" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#0891b2" />
          <stop offset="100%" stop-color="#22d3ee" />
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
          :fill="hoverIdx === i ? 'url(#barGradHover)' : 'url(#barGrad)'"
          :rx="hoverIdx === i ? 4 : 2"
          class="cursor-pointer transition-all duration-150 origin-bottom"
          :style="{
            transform: hoverIdx === i ? `scaleY(1.03)` : 'scaleY(1)',
            filter: hoverIdx === i ? 'drop-shadow(0 2px 6px rgba(6,182,212,0.35))' : 'none',
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
    <SvgTooltip v-bind="tooltip" />
  </div>
</template>

<style scoped>
@keyframes growUp {
  from {
    transform: scaleY(0);
  }
  to {
    transform: scaleY(1);
  }
}

/* 柱体入场动画 */
svg rect {
  transform-origin: bottom center;
  animation: growUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
}
</style>
