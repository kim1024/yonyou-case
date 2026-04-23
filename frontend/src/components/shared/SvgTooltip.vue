<script setup lang="ts">
defineProps<{
  visible: boolean
  x: number
  y: number
  content: string
}>()
</script>

<template>
  <div
    v-if="visible"
    class="absolute pointer-events-none bg-gray-800 text-white text-xs px-3 py-2 rounded-lg shadow-lg z-50 transition-opacity"
    :style="{ left: x + 'px', top: y + 'px', transform: 'translate(-50%, -120%)' }"
  >
    {{ content }}
    <div class="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-800" />
  </div>
</template>
