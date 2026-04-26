<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'
import { Check } from 'lucide-vue-next'

const props = defineProps<{
  visible: boolean
  stage: 1 | 2 | 3 | 4
  elapsedSeconds: number
}>()

const subtitleMessages = [
  'AI 正在分析您的专业方向和行业需求…',
  '正在构建课程模块和知识点体系…',
  '正在匹配岗位要求和教学目标…',
  '正在优化课程结构和课时分配…',
]

const subtitleIndex = ref(0)
let subtitleTimer: ReturnType<typeof setInterval> | null = null

function startSubtitleRotation() {
  if (subtitleTimer) return
  subtitleIndex.value = 0
  subtitleTimer = setInterval(() => {
    subtitleIndex.value = (subtitleIndex.value + 1) % subtitleMessages.length
  }, 4000)
}

function stopSubtitleRotation() {
  if (subtitleTimer) {
    clearInterval(subtitleTimer)
    subtitleTimer = null
  }
}

watch(() => props.visible, (val) => {
  if (val) {
    startSubtitleRotation()
  } else {
    stopSubtitleRotation()
  }
}, { immediate: true })

onUnmounted(() => {
  stopSubtitleRotation()
})

// Ring progress: non-linear over elapsed time
function getRingOffset(elapsed: number): number {
  const circumference = 2 * Math.PI * 35
  let progress: number
  if (elapsed <= 15) {
    progress = (elapsed / 15) * 0.5
  } else if (elapsed <= 30) {
    progress = 0.5 + ((elapsed - 15) / 15) * 0.25
  } else if (elapsed <= 60) {
    progress = 0.75 + ((elapsed - 30) / 30) * 0.17
  } else {
    progress = 0.92
  }
  return circumference * (1 - progress)
}

const ringCircumference = 2 * Math.PI * 35
</script>

<template>
  <Teleport to="body">
    <Transition name="overlay" mode="out-in">
      <div
        v-if="visible"
        class="generating-overlay"
      >
        <div class="generating-card glass">
          <!-- 进度指示器 -->
          <div class="progress-indicator">
            <div class="progress-step">
              <div
                :class="[
                  'progress-dot',
                  stage > 1 ? 'dot-completed' : stage === 1 ? 'dot-current' : 'dot-pending',
                ]"
              >
                <Check v-if="stage > 1" class="dot-check-icon" :stroke-width="2.5" />
              </div>
              <span class="progress-label">确认中</span>
            </div>
            <div :class="['progress-line', stage > 1 ? 'line-completed' : 'line-pending']" />
            <div class="progress-step">
              <div
                :class="[
                  'progress-dot',
                  stage > 2 ? 'dot-completed' : stage === 2 ? 'dot-current' : 'dot-pending',
                ]"
              >
                <Check v-if="stage > 2" class="dot-check-icon" :stroke-width="2.5" />
              </div>
              <span class="progress-label">响应中</span>
            </div>
            <div :class="['progress-line', stage > 2 ? 'line-completed' : 'line-pending']" />
            <div class="progress-step">
              <div
                :class="[
                  'progress-dot',
                  stage > 3 ? 'dot-completed' : stage === 3 ? 'dot-current' : 'dot-pending',
                ]"
              >
                <Check v-if="stage > 3" class="dot-check-icon" :stroke-width="2.5" />
              </div>
              <span class="progress-label">生成中</span>
            </div>
            <div :class="['progress-line', stage > 3 ? 'line-completed' : 'line-pending']" />
            <div class="progress-step">
              <div
                :class="[
                  'progress-dot',
                  stage === 4 ? 'dot-completed' : 'dot-pending',
                ]"
              >
                <Check v-if="stage === 4" class="dot-check-icon" :stroke-width="2.5" />
              </div>
              <span class="progress-label">完成</span>
            </div>
          </div>

          <!-- 阶段内容 -->
          <div class="stage-content">
            <Transition name="stage-fade" mode="out-in">
              <!-- Stage 1: 确认中 — Shield with scan arcs -->
              <div v-if="stage === 1" key="stage1" class="stage-panel">
                <div class="stage-icon-area stage1-area">
                  <!-- Rotating scan arcs -->
                  <svg class="scan-arcs" viewBox="0 0 80 80" width="80" height="80">
                    <defs>
                      <linearGradient id="s1-arc-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#818CF8" stop-opacity="0.6" />
                        <stop offset="100%" stop-color="#6366F1" stop-opacity="0" />
                      </linearGradient>
                    </defs>
                    <!-- Arc 1 - top -->
                    <path
                      d="M 40 6 A 34 34 0 0 1 74 40"
                      fill="none"
                      stroke="url(#s1-arc-grad)"
                      stroke-width="2.5"
                      stroke-linecap="round"
                      class="arc-top"
                    />
                    <!-- Arc 2 - bottom -->
                    <path
                      d="M 40 74 A 34 34 0 0 1 6 40"
                      fill="none"
                      stroke="url(#s1-arc-grad)"
                      stroke-width="2.5"
                      stroke-linecap="round"
                      class="arc-bottom"
                    />
                  </svg>

                  <!-- Main shield icon -->
                  <svg class="stage-icon stage1-icon" viewBox="0 0 24 24" width="36" height="36" role="img" aria-label="Shield verification">
                    <defs>
                      <linearGradient id="s1-shield-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#6366F1" />
                        <stop offset="100%" stop-color="#8B5CF6" />
                      </linearGradient>
                      <linearGradient id="s1-check-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#C7D2FE" />
                        <stop offset="100%" stop-color="#E0E7FF" />
                      </linearGradient>
                      <filter id="s1-glow">
                        <feGaussianBlur stdDeviation="1.5" result="blur" />
                        <feMerge>
                          <feMergeNode in="blur" />
                          <feMergeNode in="SourceGraphic" />
                        </feMerge>
                      </filter>
                    </defs>
                    <!-- Shield body -->
                    <path
                      d="M12 2L3 7v5c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7L12 2z"
                      fill="url(#s1-shield-grad)"
                      stroke="none"
                      filter="url(#s1-glow)"
                      opacity="0.9"
                    />
                    <!-- Inner highlight -->
                    <path
                      d="M12 2L3 7v5c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7L12 2z"
                      fill="none"
                      stroke="rgba(255,255,255,0.3)"
                      stroke-width="0.5"
                    />
                    <!-- Animated checkmark -->
                    <path
                      d="M8 12.5l2.5 3L16 9.5"
                      fill="none"
                      stroke="url(#s1-check-grad)"
                      stroke-width="2.2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      filter="url(#s1-glow)"
                      class="check-draw"
                    />
                  </svg>
                </div>
                <h2 class="stage-title">确认选择信息</h2>
                <p class="stage-subtitle">正在验证您的选择并准备生成请求…</p>
              </div>

              <!-- Stage 2: 响应中 — Brain with neural particles -->
              <div v-else-if="stage === 2" key="stage2" class="stage-panel">
                <div class="stage-icon-area stage2-area ripple-area">
                  <!-- Energy rings -->
                  <div class="energy-ring ring-1" />
                  <div class="energy-ring ring-2" />
                  <div class="energy-ring ring-3" />

                  <!-- Floating neural particles -->
                  <div class="neural-particle p1" />
                  <div class="neural-particle p2" />
                  <div class="neural-particle p3" />
                  <div class="neural-particle p4" />

                  <!-- Main brain icon -->
                  <svg class="stage-icon stage2-icon" viewBox="0 0 24 24" width="36" height="36" role="img" aria-label="AI brain">
                    <defs>
                      <linearGradient id="s2-brain-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#6366F1" />
                        <stop offset="50%" stop-color="#818CF8" />
                        <stop offset="100%" stop-color="#8B5CF6" />
                      </linearGradient>
                      <filter id="s2-glow">
                        <feGaussianBlur stdDeviation="1.5" result="blur" />
                        <feMerge>
                          <feMergeNode in="blur" />
                          <feMergeNode in="SourceGraphic" />
                        </feMerge>
                      </filter>
                      <filter id="s2-inner-glow">
                        <feGaussianBlur stdDeviation="0.8" result="blur" />
                        <feMerge>
                          <feMergeNode in="blur" />
                          <feMergeNode in="SourceGraphic" />
                        </feMerge>
                      </filter>
                    </defs>
                    <!-- Brain left hemisphere -->
                    <path
                      d="M12 2C8.5 2 6 4 6 7c-2 0-3.5 1.5-3.5 3.5S4 14 6 14c0 2 1 3.5 2.5 4.5
                         C8 20 8 21 8 22h8c0-1 0-2-.5-3.5C17 17.5 18 16 18 14c2 0 3.5-1.5 3.5-3.5
                         S20 7 18 7c0-3-2.5-5-6-5z"
                      fill="url(#s2-brain-grad)"
                      filter="url(#s2-glow)"
                      opacity="0.9"
                    />
                    <!-- Brain center line -->
                    <line
                      x1="12" y1="4" x2="12" y2="20"
                      stroke="rgba(255,255,255,0.25)"
                      stroke-width="0.8"
                      stroke-linecap="round"
                    />
                    <!-- Neural connection dots -->
                    <circle cx="9" cy="8" r="1.2" fill="#C7D2FE" filter="url(#s2-inner-glow)" class="neuron-dot nd1" />
                    <circle cx="15" cy="8" r="1.2" fill="#C7D2FE" filter="url(#s2-inner-glow)" class="neuron-dot nd2" />
                    <circle cx="8" cy="12" r="1" fill="#C7D2FE" filter="url(#s2-inner-glow)" class="neuron-dot nd3" />
                    <circle cx="16" cy="12" r="1" fill="#C7D2FE" filter="url(#s2-inner-glow)" class="neuron-dot nd4" />
                    <circle cx="10" cy="16" r="1.2" fill="#C7D2FE" filter="url(#s2-inner-glow)" class="neuron-dot nd5" />
                    <circle cx="14" cy="16" r="1.2" fill="#C7D2FE" filter="url(#s2-inner-glow)" class="neuron-dot nd6" />
                    <!-- Neural connections -->
                    <line x1="9" y1="8" x2="12" y2="10" stroke="rgba(199,210,254,0.4)" stroke-width="0.6" class="neural-line nl1" />
                    <line x1="15" y1="8" x2="12" y2="10" stroke="rgba(199,210,254,0.4)" stroke-width="0.6" class="neural-line nl2" />
                    <line x1="12" y1="10" x2="8" y2="12" stroke="rgba(199,210,254,0.4)" stroke-width="0.6" class="neural-line nl3" />
                    <line x1="12" y1="10" x2="16" y2="12" stroke="rgba(199,210,254,0.4)" stroke-width="0.6" class="neural-line nl4" />
                    <line x1="8" y1="12" x2="10" y2="16" stroke="rgba(199,210,254,0.4)" stroke-width="0.6" class="neural-line nl5" />
                    <line x1="16" y1="12" x2="14" y2="16" stroke="rgba(199,210,254,0.4)" stroke-width="0.6" class="neural-line nl6" />
                  </svg>
                </div>
                <h2 class="stage-title">AI 正在思考</h2>
                <p class="stage-subtitle">已连接到大模型，正在等待响应…</p>
              </div>

              <!-- Stage 3: 生成中 — Open book with progress ring -->
              <div v-else-if="stage === 3" key="stage3" class="stage-panel">
                <div class="stage-icon-area stage3-area ring-area">
                  <!-- Progress ring with glow -->
                  <svg class="ring-svg" viewBox="0 0 80 80" width="80" height="80">
                    <defs>
                      <linearGradient id="s3-ring-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#6366F1" />
                        <stop offset="100%" stop-color="#8B5CF6" />
                      </linearGradient>
                      <filter id="s3-ring-glow">
                        <feGaussianBlur stdDeviation="3" result="blur" />
                        <feMerge>
                          <feMergeNode in="blur" />
                          <feMergeNode in="SourceGraphic" />
                        </feMerge>
                      </filter>
                      <filter id="s3-trail-glow">
                        <feGaussianBlur stdDeviation="4" result="blur" />
                        <feMerge>
                          <feMergeNode in="blur" />
                          <feMergeNode in="SourceGraphic" />
                        </feMerge>
                      </filter>
                    </defs>
                    <!-- Track -->
                    <circle
                      cx="40" cy="40" r="35"
                      fill="none"
                      stroke="rgba(99, 102, 241, 0.08)"
                      stroke-width="3"
                    />
                    <!-- Progress arc -->
                    <circle
                      class="ring-progress"
                      cx="40" cy="40" r="35"
                      fill="none"
                      stroke="url(#s3-ring-grad)"
                      stroke-width="3.5"
                      stroke-linecap="round"
                      filter="url(#s3-ring-glow)"
                      :stroke-dasharray="ringCircumference"
                      :stroke-dashoffset="getRingOffset(elapsedSeconds)"
                    />
                    <!-- Glow dot at end of progress -->
                    <circle
                      class="ring-glow-dot"
                      cx="40" cy="5"
                      r="4"
                      fill="#818CF8"
                      filter="url(#s3-trail-glow)"
                      opacity="0.8"
                    />
                  </svg>

                  <!-- Book icon centered -->
                  <svg class="stage-icon ring-icon-center" viewBox="0 0 24 24" width="36" height="36" role="img" aria-label="Open book">
                    <defs>
                      <linearGradient id="s3-book-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#6366F1" />
                        <stop offset="100%" stop-color="#8B5CF6" />
                      </linearGradient>
                      <filter id="s3-book-glow">
                        <feGaussianBlur stdDeviation="1" result="blur" />
                        <feMerge>
                          <feMergeNode in="blur" />
                          <feMergeNode in="SourceGraphic" />
                        </feMerge>
                      </filter>
                    </defs>
                    <!-- Open book left page -->
                    <path
                      d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2V3z"
                      fill="url(#s3-book-grad)"
                      filter="url(#s3-book-glow)"
                      opacity="0.9"
                    />
                    <!-- Open book right page -->
                    <path
                      d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7V3z"
                      fill="url(#s3-book-grad)"
                      filter="url(#s3-book-glow)"
                      opacity="0.8"
                    />
                    <!-- Page lines left -->
                    <line x1="6" y1="8" x2="10" y2="8" stroke="rgba(255,255,255,0.3)" stroke-width="0.7" stroke-linecap="round" class="page-line pl1" />
                    <line x1="6" y1="11" x2="9" y2="11" stroke="rgba(255,255,255,0.25)" stroke-width="0.7" stroke-linecap="round" class="page-line pl2" />
                    <line x1="6" y1="14" x2="10" y2="14" stroke="rgba(255,255,255,0.3)" stroke-width="0.7" stroke-linecap="round" class="page-line pl3" />
                    <!-- Page lines right -->
                    <line x1="14" y1="8" x2="18" y2="8" stroke="rgba(255,255,255,0.25)" stroke-width="0.7" stroke-linecap="round" class="page-line pl4" />
                    <line x1="15" y1="11" x2="18" y2="11" stroke="rgba(255,255,255,0.3)" stroke-width="0.7" stroke-linecap="round" class="page-line pl5" />
                    <line x1="14" y1="14" x2="18" y2="14" stroke="rgba(255,255,255,0.25)" stroke-width="0.7" stroke-linecap="round" class="page-line pl6" />
                  </svg>
                </div>
                <h2 class="stage-title">正在生成课程方案</h2>
                <Transition name="subtitle-fade" mode="out-in">
                  <p :key="subtitleIndex" class="stage-subtitle rotating-subtitle">
                    {{ subtitleMessages[subtitleIndex] }}
                  </p>
                </Transition>
                <p class="elapsed-text">已等待 {{ elapsedSeconds }} 秒</p>
              </div>

              <!-- Stage 4: 完成 — Success circle with sparkles -->
              <div v-else-if="stage === 4" key="stage4" class="stage-panel">
                <div class="stage-icon-area stage4-area complete-area">
                  <!-- Radiant glow burst -->
                  <div class="glow-burst" />

                  <!-- Sparkle particles -->
                  <div class="sparkle s1" />
                  <div class="sparkle s2" />
                  <div class="sparkle s3" />
                  <div class="sparkle s4" />
                  <div class="sparkle s5" />
                  <div class="sparkle s6" />

                  <!-- Main success icon -->
                  <svg class="stage-icon complete-icon" viewBox="0 0 24 24" width="36" height="36" role="img" aria-label="Success">
                    <defs>
                      <linearGradient id="s4-circle-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#10B981" />
                        <stop offset="100%" stop-color="#34D399" />
                      </linearGradient>
                      <filter id="s4-glow">
                        <feGaussianBlur stdDeviation="2" result="blur" />
                        <feMerge>
                          <feMergeNode in="blur" />
                          <feMergeNode in="SourceGraphic" />
                        </feMerge>
                      </filter>
                    </defs>
                    <!-- Filled circle -->
                    <circle
                      cx="12" cy="12" r="11"
                      fill="url(#s4-circle-grad)"
                      filter="url(#s4-glow)"
                    />
                    <!-- Inner highlight -->
                    <circle
                      cx="12" cy="12" r="11"
                      fill="none"
                      stroke="rgba(255,255,255,0.25)"
                      stroke-width="0.5"
                    />
                    <!-- White checkmark -->
                    <path
                      d="M7 12.5l3.5 4L17 8"
                      fill="none"
                      stroke="#FFFFFF"
                      stroke-width="2.5"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      filter="url(#s4-glow)"
                      class="check-complete"
                    />
                  </svg>
                </div>
                <h2 class="stage-title complete-title">课程方案已生成</h2>
                <p class="stage-subtitle">正在为您跳转到方案详情…</p>
              </div>
            </Transition>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
/* ── Overlay Backdrop ── */
.generating-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(28, 25, 23, 0.50);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  padding: 24px;
}

/* ── Central Card ── */
.generating-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  padding: 36px 40px;
  border-radius: var(--radius-xl, 14px);
  box-shadow: var(--shadow-overlay);
  max-width: 400px;
  width: 100%;
  text-align: center;
  animation: cardEnter 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
}

@keyframes cardEnter {
  from {
    opacity: 0;
    transform: scale(0.92);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* ── Progress Indicator ── */
.progress-indicator {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  gap: 0;
  width: 100%;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.progress-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s ease, box-shadow 0.3s ease;
}

.dot-completed {
  background-color: #6366F1;
}

.dot-current {
  background-color: #6366F1;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2);
  animation: dotPulse 2s ease-in-out infinite;
}

.dot-pending {
  background-color: #E7E5E4;
}

.dot-check-icon {
  width: 8px;
  height: 8px;
  color: white;
}

@keyframes dotPulse {
  0%, 100% {
    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(99, 102, 241, 0.08);
  }
}

.progress-label {
  font-family: var(--font-body);
  font-size: 11px;
  color: #78716C;
  white-space: nowrap;
}

.progress-line {
  width: 32px;
  height: 2px;
  margin-top: 5px;
  border-radius: 1px;
  transition: background-color 0.3s ease;
}

.line-completed {
  background-color: #6366F1;
}

.line-pending {
  background-color: #E7E5E4;
}

/* ── Stage Content ── */
.stage-content {
  width: 100%;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.stage-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

/* ── Shared Icon Container ── */
.stage-icon-area {
  position: relative;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.4);
  box-shadow:
    0 4px 16px rgba(99, 102, 241, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  overflow: visible;
}

.stage-icon-area::before {
  content: '';
  position: absolute;
  inset: -20px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.20) 0%, transparent 70%);
  animation: glowPulse 2.5s ease-in-out infinite;
  pointer-events: none;
  z-index: -1;
}

@keyframes glowPulse {
  0%, 100% { opacity: 0.6; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.08); }
}

/* Stage-specific glow colors */
.stage1-area::before {
  background: radial-gradient(circle, rgba(99, 102, 241, 0.20) 0%, transparent 70%);
}

.stage2-area::before {
  background: radial-gradient(circle, rgba(99, 102, 241, 0.18) 0%, rgba(139, 92, 246, 0.08) 50%, transparent 70%);
}

.stage3-area::before {
  background: radial-gradient(circle, rgba(129, 140, 248, 0.18) 0%, transparent 70%);
}

.stage4-area::before {
  background: radial-gradient(circle, rgba(16, 185, 129, 0.25) 0%, transparent 70%);
  animation: glowPulseSuccess 2.5s ease-in-out infinite;
}

@keyframes glowPulseSuccess {
  0%, 100% { opacity: 0.7; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.06); }
}

.stage-icon {
  width: 36px;
  height: 36px;
  color: #6366F1;
}

.stage-title {
  font-family: var(--font-body);
  font-size: 18px;
  font-weight: 600;
  color: #1C1917;
  margin: 0;
  letter-spacing: -0.01em;
}

.stage-subtitle {
  font-family: var(--font-body);
  font-size: 13px;
  color: #78716C;
  margin: 0;
  line-height: 1.5;
}

.elapsed-text {
  font-family: var(--font-body);
  font-size: 12px;
  color: #A8A29E;
  margin: 0;
}

/* ── Stage 1: Rotating Scan Arcs ── */
.scan-arcs {
  position: absolute;
  inset: 0;
  animation: arcRotate 3s linear infinite;
}

@keyframes arcRotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.arc-top, .arc-bottom {
  opacity: 0.7;
}

/* Animated checkmark drawing */
.check-draw {
  stroke-dasharray: 20;
  stroke-dashoffset: 20;
  animation: drawCheck 1s ease-out 0.3s forwards;
}

@keyframes drawCheck {
  to { stroke-dashoffset: 0; }
}

/* Gentle float */
.stage1-icon {
  animation: gentleFloat 3.5s ease-in-out infinite;
}

@keyframes gentleFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-2px); }
}

/* ── Stage 2: Energy Rings + Neural Particles ── */
.energy-ring {
  position: absolute;
  border-radius: 50%;
  border: 1.5px solid rgba(99, 102, 241, 0.15);
  animation: energyExpand 2.8s ease-out infinite;
  pointer-events: none;
}

.ring-1 { animation-delay: 0s; }
.ring-2 { animation-delay: 0.9s; }
.ring-3 { animation-delay: 1.8s; }

@keyframes energyExpand {
  0% {
    width: 30px;
    height: 30px;
    opacity: 0.5;
    border-color: rgba(99, 102, 241, 0.3);
  }
  100% {
    width: 90px;
    height: 90px;
    opacity: 0;
    border-color: rgba(139, 92, 246, 0.05);
  }
}

/* Floating neural particles */
.neural-particle {
  position: absolute;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #818CF8;
  opacity: 0;
  pointer-events: none;
  animation: particleDrift 3s ease-in-out infinite;
}

.p1 { top: 10%; left: 20%; animation-delay: 0s; }
.p2 { top: 15%; right: 15%; animation-delay: 0.75s; }
.p3 { bottom: 20%; left: 15%; animation-delay: 1.5s; }
.p4 { bottom: 10%; right: 20%; animation-delay: 2.25s; }

@keyframes particleDrift {
  0%, 100% {
    opacity: 0;
    transform: translateY(0) scale(0.5);
  }
  20% {
    opacity: 0.7;
    transform: translateY(-4px) scale(1);
  }
  50% {
    opacity: 0.4;
    transform: translateY(-8px) scale(0.8);
  }
  80% {
    opacity: 0;
    transform: translateY(-14px) scale(0.3);
  }
}

/* Neuron dot pulsing */
.neuron-dot {
  animation: neuronPulse 2s ease-in-out infinite;
}

.nd1 { animation-delay: 0s; }
.nd2 { animation-delay: 0.3s; }
.nd3 { animation-delay: 0.6s; }
.nd4 { animation-delay: 0.9s; }
.nd5 { animation-delay: 1.2s; }
.nd6 { animation-delay: 1.5s; }

@keyframes neuronPulse {
  0%, 100% { opacity: 0.5; r: 1; }
  50% { opacity: 1; r: 1.4; }
}

/* Neural line shimmer */
.neural-line {
  stroke-dasharray: 4 4;
  animation: lineFlow 1.5s linear infinite;
}

@keyframes lineFlow {
  to { stroke-dashoffset: -8; }
}

.stage2-icon {
  animation: gentleFloat 3.5s ease-in-out infinite;
  z-index: 2;
}

/* ── Stage 3: Ring Progress ── */
.ring-area {
  position: relative;
}

.ring-svg {
  width: 80px;
  height: 80px;
  transform: rotate(-90deg);
}

.ring-progress {
  transition: stroke-dashoffset 1s ease;
}

/* Glow dot follows the ring endpoint */
.ring-glow-dot {
  transform-origin: 40px 40px;
  animation: dotOrbit 8s linear infinite;
}

@keyframes dotOrbit {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Page lines — subtle typing animation */
.page-line {
  stroke-dasharray: 4;
  animation: typeLine 2s ease-in-out infinite alternate;
}

.pl1 { animation-delay: 0s; }
.pl2 { animation-delay: 0.2s; }
.pl3 { animation-delay: 0.4s; }
.pl4 { animation-delay: 0.6s; }
.pl5 { animation-delay: 0.8s; }
.pl6 { animation-delay: 1.0s; }

@keyframes typeLine {
  0% { stroke-dashoffset: 4; opacity: 0.2; }
  100% { stroke-dashoffset: 0; opacity: 0.8; }
}

.ring-icon-center {
  position: absolute;
  animation: gentleFloat 3.5s ease-in-out infinite;
}

.rotating-subtitle {
  max-width: 280px;
}

/* ── Stage 4: Complete ── */
.complete-area .complete-icon {
  animation: successBounce 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

@keyframes successBounce {
  0% {
    transform: scale(0.3);
    opacity: 0;
  }
  50% {
    transform: scale(1.12);
  }
  70% {
    transform: scale(0.96);
  }
  100% {
    transform: scale(1);
    opacity: 1;
    filter: drop-shadow(0 0 16px rgba(16, 185, 129, 0.45));
  }
}

/* Radiant glow burst — appears on stage 4 entry */
.glow-burst {
  position: absolute;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(16, 185, 129, 0.30) 0%, rgba(52, 211, 153, 0.10) 40%, transparent 70%);
  animation: burstAppear 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

@keyframes burstAppear {
  0% {
    transform: scale(0.3);
    opacity: 0;
  }
  60% {
    transform: scale(1.15);
    opacity: 1;
  }
  100% {
    transform: scale(1);
    opacity: 0.8;
  }
}

/* Checkmark draw-in */
.check-complete {
  stroke-dasharray: 20;
  stroke-dashoffset: 20;
  animation: drawCheck 0.5s ease-out 0.3s forwards;
}

/* Sparkle particles */
.sparkle {
  position: absolute;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #34D399;
  pointer-events: none;
}

.s1 { top: 5%; left: 50%; animation: sparkleBurst 0.8s ease-out 0.2s both; }
.s2 { top: 25%; right: 5%; animation: sparkleBurst 0.8s ease-out 0.35s both; }
.s3 { bottom: 15%; right: 10%; animation: sparkleBurst 0.8s ease-out 0.5s both; }
.s4 { bottom: 5%; left: 45%; animation: sparkleBurst 0.8s ease-out 0.4s both; }
.s5 { top: 30%; left: 5%; animation: sparkleBurst 0.8s ease-out 0.3s both; }
.s6 { top: 10%; right: 20%; animation: sparkleBurst 0.8s ease-out 0.45s both; }

@keyframes sparkleBurst {
  0% {
    opacity: 0;
    transform: scale(0) translate(0, 0);
  }
  40% {
    opacity: 1;
    transform: scale(1.2);
  }
  100% {
    opacity: 0;
    transform: scale(0.3) translate(var(--tx, 8px), var(--ty, -12px));
  }
}

/* Different sparkle directions */
.s1 { --tx: 0px; --ty: -16px; }
.s2 { --tx: 14px; --ty: -8px; }
.s3 { --tx: 10px; --ty: 8px; }
.s4 { --tx: -4px; --ty: 14px; }
.s5 { --tx: -12px; --ty: -6px; }
.s6 { --tx: 8px; --ty: -10px; }

.complete-title {
  color: #10B981 !important;
}

/* ── Transitions ── */
.overlay-enter-active {
  transition: opacity 0.3s ease;
}

.overlay-leave-active {
  transition: opacity 0.25s ease;
}

.overlay-enter-from,
.overlay-leave-to {
  opacity: 0;
}

.stage-fade-enter-active {
  transition: opacity 0.3s ease, transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.stage-fade-leave-active {
  transition: opacity 0.15s ease;
}

.stage-fade-enter-from {
  opacity: 0;
  transform: translateY(8px) scale(0.95);
}

.stage-fade-leave-to {
  opacity: 0;
}

.subtitle-fade-enter-active {
  transition: opacity 0.3s ease;
}

.subtitle-fade-leave-active {
  transition: opacity 0.2s ease;
}

.subtitle-fade-enter-from,
.subtitle-fade-leave-to {
  opacity: 0;
}

/* ── Responsive ── */
@media (max-width: 767px) {
  .stage-icon-area { width: 72px; height: 72px; }
  .stage-icon-area::before { inset: -16px; }
  .stage-icon { width: 32px; height: 32px; }
  .stage-title { font-size: 16px; }
  .stage-subtitle { font-size: 12px; }
  .ring-svg { width: 72px; height: 72px; }
  .glow-burst { width: 100px; height: 100px; }
}

@media (min-width: 1280px) {
  .stage-icon-area { width: 88px; height: 88px; }
  .stage-icon { width: 40px; height: 40px; }
  .stage-title { font-size: 19px; }
  .stage-subtitle { font-size: 14px; }
  .ring-svg { width: 88px; height: 88px; }
  .glow-burst { width: 130px; height: 130px; }
}
</style>
