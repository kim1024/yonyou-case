<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useWizard } from '@/composables/useWizard'
import StepProgress from '@/components/wizard/StepProgress.vue'
import StepMajor from '@/components/wizard/StepMajor.vue'
import StepIndustry from '@/components/wizard/StepIndustry.vue'
import StepRegion from '@/components/wizard/StepRegion.vue'
import StepEnterprise from '@/components/wizard/StepEnterprise.vue'
import StepHour from '@/components/wizard/StepHour.vue'

const router = useRouter()
const { state, cascade, loading, canSubmit, init, selectMajor, selectIndustry, selectRegion, selectEnterprise, selectHour, generate } = useWizard()

onMounted(() => {
  init()
})

async function handleSubmit() {
  const result = await generate()
  if (result) {
    sessionStorage.setItem('resultContent', result.content)
    router.push({ name: 'result', query: { source: result.source } })
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm">
      <div class="max-w-4xl mx-auto px-4 py-6">
        <h1 class="text-2xl font-bold text-gray-900">产业案例教学课程定制</h1>
      </div>
    </header>

    <main class="max-w-4xl mx-auto px-4 py-8">
      <StepProgress :current-step="state.currentStep" />

      <div class="mt-8">
        <StepMajor v-if="state.currentStep === 1" :majors="cascade.majors" :loading="loading.init" @select="selectMajor" />
        <StepIndustry v-if="state.currentStep === 2" :industries="cascade.industries" :loading="loading.init" @select="selectIndustry" />
        <StepRegion v-if="state.currentStep === 3" :regions="cascade.regions" :loading="loading.regions" @select="selectRegion" />
        <StepEnterprise v-if="state.currentStep === 4" :enterprises="cascade.enterprises" :loading="loading.enterprises" :enterprise-info="cascade.enterpriseInfo" @select="selectEnterprise" />
        <StepHour v-if="state.currentStep === 5" :hours="cascade.hours" :selected-hour="state.hour" @select="selectHour" />
      </div>

      <div v-if="state.currentStep === 5" class="mt-8 text-center">
        <button
          :disabled="!canSubmit || loading.generating"
          class="px-8 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          @click="handleSubmit"
        >
          {{ loading.generating ? '生成中...' : '生成课程方案' }}
        </button>
      </div>
    </main>
  </div>
</template>
