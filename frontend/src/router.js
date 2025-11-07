import { sessionStore } from '@/stores/session'
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: { name: 'Dashboard' },
    name: 'Home',
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
  },
  {
    path: '/contratacion',
    name: 'Contratacion',
    component: () => import('@/pages/Contratacion.vue'),
  },
  {
    path: '/empleados',
    name: 'Empleados',
    component: () => import('@/pages/Empleados.vue'),
  },
  {
    path: '/vacantes',
    name: 'Vacantes',
    component: () => import('@/pages/Vacantes.vue'),
  },
  {
    path: '/solicitudes',
    name: 'Solicitudes',
    component: () => import('@/pages/Solicitudes.vue'),
  },
  {
    path: '/evaluaciones',
    name: 'Evaluaciones',
    component: () => import('@/pages/Evaluaciones.vue'),
  },
  {
    path: '/reportes',
    name: 'Reportes',
    component: () => import('@/pages/Reportes.vue'),
  },
  
  {
    path: '/ai-dashboard',
    name: 'AIDashboard',
    component: () => import('@/pages/AIDashboard.vue'),
  },
  {
    path: '/cv-analysis/:jobApplicant?/:jobOpening?',
    name: 'CVAnalysis',
    component: () => import('@/pages/CVAnalysis.vue'),
    props: route => ({
      jobApplicant: route.params.jobApplicant,
      jobOpening: route.params.jobOpening,
    }),
  },
  {
    path: '/recruitment-reports/:jobOpening?',
    name: 'RecruitmentReports',
    component: () => import('@/pages/RecruitmentReports.vue'),
    props: route => ({
      jobOpening: route.params.jobOpening,
    }),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
  },
  {
    path: '/:invalidpath',
    name: 'Invalid Page',
    component: () => import('@/pages/InvalidPage.vue'),
  },
]

const router = createRouter({
  history: createWebHistory('/portal-rrhh'),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const { isLoggedIn } = sessionStore()

  if (to.name === 'Login' && isLoggedIn) {
    next({ name: 'Dashboard' })
  } else if (to.name !== 'Login' && !isLoggedIn) {
    next({ name: 'Login' })
  } else if (to.matched.length === 0) {
    next({ name: 'Invalid Page' })
  } else {
    next()
  }
})

export default router
