<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'
import { ShieldCheck, Brain, BookOpen, CheckCircle2, Check } from 'lucide-vue-next'

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
  const circumference = 2 * Math.PI * 34
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

const ringCircumference = 2 * Math.PI * 34
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
              <!-- Stage 1: 确认中 -->
              <div v-if="stage === 1" key="stage1" class="stage-panel">
                <div class="stage-icon-area">
                  <ShieldCheck class="stage-icon" :stroke-width="1.5" />
                  <div class="scan-line" />
                </div>
                <h2 class="stage-title">确认选择信息</h2>
                <p class="stage-subtitle">正在验证您的选择并准备生成请求…</p>
              </div>

              <!-- Stage 2: 响应中 -->
              <div v-else-if="stage === 2" key="stage2" class="stage-panel">
                <div class="stage-icon-area ripple-area">
                  <Brain class="stage-icon" :stroke-width="1.5" />
                  <div class="ripple-circle ripple-1" />
                  <div class="ripple-circle ripple-2" />
                  <div class="ripple-circle ripple-3" />
                </div>
                <h2 class="stage-title">AI 正在思考</h2>
                <p class="stage-subtitle">已连接到大模型，正在等待响应…</p>
              </div>

              <!-- Stage 3: 生成中 -->
              <div v-else-if="stage === 3" key="stage3" class="stage-panel">
                <div class="stage-icon-area ring-area">
                  <svg class="ring-svg" viewBox="0 0 76 76">
                    <circle
                      class="ring-track"
                      cx="38"
                      cy="38"
                      r="34"
                      fill="none"
                      stroke-width="4"
                    />
                    <circle
                      class="ring-progress"
                      cx="38"
                      cy="38"
                      r="34"
                      fill="none"
                      stroke-width="4"
                      :stroke-dasharray="ringCircumference"
                      :stroke-dashoffset="getRingOffset(elapsedSeconds)"
                    />
                  </svg>
                  <BookOpen class="stage-icon ring-icon-center" :stroke-width="1.5" />
                </div>
                <h2 class="stage-title">正在生成课程方案</h2>
                <Transition name="subtitle-fade" mode="out-in">
                  <p :key="subtitleIndex" class="stage-subtitle rotating-subtitle">
                    {{ subtitleMessages[subtitleIndex] }}
                  </p>
                </Transition>
                <p class="elapsed-text">已等待 {{ elapsedSeconds }} 秒</p>
              </div>

              <!-- Stage 4: 完成 -->
              <div v-else-if="stage === 4" key="stage4" class="stage-panel">
                <div class="stage-icon-area complete-area">
                  <CheckCircle2 class="stage-icon complete-icon" :stroke-width="1.5" />
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

.stage-icon-area {
  position: relative;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stage-icon {
  width: 40px;
  height: 40px;
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

/* ── Stage 1: Scan Line ── */
.scan-line {
  position: absolute;
  left: 10%;
  width: 80%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #6366F1, transparent);
  border-radius: 1px;
  animation: scanMove 2s ease-in-out infinite;
}

@keyframes scanMove {
  0% { top: 10%; opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { top: 90%; opacity: 0; }
}

/* ── Stage 2: Ripple ── */
.ripple-area .stage-icon {
  z-index: 2;
}

.ripple-circle {
  position: absolute;
  border-radius: 50%;
  border: 2px solid #C7D2FE;
  animation: rippleExpand 3s ease-out infinite;
}

.ripple-1 {
  animation-delay: 0s;
}

.ripple-2 {
  animation-delay: 1s;
}

.ripple-3 {
  animation-delay: 2s;
}

@keyframes rippleExpand {
  0% {
    width: 20px;
    height: 20px;
    opacity: 0.6;
  }
  100% {
    width: 80px;
    height: 80px;
    opacity: 0;
  }
}

/* ── Stage 3: Ring Progress ── */
.ring-area {
  position: relative;
}

.ring-svg {
  width: 76px;
  height: 76px;
  transform: rotate(-90deg);
}

.ring-track {
  stroke: rgba(99, 102, 241, 0.12);
}

.ring-progress {
  stroke: #6366F1;
  stroke-linecap: round;
  transition: stroke-dashoffset 1s ease;
}

.ring-icon-center {
  position: absolute;
}

.rotating-subtitle {
  max-width: 280px;
}

/* ── Stage 4: Complete ── */
.complete-area .complete-icon {
  color: #10B981;
  animation: bounceInGlow 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

.complete-title {
  color: #10B981 !important;
}

@keyframes bounceInGlow {
  0% {
    transform: scale(0.5);
    opacity: 0;
  }
  60% {
    transform: scale(1.15);
    opacity: 1;
  }
  80% {
    transform: scale(0.95);
  }
  100% {
    transform: scale(1);
    filter: drop-shadow(0 0 12px rgba(16, 185, 129, 0.4));
  }
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
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.stage-fade-leave-active {
  transition: opacity 0.15s ease;
}

.stage-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
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
</style>
