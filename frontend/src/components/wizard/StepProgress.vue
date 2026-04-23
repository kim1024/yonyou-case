<script setup lang="ts">
defineProps<{ currentStep: number }>()

const steps = [
  { num: 1, label: '专业方向' },
  { num: 2, label: '选择行业' },
  { num: 3, label: '选择省份' },
  { num: 4, label: '选择企业' },
  { num: 5, label: '课时安排' },
]
</script>

<template>
  <div class="flex items-center justify-between">
    <div v-for="step in steps" :key="step.num" class="flex items-center">
      <div
        class="w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium transition"
        :class="step.num <= currentStep ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'"
      >
        {{ step.num }}
      </div>
      <span class="ml-2 text-sm" :class="step.num <= currentStep ? 'text-blue-600 font-medium' : 'text-gray-400'">
        {{ step.label }}
      </span>
      <div v-if="step.num < 5" class="w-12 h-0.5 mx-4" :class="step.num < currentStep ? 'bg-blue-600' : 'bg-gray-200'" />
    </div>
  </div>
</template>
