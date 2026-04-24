<script setup lang="ts">
import { ref, onMounted } from 'vue'
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

function extractValue<T>(result: PromiseSettledResult<{ data: T }>): T {
  return result.status === 'fulfilled' ? result.value.data : ([] as unknown as T)
}

onMounted(async () => {
  const results = await Promise.allSettled([
    adminApi.getAnalyticsSummary(),
    adminApi.getVisitTrends(),
    adminApi.getProvinceDistribution(),
    adminApi.getCaseFrequency(),
    adminApi.getIndustryDistribution(),
  ])

  summary.value = extractValue(results[0]) as AnalyticsSummary | null
  visitTrends.value = extractValue(results[1]) as VisitTrend[]
  provinces.value = extractValue(results[2]) as ProvinceCount[]
  caseFreq.value = extractValue(results[3]) as CaseFrequency[]
  industries.value = extractValue(results[4]) as IndustryCount[]
  loading.value = false
})
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
  </div>
</template>
