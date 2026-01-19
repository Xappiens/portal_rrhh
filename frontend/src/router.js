import { sessionStore } from '@/stores/session'
import { usersStore } from '@/stores/users'
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: { name: 'Profile' },
    name: 'Home',
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/pages/Profile.vue'),
  },
  {
    path: '/vacaciones',
    name: 'SpanishLeave',
    component: () => import('@/pages/SpanishLeave.vue'),
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
    path: '/reporte-asistencia',
    name: 'AttendanceReport',
    component: () => import('@/pages/AttendanceReport.vue'),
  },
  {
    path: '/anomalies',
    name: 'AttendanceAnomalies',
    component: () => import('@/pages/AttendanceAnomalies.vue'),
  },
  {
    path: '/timesheets',
    name: 'Timesheets',
    component: () => import('@/pages/Timesheets.vue'),
  },
  {
    path: '/fichaje',
    name: 'Fichaje',
    component: () => import('@/pages/Fichaje.vue'),
  },

  {
    path: '/onboarding',
    name: 'Onboarding',
    component: () => import('@/pages/Onboarding.vue'),
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
  const { users } = usersStore()
  const session = sessionStore()

  // Intentar fijar usuario desde window.boot primero
  if (!session.user && typeof window !== 'undefined' && window.boot && window.boot.user && window.boot.user !== 'Guest') {
    session.user = window.boot.user
  }

  // Si no hay boot, leer cookie user_id
  if (!session.user) {
    const cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
    const cookieUser = cookies.get('user_id')
    if (cookieUser && cookieUser !== 'Guest') {
      session.user = cookieUser
    }
  }

  // Si está logueado, asegurar que users esté listo
  if (session.isLoggedIn) {
    await users.promise
  }

  if (to.name === 'Login' && session.isLoggedIn) {
    next({ name: 'Profile' })
  } else if (to.name !== 'Login' && !session.isLoggedIn) {
    next({ name: 'Login' })
  } else if (to.matched.length === 0) {
    next({ name: 'Invalid Page' })
  } else {
    next()
  }
})

export default router
