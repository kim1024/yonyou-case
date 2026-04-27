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
  <div class="min-h-screen wizard-page">
    <!-- AI ambient orb (secondary) -->
    <div class="ai-orb-secondary" aria-hidden="true"></div>

    <!-- 顶部栏 -->
    <header class="ai-header">
      <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        <!-- AI icon + title cluster -->
        <div class="flex items-center gap-2.5 flex-1 justify-center">
          <div class="header-ai-badge">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="3"/>
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
            </svg>
          </div>
          <h1 class="header-title">用友产业案例教学项目课程定制系统</h1>
        </div>
        <!-- Reset button -->
        <button class="header-reset-btn" @click="reset">
          <RotateCcw class="w-4 h-4" :stroke-width="1.5" />
        </button>
      </div>
    </header>

    <!-- Hero title section -->
    <section class="ai-hero">
      <div class="ai-hero-inner">
        <!-- Decorative circuit lines -->
        <div class="circuit-line circuit-line-left" aria-hidden="true"></div>
        <div class="circuit-line circuit-line-right" aria-hidden="true"></div>

        <!-- Badge -->
        <div class="hero-badge">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>
          <span>AI 课程定制引擎</span>
        </div>

        <!-- Title -->
        <h2 class="hero-title">用友产业案例教学项目<br class="sm:hidden" />课程定制系统</h2>
        <p class="hero-subtitle">基于智能体技术，为您定制专属的产业案例教学方案</p>
      </div>
    </section>

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
    <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pb-24 lg:pb-6 relative z-10">
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
            <div class="flex items-center gap-3 px-4 py-3 rounded-xl border bg-amber-50/80 backdrop-blur-sm border-amber-200/60 text-amber-800">
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
            <div class="flex items-center gap-3 px-4 py-3 rounded-xl border bg-red-50/80 backdrop-blur-sm border-red-200/60 text-red-800">
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
              'ai-cta-button',
              canSubmit && !loading.generating && !rateLimited
                ? 'ai-cta-active'
                : 'ai-cta-disabled',
            ]"
            @click="handleSubmit"
          >
            <Loader2
              v-if="loading.generating"
              class="w-5 h-5 animate-spin"
              :stroke-width="2"
            />
            <span>{{ loading.generating ? '正在生成课程方案...' : rateLimited ? `请等待 ${cooldownRemaining} 秒...` : '查看课程方案' }}</span>
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
    <div class="fixed bottom-0 left-0 right-0 lg:hidden bg-white/85 backdrop-blur-xl border-t border-neutral-200/40 p-4 z-30">
      <!-- Mobile rate limit cooldown banner -->
      <Transition name="cooldown">
        <div v-if="rateLimited" class="mb-3">
          <div class="flex items-center gap-3 px-4 py-3 rounded-xl border bg-amber-50/80 backdrop-blur-sm border-amber-200/60 text-amber-800">
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
          <div class="flex items-center gap-3 px-4 py-3 rounded-xl border bg-red-50/80 backdrop-blur-sm border-red-200/60 text-red-800">
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
          'w-full inline-flex items-center justify-center gap-2.5 ai-cta-button',
          canSubmit && !loading.generating && !rateLimited
            ? 'ai-cta-active'
            : 'ai-cta-disabled',
        ]"
        @click="handleSubmit"
      >
        <Loader2
          v-if="loading.generating"
          class="w-5 h-5 animate-spin"
          :stroke-width="2"
        />
        <span>{{ loading.generating ? '生成中...' : rateLimited ? `请等待 ${cooldownRemaining} 秒...` : '查看课程方案' }}</span>
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

/* ── Page background ── */
.wizard-page {
  background-color: #F6F8FB;
  position: relative;
  overflow-x: hidden;
}

/* Layer 1: Neural node dot grid */
.wizard-page::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image: radial-gradient(circle, rgba(192,57,43,0.06) 1px, transparent 1px);
  background-size: 28px 28px;
  pointer-events: none;
  z-index: 0;
}

/* Layer 2: Floating gradient orb (top-right) */
.wizard-page::after {
  content: '';
  position: fixed;
  top: -120px;
  right: -80px;
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(192,57,43,0.04) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
  animation: orbDrift 20s ease-in-out infinite;
}

@keyframes orbDrift {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33%      { transform: translate(30px, -20px) scale(1.05); }
  66%      { transform: translate(-20px, 15px) scale(0.95); }
}

/* Secondary orb (bottom-left) */
.ai-orb-secondary {
  position: fixed;
  bottom: -100px;
  left: -60px;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(212,160,106,0.05) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
  animation: orbDrift 25s ease-in-out infinite reverse;
}

/* ── AI Header ── */
.ai-header {
  position: sticky;
  top: 0;
  z-index: 50;
  background: rgba(246, 248, 251, 0.82);
  backdrop-filter: blur(20px) saturate(1.4);
  -webkit-backdrop-filter: blur(20px) saturate(1.4);
  border-bottom: 1px solid transparent;
}

/* Flowing data-stream gradient border */
.ai-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(192,57,43,0.10) 15%,
    rgba(212,160,106,0.18) 35%,
    rgba(192,57,43,0.12) 50%,
    rgba(212,160,106,0.18) 65%,
    rgba(192,57,43,0.10) 85%,
    transparent 100%
  );
  background-size: 200% 100%;
  animation: streamFlow 6s linear infinite;
}

@keyframes streamFlow {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.header-ai-badge {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(192,57,43,0.08), rgba(212,160,106,0.10));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #C0392B;
  flex-shrink: 0;
}

.header-title {
  font-size: 16px;
  font-weight: 700;
  color: #292524;
  letter-spacing: -0.01em;
  margin: 0;
}

.header-reset-btn {
  flex-shrink: 0;
  margin-left: 12px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #A8A29E;
  background: transparent;
  border: 1px solid transparent;
  transition: all 0.2s ease;
  cursor: pointer;
}
.header-reset-btn:hover {
  color: #C0392B;
  background: rgba(192,57,43,0.06);
  border-color: rgba(192,57,43,0.10);
}

/* On desktop, hide header title (hero section shows it) */
@media (min-width: 640px) {
  .header-title { display: none; }
}

/* ── Hero Title Section ── */
.ai-hero {
  position: relative;
  z-index: 1;
  padding: 32px 16px 24px;
  text-align: center;
}

@media (min-width: 640px) {
  .ai-hero { padding: 40px 24px 28px; }
}

.ai-hero-inner {
  position: relative;
  max-width: 640px;
  margin: 0 auto;
}

/* Circuit decoration lines (desktop only) */
.circuit-line {
  position: absolute;
  top: 50%;
  width: 80px;
  height: 1px;
  pointer-events: none;
  display: none;
}
@media (min-width: 1024px) {
  .circuit-line { display: block; }
}

.circuit-line-left {
  right: 100%;
  margin-right: 16px;
  background: linear-gradient(90deg, transparent, rgba(192,57,43,0.12));
}
.circuit-line-left::after {
  content: '';
  position: absolute;
  right: 0;
  top: -2px;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: rgba(192,57,43,0.15);
}

.circuit-line-right {
  left: 100%;
  margin-left: 16px;
  background: linear-gradient(90deg, rgba(212,160,106,0.12), transparent);
}
.circuit-line-right::after {
  content: '';
  position: absolute;
  left: 0;
  top: -2px;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: rgba(212,160,106,0.15);
}

/* Badge above title */
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 14px;
  border-radius: 100px;
  background: linear-gradient(135deg, rgba(192,57,43,0.06), rgba(212,160,106,0.08));
  border: 1px solid rgba(192,57,43,0.08);
  color: #C0392B;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.03em;
  margin-bottom: 14px;
}

/* Main title */
.hero-title {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 800;
  color: #1C1917;
  letter-spacing: -0.02em;
  line-height: 1.3;
  margin: 0;
}
@media (min-width: 640px) {
  .hero-title { font-size: 28px; }
}

/* Subtitle */
.hero-subtitle {
  font-size: 14px;
  color: #78716C;
  margin-top: 8px;
  line-height: 1.6;
  letter-spacing: 0.01em;
}

/* ── CTA Button ── */
.ai-cta-button {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 40px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.01em;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  border: none;
}

.ai-cta-active {
  background: linear-gradient(135deg, #C0392B 0%, #B83227 50%, #C0392B 100%);
  color: #fff;
  box-shadow:
    0 4px 20px rgba(192,57,43,0.25),
    0 0 0 1px rgba(212,160,106,0.15) inset;
}

.ai-cta-active:hover {
  transform: translateY(-1px);
  box-shadow:
    0 8px 32px rgba(192,57,43,0.30),
    0 0 0 1px rgba(212,160,106,0.20) inset;
}

/* Flowing shimmer sweep on hover */
.ai-cta-active::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(212,160,106,0.15) 30%,
    rgba(255,255,255,0.10) 50%,
    rgba(212,160,106,0.15) 70%,
    transparent 100%
  );
  transition: left 0.6s ease;
  pointer-events: none;
}
.ai-cta-active:hover::before {
  left: 100%;
}

/* Glowing border ring on hover */
.ai-cta-active::after {
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(192,57,43,0.2), rgba(212,160,106,0.2));
  z-index: -1;
  opacity: 0;
  transition: opacity 0.3s ease;
}
.ai-cta-active:hover::after {
  opacity: 1;
}

.ai-cta-disabled {
  background: #E7E5E4;
  color: #A8A29E;
  cursor: not-allowed;
}
</style>
