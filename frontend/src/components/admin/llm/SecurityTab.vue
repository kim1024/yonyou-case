<script setup lang="ts">
import { Check, Info, Loader2 } from 'lucide-vue-next'
import type { SecuritySettingItem } from '@/composables/useSecuritySettings'

defineProps<{
  securitySettings: SecuritySettingItem[]
  securityLoading: boolean
  securitySaving: boolean
  securityHasChanges: boolean
}>()

const emit = defineEmits<{
  'clamp-value': [item: SecuritySettingItem]
  'save': []
}>()
</script>

<template>
  <div
    class="gradient-card"
    style="animation: fadeUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) both"
  >
    <!-- Skeleton Loading -->
    <div v-if="securityLoading" class="p-6 space-y-8">
      <div v-for="i in 4" :key="i" class="flex items-center gap-6">
        <div class="flex-1 space-y-2">
          <div class="skeleton h-4 w-40 rounded" />
          <div class="skeleton h-3 w-64 rounded" />
        </div>
        <div class="skeleton h-10 w-28 rounded-lg" />
      </div>
    </div>

    <!-- 设置表单 -->
    <div v-else class="divide-y divide-neutral-100">
      <div
        v-for="(item, index) in securitySettings"
        :key="item.key"
        class="flex flex-col sm:flex-row sm:items-center gap-4 p-6"
        :style="{ animationDelay: `${index * 60}ms` }"
        style="animation: fadeUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) both"
      >
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <h3 class="text-sm font-semibold text-neutral-800">{{ item.label }}</h3>
          </div>
          <p class="text-xs text-neutral-500 mt-1 leading-relaxed">{{ item.description }}</p>
          <p class="text-[11px] text-neutral-400 mt-1.5">
            允许范围：<span class="font-medium text-neutral-500">{{ item.min }}</span>
            ~
            <span class="font-medium text-neutral-500">{{ item.max }}</span>
            {{ item.unit }}
          </p>
        </div>
        <div class="flex items-center gap-2 flex-shrink-0">
          <div class="relative">
            <input
              v-model.number="item.value"
              type="number"
              :min="item.min"
              :max="item.max"
              class="input-macos w-28 text-center tabular-nums"
              @input="emit('clamp-value', item)"
            />
          </div>
          <span
            class="inline-block px-2.5 py-1.5 rounded-lg text-xs font-medium bg-neutral-100 text-neutral-600 whitespace-nowrap"
          >
            {{ item.unit }}
          </span>
        </div>
      </div>
    </div>

    <!-- 底部操作栏 -->
    <div
      v-if="securitySettings.length > 0"
      class="flex items-center justify-between px-6 py-4 border-t border-neutral-100"
    >
      <div class="flex items-center gap-2 text-xs text-neutral-400">
        <Info :size="14" :stroke-width="1.8" />
        <span>修改后点击保存即刻生效，无需重启服务</span>
      </div>
      <button
        class="btn-primary"
        :disabled="securitySaving || !securityHasChanges"
        @click="emit('save')"
      >
        <Loader2 v-if="securitySaving" :size="15" class="animate-spin" />
        <Check v-else :size="15" :stroke-width="2.5" />
        {{ securitySaving ? '保存中...' : '保存配置' }}
      </button>
    </div>
  </div>
</template>
