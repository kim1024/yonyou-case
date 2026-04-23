<script setup lang="ts">
import type { Enterprise } from '@/types'

defineProps<{ info: Enterprise | null }>()
</script>

<template>
  <div class="bg-white border rounded-lg p-6">
    <h3 class="text-lg font-semibold text-gray-800 mb-4">企业详情</h3>
    <div v-if="!info" class="text-gray-400 text-sm">请选择一个企业查看详细信息</div>
    <div v-else class="space-y-3 text-sm">
      <div><span class="text-gray-500">企业名称：</span>{{ info.customer_name }}</div>
      <div><span class="text-gray-500">所在省份：</span>{{ info.province }}</div>
      <div><span class="text-gray-500">所在城市：</span>{{ info.city }}</div>
      <div><span class="text-gray-500">所属行业：</span>{{ info.industry }}</div>
      <div v-if="info.company_intro"><span class="text-gray-500">企业简介：</span>{{ info.company_intro }}</div>
      <div v-if="info.yonyou_content"><span class="text-gray-500">用友建设：</span>{{ info.yonyou_content }}</div>
    </div>
  </div>
</template>
