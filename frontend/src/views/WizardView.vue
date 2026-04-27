<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useRouter, isNavigationFailure } from 'vue-router'
import { ArrowRight, RotateCcw, Loader2 } from 'lucide-vue-next'
import { useWizard } from '@/composables/useWizard'
import { wizardApi } from '@/api/wizard'
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
  generationStage,
  elapsedSeconds,
  currentRequestId,
  init,
  selectMajor,
  selectIndustry,
  selectRegion,
  selectEnterprise,
  selectHour,
  generate,
  reset,
  restoreGeneration,
  updateStage,
  clearGeneration,
  rateLimited,
  rateLimitMessage,
  cooldownRemaining,
  error,
} = useWizard()

let timerInterval: ReturnType<typeof setInterval> | null = null
let isRestorePolling = false
let hasRetriedGeneration = false

async function pollStatus() {
  const requestId = currentRequestId.value
  if (!requestId) return
  try {
    const res = await wizardApi.getGenerateStatus(requestId)
    const statusData = res.data
    if (statusData.status === 'completed') {
      generationStage.value = 4
      sessionStorage.setItem('resultContent', JSON.stringify(statusData.data))
      sessionStorage.setItem('resultSource', statusData.source)
      if (statusData.llm_error) {
        sessionStorage.setItem('resultLlmError', statusData.llm_error)
      }
      const savedSelections = localStorage.getItem('generating_selections')
      if (savedSelections) {
        sessionStorage.setItem('resultSelections', savedSelections)
      }
      stopTimer()
      setTimeout(async () => {
        try {
          const navResult = await router.push({ name: 'result', query: { source: statusData.source } })
          if (isNavigationFailure(navResult)) {
            console.error('[pollStatus] 导航被阻止:', navResult)
            window.location.href = `/result?source=${encodeURIComponent(statusData.source)}`
          }
        } catch (e) {
          console.error('[pollStatus] 导航异常:', e)
          window.location.href = `/result?source=${encodeURIComponent(statusData.source)}`
        } finally {
          loading.generating = false
          clearGeneration()
        }
      }, 1500)
    } else if (statusData.status === 'failed' || statusData.status === 'expired') {
      if (!hasRetriedGeneration) {
        // 首次失败，自动重新发起生成（后端模板兜底）
        hasRetriedGeneration = true
        console.warn('[pollStatus] 生成失败，自动重试:', statusData.message)
        clearGeneration()
        const retryResult = await generate()
        if (retryResult && 'templateData' in retryResult) {
          // 模板兜底成功 — 直接展示结果
          stopTimer()
          loading.generating = false
          sessionStorage.setItem('resultContent', JSON.stringify(retryResult.templateData))
          sessionStorage.setItem('resultSource', retryResult.source)
          if (retryResult.llm_error) {
            sessionStorage.setItem('resultLlmError', retryResult.llm_error)
          }
          const savedSelections = localStorage.getItem('generating_selections')
          if (savedSelections) {
            sessionStorage.setItem('resultSelections', savedSelections)
          }
          clearGeneration()
          hasRetriedGeneration = false
          router.push({ name: 'result', query: { source: retryResult.source } })
          return
        } else if (retryResult && 'client_request_id' in retryResult) {
          // 重试成功（202），继续轮询新请求
          pollStatus()
          return
        }
      }
      // 重试也失败，或已经是第二次失败
      stopTimer()
      error.value = statusData.message || '生成失败，请重试'
      loading.generating = false
      clearGeneration()
      hasRetriedGeneration = false
    }
    // pending → keep polling
  } catch {
    // network error → keep polling, don't crash
  }
}

function startTimer(polling = false) {
  if (timerInterval) return
  isRestorePolling = polling
  timerInterval = setInterval(() => {
    if (loading.generating && generationStage.value < 4) {
      updateStage()
      // 恢复场景：每 3 秒轮询一次后端状态
      if (isRestorePolling && elapsedSeconds.value % 3 === 0) {
        pollStatus()
      }
    }
    if (generationStage.value >= 4 && timerInterval) {
      clearInterval(timerInterval)
      timerInterval = null
    }
  }, 1000)
  // 恢复场景：立即执行一次轮询
  if (polling) {
    pollStatus()
  }
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  isRestorePolling = false
}

function handleBeforeUnload(e: BeforeUnloadEvent) {
  if (loading.generating) {
    e.preventDefault()
  }
}

onMounted(async () => {
  init()
  window.addEventListener('beforeunload', handleBeforeUnload)

  const result = await restoreGeneration()
  if (result && 'status' in result && result.status === 'pending') {
    startTimer(true)
  } else if (result && 'data' in result) {
    sessionStorage.setItem('resultContent', JSON.stringify(result.data))
    sessionStorage.setItem('resultSource', result.source)
    if (result.llm_error) {
      sessionStorage.setItem('resultLlmError', result.llm_error)
    }
    const savedSelections = localStorage.getItem('generating_selections')
    if (savedSelections) {
      sessionStorage.setItem('resultSelections', savedSelections)
    }
    try {
      const navResult = await router.push({ name: 'result', query: { source: result.source } })
      if (isNavigationFailure(navResult)) {
        console.error('[restoreGeneration] 导航被阻止:', navResult)
        window.location.href = `/result?source=${encodeURIComponent(result.source)}`
      }
    } catch (e) {
      console.error('[restoreGeneration] 导航异常:', e)
      window.location.href = `/result?source=${encodeURIComponent(result.source)}`
    }
  }
})

onUnmounted(() => {
  stopTimer()
  window.removeEventListener('beforeunload', handleBeforeUnload)
})

async function handleSubmit() {
  if (!canSubmit.value || loading.generating) return
  hasRetriedGeneration = false
  console.log('[handleSubmit] 开始生成...')
  startTimer()
  const result = await generate()
  console.log('[handleSubmit] generate 返回:', result ? '成功' : '失败', 'stage:', generationStage.value)
  if (result && 'templateData' in result) {
    // 模板兜底 — 直接展示结果
    stopTimer()
    loading.generating = false
    sessionStorage.setItem('resultContent', JSON.stringify(result.templateData))
    sessionStorage.setItem('resultSource', result.source)
    if (result.llm_error) {
      sessionStorage.setItem('resultLlmError', result.llm_error)
    }
    const savedSelections = localStorage.getItem('generating_selections')
    if (savedSelections) {
      sessionStorage.setItem('resultSelections', savedSelections)
    }
    clearGeneration()
    router.push({ name: 'result', query: { source: result.source } })
  } else if (result && 'client_request_id' in result) {
    // 202 accepted — keep timer running, start polling for completion
    isRestorePolling = true
    pollStatus()
  } else {
    // Error or cancelled — stop timer, reset loading
    stopTimer()
    loading.generating = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-neutral-50">
    <!-- 顶部栏 -->
    <header class="bg-white/80 backdrop-blur-md border-b border-neutral-200">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        <h1 class="text-lg font-bold text-neutral-900 tracking-tight">
          <span class="md:hidden">课程定制</span>
          <span class="hidden md:inline">用友产业案例教学项目课程定制系统</span>
        </h1>
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
    <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pb-24 lg:pb-6">
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
      <div class="hidden lg:block pt-2 pb-4">
        <!-- Rate limit cooldown banner -->
        <Transition name="cooldown">
          <div
            v-if="rateLimited"
            class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-4"
          >
            <div class="flex items-center gap-3 px-4 py-3 rounded-xl border bg-amber-50 border-amber-200 text-amber-800">
              <svg class="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <div class="flex-1">
                <p class="text-sm font-medium">{{ rateLimitMessage || '生成请求过于频繁，请稍后再试' }}</p>
                <p v-if="cooldownRemaining > 0" class="text-xs mt-0.5 text-amber-600">
                  {{ cooldownRemaining }} 秒后可重新生成
                </p>
              </div>
            </div>
          </div>
        </Transition>

        <!-- Error banner -->
        <Transition name="cooldown">
          <div v-if="error" class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-4">
            <div class="flex items-center gap-3 px-4 py-3 rounded-xl border bg-red-50 border-red-200 text-red-800">
              <svg class="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <div class="flex-1">
                <p class="text-sm font-medium">{{ error }}</p>
              </div>
              <button
                class="text-red-400 hover:text-red-600 transition-colors cursor-pointer"
                @click="error = ''"
              >
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </Transition>

        <div class="text-center">
          <button
            :disabled="!canSubmit || loading.generating || rateLimited"
            :class="[
              'inline-flex items-center gap-2.5 px-10 py-3.5 rounded-xl font-semibold text-base',
              'transition-all duration-300 cursor-pointer',
              canSubmit && !loading.generating && !rateLimited
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
            <span>{{ loading.generating ? '正在生成课程方案...' : rateLimited ? `请等待 ${cooldownRemaining} 秒...` : '生成课程方案' }}</span>
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
    <GeneratingOverlay
      :visible="loading.generating"
      :stage="generationStage"
      :elapsed-seconds="elapsedSeconds"
    />

    <!-- 移动端固定底部 CTA -->
    <div class="fixed bottom-0 left-0 right-0 lg:hidden bg-white/90 backdrop-blur-md border-t border-neutral-200 p-4 z-30">
      <!-- Mobile rate limit cooldown banner -->
      <Transition name="cooldown">
        <div v-if="rateLimited" class="mb-3">
          <div class="flex items-center gap-3 px-4 py-3 rounded-xl border bg-amber-50 border-amber-200 text-amber-800">
            <svg class="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <div class="flex-1">
              <p class="text-sm font-medium">{{ rateLimitMessage || '生成请求过于频繁，请稍后再试' }}</p>
              <p v-if="cooldownRemaining > 0" class="text-xs mt-0.5 text-amber-600">
                {{ cooldownRemaining }} 秒后可重新生成
              </p>
            </div>
          </div>
        </div>
      </Transition>

      <!-- Mobile error banner -->
      <Transition name="cooldown">
        <div v-if="error" class="mb-3">
          <div class="flex items-center gap-3 px-4 py-3 rounded-xl border bg-red-50 border-red-200 text-red-800">
            <svg class="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <div class="flex-1">
              <p class="text-sm font-medium">{{ error }}</p>
            </div>
            <button
              class="text-red-400 hover:text-red-600 transition-colors cursor-pointer"
              @click="error = ''"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </Transition>

      <button
        :disabled="!canSubmit || loading.generating || rateLimited"
        :class="[
          'w-full inline-flex items-center justify-center gap-2.5 py-3.5 rounded-xl font-semibold text-base',
          'transition-all duration-300 cursor-pointer',
          canSubmit && !loading.generating && !rateLimited
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
        <span>{{ loading.generating ? '生成中...' : rateLimited ? `请等待 ${cooldownRemaining} 秒...` : '生成课程方案' }}</span>
        <ArrowRight
          v-if="!loading.generating"
          class="w-5 h-5"
          :stroke-width="2"
        />
      </button>
    </div>
  </div>
</template>

<style scoped>
.cooldown-enter-active {
  animation: fadeUp 0.3s ease-out;
}
.cooldown-leave-active {
  transition: all 0.2s ease-in;
}
.cooldown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
