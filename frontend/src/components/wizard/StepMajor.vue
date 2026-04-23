<script setup lang="ts">
import { ref } from 'vue'
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
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
      <div
        v-for="i in 3"
        :key="i"
        class="flex items-center gap-3 p-3 rounded-xl bg-neutral-100 animate-pulse"
      >
        <div class="shrink-0 w-10 h-10 rounded-xl bg-neutral-200" />
        <div class="flex-1 space-y-1.5">
          <div class="skeleton h-4 w-24" />
          <div class="skeleton h-3 w-36" />
        </div>
      </div>
    </div>

    <!-- 专业选项列表 -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
      <button
        v-for="major in majors"
        :key="major.id"
        :class="[
          'flex items-center gap-3 p-3 rounded-xl cursor-pointer',
          'bg-white border transition-all duration-200',
          'hover:border-neutral-300 hover:shadow-lifted hover:-translate-y-0.5',
          selectedMajor === major.name
            ? 'bg-primary-50/60 border-primary-400 shadow-lifted'
            : 'border-neutral-200',
          poppedKey === major.name ? 'animate-select-pop' : '',
        ]"
        @click="handleSelect(major)"
      >
        <!-- 图标 -->
        <div
          :class="[
            'shrink-0 w-10 h-10 rounded-xl flex items-center justify-center transition-colors duration-200',
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

        <!-- 文字 -->
        <div class="flex-1 min-w-0 text-left">
          <div
            :class="[
              'text-sm font-semibold transition-colors duration-200',
              selectedMajor === major.name ? 'text-primary-700' : 'text-neutral-900',
            ]"
          >
            {{ major.name }}
          </div>
          <p class="text-xs mt-0.5 leading-relaxed text-neutral-400 line-clamp-1">
            {{ major.description }}
          </p>
        </div>
      </button>
    </div>
  </div>
</template>
