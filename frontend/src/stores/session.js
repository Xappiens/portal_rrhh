import router from '@/router'
import { createResource } from 'frappe-ui'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { usersStore } from './users'

// Simplificado para replicar el comportamiento estable de CRM:
// - Lee la sesión desde la cookie user_id
// - Tras login exitoso, recarga usuarios y hace push a /
// - No depende de window.boot para decidir si el usuario está logueado

export const sessionStore = defineStore('portal-rrhh-session', () => {
  const { users } = usersStore()

  function sessionUser() {
    try {
      let _sessionUser = null

      // 1) Preferir window.boot.user si ya está disponible tras recarga
      if (typeof window !== 'undefined' && window.boot && window.boot.user) {
        _sessionUser = window.boot.user
      }

      // 2) Si no hay boot, leer cookie user_id
      if (!_sessionUser && typeof document !== 'undefined') {
        const cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
        _sessionUser = cookies.get('user_id')
      }

      if (_sessionUser === 'Guest') _sessionUser = null
      return _sessionUser
    } catch (e) {
      console.error('Error reading session:', e)
      return null
    }
  }

  let user = ref(sessionUser())
  const isLoggedIn = computed(() => !!user.value)

  // Refrescar el usuario unas veces tras la carga por si la cookie llega tarde
  if (typeof window !== 'undefined') {
    const refreshUser = () => {
      const u = sessionUser()
      if (u && u !== user.value) user.value = u
    }
    refreshUser()
    setTimeout(refreshUser, 50)
    setTimeout(refreshUser, 100)
    setTimeout(refreshUser, 300)
    setTimeout(refreshUser, 500)
  }

  const login = createResource({
    url: 'login',
    onError() {
      throw new Error('Invalid email or password')
    },
    onSuccess() {
      // Tras login, recargar para obtener window.boot.user ya poblado
      window.location.href = '/portal-rrhh'
    },
  })

  const logout = createResource({
    url: 'logout',
    onSuccess() {
      users.reset()
      user.value = null
      router.replace({ name: 'Login' })
    },
  })

  return {
    user,
    isLoggedIn,
    login,
    logout,
  }
})
