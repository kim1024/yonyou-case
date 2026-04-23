<script setup lang="ts">
import { ref, onMounted } from 'vue'
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

onMounted(async () => {
  try {
    const [s, v, p, c, ind] = await Promise.all([
      adminApi.getAnalyticsSummary(),
      adminApi.getVisitTrends(),
      adminApi.getProvinceDistribution(),
      adminApi.getCaseFrequency(),
      adminApi.getIndustryDistribution(),
    ])
    summary.value = s.data
    visitTrends.value = v.data
    provinces.value = p.data
    caseFreq.value = c.data
    industries.value = ind.data
  } catch (e) {
    console.error('加载统计数据失败:', e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold text-gray-800 mb-6">统计面板</h1>

    <div v-if="loading" class="text-gray-500">加载中...</div>

    <template v-else>
      <DashboardStats :summary="summary" />

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <VisitTimeline :data="visitTrends" />
        <ProvinceBarChart :data="provinces" />
        <CaseFrequencyChart :data="caseFreq" />
        <IndustryPieChart :data="industries" />
      </div>
    </template>
  </div>
</template>
