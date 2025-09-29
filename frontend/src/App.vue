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
import { useRoute } from 'vue-router'

const route = useRoute()

console.log('🔍 Portal RRHH - App.vue - Route name:', route.name)
console.log('🔍 Portal RRHH - App.vue - Is logged in:', session().isLoggedIn)
console.log('🔍 Portal RRHH - App.vue - User:', session().user)
</script>
