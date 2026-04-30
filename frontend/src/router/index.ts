import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../views/auth/Login.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/auth/Register.vue') },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'Dashboard', component: () => import('../views/dashboard/Dashboard.vue') },
      { path: 'diet-log', name: 'DietLog', component: () => import('../views/diet-log/DietLog.vue') },
      { path: 'health', name: 'Health', component: () => import('../views/health/HealthProfile.vue') },
      { path: 'exercise', name: 'Exercise', component: () => import('../views/exercise/ExerciseLog.vue') },
      { path: 'ai', name: 'AI', component: () => import('../views/ai/AIRecommend.vue') },
      { path: 'analytics', name: 'Analytics', component: () => import('../views/analytics/Analytics.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (to.name !== 'Login' && to.name !== 'Register' && !token) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router
