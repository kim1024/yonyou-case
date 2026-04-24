<script setup lang="ts">
import type { AnalyticsSummary } from '@/types'
import { Eye, Building2, CalendarDays, TrendingUp } from 'lucide-vue-next'

defineProps<{ summary: AnalyticsSummary | null }>()

const cards = [
  { key: 'total_visits', label: '总访问量', icon: Eye, gradient: 'linear-gradient(90deg, #6366F1, #A78BFA)' },
  { key: 'total_enterprises', label: '企业总数', icon: Building2, gradient: 'linear-gradient(90deg, #10B981, #6EE7B7)' },
  { key: 'today_visits', label: '今日访问', icon: CalendarDays, gradient: 'linear-gradient(90deg, #F59E0B, #FCD34D)' },
  { key: 'week_visits', label: '本周访问', icon: TrendingUp, gradient: 'linear-gradient(90deg, #EC4899, #F9A8D4)' },
]

function formatNumber(val: number | null | undefined): string {
  if (val == null) return '--'
  return val.toLocaleString('zh-CN')
}
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
    <div
      v-for="(card, idx) in cards"
      :key="card.key"
      class="gradient-card p-3 relative overflow-hidden"
      :style="{ animationDelay: `${idx * 100}ms` }"
      style="animation: fadeUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) both"
    >
      <!-- 渐变装饰条 -->
      <div
        class="absolute top-0 left-0 right-0 h-[2px]"
        :style="{ background: card.gradient }"
      />

      <!-- 装饰性渐变光晕 -->
      <div
        class="absolute -top-4 -right-4 w-12 h-12 rounded-full opacity-10 blur-lg"
        :style="{ background: card.gradient }"
      />

      <!-- 居中内容区 -->
      <div class="flex flex-col items-center">
        <!-- 图标 -->
        <div
          class="flex items-center justify-center w-7 h-7 rounded-lg mb-1.5"
          :style="{ background: card.gradient.replace('linear-gradient(90deg', 'linear-gradient(135deg') + ', rgba(255,255,255,0.18))' }"
        >
          <component
            :is="card.icon"
            :size="14"
            class="text-white"
          />
        </div>

        <!-- 指标名称 -->
        <span class="text-sm font-medium text-neutral-500 tracking-wide uppercase mb-1">{{ card.label }}</span>

        <!-- 数字 -->
        <div class="text-[28px] font-bold text-neutral-900 leading-none tracking-tight tabular-nums">
          {{ formatNumber(summary ? (summary as Record<string, number>)[card.key] : null) }}
        </div>
      </div>
    </div>
  </div>
</template>
