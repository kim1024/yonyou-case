<script setup lang="ts">
defineProps<{ hours: number[]; selectedHour: number | string | null; loading: boolean }>()
const emit = defineEmits<{ select: [hour: number] }>()

function weekText(hour: number): string {
  const weeks = Math.round(hour / 2)
  return `约 ${weeks} 周`
}
</script>

<template>
  <div>
    <!-- 骨架屏 -->
    <div v-if="loading || hours.length === 0" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div
        v-for="i in 4"
        :key="i"
        class="p-6 rounded-2xl bg-neutral-100 animate-pulse flex flex-col items-center gap-2"
      >
        <div class="w-10 h-10 bg-neutral-200 rounded-xl" />
        <div class="w-14 h-10 bg-neutral-200 rounded" />
        <div class="w-8 h-3 bg-neutral-200 rounded" />
        <div class="w-12 h-3 bg-neutral-100 rounded mt-1" />
      </div>
    </div>

    <!-- 课时卡片 -->
    <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <button
        v-for="hour in hours"
        :key="hour"
        class="relative p-6 rounded-2xl text-center transition-all duration-200 cursor-pointer border"
        :class="
          selectedHour == hour
            ? 'bg-primary-50 border-primary-400 shadow-md shadow-primary-500/10 -translate-y-0.5'
            : 'bg-white border-neutral-200 hover:border-primary-300 hover:shadow-lifted hover:-translate-y-0.5'
        "
        @click="emit('select', hour)"
      >
        <!-- 选中态顶部装饰条 -->
        <div
          v-if="selectedHour == hour"
          class="absolute top-0 left-6 right-6 h-[3px] bg-primary-500 rounded-full"
        />

        <!-- 超大数字 -->
        <div
          class="text-5xl font-bold tracking-tight"
          :class="selectedHour == hour ? 'text-primary-600' : 'text-neutral-300 transition-colors duration-200'"
        >
          {{ hour }}
        </div>

        <!-- 单位 -->
        <div class="text-sm font-medium mt-1" :class="selectedHour == hour ? 'text-primary-500' : 'text-neutral-400'">
          课时
        </div>

        <!-- 约周数 -->
        <div class="text-xs text-neutral-400 mt-3">{{ weekText(hour) }}</div>
      </button>
    </div>
  </div>
</template>
