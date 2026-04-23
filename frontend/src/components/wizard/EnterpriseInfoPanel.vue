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
    class="bg-white border border-neutral-200 rounded-xl p-6 flex flex-col items-center justify-center min-h-[140px]"
  >
    <Building2 class="w-10 h-10 text-neutral-200 mb-3" :stroke-width="1" />
    <p class="text-neutral-400 text-center text-sm">请从上方选择一家企业<br />查看详细信息</p>
  </div>

  <!-- 加载中状态 -->
  <div
    v-else-if="loading"
    class="bg-white border border-neutral-200 rounded-xl p-4 min-h-[140px]"
  >
    <div class="flex items-center gap-3 mb-3 pb-3 border-b border-neutral-100">
      <div class="skeleton w-8 h-8 rounded-lg" />
      <div class="flex-1 space-y-1.5">
        <div class="skeleton h-4 w-32" />
        <div class="skeleton h-3 w-24" />
      </div>
    </div>
    <div class="space-y-2">
      <div class="skeleton h-3 w-20 mb-1" />
      <div class="skeleton h-4 w-full" />
      <div class="skeleton h-4 w-3/4" />
    </div>
  </div>

  <!-- 已选中时（展示详情） -->
  <div
    v-else-if="info"
    class="bg-white border border-neutral-200 rounded-xl p-4 transition-border-color duration-200 hover:border-neutral-300"
  >
    <!-- 头部：紧凑单行 -->
    <div class="flex items-center gap-3 mb-3 pb-3 border-b border-neutral-100">
      <div class="shrink-0 w-8 h-8 rounded-lg bg-primary-50 flex items-center justify-center">
        <Building2 class="w-4 h-4 text-primary-500" />
      </div>
      <div class="flex-1 min-w-0">
        <h3 class="text-sm font-bold text-neutral-900 truncate">{{ info.customer_name }}</h3>
        <div class="flex items-center gap-2 mt-0.5 text-xs text-neutral-500">
          <span class="inline-flex items-center gap-1">
            <MapPin class="w-3 h-3" :stroke-width="1.5" />
            {{ info.province }} · {{ info.city }}
          </span>
          <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-primary-50 text-primary-700">
            {{ info.industry }}
          </span>
        </div>
      </div>
    </div>

    <!-- 企业简介（次要信息） -->
    <div v-if="info.company_intro" class="mb-3">
      <h4 class="text-xs font-semibold text-neutral-900 mb-1.5 flex items-center gap-1.5 uppercase tracking-wide">
        <BookOpen class="w-3 h-3 text-neutral-400" :stroke-width="1.5" />
        关于该企业
      </h4>
      <p class="text-xs text-neutral-500 leading-relaxed bg-neutral-50 rounded-lg p-3">{{ info.company_intro }}</p>
    </div>

    <!-- 用友可提供的内容（突出显示） -->
    <div
      v-if="info.yonyou_content"
      class="bg-gradient-to-r from-primary-50 to-info-light border border-primary-200/50 rounded-xl p-3.5 relative overflow-hidden"
    >
      <!-- 左侧蓝色竖条 -->
      <div class="absolute left-0 top-3 bottom-3 w-[3px] bg-primary-500 rounded-full" />

      <h4 class="text-xs font-bold uppercase tracking-wider text-primary-600 flex items-center gap-1.5 mb-1.5 pl-1">
        <Sparkles class="w-3.5 h-3.5 text-primary-500" :stroke-width="1.5" />
        用友可提供的内容
      </h4>
      <p class="text-sm text-neutral-700 font-medium leading-relaxed pl-1">{{ info.yonyou_content }}</p>
    </div>
  </div>
</template>
