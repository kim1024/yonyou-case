<script setup lang="ts">
defineProps<{
  currentStep: number
}>()

const emit = defineEmits<{
  goToStep: [step: number]
}>()

const steps = [
  { num: 1, label: '专业方向' },
  { num: 2, label: '选择行业' },
  { num: 3, label: '选择省份' },
  { num: 4, label: '选择企业' },
  { num: 5, label: '课时安排' },
]

function handleClick(num: number, currentStep: number) {
  if (num < currentStep) {
    emit('goToStep', num)
  }
}
</script>

<template>
  <div class="flex items-center justify-start gap-0">
    <template v-for="(step, index) in steps" :key="step.num">
      <!-- Step node -->
      <div class="flex flex-col items-center gap-2 group">
        <button
          :class="[
            step.num < currentStep
              ? 'w-9 h-9 rounded-full bg-emerald-500 text-white cursor-pointer hover:scale-110 shadow-sm'
              : step.num === currentStep
                ? 'w-10 h-10 rounded-full bg-indigo-500 text-white ring-4 ring-indigo-100 shadow-md'
                : 'w-9 h-9 rounded-full bg-gray-200 text-gray-400',
          ]"
          class="flex items-center justify-center text-sm font-medium transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400"
          @click="handleClick(step.num, currentStep)"
        >
          <svg v-if="step.num < currentStep" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
          <span v-else>{{ step.num }}</span>
        </button>
        <span
          class="text-xs font-medium whitespace-nowrap transition-colors duration-200 hidden sm:block"
          :class="step.num < currentStep ? 'text-emerald-600' : step.num === currentStep ? 'text-indigo-600' : 'text-gray-400'"
        >
          {{ step.label }}
        </span>
      </div>

      <!-- Connector line (between nodes, not after last) -->
      <div
        v-if="index < steps.length - 1"
        class="flex-1 h-0.5 mx-2 sm:mx-3 mt-[-1.25rem] sm:mt-0 transition-colors duration-300 rounded-full"
        :class="step.num < currentStep ? 'bg-emerald-500' : 'bg-gray-200'"
      />
    </template>
  </div>
</template>
