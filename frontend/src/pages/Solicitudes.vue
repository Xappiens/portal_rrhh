<template>
  <div class="flex-1 p-6 bg-gray-50">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900">Solicitudes</h1>
      <p class="text-gray-600 mt-2">Gestiona las solicitudes de empleo y candidatos</p>
    </div>

    <!-- Under Construction -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
      <div class="flex flex-col items-center">
        <div class="p-4 rounded-full bg-yellow-100 text-yellow-600 mb-4">
          <FeatherIcon name="construction" class="h-12 w-12" />
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">Página en Construcción</h2>
        <p class="text-gray-600 mb-6 max-w-md">
          Esta sección está siendo desarrollada. Pronto podrás revisar solicitudes,
          gestionar candidatos y administrar el proceso de selección.
        </p>
        <div class="flex space-x-4">
          <Button variant="outline" size="md">
            <template #prefix>
              <FeatherIcon name="clock" class="h-4" />
            </template>
            Notificarme cuando esté listo
          </Button>
          <Button variant="solid" size="md">
            <template #prefix>
              <FeatherIcon name="arrow-left" class="h-4" />
            </template>
            Volver al Dashboard
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { FeatherIcon, Button } from 'frappe-ui'
</script>
