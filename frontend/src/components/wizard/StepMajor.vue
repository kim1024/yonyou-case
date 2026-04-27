<script setup lang="ts">
import { ref, type Component } from 'vue'
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
          selectedMajor === major.name
            ? 'relative flex items-center gap-3 p-3.5 rounded-xl cursor-pointer bg-gradient-to-br from-[rgba(192,57,43,0.04)] to-[rgba(212,160,106,0.04)] border border-[rgba(192,57,43,0.18)] shadow-[0_0_20px_rgba(192,57,43,0.06),0_4px_16px_rgba(192,57,43,0.04)] transition-all duration-300'
            : 'flex items-center gap-3 p-3.5 rounded-xl cursor-pointer bg-white/60 border border-neutral-200/60 backdrop-blur-sm transition-all duration-300 hover:border-[rgba(192,57,43,0.15)] hover:shadow-[0_4px_20px_rgba(192,57,43,0.06)] hover:-translate-y-0.5',
          poppedKey === major.name ? 'animate-select-pop' : '',
        ]"
        @click="handleSelect(major)"
      >
        <!-- 图标 -->
        <div
          :class="[
            'shrink-0 w-10 h-10 rounded-xl flex items-center justify-center transition-colors duration-200',
            selectedMajor === major.name ? 'bg-gradient-to-br from-[rgba(192,57,43,0.10)] to-[rgba(212,160,106,0.08)]' : 'bg-neutral-100',
          ]"
        >
          <component
            :is="resolveIcon(major.icon)"
            :class="[
              'w-5 h-5 transition-colors duration-200',
              selectedMajor === major.name ? 'text-[#C0392B]' : 'text-neutral-400',
            ]"
            :stroke-width="1.5"
          />
        </div>

        <!-- 文字 -->
        <div class="flex-1 min-w-0 text-left">
          <div
            :class="[
              'text-sm font-semibold transition-colors duration-200',
              selectedMajor === major.name ? 'text-[#991B1B]' : 'text-neutral-900',
            ]"
          >
            {{ major.name }}
          </div>
          <p class="text-xs mt-0.5 leading-relaxed text-neutral-400 line-clamp-1">
            {{ major.description }}
          </p>
        </div>

        <!-- Selection accent bar -->
        <div
          v-if="selectedMajor === major.name"
          class="absolute bottom-0 left-3 right-3 h-[2px] rounded-full"
          style="background: linear-gradient(90deg, transparent, #C0392B, #D4A06A, transparent);"
        />
      </button>
    </div>
  </div>
</template>
