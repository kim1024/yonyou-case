<script setup lang="ts">
import { AlertTriangle, Gauge } from 'lucide-vue-next'
import SvgTooltip from '@/components/shared/SvgTooltip.vue'
import ModelConsumptionChart from '@/components/admin/ModelConsumptionChart.vue'
import { formatMonthDay } from '@/utils/date'
import type { useTokenStats } from '@/composables/useTokenStats'
import type { QuotaStatus } from '@/types'

const props = defineProps<{
  ts: ReturnType<typeof useTokenStats>
  /* quota data from llm composable */
  hasQuotaLimits: boolean
  overallQuotaStatus: { text: string; color: string }
  quotaStatusList: QuotaStatus[]
  quotaPercent: (q: QuotaStatus) => number
  quotaBarColor: (q: QuotaStatus) => string
  formatQuotaNumber: (val: number) => string
  percentTextColor: (q: QuotaStatus) => string
}>()

function onTrendDaysChange(days: 7 | 30) {
  props.ts.trendDays.value = days
  props.ts.loadTokenStats()
}

function onCircleEnter(e: MouseEvent, d: { date: string; tokens: number; calls: number }) {
  props.ts.trendHoverIdx.value = props.ts.trendData.value.indexOf(d)
  props.ts.showTrendTooltip(e, d)
}

function onCircleLeave() {
  props.ts.trendHoverIdx.value = -1
  props.ts.hideTrendTooltip()
}
</script>

<template>
  <div>
    <!-- Skeleton -->
    <div v-if="ts.tokenLoading.value" class="space-y-6">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div v-for="i in 4" :key="i" class="gradient-card p-5 space-y-3">
          <div class="skeleton h-4 w-20 rounded" />
          <div class="skeleton h-9 w-28 rounded" />
        </div>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div v-for="i in 2" :key="i" class="gradient-card p-6">
          <div class="skeleton h-5 w-32 mb-4 rounded" />
          <div class="skeleton h-64 w-full rounded-lg" />
        </div>
      </div>
    </div>

    <template v-else-if="ts.tokenStats.value">
      <!-- 4 张统计卡片 -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <div
          v-for="(card, idx) in ts.tokenStatCards.value"
          :key="card.key"
          class="gradient-card p-5 relative overflow-hidden"
          :style="{ animationDelay: `${idx * 80}ms` }"
          style="animation: fadeUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) both"
        >
          <div class="absolute top-0 left-0 right-0 h-[3px]" :style="{ background: card.gradient }" />
          <div class="absolute -top-6 -right-6 w-20 h-20 rounded-full opacity-10 blur-xl" :style="{ background: card.gradient }" />
          <div class="flex items-center justify-center gap-2 mb-4">
            <div
              class="flex items-center justify-center w-7 h-7 rounded-lg"
              :style="{ background: card.gradient.replace('linear-gradient(90deg', 'linear-gradient(135deg') + ', rgba(255,255,255,0.18))' }"
            >
              <component :is="card.icon" :size="15" class="text-white" />
            </div>
            <span class="text-xs font-medium text-neutral-500 tracking-wide uppercase">{{ card.label }}</span>
          </div>
          <div class="text-center">
            <div class="text-[36px] font-bold text-neutral-900 leading-none tracking-tight tabular-nums">
              {{ ts.formatTokenNumber(card.value) }}
            </div>
          </div>
        </div>
      </div>

      <!-- 限额使用概览 - 紧凑满宽行 -->
      <div
        v-if="hasQuotaLimits"
        class="gradient-card px-5 py-3 relative overflow-hidden mb-6"
        style="animation: fadeUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) 240ms both"
      >
        <div class="flex items-center gap-2 mb-2.5">
          <Gauge :size="14" class="text-indigo-500" />
          <h3 class="text-sm font-semibold text-neutral-700">限额使用概览</h3>
          <span
            class="inline-flex items-center px-1.5 py-0.5 rounded-full text-[10px] font-medium border"
            :class="overallQuotaStatus.color"
          >{{ overallQuotaStatus.text }}</span>
        </div>
        <div class="space-y-2">
          <div
            v-for="qs in quotaStatusList.filter(q => q.limit > 0)"
            :key="qs.config_id"
            class="flex items-center gap-4"
          >
            <div class="flex items-center gap-1.5 min-w-0 shrink-0" style="width: 160px">
              <span class="text-[13px] font-medium text-neutral-800 truncate">{{ qs.config_name }}</span>
              <span v-if="qs.is_chain" class="shrink-0 text-[9px] px-1 py-0.5 rounded bg-indigo-50 text-indigo-500 font-medium">链路</span>
            </div>
            <span class="text-[11px] text-neutral-400 truncate shrink-0" style="width: 120px">{{ qs.model }}</span>
            <div class="flex-1 h-[5px] rounded-full bg-neutral-100 overflow-hidden">
              <div
                class="h-full rounded-full transition-all duration-500"
                :class="quotaBarColor(qs)"
                :style="{ width: Math.min(100, quotaPercent(qs)) + '%' }"
              />
            </div>
            <span class="text-[12px] font-bold tabular-nums shrink-0 w-10 text-right" :class="percentTextColor(qs)">
              {{ quotaPercent(qs).toFixed(0) }}%
            </span>
            <span class="text-[11px] text-neutral-400 tabular-nums shrink-0 w-24 text-right">
              {{ formatQuotaNumber(qs.used) }} / {{ formatQuotaNumber(qs.limit) }}
            </span>
          </div>
        </div>
      </div>

      <!-- 图表区域 - 始终 2 列 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- 趋势折线图 -->
        <div
          class="gradient-card p-6 relative overflow-hidden"
          style="animation: fadeUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) 320ms both"
        >
          <div :ref="(el: any) => { if (el) ts.trendContainerEl.value = el as HTMLElement }" class="relative">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-base font-semibold text-neutral-800">Token 消耗趋势</h3>
              <div class="flex gap-1 p-0.5 bg-neutral-100 rounded-lg">
                <button
                  class="px-3 py-1 text-xs font-medium rounded-md transition-all duration-150"
                  :class="ts.trendDays.value === 7 ? 'bg-white text-neutral-800 shadow-sm' : 'text-neutral-500 hover:text-neutral-700'"
                  @click="onTrendDaysChange(7)"
                >7 天</button>
                <button
                  class="px-3 py-1 text-xs font-medium rounded-md transition-all duration-150"
                  :class="ts.trendDays.value === 30 ? 'bg-white text-neutral-800 shadow-sm' : 'text-neutral-500 hover:text-neutral-700'"
                  @click="onTrendDaysChange(30)"
                >30 天</button>
              </div>
            </div>
            <svg :viewBox="`0 0 ${ts.LINE_W} ${ts.LINE_H}`" class="w-full">
              <defs>
                <linearGradient id="tokenAreaGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#6366F1" stop-opacity="0.25" />
                  <stop offset="100%" stop-color="#6366F1" stop-opacity="0.02" />
                </linearGradient>
              </defs>
              <line v-for="(y, i) in ts.trendGridLines.value" :key="'g'+i" :x1="ts.LINE_PAD" :y1="y" :x2="ts.LINE_W-ts.LINE_PAD" :y2="y" stroke="#f1f5f9" stroke-width="1" />
              <line :x1="ts.LINE_PAD" :y1="ts.LINE_H-ts.LINE_PAD" :x2="ts.LINE_W-ts.LINE_PAD" :y2="ts.LINE_H-ts.LINE_PAD" stroke="#e2e8f0" stroke-width="1" />
              <line :x1="ts.LINE_PAD" :y1="ts.LINE_PAD" :x2="ts.LINE_PAD" :y2="ts.LINE_H-ts.LINE_PAD" stroke="#e2e8f0" stroke-width="1" />
              <path v-if="ts.trendData.value.length" :d="ts.trendAreaD.value" fill="url(#tokenAreaGrad)" />
              <path v-if="ts.trendData.value.length" :d="ts.trendPathD.value" fill="none" stroke="#6366F1" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="token-line-animate" />
              <circle
                v-for="(d, i) in ts.trendData.value" :key="i"
                :cx="ts.trendPx(i)" :cy="ts.trendPy(d.tokens)"
                :r="ts.trendHoverIdx.value === i ? 6 : 4"
                fill="#6366F1" stroke="white" stroke-width="2"
                class="cursor-pointer"
                style="transition: r 0.15s ease"
                @mouseenter="onCircleEnter($event, d)"
                @mouseleave="onCircleLeave()"
              />
              <text
                v-for="i in ts.trendVisibleLabelIndices.value" :key="'l'+i"
                :x="ts.trendPx(i)" :y="ts.LINE_H-ts.LINE_PAD+20"
                text-anchor="middle" class="text-[10px] fill-neutral-400"
              >{{ formatMonthDay(ts.trendData.value[i].date) }}</text>
            </svg>
            <SvgTooltip v-bind="ts.trendTooltip.value" :container-width="ts.trendContainerWidth.value" />
          </div>
        </div>

        <!-- 模型分布环形图 -->
        <div
          class="gradient-card p-6 relative overflow-hidden"
          style="animation: fadeUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) 400ms both"
        >
          <ModelConsumptionChart :data="ts.tokenStats.value?.by_model ?? []" />
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
/* ── 折线图动画 ── */
@keyframes tokenLineDrawIn {
  from { stroke-dashoffset: 2000; }
  to   { stroke-dashoffset: 0; }
}

.token-line-animate {
  stroke-dasharray: 2000;
  stroke-dashoffset: 2000;
  animation: tokenLineDrawIn 1.2s cubic-bezier(0.16, 1, 0.3, 1) 0.2s forwards;
}
</style>
