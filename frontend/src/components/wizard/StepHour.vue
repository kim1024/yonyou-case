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
        class="p-3 rounded-xl bg-neutral-100 animate-pulse flex flex-col items-center gap-1.5"
      >
        <div class="w-5 h-5 bg-neutral-200 rounded" />
        <div class="w-10 h-5 bg-neutral-200 rounded" />
        <div class="w-6 h-2.5 bg-neutral-200 rounded" />
      </div>
    </div>

    <!-- 课时选择网格 -->
    <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-2">
      <button
        v-for="hour in hours"
        :key="hour"
        class="p-3 rounded-xl text-center transition-all duration-200 cursor-pointer border"
        :class="
          selectedHour == hour
            ? 'bg-primary-50 border-primary-400 shadow-lifted shadow-primary-500/10 -translate-y-0.5'
            : 'bg-white border-neutral-200 hover:border-primary-300 hover:shadow-lifted hover:-translate-y-0.5'
        "
        @click="emit('select', hour)"
      >
        <!-- 图标 -->
        <Clock
          class="w-5 h-5 mx-auto mb-1.5"
          :class="selectedHour == hour ? 'text-primary-500' : 'text-neutral-300 transition-colors duration-200'"
          :stroke-width="1.5"
        />

        <!-- 数字 -->
        <div
          class="text-xl font-bold tracking-tight"
          :class="selectedHour == hour ? 'text-primary-600' : 'text-neutral-400 transition-colors duration-200'"
        >
          {{ hour }}
        </div>

        <!-- 单位 -->
        <div class="text-xs font-medium" :class="selectedHour == hour ? 'text-primary-500' : 'text-neutral-400'">
          课时
        </div>
      </button>
    </div>
  </div>
</template>
