<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'

const route = useRoute()
const router = useRouter()

const content = computed(() => {
  const raw = route.query.content as string || ''
  return decodeURIComponent(raw)
})

const source = computed(() => route.query.source as string || 'template')

const html = computed(() => marked.parse(content.value) as string)
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow-sm">
      <div class="max-w-4xl mx-auto px-4 py-6 flex items-center justify-between">
        <h1 class="text-2xl font-bold text-gray-900">课程方案</h1>
        <div class="flex items-center gap-4">
          <span class="text-sm px-3 py-1 rounded-full" :class="source === 'ai' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'">
            {{ source === 'ai' ? 'AI 生成' : '模板生成' }}
          </span>
          <button class="text-sm text-blue-600 hover:text-blue-700" @click="router.push('/')">返回重新定制</button>
        </div>
      </div>
    </header>

    <main class="max-w-4xl mx-auto px-4 py-8">
      <div class="bg-white rounded-xl shadow-sm p-8 prose max-w-none" v-html="html" />
    </main>
  </div>
</template>
