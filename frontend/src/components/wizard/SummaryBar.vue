<script setup lang="ts">
import {
  GraduationCap,
  Factory,
  MapPin,
  Building2,
  Clock,
} from 'lucide-vue-next'
import type { Component } from 'vue'

interface SummaryItem {
  icon: Component
  label: string
  value: string | number | null
}

const props = defineProps<{
  major: string | null
  industry: string | null
  region: string | null
  enterprise: string | null
  hour: number | null
}>()

const emit = defineEmits<{
  reset: []
}>()

const items: SummaryItem[] = [
  { icon: GraduationCap, label: '专业', get value() { return props.major } },
  { icon: Factory, label: '行业', get value() { return props.industry } },
  { icon: MapPin, label: '地区', get value() { return props.region } },
  { icon: Building2, label: '企业', get value() { return props.enterprise } },
  { icon: Clock, label: '课时', get value() { return props.hour ? `${props.hour}h` : null } },
]
</script>

<template>
  <div class="sticky top-0 z-40 glass border-b border-white/20">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-12 flex items-center justify-between gap-4">
      <!-- 左侧：摘要芯片 -->
      <div class="flex items-center gap-2 overflow-x-auto no-scrollbar">
        <div
          v-for="item in items"
          :key="item.label"
          :class="[
            'inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-all duration-300',
            item.value
              ? 'bg-primary-50 text-primary-700 ring-1 ring-primary-200/60'
              : 'bg-neutral-100 text-neutral-400 border border-dashed border-neutral-300',
          ]"
        >
          <component :is="item.icon" class="w-3.5 h-3.5" :stroke-width="1.5" />
          <span>{{ item.label }}:</span>
          <span v-if="item.value" class="max-w-[120px] truncate">{{ item.value }}</span>
          <span v-else>未选</span>
        </div>
      </div>

      <!-- 右侧：重新开始 -->
      <button
        class="shrink-0 text-xs text-neutral-400 hover:text-neutral-700 transition-colors duration-200 font-medium"
        @click="emit('reset')"
      >
        重新开始
      </button>
    </div>
  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
