<script setup lang="ts">
import { Loader2 } from 'lucide-vue-next'

defineProps<{
  visible: boolean
}>()
</script>

<template>
  <Teleport to="body">
    <Transition name="overlay">
      <div
        v-if="visible"
        class="generating-overlay"
      >
        <div class="generating-card glass">
          <!-- 旋转环形动画 -->
          <div class="spinner-ring">
            <div class="ring-track" />
            <div class="ring-spin" />
            <Loader2 class="ring-icon" :stroke-width="1.5" />
          </div>

          <!-- 主文案 -->
          <h2 class="generating-title">正在生成课程方案</h2>

          <!-- 副文案 -->
          <p class="generating-subtitle">
            AI 正在分析您的需求，精心定制最佳课程方案，请稍候…
          </p>

          <!-- 脉动点点动画 -->
          <div class="dots-row">
            <span class="dot dot-1" />
            <span class="dot dot-2" />
            <span class="dot dot-3" />
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
  background: rgba(28, 25, 23, 0.45);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  padding: 24px;
}

/* ── Central Card ── */
.generating-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 48px 56px;
  border-radius: var(--radius-xl, 14px);
  box-shadow: var(--shadow-overlay);
  max-width: 420px;
  width: 100%;
  text-align: center;
  animation: cardEnter 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
}

@keyframes cardEnter {
  from {
    opacity: 0;
    transform: scale(0.92) translateY(8px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* ── Spinner Ring ── */
.spinner-ring {
  position: relative;
  width: 64px;
  height: 64px;
  flex-shrink: 0;
}

.ring-track {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 3px solid rgba(99, 102, 241, 0.12);
}

.ring-spin {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 3px solid transparent;
  border-top-color: var(--color-primary-500, #6366F1);
  border-right-color: var(--color-primary-400, #818CF8);
  animation: ringRotate 1.2s cubic-bezier(0.45, 0.05, 0.55, 0.95) infinite;
}

@keyframes ringRotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.ring-icon {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  color: var(--color-primary-500, #6366F1);
  animation: ringPulse 2s ease-in-out infinite;
  opacity: 0.25;
}

@keyframes ringPulse {
  0%, 100% { opacity: 0.15; transform: scale(1); }
  50% { opacity: 0.3; transform: scale(1.06); }
}

/* ── Text ── */
.generating-title {
  font-family: var(--font-body);
  font-size: 18px;
  font-weight: 600;
  color: var(--color-neutral-900, #1C1917);
  letter-spacing: -0.01em;
  margin: 0;
}

.generating-subtitle {
  font-family: var(--font-body);
  font-size: 13px;
  line-height: 1.6;
  color: var(--color-neutral-500, #78716C);
  margin: 0;
  max-width: 300px;
}

/* ── Dot Animation ── */
.dots-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding-top: 4px;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--color-primary-400, #818CF8);
  animation: dotBounce 1.4s ease-in-out infinite;
}

.dot-1 { animation-delay: 0s; }
.dot-2 { animation-delay: 0.16s; }
.dot-3 { animation-delay: 0.32s; }

@keyframes dotBounce {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-8px);
    opacity: 1;
  }
}

/* ── Overlay Transition ── */
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
</style>
