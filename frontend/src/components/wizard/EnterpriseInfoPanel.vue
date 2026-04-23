<script setup lang="ts">
import { Building2, MapPin, BookOpen, Sparkles } from 'lucide-vue-next'
import type { MajorEnterpriseInfo } from '@/types'

defineProps<{
  info: MajorEnterpriseInfo | null
  loading: boolean
}>()
</script>

<template>
  <!-- 未选中时（占位态） -->
  <div
    v-if="!info && !loading"
    class="bg-white border border-neutral-200 rounded-2xl p-8 flex flex-col items-center justify-center min-h-[380px]"
  >
    <Building2 class="w-14 h-14 text-neutral-200 mb-4" :stroke-width="1" />
    <p class="text-neutral-400 text-center text-sm">请从左侧选择一家企业<br />查看详细信息</p>
  </div>

  <!-- 加载中状态 -->
  <div
    v-else-if="loading"
    class="bg-white border border-neutral-200 rounded-2xl p-6 min-h-[380px]"
  >
    <div class="skeleton w-12 h-12 rounded-full mx-auto mb-4" />
    <div class="skeleton w-48 h-6 mx-auto mb-2" />
    <div class="skeleton w-32 h-4 mx-auto mb-6" />
    <div class="space-y-3">
      <div class="skeleton h-4 w-full" />
      <div class="skeleton h-4 w-3/4" />
      <div class="skeleton h-4 w-5/6" />
    </div>
  </div>

  <!-- 已选中时（展示详情） -->
  <div
    v-else-if="info"
    class="bg-white border border-neutral-200 rounded-2xl p-6 min-h-[380px]"
  >
    <!-- 头部：图标 + 企业名 + 位置 -->
    <div class="text-center mb-5 pb-5 border-b border-neutral-100">
      <div class="w-12 h-12 rounded-2xl bg-primary-50 flex items-center justify-center mx-auto mb-3">
        <Building2 class="w-6 h-6 text-primary-500" />
      </div>
      <h3 class="text-lg font-bold text-neutral-900">{{ info.customer_name }}</h3>
      <div class="flex items-center justify-center gap-2 mt-2 text-sm text-neutral-500">
        <MapPin class="w-3.5 h-3.5" :stroke-width="1.5" />
        <span>{{ info.province }} · {{ info.city }}</span>
      </div>
      <div class="mt-2">
        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-50 text-primary-700">
          {{ info.industry }}
        </span>
      </div>
    </div>

    <!-- 企业简介 -->
    <div v-if="info.company_intro" class="mb-5">
      <h4 class="text-xs font-semibold text-neutral-900 mb-2 flex items-center gap-2 uppercase tracking-wide">
        <BookOpen class="w-3.5 h-3.5 text-primary-500" :stroke-width="1.5" />
        关于该企业
      </h4>
      <p class="text-sm text-neutral-600 leading-relaxed">{{ info.company_intro }}</p>
    </div>

    <!-- 用友可提供的内容 -->
    <div v-if="info.yonyou_content">
      <h4 class="text-xs font-semibold text-neutral-900 mb-2 flex items-center gap-2 uppercase tracking-wide">
        <Sparkles class="w-3.5 h-3.5 text-primary-500" :stroke-width="1.5" />
        用友可提供的内容
      </h4>
      <p class="text-sm text-neutral-600 leading-relaxed">{{ info.yonyou_content }}</p>
    </div>
  </div>
</template>

<style scoped>
.skeleton {
  background: linear-gradient(90deg, #f5f5f7 25%, #e5e5ea 50%, #f5f5f7 75%);
  background-size: 200% 100%;
  animation: shimmer 1.8s ease-in-out infinite;
  border-radius: 8px;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
