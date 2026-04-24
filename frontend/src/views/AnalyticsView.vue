<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { BarChart3 } from 'lucide-vue-next'
import { adminApi } from '@/api/admin'
import DashboardStats from '@/components/admin/DashboardStats.vue'
import VisitTimeline from '@/components/admin/VisitTimeline.vue'
import ProvinceBarChart from '@/components/admin/ProvinceBarChart.vue'
import CaseFrequencyChart from '@/components/admin/CaseFrequencyChart.vue'
import IndustryPieChart from '@/components/admin/IndustryPieChart.vue'
import type { AnalyticsSummary, VisitTrend, ProvinceCount, CaseFrequency, IndustryCount } from '@/types'

const summary = ref<AnalyticsSummary | null>(null)
const visitTrends = ref<VisitTrend[]>([])
const provinces = ref<ProvinceCount[]>([])
const caseFreq = ref<CaseFrequency[]>([])
const industries = ref<IndustryCount[]>([])
const loading = ref(true)
const switching = ref(false)

type TimeRange = '1d' | '7d' | '30d'
const selectedRange = ref<TimeRange>('7d')

const timeOptions = [
  { value: '1d' as const, label: '今天' },
  { value: '7d' as const, label: '最近7天' },
  { value: '30d' as const, label: '最近30天' },
]

const daysMap: Record<TimeRange, number> = { '1d': 1, '7d': 7, '30d': 30 }

function extractValue<T>(result: PromiseSettledResult<{ data: T }>): T {
  return result.status === 'fulfilled' ? result.value.data : ([] as unknown as T)
}

async function fetchData() {
  switching.value = true
  const days = daysMap[selectedRange.value]
  const results = await Promise.allSettled([
    adminApi.getAnalyticsSummary(),
    adminApi.getVisitTrends(days),
    adminApi.getProvinceDistribution(days),
    adminApi.getCaseFrequency(days),
    adminApi.getIndustryDistribution(days),
  ])

  summary.value = extractValue(results[0]) as AnalyticsSummary | null
  visitTrends.value = extractValue(results[1]) as VisitTrend[]
  provinces.value = extractValue(results[2]) as ProvinceCount[]
  caseFreq.value = extractValue(results[3]) as CaseFrequency[]
  industries.value = extractValue(results[4]) as IndustryCount[]
  loading.value = false
  switching.value = false
}

watch(selectedRange, () => fetchData())

onMounted(() => fetchData())
</script>

<template>
  <div class="animate-fade-up">
    <div class="page-header">
      <div class="flex items-center gap-3">
        <div
          class="w-10 h-10 rounded-xl flex items-center justify-center"
          style="background: linear-gradient(135deg, #14B8A6 0%, #2DD4BF 100%);"
        >
          <BarChart3 :size="20" color="#fff" :stroke-width="1.8" />
        </div>
        <div>
          <h1>统计面板</h1>
          <p>系统访问数据与业务洞察</p>
        </div>
      </div>
    </div>

    <!-- 时间维度切换器 -->
    <div class="flex items-center gap-3 mb-6">
      <div class="inline-flex items-center p-1 rounded-lg bg-neutral-100 border border-neutral-200"
           style="box-shadow: inset 0 1px 2px rgba(28,25,23,0.04);">
        <button
          v-for="opt in timeOptions"
          :key="opt.value"
          class="px-4 py-1.5 text-[13px] rounded-md transition-all duration-200 ease-out cursor-pointer"
          :class="selectedRange === opt.value
            ? 'font-semibold text-neutral-800 bg-white shadow-[0_1px_3px_rgba(28,25,23,0.08),0_1px_2px_rgba(28,25,23,0.04)]'
            : 'font-medium text-neutral-500 hover:text-neutral-700 hover:bg-black/[0.03]'"
          @click="selectedRange = opt.value"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <!-- Skeleton Loading -->
    <div v-if="loading" class="space-y-8">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div v-for="i in 4" :key="i" class="gradient-card p-5 space-y-3">
          <div class="skeleton h-4 w-20 rounded" />
          <div class="skeleton h-9 w-28 rounded" />
        </div>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div v-for="i in 4" :key="i" class="gradient-card p-6">
          <div class="skeleton h-5 w-32 mb-4 rounded" />
          <div class="skeleton h-48 w-full rounded-lg" />
        </div>
      </div>
    </div>

    <template v-else>
      <DashboardStats :summary="summary" />

      <template v-if="switching">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div v-for="i in 4" :key="i" class="gradient-card p-6">
            <div class="skeleton h-5 w-32 mb-4 rounded" />
            <div class="skeleton h-48 w-full rounded-lg" />
          </div>
        </div>
      </template>
      <template v-else>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div
            :style="{ animationDelay: '0ms' }"
            style="animation: fadeUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) both"
            class="gradient-card p-6 relative overflow-hidden"
          >
            <VisitTimeline :data="visitTrends" />
          </div>
          <div
            :style="{ animationDelay: '80ms' }"
            style="animation: fadeUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) both"
            class="gradient-card p-6 relative overflow-hidden"
          >
            <ProvinceBarChart :data="provinces" />
          </div>
          <div
            :style="{ animationDelay: '160ms' }"
            style="animation: fadeUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) both"
            class="gradient-card p-6 relative overflow-hidden"
          >
            <CaseFrequencyChart :data="caseFreq" />
          </div>
          <div
            :style="{ animationDelay: '240ms' }"
            style="animation: fadeUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) both"
            class="gradient-card p-6 relative overflow-hidden"
          >
            <IndustryPieChart :data="industries" />
          </div>
        </div>
      </template>
    </template>
  </div>
</template>
