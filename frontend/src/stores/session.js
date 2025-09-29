import router from '@/router'
import { createResource } from 'frappe-ui'
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { usersStore } from './users'

export const sessionStore = defineStore('portal-rrhh-session', () => {
  const { users } = usersStore()

  function sessionUser() {
    let cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
    let _sessionUser = cookies.get('user_id')
    console.log('🔍 Portal RRHH - Cookies:', document.cookie)
    console.log('🔍 Portal RRHH - User ID from cookie:', _sessionUser)
    if (_sessionUser === 'Guest') {
      _sessionUser = null
    }
    console.log('🔍 Portal RRHH - Final user:', _sessionUser)
    return _sessionUser
  }

  let user = ref(sessionUser())
  const isLoggedIn = computed(() => !!user.value)

  const login = createResource({
    url: 'login',
    onError() {
      throw new Error('Invalid email or password')
    },
    onSuccess() {
      users.reload()
      user.value = sessionUser()
      login.reset()
      router.replace({ path: '/' })
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
