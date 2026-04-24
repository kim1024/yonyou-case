<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { Building2, BarChart3, GraduationCap, Briefcase, MapPin, Clock, LogOut, LayoutDashboard, Bot, FileStack, ChevronLeft, ChevronRight } from 'lucide-vue-next'

const router = useRouter()
const { username, logout } = useAuth()
const collapsed = ref(false)

function handleLogout() {
  logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen flex" style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);">
    <!-- 侧边栏 -->
    <aside
      class="sidebar-root flex flex-col fixed inset-y-0 left-0 z-30"
      :style="{ width: collapsed ? '72px' : '256px' }"
      style="background: linear-gradient(180deg, #141425 0%, #0F0F1A 100%);"
    >
      <!-- 品牌区 -->
      <div
        class="border-b flex items-center"
        :class="collapsed ? 'justify-center px-0 py-7' : 'px-6 py-7'"
        style="border-color: var(--sidebar-dark-border);"
      >
        <div class="flex items-center gap-3 min-w-0">
          <div
            class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
            style="background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);"
          >
            <LayoutDashboard :size="16" color="#fff" :stroke-width="2" />
          </div>
          <div v-show="!collapsed" class="sidebar-text overflow-hidden whitespace-nowrap">
            <h1 class="text-sm font-bold text-white tracking-tight" style="font-family: var(--font-display);">产业案例管理</h1>
            <p class="text-xs mt-0.5" style="color: var(--sidebar-dark-text);">用友教育</p>
          </div>
        </div>
      </div>

      <!-- 导航 -->
      <nav class="flex-1 py-4 overflow-y-auto overflow-x-hidden">
        <div v-show="!collapsed" class="px-4 mb-2">
          <p class="text-xs font-semibold uppercase tracking-wider px-2 mb-2" style="color: rgba(255,255,255,0.25);">导航</p>
        </div>

        <router-link
          to="/admin/analytics"
          class="sidebar-nav-item"
          :class="{ 'is-active': $route.name === 'analytics', 'is-collapsed': collapsed }"
        >
          <BarChart3 :size="18" :stroke-width="1.8" />
          <span v-show="!collapsed" class="sidebar-text">统计面板</span>
        </router-link>

        <router-link
          to="/admin/enterprises"
          class="sidebar-nav-item"
          :class="{ 'is-active': $route.name === 'enterprises', 'is-collapsed': collapsed }"
        >
          <Building2 :size="18" :stroke-width="1.8" />
          <span v-show="!collapsed" class="sidebar-text">企业管理</span>
        </router-link>

        <router-link
          to="/admin/majors"
          class="sidebar-nav-item"
          :class="{ 'is-active': $route.name === 'majors', 'is-collapsed': collapsed }"
        >
          <GraduationCap :size="18" :stroke-width="1.8" />
          <span v-show="!collapsed" class="sidebar-text">专业管理</span>
        </router-link>

        <router-link
          to="/admin/industries"
          class="sidebar-nav-item"
          :class="{ 'is-active': $route.name === 'industries', 'is-collapsed': collapsed }"
        >
          <Briefcase :size="18" :stroke-width="1.8" />
          <span v-show="!collapsed" class="sidebar-text">行业管理</span>
        </router-link>

        <router-link
          to="/admin/regions"
          class="sidebar-nav-item"
          :class="{ 'is-active': $route.name === 'regions', 'is-collapsed': collapsed }"
        >
          <MapPin :size="18" :stroke-width="1.8" />
          <span v-show="!collapsed" class="sidebar-text">地区管理</span>
        </router-link>

        <router-link
          to="/admin/hours"
          class="sidebar-nav-item"
          :class="{ 'is-active': $route.name === 'hours', 'is-collapsed': collapsed }"
        >
          <Clock :size="18" :stroke-width="1.8" />
          <span v-show="!collapsed" class="sidebar-text">课时管理</span>
        </router-link>

        <router-link
          to="/admin/llm"
          class="sidebar-nav-item"
          :class="{ 'is-active': $route.name === 'llm', 'is-collapsed': collapsed }"
        >
          <Bot :size="18" :stroke-width="1.8" />
          <span v-show="!collapsed" class="sidebar-text">大模型管理</span>
        </router-link>

        <router-link
          to="/admin/plans"
          class="sidebar-nav-item"
          :class="{ 'is-active': $route.name === 'plans', 'is-collapsed': collapsed }"
        >
          <FileStack :size="18" :stroke-width="1.8" />
          <span v-show="!collapsed" class="sidebar-text">方案管理</span>
        </router-link>
      </nav>

      <!-- 浮动收缩/展开按钮 -->
      <button
        class="sidebar-toggle-handle absolute right-0 top-1/2 z-40 flex items-center justify-center
               w-6 h-6 rounded-md border cursor-pointer
               transition-all duration-200 ease-out"
        :style="{
          transform: 'translateY(-50%) translateX(50%)',
          background: '#0F0F1A',
          borderColor: 'rgba(255,255,255,0.10)',
          color: 'rgba(255,255,255,0.50)'
        }"
        :title="collapsed ? '展开导航' : '收缩导航'"
        @click="collapsed = !collapsed"
      >
        <ChevronLeft v-if="!collapsed" :size="14" :stroke-width="2" />
        <ChevronRight v-else :size="14" :stroke-width="2" />
      </button>

      <!-- 底部用户区 -->
      <div class="px-4 py-4 border-t" style="border-color: var(--sidebar-dark-border);">
        <div
          class="flex items-center justify-between"
          :class="collapsed ? 'flex-col gap-2 px-0' : 'flex-row px-2'"
        >
          <div class="flex items-center gap-2 min-w-0" :class="collapsed ? 'justify-center' : ''">
            <div
              class="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-semibold"
              style="background: rgba(255,255,255,0.08); color: rgba(255,255,255,0.7);"
            >
              {{ (username || '?').charAt(0).toUpperCase() }}
            </div>
            <span v-show="!collapsed" class="sidebar-text text-sm truncate" style="color: var(--sidebar-dark-text);">
              {{ username }}
            </span>
          </div>
          <button
            v-show="!collapsed"
            class="logout-btn flex items-center justify-center w-8 h-8 rounded-lg flex-shrink-0"
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
      class="flex-1 p-8 animate-fade-up"
      :style="{ marginLeft: collapsed ? '72px' : '256px' }"
      style="min-height: 100vh; transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1);"
    >
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.sidebar-root {
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-text {
  transition: opacity 0.2s ease;
}

.sidebar-nav-item.is-collapsed {
  justify-content: center;
  padding: 10px;
  margin: 0 4px;
}

.sidebar-nav-item.is-collapsed::before {
  left: -4px;
}

.sidebar-toggle-handle:hover {
  background-color: rgba(99, 102, 241, 0.30) !important;
  color: rgba(255, 255, 255, 0.90) !important;
  border-color: rgba(99, 102, 241, 0.40) !important;
  transform: translateY(-50%) translateX(50%) scale(1.1);
}

.sidebar-toggle-handle:active {
  background-color: rgba(99, 102, 241, 0.45) !important;
  color: #FFFFFF !important;
  border-color: rgba(99, 102, 241, 0.50) !important;
  transform: translateY(-50%) translateX(50%) scale(0.95);
}

.logout-btn {
  transition: background-color 0.15s ease;
}

.logout-btn:hover {
  background-color: rgba(255, 255, 255, 0.08);
}
</style>
