<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Factory,
  ShoppingBag,
  Landmark,
  HeartPulse,
  GraduationCap,
  Building,
  UtensilsCrossed,
  Cpu,
  Leaf,
  Building2,
  BarChart3,
  Brain,
  type Component,
} from 'lucide-vue-next'
import type { WizardMajor } from '@/types'

const props = defineProps<{
  majors: WizardMajor[]
  loading: boolean
  selectedMajor: string | null
}>()
const emit = defineEmits<{ select: [name: string, id: number] }>()

const poppedKey = ref<string | null>(null)

// 图标名 → 组件映射
const iconMap: Record<string, Component> = {
  Factory,
  ShoppingBag,
  Landmark,
  HeartPulse,
  GraduationCap,
  Building,
  UtensilsCrossed,
  Cpu,
  Leaf,
  Building2,
  BarChart3,
  Brain,
}

function resolveIcon(iconName: string): Component {
  return iconMap[iconName] ?? Building2
}

function handleSelect(major: WizardMajor) {
  poppedKey.value = major.name
  setTimeout(() => {
    emit('select', major.name, major.id)
    poppedKey.value = null
  }, 250)
}
</script>

<template>
  <div>
    <!-- 骨架屏 -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-3 gap-3">
      <div
        v-for="i in 3"
        :key="i"
        class="card p-3"
      >
        <div class="skeleton w-9 h-9 rounded-full mx-auto mb-2" />
        <div class="skeleton h-4 w-32 mx-auto mb-2" />
        <div class="skeleton h-3 w-48 mx-auto" />
      </div>
    </div>

    <!-- 专业卡片 -->
    <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-3">
      <button
        v-for="major in majors"
        :key="major.id"
        :class="[
          'card p-3 text-center cursor-pointer',
          'hover:shadow-lifted hover:-translate-y-0.5',
          'transition-all duration-200',
          selectedMajor === major.name
            ? 'ring-2 ring-primary-500 bg-primary-50/50 shadow-lifted'
            : '',
          poppedKey === major.name ? 'animate-select-pop' : '',
        ]"
        @click="handleSelect(major)"
      >
        <div
          :class="[
            'w-9 h-9 rounded-xl flex items-center justify-center mx-auto mb-2 transition-colors duration-200',
            selectedMajor === major.name ? 'bg-primary-100' : 'bg-neutral-100',
          ]"
        >
          <component
            :is="resolveIcon(major.icon)"
            :class="[
              'w-5 h-5 transition-colors duration-200',
              selectedMajor === major.name ? 'text-primary-600' : 'text-neutral-400',
            ]"
            :stroke-width="1.5"
          />
        </div>
        <div class="text-sm font-semibold text-neutral-900">{{ major.name }}</div>
        <p class="text-xs mt-1 text-neutral-400">{{ major.description }}</p>
      </button>
    </div>
  </div>
</template>
