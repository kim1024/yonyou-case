<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { username, logout } = useAuth()

function handleLogout() {
  logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen bg-gray-100 flex">
    <!-- 侧边栏 -->
    <aside class="w-64 bg-white shadow-sm">
      <div class="p-6">
        <h2 class="text-lg font-bold text-gray-800">管理后台</h2>
      </div>
      <nav class="px-4 space-y-1">
        <router-link
          to="/admin/enterprises"
          class="block px-4 py-3 rounded-lg text-sm font-medium transition"
          :class="$route.name === 'enterprises' ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50'"
        >
          企业管理
        </router-link>
        <router-link
          to="/admin/analytics"
          class="block px-4 py-3 rounded-lg text-sm font-medium transition"
          :class="$route.name === 'analytics' ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50'"
        >
          统计面板
        </router-link>
        <router-link
          to="/admin/majors"
          class="block px-4 py-3 rounded-lg text-sm font-medium transition"
          :class="$route.name === 'majors' ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50'"
        >
          专业管理
        </router-link>
        <router-link
          to="/admin/industries"
          class="block px-4 py-3 rounded-lg text-sm font-medium transition"
          :class="$route.name === 'industries' ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50'"
        >
          行业管理
        </router-link>
        <router-link
          to="/admin/regions"
          class="block px-4 py-3 rounded-lg text-sm font-medium transition"
          :class="$route.name === 'regions' ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50'"
        >
          地区管理
        </router-link>
        <router-link
          to="/admin/hours"
          class="block px-4 py-3 rounded-lg text-sm font-medium transition"
          :class="$route.name === 'hours' ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50'"
        >
          课时管理
        </router-link>
      </nav>
      <div class="absolute bottom-0 w-64 p-4 border-t">
        <div class="flex items-center justify-between">
          <span class="text-sm text-gray-600">{{ username }}</span>
          <button class="text-sm text-red-500 hover:text-red-600" @click="handleLogout">退出</button>
        </div>
      </div>
    </aside>

    <!-- 内容区 -->
    <main class="flex-1 p-8">
      <router-view />
    </main>
  </div>
</template>
