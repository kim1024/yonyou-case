<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWizard } from '@/composables/useWizard'
import StepProgress from '@/components/wizard/StepProgress.vue'
import StepMajor from '@/components/wizard/StepMajor.vue'
import StepIndustry from '@/components/wizard/StepIndustry.vue'
import StepRegion from '@/components/wizard/StepRegion.vue'
import StepEnterprise from '@/components/wizard/StepEnterprise.vue'
import StepHour from '@/components/wizard/StepHour.vue'

const router = useRouter()
const {
  state,
  cascade,
  loading,
  canSubmit,
  init,
  selectMajor,
  selectIndustry,
  selectRegion,
  selectEnterprise,
  confirmEnterprise,
  goToStep,
  selectHour,
  generate,
  reset,
} = useWizard()

// 追踪动画方向
let prevStep = 1
const stepDirection = ref<'left' | 'right'>('left')

const transitionName = computed(() => {
  return stepDirection.value === 'left' ? 'slide-left' : 'slide-right'
})

const currentStepKey = computed(() => {
  return `${stepDirection.value}-${state.currentStep}`
})

// 包装原始函数以追踪步骤方向
function handleSelectMajor(major: string) {
  stepDirection.value = 'left'
  prevStep = state.currentStep
  selectMajor(major)
}

async function handleSelectIndustry(industry: string) {
  stepDirection.value = 'left'
  prevStep = state.currentStep
  await selectIndustry(industry)
}

async function handleSelectRegion(region: string) {
  stepDirection.value = 'left'
  prevStep = state.currentStep
  await selectRegion(region)
}

async function handleSelectEnterprise(name: string) {
  stepDirection.value = 'left'
  prevStep = state.currentStep
  await selectEnterprise(name)
}

function handleGoToStep(targetStep: number) {
  stepDirection.value = targetStep < prevStep ? 'right' : 'left'
  prevStep = state.currentStep
  goToStep(targetStep)
}

function handleConfirmEnterprise() {
  stepDirection.value = 'left'
  prevStep = state.currentStep
  confirmEnterprise()
}

function handleSelectHour(hour: number) {
  selectHour(hour)
}

function handleReset() {
  stepDirection.value = 'left'
  prevStep = 1
  reset()
}

onMounted(() => {
  init()
})

async function handleSubmit() {
  const result = await generate()
  if (result) {
    sessionStorage.setItem('resultContent', result.content)
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
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200">
      <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <h1 class="text-xl font-bold text-gray-900">产业案例课程定制</h1>
        <button
          class="text-sm text-gray-500 hover:text-gray-700 transition"
          @click="handleReset"
        >
          重新开始
        </button>
      </div>
    </header>

    <!-- Progress bar -->
    <div class="bg-white border-b border-gray-100">
      <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <StepProgress
          :current-step="state.currentStep"
          @go-to-step="handleGoToStep"
        />
      </div>
    </div>

    <!-- Step content -->
    <main class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <Transition :name="transitionName" mode="out-in">
        <StepMajor
          v-if="state.currentStep === 1"
          :key="currentStepKey"
          :majors="cascade.majors"
          :loading="loading.init"
          @select="handleSelectMajor"
        />
        <StepIndustry
          v-else-if="state.currentStep === 2"
          :key="currentStepKey"
          :industries="cascade.industries"
          :loading="loading.init"
          @select="handleSelectIndustry"
        />
        <StepRegion
          v-else-if="state.currentStep === 3"
          :key="currentStepKey"
          :regions="cascade.regions"
          :loading="loading.regions"
          @select="handleSelectRegion"
        />
        <StepEnterprise
          v-else-if="state.currentStep === 4"
          :key="currentStepKey"
          :enterprises="cascade.enterprises"
          :loading="loading.enterprises"
          :enterprise-info="cascade.enterpriseInfo"
          :selected-enterprise="state.enterprise"
          :info-loading="loading.enterpriseInfo"
          @select="handleSelectEnterprise"
        />
        <StepHour
          v-else-if="state.currentStep === 5"
          :key="currentStepKey"
          :hours="cascade.hours"
          :selected-hour="state.hour"
          @select="handleSelectHour"
        />
      </Transition>

      <!-- Step 4: 确认按钮（选择企业后显示） -->
      <div v-if="state.currentStep === 4 && state.enterprise" class="mt-8 text-center">
        <button
          class="px-8 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition shadow-sm"
          @click="handleConfirmEnterprise"
        >
          下一步 &rarr;
        </button>
      </div>

      <!-- Step 5: 生成按钮 -->
      <div v-if="state.currentStep === 5" class="mt-8 text-center">
        <button
          :disabled="!canSubmit || loading.generating"
          class="px-8 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition shadow-sm"
          @click="handleSubmit"
        >
          {{ loading.generating ? '生成中...' : '生成课程方案' }}
        </button>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Forward transition: new slide enters from right, old exits to left */
.slide-left-enter-active,
.slide-left-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-left-enter-from {
  opacity: 0;
  transform: translateX(40px);
}

.slide-left-leave-to {
  opacity: 0;
  transform: translateX(-40px);
}

/* Backward transition: new slide enters from left, old exits to right */
.slide-right-enter-active,
.slide-right-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-right-enter-from {
  opacity: 0;
  transform: translateX(-40px);
}

.slide-right-leave-to {
  opacity: 0;
  transform: translateX(40px);
}
</style>
