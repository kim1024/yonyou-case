<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, RotateCcw, Loader2 } from 'lucide-vue-next'
import { useWizard } from '@/composables/useWizard'
import SummaryBar from '@/components/wizard/SummaryBar.vue'
import WizardSection from '@/components/wizard/WizardSection.vue'
import StepMajor from '@/components/wizard/StepMajor.vue'
import StepIndustry from '@/components/wizard/StepIndustry.vue'
import StepRegion from '@/components/wizard/StepRegion.vue'
import StepEnterprise from '@/components/wizard/StepEnterprise.vue'
import StepHour from '@/components/wizard/StepHour.vue'
import GeneratingOverlay from '@/components/wizard/GeneratingOverlay.vue'

const router = useRouter()
const {
  state,
  cascade,
  loading,
  unlocked,
  canSubmit,
  init,
  selectMajor,
  selectIndustry,
  selectRegion,
  selectEnterprise,
  selectHour,
  generate,
  reset,
} = useWizard()

onMounted(() => {
  init()
})

async function handleSubmit() {
  if (!canSubmit.value || loading.generating) return
  const result = await generate()
  if (result) {
    sessionStorage.setItem('resultContent', JSON.stringify(result.data))
    sessionStorage.setItem('resultSource', result.source)
    sessionStorage.setItem('resultSelections', JSON.stringify({
      major: state.major,
      industry: state.industry,
      enterprise: state.enterprise,
      hour: state.hour,
    }))
    router.push({ name: 'result', query: { source: result.source } })
  }
}
</script>

<template>
  <div class="min-h-screen bg-neutral-50">
    <!-- 顶部栏 -->
    <header class="bg-white/80 backdrop-blur-md border-b border-neutral-200">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        <h1 class="text-lg font-bold text-neutral-900 tracking-tight">产业案例课程定制</h1>
        <button
          class="btn-ghost text-sm"
          @click="reset"
        >
          <RotateCcw class="w-4 h-4" :stroke-width="1.5" />
          重新开始
        </button>
      </div>
    </header>

    <!-- 摘要栏 -->
    <SummaryBar
      :major="state.major"
      :industry="state.industry"
      :region="state.region"
      :enterprise="state.enterprise"
      :hour="state.hour"
      @reset="reset"
    />

    <!-- 主体内容 -->
    <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pb-6">
      <!-- Section 01: 专业方向（始终激活） -->
      <WizardSection
        number="01"
        title="专业方向"
        description="请选择您的教学专业，我们将为您定制专属课程方案"
        :unlocked="true"
        :generating="loading.generating"
      >
        <StepMajor
          :majors="cascade.majors"
          :loading="loading.init"
          :selected-major="state.major"
          @select="selectMajor"
        />
      </WizardSection>

      <!-- Section 02: 行业选择（选专业后解锁） -->
      <WizardSection
        number="02"
        title="行业选择"
        description="选择案例所属行业，系统将匹配该行业的标杆企业"
        :unlocked="unlocked.industry"
        :generating="loading.generating"
      >
        <StepIndustry
          :industries="cascade.industries"
          :loading="loading.industries"
          :selected-industry="state.industry"
          @select="selectIndustry"
        />
      </WizardSection>

      <!-- Section 03: 地区选择（选行业后解锁） -->
      <WizardSection
        number="03"
        title="地区选择"
        description="选择企业所在省份，缩小企业匹配范围"
        :unlocked="unlocked.region"
        :generating="loading.generating"
      >
        <StepRegion
          :regions="cascade.regions"
          :loading="loading.regions"
          :selected-region="state.region"
          @select="selectRegion"
        />
      </WizardSection>

      <!-- Section 04: 企业选择（选地区后解锁） -->
      <WizardSection
        number="04"
        title="企业选择"
        description="选择一家企业，查看其详细信息和用友可提供的内容"
        :unlocked="unlocked.enterprise"
        :generating="loading.generating"
      >
        <StepEnterprise
          :enterprises="cascade.enterprises"
          :loading="loading.enterprises"
          :enterprise-info="cascade.enterpriseInfo"
          :selected-enterprise="state.enterprise"
          :info-loading="loading.enterpriseInfo"
          @select="selectEnterprise"
        />
      </WizardSection>

      <!-- Section 05: 课时安排（选企业后解锁） -->
      <WizardSection
        number="05"
        title="课时安排"
        description="选择课程总课时数，不同课时数对应不同的教学深度"
        :unlocked="unlocked.hour"
        :generating="loading.generating"
      >
        <StepHour
          :hours="cascade.hours"
          :selected-hour="state.hour"
          :loading="loading.init"
          @select="selectHour"
        />
      </WizardSection>

      <!-- 底部 CTA -->
      <div class="pt-2 pb-4">
        <div class="text-center">
          <button
            :disabled="!canSubmit || loading.generating"
            :class="[
              'inline-flex items-center gap-2.5 px-10 py-3.5 rounded-xl font-semibold text-base',
              'transition-all duration-300 cursor-pointer',
              canSubmit && !loading.generating
                ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/25 hover:bg-primary-600 hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0'
                : 'bg-neutral-200 text-neutral-400 cursor-not-allowed',
            ]"
            @click="handleSubmit"
          >
            <Loader2
              v-if="loading.generating"
              class="w-5 h-5 animate-spin"
              :stroke-width="2"
            />
            <span>{{ loading.generating ? '正在生成课程方案...' : '生成课程方案' }}</span>
            <ArrowRight
              v-if="!loading.generating"
              class="w-5 h-5"
              :stroke-width="2"
            />
          </button>
        </div>
      </div>
    </main>

    <!-- 全屏生成中遮罩 -->
    <GeneratingOverlay :visible="loading.generating" />

    <!-- 移动端固定底部 CTA -->
    <div class="fixed bottom-0 left-0 right-0 lg:hidden bg-white/90 backdrop-blur-md border-t border-neutral-200 p-4 z-30">
      <button
        :disabled="!canSubmit || loading.generating"
        :class="[
          'w-full inline-flex items-center justify-center gap-2.5 py-3.5 rounded-xl font-semibold text-base',
          'transition-all duration-300 cursor-pointer',
          canSubmit && !loading.generating
            ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/25 active:translate-y-0'
            : 'bg-neutral-200 text-neutral-400 cursor-not-allowed',
        ]"
        @click="handleSubmit"
      >
        <Loader2
          v-if="loading.generating"
          class="w-5 h-5 animate-spin"
          :stroke-width="2"
        />
        <span>{{ loading.generating ? '生成中...' : '生成课程方案' }}</span>
        <ArrowRight
          v-if="!loading.generating"
          class="w-5 h-5"
          :stroke-width="2"
        />
      </button>
    </div>
  </div>
</template>
