<template>
  <div class="flex h-screen w-screen items-center justify-center bg-gray-100">
    <div class="text-center">
      <FeatherIcon name="alert-circle" class="h-16 w-16 text-gray-400 mx-auto mb-4" />
      <h2 class="text-2xl font-semibold text-gray-800 mb-2">Página no encontrada</h2>
      <p class="text-gray-600 mb-4">La página que buscas no existe o no tienes permisos para acceder a ella.</p>
      <Button variant="solid" @click="goHome">Volver al inicio</Button>
    </div>
  </div>
</template>

<script setup>
import { FeatherIcon, Button } from 'frappe-ui'
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push({ name: 'Dashboard' })
}
</script>
