<script setup lang="ts">
import { Building2, MapPin, BookOpen, Sparkles } from 'lucide-vue-next'
import type { Enterprise } from '@/types'

defineProps<{
  info: Enterprise | null
  loading: boolean
}>()
</script>

<template>
  <!-- 未选中时（占位态） -->
  <div
    v-if="!info && !loading"
    class="bg-white border border-gray-200 rounded-[10px] p-8 flex flex-col items-center justify-center min-h-[400px]"
  >
    <Building2 class="w-16 h-16 text-gray-200 mb-4" />
    <p class="text-gray-400 text-center">请从左侧选择一家企业<br />查看详细信息</p>
  </div>

  <!-- 加载中状态 -->
  <div
    v-else-if="loading"
    class="bg-white border border-gray-200 rounded-[10px] p-6 min-h-[400px]"
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
    class="bg-white border border-gray-200 rounded-[10px] p-6 min-h-[400px]"
  >
    <!-- 头部：图标 + 企业名 + 位置 -->
    <div class="text-center mb-6 pb-6 border-b border-gray-100">
      <div class="w-14 h-14 rounded-full bg-indigo-50 flex items-center justify-center mx-auto mb-3">
        <Building2 class="w-7 h-7 text-indigo-500" />
      </div>
      <h3 class="text-xl font-bold text-gray-900">{{ info.customer_name }}</h3>
      <div class="flex items-center justify-center gap-2 mt-2 text-sm text-gray-500">
        <MapPin class="w-4 h-4" />
        <span>{{ info.province }} · {{ info.city }}</span>
      </div>
      <div class="mt-2">
        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-indigo-50 text-indigo-700">
          {{ info.industry }}
        </span>
      </div>
    </div>

    <!-- 企业简介 -->
    <div v-if="info.company_intro" class="mb-6">
      <h4 class="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
        <BookOpen class="w-4 h-4 text-indigo-500" />
        关于该企业
      </h4>
      <p class="text-sm text-gray-600 leading-relaxed">{{ info.company_intro }}</p>
    </div>

    <!-- 用友可提供的内容 -->
    <div v-if="info.yonyou_content">
      <h4 class="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-2">
        <Sparkles class="w-4 h-4 text-indigo-500" />
        用友可提供的内容
      </h4>
      <p class="text-sm text-gray-600 leading-relaxed">{{ info.yonyou_content }}</p>
    </div>
  </div>
</template>

<style scoped>
.skeleton {
  background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%);
  background-size: 200% 100%;
  animation: shimmer 1.8s ease-in-out infinite;
  border-radius: 6px;
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
