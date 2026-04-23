<script setup lang="ts">
import { Clock } from 'lucide-vue-next'

defineProps<{ hours: number[]; selectedHour: number | string | null }>()
const emit = defineEmits<{ select: [hour: number] }>()

function weekText(hour: number): string {
  const weeks = Math.round(hour / 2)
  return `约 ${weeks} 周`
}
</script>

<template>
  <div>
    <!-- 标题区域 -->
    <div class="mb-8">
      <span class="text-sm font-bold text-indigo-500 tracking-wide uppercase">05</span>
      <h2 class="mt-1 text-2xl font-bold text-gray-900">课时安排</h2>
      <p class="mt-1 text-sm text-gray-500">选择课程总课时数，不同课时数对应不同的教学深度</p>
    </div>

    <!-- 课时卡片 -->
    <div v-if="hours.length > 0" class="grid grid-cols-2 md:grid-cols-4 gap-6">
      <button
        v-for="hour in hours"
        :key="hour"
        class="p-8 text-center rounded-[10px] transition-all duration-200 cursor-pointer relative overflow-hidden"
        :class="
          selectedHour == hour
            ? 'bg-indigo-50 border-2 border-indigo-500 shadow-[0_0_0_3px_rgba(99,102,241,0.15)] -translate-y-0.5'
            : 'bg-white border border-gray-200 hover:border-indigo-400 hover:shadow-md hover:-translate-y-0.5'
        "
        @click="emit('select', hour)"
      >
        <!-- 选中态顶部装饰条 -->
        <div
          v-if="selectedHour == hour"
          class="absolute top-0 left-4 right-4 h-[3px] bg-indigo-500 rounded-full"
        />

        <!-- Clock 图标 -->
        <Clock
          :class="
            selectedHour == hour
              ? 'w-8 h-8 text-indigo-400 mx-auto mb-3'
              : 'w-8 h-8 text-gray-300 mx-auto mb-3 transition-colors'
          "
        />

        <!-- 超大数字 -->
        <div
          class="font-mono text-4xl font-bold"
          :class="selectedHour == hour ? 'text-indigo-600' : 'text-gray-300 hover:text-gray-600 transition-colors'"
        >
          {{ hour }}
        </div>

        <!-- 单位 -->
        <div class="text-sm text-gray-400 mt-1">课时</div>

        <!-- 约周数 -->
        <div class="text-xs text-gray-500 mt-3">{{ weekText(hour) }}</div>
      </button>
    </div>

    <!-- 骨架屏加载态 -->
    <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-6">
      <div
        v-for="i in 4"
        :key="i"
        class="p-8 rounded-[10px] bg-gray-50 border border-gray-100 animate-pulse"
      >
        <div class="w-8 h-8 bg-gray-200 rounded mx-auto mb-3" />
        <div class="w-16 h-10 bg-gray-200 rounded mx-auto mb-1" />
        <div class="w-10 h-3 bg-gray-200 rounded mx-auto mt-1" />
        <div class="w-12 h-3 bg-gray-100 rounded mx-auto mt-3" />
      </div>
    </div>
  </div>
</template>
