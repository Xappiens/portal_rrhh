<template>
  <router-view v-if="route.name == 'Login'" />
  <DesktopLayout v-else-if="session().isLoggedIn">
    <router-view />
  </DesktopLayout>
  <Dialogs />
  <Toasts />
</template>

<script setup>
import DesktopLayout from '@/components/Layouts/DesktopLayout.vue'
import { Dialogs } from '@/utils/dialogs'
import { sessionStore as session } from '@/stores/session'
import { Toasts } from 'frappe-ui'
import { useRoute, useRouter } from 'vue-router'
import { watch } from 'vue'

const route = useRoute()
const router = useRouter()

// Watcher para redirigir al login si el usuario se desloguea mientras está en la app
watch(
  () => session().isLoggedIn,
  (isLoggedIn) => {
    if (!isLoggedIn && route.name !== 'Login') {
      router.replace({ name: 'Login' })
    }
  }
)
</script>
