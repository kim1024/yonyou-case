<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { Building2, BarChart3, GraduationCap, Briefcase, MapPin, Clock, LogOut, LayoutDashboard } from 'lucide-vue-next'

const router = useRouter()
const { username, logout } = useAuth()

function handleLogout() {
  logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen flex" style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);">
    <!-- 侧边栏 -->
    <aside
      class="w-64 flex flex-col fixed inset-y-0 left-0 z-30"
      style="background: linear-gradient(180deg, #141620 0%, #0F1117 100%);"
    >
      <!-- 品牌区 -->
      <div class="px-6 py-7 border-b" style="border-color: var(--sidebar-dark-border);">
        <div class="flex items-center gap-3">
          <div
            class="w-8 h-8 rounded-lg flex items-center justify-center"
            style="background: linear-gradient(135deg, var(--color-primary-500) 0%, #4F46E5 100%);"
          >
            <LayoutDashboard :size="16" color="#fff" :stroke-width="2" />
          </div>
          <div>
            <h1 class="text-sm font-bold text-white tracking-tight" style="font-family: var(--font-display);">产业案例管理</h1>
            <p class="text-xs mt-0.5" style="color: var(--sidebar-dark-text);">用友教育</p>
          </div>
        </div>
      </div>

      <!-- 导航 -->
      <nav class="flex-1 py-4 overflow-y-auto">
        <div class="px-4 mb-2">
          <p class="text-xs font-semibold uppercase tracking-wider px-2 mb-2" style="color: rgba(255,255,255,0.25);">导航</p>
        </div>

        <router-link
          to="/admin/enterprises"
          class="sidebar-nav-item"
          :class="{ 'is-active': $route.name === 'enterprises' }"
        >
          <Building2 :size="18" :stroke-width="1.8" />
          <span>企业管理</span>
        </router-link>

        <router-link
          to="/admin/analytics"
          class="sidebar-nav-item"
          :class="{ 'is-active': $route.name === 'analytics' }"
        >
          <BarChart3 :size="18" :stroke-width="1.8" />
          <span>统计面板</span>
        </router-link>

        <router-link
          to="/admin/majors"
          class="sidebar-nav-item"
          :class="{ 'is-active': $route.name === 'majors' }"
        >
          <GraduationCap :size="18" :stroke-width="1.8" />
          <span>专业管理</span>
        </router-link>

        <router-link
          to="/admin/industries"
          class="sidebar-nav-item"
          :class="{ 'is-active': $route.name === 'industries' }"
        >
          <Briefcase :size="18" :stroke-width="1.8" />
          <span>行业管理</span>
        </router-link>

        <router-link
          to="/admin/regions"
          class="sidebar-nav-item"
          :class="{ 'is-active': $route.name === 'regions' }"
        >
          <MapPin :size="18" :stroke-width="1.8" />
          <span>地区管理</span>
        </router-link>

        <router-link
          to="/admin/hours"
          class="sidebar-nav-item"
          :class="{ 'is-active': $route.name === 'hours' }"
        >
          <Clock :size="18" :stroke-width="1.8" />
          <span>课时管理</span>
        </router-link>
      </nav>

      <!-- 底部用户区 -->
      <div class="px-4 py-4 border-t" style="border-color: var(--sidebar-dark-border);">
        <div class="flex items-center justify-between px-2">
          <div class="flex items-center gap-2 min-w-0">
            <div
              class="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-semibold"
              style="background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.7);"
            >
              {{ (username || '?').charAt(0).toUpperCase() }}
            </div>
            <span class="text-sm truncate" style="color: var(--sidebar-dark-text);">{{ username }}</span>
          </div>
          <button
            class="logout-btn flex items-center justify-center w-8 h-8 rounded-lg"
            style="color: var(--sidebar-dark-text);"
            title="退出登录"
            @click="handleLogout"
          >
            <LogOut :size="16" :stroke-width="1.8" />
          </button>
        </div>
      </div>
    </aside>

    <!-- 内容区 -->
    <main
      class="flex-1 ml-64 p-8 animate-fade-up"
      style="min-height: 100vh;"
    >
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.logout-btn {
  transition: background-color 0.15s ease;
}
.logout-btn:hover {
  background-color: rgba(255, 255, 255, 0.08);
}
</style>
