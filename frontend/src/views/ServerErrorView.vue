<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ServerCrash, Home } from 'lucide-vue-next'

const router = useRouter()

const stagger = {
  icon: '80ms',
  code: '160ms',
  heading: '280ms',
  subtext: '360ms',
  button: '480ms',
}
</script>

<template>
  <div
    class="relative flex min-h-dvh items-center justify-center overflow-hidden bg-gradient-to-br from-slate-900 via-slate-800 to-rose-950"
  >
    <!-- Ambient blobs -->
    <div
      class="absolute -left-40 -top-40 h-[520px] w-[520px] rounded-full bg-rose-500 opacity-15 blur-[100px]"
    />
    <div
      class="absolute -bottom-32 -right-32 h-[440px] w-[440px] rounded-full bg-pink-500 opacity-15 blur-[100px]"
    />

    <!-- Content -->
    <div class="relative z-10 flex flex-col items-center px-6 text-center">
      <!-- Icon -->
      <div
        class="animate-fade-up mb-6"
        :style="{ animationDelay: stagger.icon }"
      >
        <ServerCrash :size="48" class="text-slate-400" />
      </div>

      <!-- Error code -->
      <h1
        class="error-code animate-fade-up text-6xl font-bold tracking-tighter md:text-8xl"
        :style="{ animationDelay: stagger.code }"
      >
        500
      </h1>

      <!-- Heading -->
      <h2
        class="animate-fade-up mt-4 text-2xl font-semibold text-white"
        :style="{ animationDelay: stagger.heading }"
      >
        服务器开了小差
      </h2>

      <!-- Subtext -->
      <p
        class="animate-fade-up mt-3 max-w-md text-slate-400"
        :style="{ animationDelay: stagger.subtext }"
      >
        服务器遇到了意外错误，请稍后再试。如果问题持续存在，请联系管理员。
      </p>

      <!-- Button -->
      <button
        class="gradient-accent animate-fade-up mt-8 inline-flex items-center gap-2 rounded-lg px-5 py-2.5 text-sm font-semibold shadow-lg shadow-indigo-500/25 transition-all duration-200 hover:-translate-y-0.5"
        :style="{ animationDelay: stagger.button }"
        @click="router.push('/')"
      >
        <Home :size="16" />
        返回首页
      </button>
    </div>
  </div>
</template>

<style scoped>
.error-code {
  background: linear-gradient(to bottom, #ffffff, #e2e8f0, #fda4af);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
</style>
