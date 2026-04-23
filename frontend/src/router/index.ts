import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'wizard',
      component: () => import('@/views/WizardView.vue'),
    },
    {
      path: '/result',
      name: 'result',
      component: () => import('@/views/ResultView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
    },
    {
      path: '/admin',
      component: () => import('@/views/AdminLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: 'enterprises',
          name: 'enterprises',
          component: () => import('@/views/EnterpriseView.vue'),
        },
        {
          path: 'analytics',
          name: 'analytics',
          component: () => import('@/views/AnalyticsView.vue'),
        },
        {
          path: 'majors',
          name: 'majors',
          component: () => import('@/views/MajorView.vue'),
        },
        {
          path: 'industries',
          name: 'industries',
          component: () => import('@/views/IndustryView.vue'),
        },
        {
          path: 'regions',
          name: 'regions',
          component: () => import('@/views/RegionView.vue'),
        },
        {
          path: 'hours',
          name: 'hours',
          component: () => import('@/views/HourView.vue'),
        },
        {
          path: 'llm',
          name: 'llm',
          component: () => import('@/views/LlmView.vue'),
        },
        {
          path: '',
          redirect: '/admin/enterprises',
        },
      ],
    },
  ],
})

// 导航守卫
function isTokenValid(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    // exp 是秒级时间戳
    return typeof payload.exp === 'number' && payload.exp * 1000 > Date.now()
  } catch {
    return false
  }
}

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  if (to.meta.requiresAuth) {
    if (!token || !isTokenValid(token)) {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      next({ name: 'login', query: { redirect: to.fullPath } })
      return
    }
  }

  if (to.name === 'login' && token && isTokenValid(token)) {
    next({ name: 'enterprises' })
  } else {
    next()
  }
})

export default router
