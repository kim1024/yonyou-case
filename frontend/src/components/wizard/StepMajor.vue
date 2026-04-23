<script setup lang="ts">
defineProps<{ majors: string[]; loading: boolean }>()
const emit = defineEmits<{ select: [major: string] }>()
</script>

<template>
  <div>
    <h2 class="text-xl font-semibold text-gray-800 mb-6">选择专业方向</h2>
    <div v-if="loading" class="text-gray-500">加载中...</div>
    <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <button
        v-for="major in majors"
        :key="major"
        class="p-6 border-2 border-gray-200 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition text-center"
        @click="emit('select', major)"
      >
        <div class="text-lg font-medium text-gray-800">{{ major }}</div>
      </button>
    </div>
  </div>
</template>
