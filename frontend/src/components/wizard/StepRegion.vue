<script setup lang="ts">
import { ref } from 'vue'
import { MapPin } from 'lucide-vue-next'

defineProps<{ regions: string[]; loading: boolean }>()
const emit = defineEmits<{ select: [region: string] }>()

const poppedKey = ref<string | null>(null)

function handleSelect(region: string) {
  poppedKey.value = region
  setTimeout(() => {
    emit('select', region)
    poppedKey.value = null
  }, 250)
}
</script>

<template>
  <div>
    <div class="mb-8">
      <span class="text-sm font-bold text-indigo-500 tracking-wide uppercase">03</span>
      <h2 class="mt-1 text-2xl font-bold text-gray-900">选择省份</h2>
      <p class="mt-1 text-sm text-gray-500">选择企业所在省份，缩小企业匹配范围</p>
    </div>

    <!-- 骨架屏 -->
    <div v-if="loading" class="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
      <div
        v-for="i in 18"
        :key="i"
        class="bg-white border border-gray-200 rounded-lg p-3"
      >
        <div class="skeleton h-4 w-16 mx-auto" />
      </div>
    </div>

    <!-- 省份网格 -->
    <div
      v-else
      class="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3 max-h-[400px] overflow-y-auto pr-1"
    >
      <button
        v-for="region in regions"
        :key="region"
        :class="[
          'p-3 border border-gray-200 rounded-lg text-center',
          'hover:border-indigo-400 hover:bg-indigo-50 hover:-translate-y-0.5',
          'transition-all duration-200 cursor-pointer flex items-center justify-center gap-1.5',
          poppedKey === region ? 'animate-select-pop' : '',
        ]"
        @click="handleSelect(region)"
      >
        <MapPin class="w-4 h-4 text-indigo-400 shrink-0" :stroke-width="1.5" />
        <span class="text-sm font-medium text-gray-700">{{ region }}</span>
      </button>
    </div>
  </div>
</template>
