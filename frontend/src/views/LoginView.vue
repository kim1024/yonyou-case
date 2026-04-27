<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const route = useRoute()
const { login, loading, error } = useAuth()

const username = ref('')
const password = ref('')

async function handleLogin() {
  const success = await login(username.value, password.value)
  if (success) {
    const redirect = (route.query.redirect as string) || '/admin/analytics'
    const safeRedirect = redirect.startsWith('/') && !redirect.startsWith('//')
      ? redirect
      : '/admin/analytics'
    router.push(safeRedirect)
  }
}
</script>

<template>
  <div
    class="min-h-screen flex items-center justify-center relative overflow-hidden"
    style="background: linear-gradient(135deg, #0F0F1A 0%, #1E1B4B 50%, #0F0F1A 100%);"
  >
    <!-- 背景装饰 -->
    <div class="absolute inset-0 pointer-events-none">
      <div
        class="absolute rounded-full"
        style="
          width: 600px; height: 600px;
          top: -200px; right: -150px;
          background: radial-gradient(circle, rgba(99, 102, 241, 0.12) 0%, transparent 70%);
        "
      />
      <div
        class="absolute rounded-full"
        style="
          width: 500px; height: 500px;
          bottom: -180px; left: -120px;
          background: radial-gradient(circle, rgba(79, 70, 229, 0.10) 0%, transparent 70%);
        "
      />
      <div
        class="absolute rounded-full"
        style="
          width: 300px; height: 300px;
          top: 50%; left: 50%;
          transform: translate(-50%, -50%);
          background: radial-gradient(circle, rgba(99, 102, 241, 0.06) 0%, transparent 70%);
        "
      />
      <!-- 几何装饰线 -->
      <div
        class="absolute"
        style="
          width: 200px; height: 1px;
          top: 30%; left: 10%;
          background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.06) 50%, transparent 100%);
          transform: rotate(-25deg);
        "
      />
      <div
        class="absolute"
        style="
          width: 160px; height: 1px;
          bottom: 25%; right: 12%;
          background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.05) 50%, transparent 100%);
          transform: rotate(15deg);
        "
      />
    </div>

    <!-- 登录卡片 -->
    <div
      class="relative w-full max-w-md mx-4 animate-fade-up"
      style="
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        box-shadow: 0 24px 80px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.06);
      "
    >
      <div class="p-10">
        <!-- 标题 -->
        <div class="text-center mb-10">
          <div
            class="inline-flex items-center justify-center w-12 h-12 rounded-xl mb-5"
            style="background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%); box-shadow: 0 8px 24px rgba(99, 102, 241, 0.3);"
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
              <polyline points="9 22 9 12 15 12 15 22"/>
            </svg>
          </div>
          <h1
            class="text-2xl font-bold tracking-tight"
            style="color: rgba(255,255,255,0.95); font-family: var(--font-display);"
          >用友产业案例教学项目课程定制系统</h1>
          <p class="text-sm mt-2" style="color: rgba(255,255,255,0.4);">用友教育 · 课程定制平台</p>
        </div>

        <!-- 表单 -->
        <form @submit.prevent="handleLogin" class="space-y-5">
          <div>
            <label
              class="block text-xs font-medium mb-2 tracking-wide"
              style="color: rgba(255,255,255,0.5);"
            >用户名</label>
            <input
              v-model="username"
              type="text"
              required
              placeholder="请输入用户名"
              class="login-input w-full px-4 py-3 rounded-xl text-sm"
            />
          </div>
          <div>
            <label
              class="block text-xs font-medium mb-2 tracking-wide"
              style="color: rgba(255,255,255,0.5);"
            >密码</label>
            <input
              v-model="password"
              type="password"
              required
              placeholder="请输入密码"
              class="login-input w-full px-4 py-3 rounded-xl text-sm"
            />
          </div>

          <div
            v-if="error"
            class="text-sm px-4 py-3 rounded-xl"
            style="background: rgba(255, 69, 58, 0.12); color: #FF6B6B; border: 1px solid rgba(255, 69, 58, 0.2);"
          >{{ error }}</div>

          <button
            type="submit"
            :disabled="loading"
            class="login-btn w-full py-3 rounded-xl font-semibold text-sm tracking-wide transition-all duration-200 disabled:opacity-50"
            style="color: white;"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </button>
        </form>

        <!-- 底部 -->
        <div class="text-center mt-8">
          <p class="text-xs" style="color: rgba(255,255,255,0.25);">仅限授权人员访问</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-input {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  font-family: var(--font-body);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.login-input:focus {
  border-color: rgba(99, 102, 241, 0.5);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
  outline: none;
}
.login-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.login-btn {
  background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.login-btn:hover {
  box-shadow: 0 8px 28px rgba(99, 102, 241, 0.45);
  transform: translateY(-1px);
}
.login-btn:active {
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3);
  transform: translateY(0);
}
</style>
