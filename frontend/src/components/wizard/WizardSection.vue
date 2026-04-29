<script setup lang="ts">
import { Lock, Loader2 } from 'lucide-vue-next'

withDefaults(
  defineProps<{
    number: string
    title: string
    description?: string
    unlocked: boolean
    generating?: boolean
  }>(),
  {
    generating: false,
  },
)
</script>

<template>
  <section
    :class="[
      'ai-section',
      unlocked && !generating ? 'ai-section-active' : 'ai-section-locked',
    ]"
  >
    <!-- Section header -->
    <div class="mb-3 flex items-start gap-3">
      <div
        :class="[
          'ai-number-badge',
          unlocked ? 'ai-number-badge-active' : 'ai-number-badge-locked',
        ]"
      >
        {{ number }}
      </div>
      <div>
        <h2 class="text-lg font-semibold text-neutral-900">{{ title }}</h2>
        <p v-if="description" class="mt-0.5 text-sm text-neutral-500">
          {{ description }}
        </p>
      </div>
    </div>

    <!-- Content area -->
    <div class="pl-10">
      <slot />
    </div>

    <!-- Lock overlay -->
    <Transition name="fade">
      <div v-if="!unlocked" class="ai-overlay">
        <div class="ai-overlay-card">
          <Lock class="w-4 h-4" :stroke-width="1.5" />
          <span>请先完成上方选择</span>
        </div>
      </div>
    </Transition>

    <!-- Generating overlay -->
    <Transition name="fade">
      <div v-if="generating" class="ai-overlay">
        <div class="ai-overlay-card">
          <Loader2 class="w-4 h-4 animate-spin" :stroke-width="1.5" />
          <span>生成中...</span>
        </div>
      </div>
    </Transition>
  </section>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.ai-section {
  position: relative;
  padding: 16px 0;
  transition: all 0.5s ease;
  border-radius: 16px;
  margin-bottom: 4px;
}

.ai-section-active { opacity: 1; }
.ai-section-locked {
  opacity: 0.35;
  pointer-events: none;
}

/* Number badge */
.ai-number-badge {
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.02em;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.ai-number-badge-active {
  background: linear-gradient(135deg, #DC2626 0%, #B91C1C 100%);
  color: #FFFFFF;
  border: none;
  box-shadow:
    0 1px 3px rgba(220, 38, 38, 0.30),
    0 4px 12px rgba(220, 38, 38, 0.15),
    0 0 0 3px rgba(220, 38, 38, 0.08);
}

.ai-number-badge-locked {
  background: linear-gradient(135deg, #F5F5F4 0%, #E7E5E4 100%);
  color: #A8A29E;
  font-weight: 600;
  border: 1px solid rgba(168, 162, 158, 0.20);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

/* Overlays */
.ai-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  border-radius: 16px;
}

.ai-overlay-card {
  background: rgba(255,255,255,0.80);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(220,38,38,0.08);
  padding: 12px 24px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #78716C;
  font-size: 13px;
  font-weight: 500;
  box-shadow: 0 4px 20px rgba(0,0,0,0.04);
}
</style>
