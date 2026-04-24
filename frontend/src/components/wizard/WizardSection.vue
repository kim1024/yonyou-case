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
      'relative py-3 transition-all duration-500',
      unlocked && !generating ? 'opacity-100' : 'opacity-40 pointer-events-none',
    ]"
  >
    <!-- 区域头部 -->
    <div class="mb-2 flex items-start gap-3">
      <!-- 编号徽章 -->
      <div
        :class="[
          'shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-colors duration-300',
          unlocked
            ? 'bg-primary-50 text-primary-600 ring-2 ring-primary-200'
            : 'bg-neutral-100 text-neutral-400',
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

    <!-- 内容区 -->
    <div class="pl-10">
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

    <!-- 生成中遮罩 -->
    <Transition name="fade">
      <div
        v-if="generating"
        class="absolute inset-0 flex items-center justify-center z-10"
      >
        <div
          class="glass px-6 py-3 rounded-xl flex items-center gap-2.5 text-neutral-500 text-sm font-medium shadow-sm"
        >
          <Loader2 class="w-4 h-4 animate-spin" :stroke-width="1.5" />
          <span>正在生成课程方案…</span>
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
