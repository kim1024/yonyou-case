<script setup lang="ts">
defineProps<{ industries: string[]; loading: boolean }>()
const emit = defineEmits<{ select: [industry: string] }>()
</script>

<template>
  <div>
    <h2 class="text-xl font-semibold text-gray-800 mb-6">选择行业</h2>
    <div v-if="loading" class="text-gray-500">加载中...</div>
    <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
      <button
        v-for="industry in industries"
        :key="industry"
        class="p-4 border-2 border-gray-200 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition text-center"
        @click="emit('select', industry)"
      >
        <div class="text-sm font-medium text-gray-700">{{ industry }}</div>
      </button>
    </div>
  </div>
</template>
