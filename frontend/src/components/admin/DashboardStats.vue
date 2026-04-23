<script setup lang="ts">
import type { AnalyticsSummary } from '@/types'

defineProps<{ summary: AnalyticsSummary | null }>()

const cards = [
  { key: 'total_visits', label: '总访问量', icon: '📊', color: 'text-blue-600' },
  { key: 'total_enterprises', label: '企业总数', icon: '🏢', color: 'text-green-600' },
  { key: 'today_visits', label: '今日访问', icon: '📅', color: 'text-orange-600' },
  { key: 'week_visits', label: '本周访问', icon: '📈', color: 'text-purple-600' },
]
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
    <div v-for="card in cards" :key="card.key" class="bg-white rounded-xl shadow-sm p-6">
      <div class="text-sm text-gray-500 mb-1">{{ card.label }}</div>
      <div class="text-3xl font-bold" :class="card.color">
        {{ summary ? (summary as any)[card.key] : '--' }}
      </div>
    </div>
  </div>
</template>
