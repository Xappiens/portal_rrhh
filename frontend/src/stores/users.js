import { createResource } from 'frappe-ui'
import { defineStore } from 'pinia'
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { sessionStore } from './session'

export const usersStore = defineStore('portal-rrhh-users', () => {
  const session = sessionStore()

  let usersByName = reactive({})
  const router = useRouter()

  const users = createResource({
    url: 'portal_rrhh.api.session.get_users',
    cache: 'Users',
    initialData: [],
    auto: true,
    transform(users) {
      for (let user of users) {
        if (user.name === 'Administrator') {
          user.email = 'Administrator'
        }
        usersByName[user.name] = user
      }
      return users
    },
    onError(error) {
      if (error && error.exc_type === 'AuthenticationError') {
        router.push('/login')
      }
    },
  })

  function getUser(email) {
    if (!email || email === 'sessionUser') {
      email = session.user
    }
    if (!usersByName[email]) {
      usersByName[email] = {
        name: email,
        email: email,
        full_name: email.split('@')[0],
        user_image: null,
        role: null,
      }
    }
    return usersByName[email]
  }

  function isManager(email) {
    return getUser(email).is_manager
  }

  return {
    users,
    getUser,
    isManager,
  }
})
