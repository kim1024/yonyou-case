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


const items: SummaryItem[] = [
  { icon: GraduationCap, label: '专业', get value() { return props.major } },
  { icon: Factory, label: '行业', get value() { return props.industry } },
  { icon: MapPin, label: '地区', get value() { return props.region } },
  { icon: Building2, label: '企业', get value() { return props.enterprise } },
  { icon: Clock, label: '课时', get value() { return props.hour ? `${props.hour}h` : null } },
]
</script>

<template>
  <div class="sticky top-0 z-40 ai-summary-bar">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-12 flex items-center justify-between gap-4">
      <div class="flex items-center gap-2 overflow-x-auto no-scrollbar">
        <div
          v-for="item in items"
          :key="item.label"
          :class="[
            'ai-chip',
            item.value ? 'ai-chip-active' : 'ai-chip-empty',
          ]"
        >
          <component :is="item.icon" class="w-3.5 h-3.5" :stroke-width="1.5" />
          <span>{{ item.label }}:</span>
          <span v-if="item.value" class="max-w-[120px] truncate">{{ item.value }}</span>
          <span v-else>未选</span>
        </div>
      </div>
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

.ai-summary-bar {
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(24px) saturate(1.5);
  -webkit-backdrop-filter: blur(24px) saturate(1.5);
  border-bottom: 1px solid rgba(192,57,43,0.06);
}

.ai-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 100px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  transition: all 0.3s ease;
}

.ai-chip-active {
  background: linear-gradient(135deg, rgba(192,57,43,0.07), rgba(212,160,106,0.06));
  color: #991B1B;
  border: 1px solid rgba(192,57,43,0.12);
  box-shadow: 0 0 12px rgba(192,57,43,0.04);
}

.ai-chip-empty {
  background: rgba(245,243,240,0.6);
  color: #A8A29E;
  border: 1px dashed rgba(168,162,158,0.3);
}
</style>
