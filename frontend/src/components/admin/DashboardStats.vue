<script setup lang="ts">
import { computed } from 'vue'
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
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
    <div
      v-for="(card, idx) in cards"
      :key="card.key"
      class="gradient-card p-5 relative overflow-hidden"
      :style="{ animationDelay: `${idx * 100}ms` }"
      style="animation: fadeUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) both"
    >
      <!-- 渐变装饰条 -->
      <div
        class="absolute top-0 left-0 right-0 h-[3px]"
        :style="{ background: card.gradient }"
      />

      <!-- 装饰性渐变光晕 -->
      <div
        class="absolute -top-6 -right-6 w-20 h-20 rounded-full opacity-10 blur-xl"
        :style="{ background: card.gradient }"
      />

      <div class="flex items-center gap-2 mb-3">
        <div
          class="flex items-center justify-center w-7 h-7 rounded-lg"
          :style="{ background: card.gradient.replace('linear-gradient(90deg', 'linear-gradient(135deg') + ', rgba(255,255,255,0.18))' }"
        >
          <component
            :is="card.icon"
            :size="15"
            class="text-white"
          />
        </div>
        <span class="text-xs font-medium text-neutral-500 tracking-wide uppercase">{{ card.label }}</span>
      </div>

      <div class="text-[36px] font-bold text-neutral-900 leading-none tracking-tight">
        {{ formatNumber(summary ? (summary as Record<string, number>)[card.key] : null) }}
      </div>
    </div>
  </div>
</template>
