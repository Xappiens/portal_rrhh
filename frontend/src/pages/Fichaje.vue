<script setup>
import CheckInWidget from '@/components/CheckInWidget.vue'
import AttendanceCalendar from '@/components/AttendanceCalendar.vue'
import Modelo145Dialog from '@/components/Modelo145Dialog.vue'
import { createResource, Dialog, Button, FeatherIcon } from 'frappe-ui'
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const __ = (text) => text

const isBlockedOnboarding = ref(false)
const isBlockedModelo145 = ref(false)
const showModelo145Dialog = ref(false)

// Check Onboarding Status
const onboardingStatus = createResource({
    url: "portal_rrhh.api.onboarding.has_pending_onboarding",
    auto: true,
    onSuccess: (data) => {
        if (data.has_pending) {
            isBlockedOnboarding.value = true
        }
    }
})

// Check Modelo 145 Status
const modelo145Status = createResource({
    url: "portal_rrhh.api.modelo145.has_modelo_145",
    auto: true,
    onSuccess: (data) => {
        if (!data.has_modelo) {
            isBlockedModelo145.value = true
        }
    }
})

// Fetch Employee Info to pass to calendar
const employee = createResource({
    url: "hrms.api.get_current_employee_info",
    auto: true,
})

const goToOnboarding = () => {
    router.push({ name: 'Onboarding' })
}

const openModelo145Dialog = () => {
    showModelo145Dialog.value = true
}

const handleModelo145Success = () => {
    isBlockedModelo145.value = false
    modelo145Status.reload()
}
</script>

<template>
  <div class="flex flex-col h-full overflow-hidden">
    <!-- Bloqueo total si hay onboarding pendiente -->
    <div v-if="isBlockedOnboarding" class="flex-1 flex items-center justify-center p-5">
      <div class="flex flex-col items-center justify-center p-8 text-center bg-white rounded-xl shadow-lg border border-orange-200 max-w-lg">
        <div class="w-20 h-20 bg-orange-100 rounded-full flex items-center justify-center mb-6">
          <FeatherIcon name="alert-circle" class="w-10 h-10 text-orange-600" />
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-3">
          Acción Requerida
        </h2>
        <p class="text-lg text-gray-600 mb-6">
          No puedes registrar tu jornada hasta completar tu proceso de onboarding.
          <br>
          Por favor, revisa y firma los documentos pendientes.
        </p>
        <Button variant="solid" size="xl" @click="goToOnboarding">
          <template #prefix>
            <FeatherIcon name="file-text" class="w-5 h-5" />
          </template>
          Ir al Onboarding
        </Button>
      </div>
    </div>

    <!-- Bloqueo total si falta Modelo 145 -->
    <div v-else-if="isBlockedModelo145" class="flex-1 flex items-center justify-center p-5">
      <div class="flex flex-col items-center justify-center p-8 text-center bg-white rounded-xl shadow-lg border border-amber-200 max-w-lg">
        <div class="w-20 h-20 bg-amber-100 rounded-full flex items-center justify-center mb-6">
          <FeatherIcon name="file-text" class="w-10 h-10 text-amber-600" />
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-3">
          Modelo 145 Requerido
        </h2>
        <p class="text-lg text-gray-600 mb-4">
          No puedes registrar tu jornada hasta presentar tu Modelo 145.
        </p>
        <p class="text-sm text-gray-500 mb-6">
          El Modelo 145 es la comunicación de datos al pagador para el cálculo de retenciones del IRPF.
          Es obligatorio para todos los empleados.
        </p>
        <Button variant="solid" size="xl" class="!bg-amber-600 hover:!bg-amber-700" @click="openModelo145Dialog">
          <template #prefix>
            <FeatherIcon name="file-text" class="w-5 h-5" />
          </template>
          Rellenar Modelo 145
        </Button>
      </div>
    </div>

    <!-- Contenido normal solo si no hay bloqueos -->
    <div v-else class="flex-1 overflow-y-auto p-5">
      <CheckInWidget />
      
      <!-- Calendar View -->
      <div v-if="employee.data">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">{{ __('Mi Asistencia') }}</h3>
        <AttendanceCalendar :employeeId="employee.data.name" />
      </div>
    </div>

    <!-- Modelo 145 Dialog -->
    <Modelo145Dialog 
      v-model="showModelo145Dialog" 
      :employee-id="employee.data?.name || ''" 
      @success="handleModelo145Success" 
    />
  </div>
</template>
