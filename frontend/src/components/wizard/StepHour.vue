<script setup lang="ts">
defineProps<{ hours: number[]; selectedHour: number | string | null }>()
const emit = defineEmits<{ select: [hour: number] }>()
</script>

<template>
  <div>
    <h2 class="text-xl font-semibold text-gray-800 mb-6">选择课时</h2>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <button
        v-for="hour in hours"
        :key="hour"
        class="p-6 border-2 rounded-xl transition text-center"
        :class="selectedHour == hour ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-500 hover:bg-blue-50'"
        @click="emit('select', hour)"
      >
        <div class="text-2xl font-bold" :class="selectedHour == hour ? 'text-blue-600' : 'text-gray-800'">{{ hour }}</div>
        <div class="text-sm text-gray-500">课时</div>
      </button>
    </div>
  </div>
</template>
