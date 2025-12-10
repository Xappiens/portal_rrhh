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
  </div>
</template>

<script setup>
import CheckInWidget from '@/components/CheckInWidget.vue'
import AttendanceCalendar from '@/components/AttendanceCalendar.vue'
import { createResource } from 'frappe-ui'

const __ = (text) => text

// Fetch Employee Info to pass to calendar
const employee = createResource({
    url: "hrms.api.get_current_employee_info",
    auto: true,
})
</script>
