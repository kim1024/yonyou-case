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

function getRingOffset(elapsed: number): number {
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
  return ringCircumference * (1 - progress)
}

const ringCircumference = 2 * Math.PI * 35
</script>

<template>
  <Teleport to="body">
    <Transition name="overlay">
      <div
        v-if="visible"
        class="generating-overlay"
      >
        <div class="orb-container">
          <div :class="'orb orb-stage-' + stage">
            <Check
              v-if="stage === 4"
              :size="24"
              color="#FFFFFF"
              :stroke-width="2.5"
            />
          </div>
          <div :class="'orb-glow orb-glow-stage-' + stage" />

          <svg
            v-if="stage >= 2"
            :class="'saturn-ring saturn-stage-' + stage"
            viewBox="0 0 100 100"
          >
            <circle
              cx="50" cy="50" r="35"
              fill="none"
              stroke="rgba(255,255,255,0.06)"
              stroke-width="1"
            />
            <circle
              v-if="stage === 3"
              cx="50" cy="50" r="35"
              fill="none"
              stroke="rgba(220,38,38,0.3)"
              stroke-width="1.5"
              stroke-linecap="round"
              :stroke-dasharray="ringCircumference"
              :stroke-dashoffset="getRingOffset(elapsedSeconds)"
            />
          </svg>
        </div>

        <div class="progress-bar-container">
          <div class="progress-bar-track">
            <div
              class="progress-bar-fill"
              :class="{ 'fill-stage-4': stage === 4 }"
              :style="{ width: [0, 25, 50, 75, 100][stage] + '%' }"
            />
          </div>
        </div>

        <Transition name="stage-fade" mode="out-in">
          <div :key="stage" class="stage-info">
            <h2 :class="['stage-title', { 'title-stage-4': stage === 4 }]">
              {{ ['确认选择信息', 'AI 正在思考', '正在生成课程方案', '课程方案已生成'][stage - 1] }}
            </h2>
            <p v-if="stage === 3" class="stage-subtitle">
              <Transition name="subtitle-fade" mode="out-in">
                <span :key="subtitleIndex">{{ subtitleMessages[subtitleIndex] }}</span>
              </Transition>
            </p>
            <p v-else class="stage-subtitle">
              {{ ['正在验证您的选择并准备生成请求…', '已连接到大模型，正在等待响应…', '', '正在为您跳转到方案详情…'][stage - 1] }}
            </p>
            <p v-if="stage === 3" class="elapsed-text">已等待 {{ elapsedSeconds }} 秒</p>
          </div>
        </Transition>
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
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(15, 15, 20, 0.60);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
}

/* ── Orb Container ── */
.orb-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
}

/* ── The Orb ── */
.orb {
  position: relative;
  width: 64px;
  height: 64px;
  border-radius: 40% 60% 60% 40% / 60% 30% 70% 40%;
  background: radial-gradient(circle at 40% 40%, #DC2626, rgba(220, 38, 38, 0.3) 60%, transparent);
  box-shadow: 0 0 40px rgba(220, 38, 38, 0.15);
  animation: orbMorph 8s cubic-bezier(0.45, 0.05, 0.55, 0.95) infinite,
             orbFloat 4s cubic-bezier(0.37, 0, 0.63, 1) infinite;
  transition: width 0.8s, height 0.8s, background 0.8s;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.orb-stage-2 {
  width: 68px;
  height: 68px;
  background: radial-gradient(circle at 40% 40%, #DC2626, #EF4444 40%, rgba(248, 113, 113, 0.2) 70%, transparent);
  animation-duration: 6s, 3s;
  box-shadow: 0 0 50px rgba(220, 38, 38, 0.18);
}

.orb-stage-3 {
  width: 72px;
  height: 72px;
  background: radial-gradient(circle at 40% 40%, #F87171, rgba(248, 113, 113, 0.3) 60%, transparent);
  animation-duration: 5s, 3s;
  box-shadow: 0 0 60px rgba(248, 113, 113, 0.22);
}

.orb-stage-4 {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: radial-gradient(circle, #10B981, #34D399 60%, rgba(52, 211, 153, 0.3) 80%, transparent);
  animation: successPulse 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) both;
  box-shadow: 0 0 50px rgba(16, 185, 129, 0.25);
}

/* ── Orb Ambient Glow ── */
.orb-glow {
  position: absolute;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(220, 38, 38, 0.12) 0%, transparent 70%);
  animation: glowPulse 3s ease-in-out infinite;
  z-index: 0;
}

.orb-glow-stage-4 {
  background: radial-gradient(circle, rgba(16, 185, 129, 0.15) 0%, transparent 70%);
}

/* ── Saturn Ring (stage 2+) ── */
.saturn-ring {
  position: absolute;
  width: 100px;
  height: 100px;
  transform: rotateX(70deg);
  animation: ringRotate 12s linear infinite;
  pointer-events: none;
  z-index: 0;
  transition: opacity 0.5s;
}

.saturn-stage-4 {
  opacity: 0;
}

/* ── Progress Bar ── */
.progress-bar-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 24px;
}

.progress-bar-track {
  width: 120px;
  height: 2px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 1px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #DC2626, #F87171);
  border-radius: 1px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.progress-bar-fill.fill-stage-4 {
  background: linear-gradient(90deg, #10B981, #34D399);
}

/* ── Stage Info Typography ── */
.stage-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding-top: 20px;
}

.stage-title {
  font-family: var(--font-body);
  font-size: 17px;
  font-weight: 500;
  color: #F5F5F4;
  letter-spacing: 0.01em;
  margin: 0;
  text-align: center;
}

.title-stage-4 {
  color: #34D399;
}

.stage-subtitle {
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 400;
  color: rgba(245, 245, 244, 0.55);
  letter-spacing: 0.02em;
  margin: 0;
  text-align: center;
  line-height: 1.5;
  max-width: 280px;
}

.elapsed-text {
  font-family: var(--font-body);
  font-size: 12px;
  color: rgba(245, 245, 244, 0.30);
  letter-spacing: 0.03em;
  margin: 0;
}

/* ── Keyframes ── */
@keyframes orbMorph {
  0%, 100% { border-radius: 40% 60% 60% 40% / 60% 30% 70% 40%; }
  25%      { border-radius: 60% 40% 30% 70% / 40% 60% 50% 50%; }
  50%      { border-radius: 30% 60% 70% 40% / 50% 60% 30% 60%; }
  75%      { border-radius: 50% 40% 50% 60% / 40% 50% 60% 50%; }
}

@keyframes orbFloat {
  0%, 100% { transform: translateY(0); }
  50%      { transform: translateY(-3px); }
}

@keyframes successPulse {
  0%   { transform: scale(0.9); opacity: 0.7; }
  50%  { transform: scale(1.12); }
  70%  { transform: scale(0.98); }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes ringRotate {
  from { transform: rotateX(70deg) rotateZ(0deg); }
  to   { transform: rotateX(70deg) rotateZ(360deg); }
}

@keyframes glowPulse {
  0%, 100% { transform: scale(1); opacity: 0.7; }
  50%      { transform: scale(1.1); opacity: 1; }
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
  .orb { width: 56px; height: 56px; }
  .orb-stage-2 { width: 60px; height: 60px; }
  .orb-stage-3 { width: 64px; height: 64px; }
  .orb-stage-4 { width: 56px; height: 56px; }
  .saturn-ring { width: 88px; height: 88px; }
  .stage-title { font-size: 15px; }
  .stage-subtitle { font-size: 12px; }
}

@media (min-width: 1280px) {
  .orb { width: 72px; height: 72px; }
  .orb-stage-2 { width: 76px; height: 76px; }
  .orb-stage-3 { width: 80px; height: 80px; }
  .orb-stage-4 { width: 72px; height: 72px; }
  .saturn-ring { width: 110px; height: 110px; }
  .stage-title { font-size: 18px; }
  .stage-subtitle { font-size: 14px; }
}
</style>
