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
    class="absolute pointer-events-none z-50 tooltip-entrance"
    :style="{ left: x + 'px', top: y + 'px', transform: 'translate(-50%, -120%)' }"
  >
    <div
      class="text-xs px-3 py-2 rounded-lg whitespace-nowrap"
      style="
        background: rgba(15, 17, 23, 0.92);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        color: rgba(255, 255, 255, 0.92);
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35), 0 2px 8px rgba(0, 0, 0, 0.2);
        font-family: var(--font-body);
        letter-spacing: 0.01em;
      "
    >
      {{ content }}
    </div>
    <!-- 箭头 -->
    <div
      class="absolute left-1/2 -translate-x-1/2"
      style="
        top: 100%;
        width: 0; height: 0;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid rgba(15, 17, 23, 0.92);
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.15));
      "
    />
  </div>
</template>

<style scoped>
@keyframes tooltipIn {
  from {
    opacity: 0;
    transform: translate(-50%, -115%);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -120%);
  }
}

.tooltip-entrance {
  animation: tooltipIn 0.15s cubic-bezier(0.16, 1, 0.3, 1) both;
}
</style>
