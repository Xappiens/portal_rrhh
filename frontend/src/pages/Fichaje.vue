<script setup>
import CheckInWidget from '@/components/CheckInWidget.vue'
import AttendanceCalendar from '@/components/AttendanceCalendar.vue'
import { createResource, Dialog, Button, FeatherIcon } from 'frappe-ui'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const __ = (text) => text

const isBlocked = ref(false)

// Check Onboarding Status
const onboardingStatus = createResource({
    url: "portal_rrhh.api.onboarding.has_pending_onboarding",
    auto: true,
    onSuccess: (data) => {
        if (data.has_pending) {
            isBlocked.value = true
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
</script>

<template>
  <div class="flex flex-col h-full overflow-hidden">
    <div class="flex-1 overflow-y-auto p-5">
      <CheckInWidget />
      
      <!-- Calendar View -->
      <div v-if="employee.data">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">{{ __('Mi Asistencia') }}</h3>
        <AttendanceCalendar :employeeId="employee.data.name" />
      </div>

    </div>

    <!-- Blocking Modal -->
    <Dialog v-model="isBlocked" :options="{ size: 'xl', preventClose: true }">
      <template #body-content>
        <div class="flex flex-col items-center justify-center p-6 text-center">
            <div class="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mb-4">
                <FeatherIcon name="alert-circle" class="w-8 h-8 text-orange-600" />
            </div>
            <h2 class="text-2xl font-bold text-gray-900 mb-2">
                Acción Requerida
            </h2>
            <p class="text-lg text-gray-600 mb-6">
                No puedes registrar tu jornada hasta completar tu proceso de onboarding.
                <br>
                Por favor, revisa y firma los documentos pendientes.
            </p>
            <Button variant="solid" size="xl" @click="goToOnboarding">
                Ir al Onboarding
            </Button>
        </div>
      </template>
      <!-- Hide default actions to enforce the flow -->
      <template #actions>
         <div></div> 
      </template>
    </Dialog>
  </div>
</template>
