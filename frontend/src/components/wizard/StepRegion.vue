<script setup lang="ts">
defineProps<{ regions: string[]; loading: boolean }>()
const emit = defineEmits<{ select: [region: string] }>()
</script>

<template>
  <div>
    <h2 class="text-xl font-semibold text-gray-800 mb-6">选择省份</h2>
    <div v-if="loading" class="text-gray-500">加载中...</div>
    <div v-else class="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
      <button
        v-for="region in regions"
        :key="region"
        class="p-3 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition text-center"
        @click="emit('select', region)"
      >
        <div class="text-sm font-medium text-gray-700">{{ region }}</div>
      </button>
    </div>
  </div>
</template>
