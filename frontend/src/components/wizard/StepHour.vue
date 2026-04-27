<script setup lang="ts">
import { Clock } from 'lucide-vue-next'
import type { WizardHour } from '@/types'

defineProps<{ hours: WizardHour[]; selectedHour: number | string | null; loading: boolean }>()
const emit = defineEmits<{ select: [hour: number] }>()
</script>

<template>
  <div>
    <!-- 骨架屏 -->
    <div v-if="loading || hours.length === 0" class="grid grid-cols-2 md:grid-cols-4 gap-2">
      <div
        v-for="i in 4"
        :key="i"
        class="h-20 md:h-24 rounded-xl bg-neutral-100 animate-pulse flex flex-col items-center justify-center gap-1.5"
      >
        <div class="w-5 h-5 bg-neutral-200 rounded" />
        <div class="w-10 h-6 bg-neutral-200 rounded" />
        <div class="w-6 h-2.5 bg-neutral-200 rounded" />
      </div>
    </div>

    <!-- 课时选择网格 -->
    <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-2">
      <button
        v-for="hour in hours"
        :key="hour.value"
        class="group relative h-20 md:h-24 rounded-xl text-center transition-all duration-300 cursor-pointer border"
        :class="
          selectedHour == hour.value
            ? 'bg-gradient-to-br from-[rgba(192,57,43,0.04)] to-[rgba(212,160,106,0.04)] border-[rgba(192,57,43,0.18)] shadow-[0_0_24px_rgba(192,57,43,0.06)]'
            : 'bg-white/60 backdrop-blur-sm border-neutral-200/60 hover:border-neutral-300 hover:bg-white/80'
        "
        @click="emit('select', hour.value)"
      >
        <!-- 选中态底部指示条 -->
        <span
          v-if="selectedHour == hour.value"
          class="absolute bottom-0 left-3 right-3 h-[2px] rounded-full"
          style="background: linear-gradient(90deg, transparent, #C0392B, #D4A06A, transparent);"
        />

        <!-- 图标 -->
        <Clock
          class="w-4 h-4 mx-auto mt-2 mb-0.5 md:mt-3 md:mb-1"
          :class="selectedHour == hour.value ? 'text-[#C0392B]' : 'text-neutral-300 group-hover:text-neutral-400'"
          :stroke-width="1.5"
        />

        <!-- 数字 -->
        <div
          class="text-lg md:text-xl font-bold tracking-tight leading-none"
          :class="selectedHour == hour.value ? 'text-[#C0392B]' : 'text-neutral-500 group-hover:text-neutral-600'"
        >
          {{ hour.value }}
        </div>

        <!-- 单位 -->
        <div
          class="text-[10px] md:text-[11px] font-medium mt-0.5 md:mt-1"
          :class="selectedHour == hour.value ? 'text-[#C0392B]' : 'text-neutral-400'"
        >
          课时
        </div>
      </button>
    </div>
  </div>
</template>
