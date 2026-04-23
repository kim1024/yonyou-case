<script setup lang="ts">
import { Lock } from 'lucide-vue-next'

defineProps<{
  number: string
  title: string
  description?: string
  unlocked: boolean
}>()
</script>

<template>
  <section
    :class="[
      'relative py-10 transition-all duration-500',
      unlocked ? 'opacity-100' : 'opacity-40 pointer-events-none',
    ]"
  >
    <!-- 区域头部 -->
    <div class="mb-6 flex items-start gap-4">
      <!-- 编号徽章 -->
      <div
        :class="[
          'shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold transition-colors duration-300',
          unlocked
            ? 'bg-primary-50 text-primary-600 ring-2 ring-primary-200'
            : 'bg-neutral-100 text-neutral-400',
        ]"
      >
        {{ number }}
      </div>

      <div>
        <h2 class="text-xl font-bold text-neutral-900">{{ title }}</h2>
        <p v-if="description" class="mt-0.5 text-sm text-neutral-500">
          {{ description }}
        </p>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="pl-14">
      <slot />
    </div>

    <!-- 锁定遮罩 -->
    <Transition name="fade">
      <div
        v-if="!unlocked"
        class="absolute inset-0 flex items-center justify-center z-10"
      >
        <div
          class="glass px-6 py-3 rounded-xl flex items-center gap-2.5 text-neutral-500 text-sm font-medium shadow-sm"
        >
          <Lock class="w-4 h-4" :stroke-width="1.5" />
          <span>请先完成上方选择</span>
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
</style>
