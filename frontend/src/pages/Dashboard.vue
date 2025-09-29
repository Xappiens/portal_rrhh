<template>
  <div class="flex-1 p-6 bg-gray-50">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <!-- Tarjetas de estadísticas -->
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                <FeatherIcon name="users" class="w-5 h-5 text-white" />
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">Total Empleados</p>
              <p class="text-2xl font-semibold text-gray-900">156</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                <FeatherIcon name="briefcase" class="w-5 h-5 text-white" />
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">Vacantes Activas</p>
              <p class="text-2xl font-semibold text-gray-900">12</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                <FeatherIcon name="file-text" class="w-5 h-5 text-white" />
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">Solicitudes Pendientes</p>
              <p class="text-2xl font-semibold text-gray-900">8</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
                <FeatherIcon name="trending-up" class="w-5 h-5 text-white" />
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">Evaluaciones Completadas</p>
              <p class="text-2xl font-semibold text-gray-900">45</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Contenido adicional -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Actividad Reciente</h3>
          <div class="space-y-4">
            <div class="flex items-center space-x-3">
              <div class="w-2 h-2 bg-blue-500 rounded-full"></div>
              <p class="text-sm text-gray-600">Nuevo empleado registrado: Juan Pérez</p>
            </div>
            <div class="flex items-center space-x-3">
              <div class="w-2 h-2 bg-green-500 rounded-full"></div>
              <p class="text-sm text-gray-600">Vacante publicada: Desarrollador Frontend</p>
            </div>
            <div class="flex items-center space-x-3">
              <div class="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <p class="text-sm text-gray-600">Solicitud de vacaciones aprobada</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Próximas Evaluaciones</h3>
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-900">María García</p>
                <p class="text-sm text-gray-500">Evaluación Trimestral</p>
              </div>
              <span class="text-sm text-gray-500">15 Ene</span>
            </div>
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-900">Carlos López</p>
                <p class="text-sm text-gray-500">Evaluación Anual</p>
              </div>
              <span class="text-sm text-gray-500">20 Ene</span>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'
</script>
