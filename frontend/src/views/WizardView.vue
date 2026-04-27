<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, isNavigationFailure } from 'vue-router'
import { Sparkles, Loader2 } from 'lucide-vue-next'
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

// ── Hero scroll animation refs ──
const heroRef = ref<HTMLElement | null>(null)
let heroObserver: IntersectionObserver | null = null
let idleTimeout: ReturnType<typeof setTimeout> | null = null
let scrollTicking = false
let exitTimeout: ReturnType<typeof setTimeout> | null = null
let enterTimeout: ReturnType<typeof setTimeout> | null = null

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

  // ── Hero scroll animation: IntersectionObserver ──
  if (heroRef.value) {
    const hero = heroRef.value

    heroObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            hero.classList.remove('hero-exiting')
            hero.classList.add('hero-entering')
            if (enterTimeout) clearTimeout(enterTimeout)
            enterTimeout = setTimeout(() => {
              hero.classList.remove('hero-entering')
            }, 500)
          } else {
            hero.classList.remove('hero-entering', 'hero-idle')
            hero.classList.add('hero-exiting')
            if (exitTimeout) clearTimeout(exitTimeout)
            exitTimeout = setTimeout(() => {
              hero.classList.remove('hero-exiting')
            }, 400)
          }
        })
      },
      {
        root: null,
        rootMargin: '-20px 0px 0px 0px',
        threshold: [0, 0.25, 0.5, 0.75, 1],
      }
    )
    heroObserver.observe(hero)

    // ── Hero scroll animation: idle detection with rAF throttle ──
    const onScroll = () => {
      if (!scrollTicking) {
        requestAnimationFrame(() => {
          hero.classList.remove('hero-idle')
          if (idleTimeout) clearTimeout(idleTimeout)
          idleTimeout = setTimeout(() => {
            if (!hero.classList.contains('hero-exiting')) {
              hero.classList.add('hero-idle')
            }
          }, 800)
          scrollTicking = false
        })
        scrollTicking = true
      }
    }
    window.addEventListener('scroll', onScroll, { passive: true })

    // Store cleanup references on the element for unmount
    ;(hero as any).__scrollCleanup = () => {
      window.removeEventListener('scroll', onScroll)
      if (idleTimeout) clearTimeout(idleTimeout)
    }
  }

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

  // ── Hero scroll animation cleanup ──
  if (heroObserver) {
    heroObserver.disconnect()
    heroObserver = null
  }
  if (exitTimeout) clearTimeout(exitTimeout)
  if (enterTimeout) clearTimeout(enterTimeout)
  if (heroRef.value && (heroRef.value as any).__scrollCleanup) {
    ;(heroRef.value as any).__scrollCleanup()
  }
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

    <!-- Hero title section -->
    <section ref="heroRef" class="ai-hero hero-visible">
      <div class="ai-hero-inner">
        <!-- Decorative circuit lines -->
        <div class="circuit-line circuit-line-left" aria-hidden="true"></div>
        <div class="circuit-line circuit-line-right" aria-hidden="true"></div>

        <!-- Ambient glow (idle animation target) -->
        <div class="hero-glow" aria-hidden="true"></div>

        <!-- Badge -->
        <div class="hero-badge">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>
          <span>课程定制引擎</span>
        </div>

        <!-- Title -->
        <h2 class="hero-title">用友产业案例教学项目<br class="sm:hidden" />课程定制系统</h2>
        <p class="hero-subtitle">为您定制专属的产业案例教学方案</p>
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
            <Sparkles
              v-if="!loading.generating"
              class="w-5 h-5 opacity-90"
              :stroke-width="1.5"
            />
            <span>{{ loading.generating ? '正在生成课程方案...' : rateLimited ? `请等待 ${cooldownRemaining} 秒...` : '查看课程方案' }}</span>
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
        <Sparkles
          v-if="!loading.generating"
          class="w-5 h-5 opacity-90"
          :stroke-width="1.5"
        />
        <span>{{ loading.generating ? '生成中...' : rateLimited ? `请等待 ${cooldownRemaining} 秒...` : '查看课程方案' }}</span>
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

/* ═══════════════════════════════════════════════════════
   Hero Scroll Animation — Three States
   ═══════════════════════════════════════════════════════ */

/* ── Keyframes: Exit ── */

@keyframes heroExit {
  from { opacity: 1; transform: translateY(0) scale(1); filter: blur(0px); }
  to   { opacity: 0; transform: translateY(-12px) scale(0.97); filter: blur(2px); }
}

@keyframes heroBadgeExit {
  from { opacity: 1; transform: translateY(0); }
  to   { opacity: 0; transform: translateY(-8px); }
}

@keyframes heroTitleExit {
  from { opacity: 1; transform: translateY(0) scaleX(1); }
  to   { opacity: 0; transform: translateY(-6px) scaleX(0.98); }
}

@keyframes heroSubtitleExit {
  from { opacity: 1; transform: translateY(0); }
  to   { opacity: 0; transform: translateY(-4px); }
}

@keyframes heroCircuitExit {
  from { opacity: 1; transform: scaleX(1); }
  to   { opacity: 0; transform: scaleX(0.3); }
}

/* ── Keyframes: Enter ── */

@keyframes heroEnter {
  from { opacity: 0; transform: translateY(8px) scale(0.97); filter: blur(2px); }
  to   { opacity: 1; transform: translateY(0) scale(1); filter: blur(0px); }
}

@keyframes heroBadgeEnter {
  from { opacity: 0; transform: translateY(-12px) scale(0.9); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

@keyframes heroTitleEnter {
  from { opacity: 0; transform: translateY(10px) scaleX(0.98); }
  to   { opacity: 1; transform: translateY(0) scaleX(1); }
}

@keyframes heroSubtitleEnter {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes heroCircuitEnter {
  from { opacity: 0; transform: scaleX(0.3); }
  to   { opacity: 1; transform: scaleX(1); }
}

/* ── Keyframes: Idle ── */

@keyframes idleBadgeBreathe {
  0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(192,57,43,0); }
  50%      { transform: scale(1.02); box-shadow: 0 0 12px 0 rgba(192,57,43,0.06); }
}

@keyframes idleTitleShimmer {
  0%   { background-position: -200% center; }
  100% { background-position: 200% center; }
}

@keyframes idleSubtitleFloat {
  0%, 100% { transform: translateY(0); opacity: 1; }
  50%      { transform: translateY(-1px); opacity: 0.85; }
}

@keyframes idleCircuitPulse {
  0%   { transform: scaleX(1); opacity: 1; }
  25%  { transform: scaleX(1.05); opacity: 0.8; }
  50%  { transform: scaleX(1); opacity: 1; }
  75%  { transform: scaleX(0.95); opacity: 0.8; }
  100% { transform: scaleX(1); opacity: 1; }
}

@keyframes idleCircuitDotTravel {
  0%, 100% { transform: translateX(0); opacity: 0.15; }
  50%      { transform: translateX(8px); opacity: 0.4; }
}

@keyframes idleGlow {
  0%, 100% { opacity: 0; transform: translate(-50%,-50%) scale(0.95); }
  50%      { opacity: 1; transform: translate(-50%,-50%) scale(1); }
}

/* ── Exit State ── */

.hero-exiting {
  animation: heroExit 0.4s cubic-bezier(0.4, 0, 0.8, 0.2) forwards;
}
.hero-exiting .hero-badge {
  animation: heroBadgeExit 0.3s cubic-bezier(0.4, 0, 0.8, 0.2) forwards;
}
.hero-exiting .hero-title {
  animation: heroTitleExit 0.35s cubic-bezier(0.4, 0, 0.8, 0.2) forwards;
  animation-delay: 0.04s;
}
.hero-exiting .hero-subtitle {
  animation: heroSubtitleExit 0.3s cubic-bezier(0.4, 0, 0.8, 0.2) forwards;
  animation-delay: 0.08s;
}
.hero-exiting .circuit-line {
  animation: heroCircuitExit 0.35s cubic-bezier(0.4, 0, 0.8, 0.2) forwards;
  animation-delay: 0.02s;
}

/* ── Enter State ── */

.hero-entering {
  animation: heroEnter 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.hero-entering .hero-badge {
  animation: heroBadgeEnter 0.45s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
  animation-delay: 0.06s;
}
.hero-entering .hero-title {
  animation: heroTitleEnter 0.45s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  animation-delay: 0.12s;
}
.hero-entering .hero-subtitle {
  animation: heroSubtitleEnter 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  animation-delay: 0.18s;
}
.hero-entering .circuit-line {
  animation: heroCircuitEnter 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  animation-delay: 0.1s;
}

/* ── Idle State ── */

.hero-idle .hero-badge {
  animation: idleBadgeBreathe 4s ease-in-out infinite;
}
.hero-idle .hero-title {
  background: linear-gradient(
    90deg,
    #1C1917 0%, #1C1917 40%,
    rgba(192,57,43,0.15) 50%,
    #1C1917 60%, #1C1917 100%
  );
  background-size: 200% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: idleTitleShimmer 6s ease-in-out infinite;
  animation-delay: 1s;
}
.hero-idle .hero-subtitle {
  animation: idleSubtitleFloat 5s ease-in-out infinite;
  animation-delay: 0.5s;
}
.hero-idle .circuit-line-left {
  animation: idleCircuitPulse 5s ease-in-out infinite;
}
.hero-idle .circuit-line-left::after {
  animation: idleCircuitDotTravel 5s ease-in-out infinite;
}
.hero-idle .circuit-line-right {
  animation: idleCircuitPulse 5s ease-in-out infinite reverse;
}
.hero-idle .circuit-line-right::after {
  animation: idleCircuitDotTravel 5s ease-in-out infinite reverse;
}
.hero-idle .hero-glow {
  animation: idleGlow 6s ease-in-out infinite;
}

/* ── Ambient Glow Element ── */

.hero-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 200px;
  height: 80px;
  background: radial-gradient(
    ellipse at center,
    rgba(192,57,43,0.04) 0%,
    rgba(212,160,106,0.02) 50%,
    transparent 70%
  );
  border-radius: 50%;
  pointer-events: none;
  z-index: -1;
  opacity: 0;
}

/* ── Reduced Motion ── */

@media (prefers-reduced-motion: reduce) {
  .hero-exiting,
  .hero-exiting .hero-badge,
  .hero-exiting .hero-title,
  .hero-exiting .hero-subtitle,
  .hero-exiting .circuit-line {
    animation: none !important;
  }
  .hero-exiting {
    opacity: 0;
    transition: opacity 0.15s ease;
  }

  .hero-entering,
  .hero-entering .hero-badge,
  .hero-entering .hero-title,
  .hero-entering .hero-subtitle,
  .hero-entering .circuit-line {
    animation: none !important;
    transform: none !important;
    filter: none !important;
  }
  .hero-entering {
    opacity: 1;
    transition: opacity 0.15s ease;
  }

  .hero-idle .hero-badge,
  .hero-idle .hero-title,
  .hero-idle .hero-subtitle,
  .hero-idle .circuit-line,
  .hero-idle .circuit-line-left,
  .hero-idle .circuit-line-right,
  .hero-idle .hero-glow {
    animation: none !important;
    transform: none !important;
    background: none !important;
    -webkit-text-fill-color: #1C1917 !important;
    color: #1C1917 !important;
    opacity: 1 !important;
  }
}
</style>
