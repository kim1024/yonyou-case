<script setup lang="ts">
import { Clock } from 'lucide-vue-next'

defineProps<{ hours: number[]; selectedHour: number | string | null; loading: boolean }>()
const emit = defineEmits<{ select: [hour: number] }>()
</script>

<template>
  <div>
    <!-- 骨架屏 -->
    <div v-if="loading || hours.length === 0" class="grid grid-cols-2 md:grid-cols-4 gap-2">
      <div
        v-for="i in 4"
        :key="i"
        class="h-24 rounded-xl bg-neutral-100 animate-pulse flex flex-col items-center justify-center gap-1.5"
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
        :key="hour"
        class="group relative h-24 rounded-xl text-center transition-all duration-150 cursor-pointer border"
        :class="
          selectedHour == hour
            ? 'bg-primary-50 border-primary-400'
            : 'bg-white border-neutral-200 hover:border-neutral-300 hover:bg-neutral-50'
        "
        @click="emit('select', hour)"
      >
        <!-- 选中态底部指示条 -->
        <span
          v-if="selectedHour == hour"
          class="absolute bottom-0 left-3 right-3 h-[2px] rounded-full bg-primary-500"
        />

        <!-- 图标 -->
        <Clock
          class="w-4 h-4 mx-auto mt-3 mb-1"
          :class="selectedHour == hour ? 'text-primary-500' : 'text-neutral-300 group-hover:text-neutral-400'"
          :stroke-width="1.5"
        />

        <!-- 数字 -->
        <div
          class="text-xl font-bold tracking-tight leading-none"
          :class="selectedHour == hour ? 'text-primary-600' : 'text-neutral-500 group-hover:text-neutral-600'"
        >
          {{ hour }}
        </div>

        <!-- 单位 -->
        <div
          class="text-[11px] font-medium mt-1"
          :class="selectedHour == hour ? 'text-primary-500' : 'text-neutral-400'"
        >
          课时
        </div>
      </button>
    </div>
  </div>
</template>
