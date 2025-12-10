<template>
  <div class="flex flex-col h-full overflow-hidden bg-white">
    <div class="flex-1 overflow-y-auto p-5">
      <div class="mb-6 flex items-center justify-between">
        <h1 class="text-2xl font-bold text-gray-900">{{ __('Reporte de Asistencia') }}</h1>
        <div class="flex items-center space-x-2">
            <Button
                v-if="filters.employee"
                variant="outline"
                @click="downloadReport"
            >
                {{ __('Exportar a Excel') }}
            </Button>
        </div>
      </div>

      <!-- Filters -->
      <div class="bg-gray-50 rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 items-end">
            <!-- Employee Search -->
            <div class="flex-1">
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __('Empleado') }}</label>
                <Autocomplete
                    v-model="filters.employee"
                    :options="employeeOptions"
                    placeholder="Buscar por nombre, DNI o ID..."
                    @update:query="searchEmployees"
                />
            </div>
        </div>
      </div>

      <!-- Report View with Shared Calendar -->
      <AttendanceCalendar 
        v-if="filters.employee" 
        :employeeId="filters.employee.value" 
      />
      
      <div v-else class="text-center py-10 text-gray-500">
          {{ __('Selecciona un empleado para ver su reporte.') }}
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Button, Autocomplete, call, debounce } from 'frappe-ui'
import AttendanceCalendar from '@/components/AttendanceCalendar.vue'
import dayjs from 'dayjs'
import 'dayjs/locale/es'

dayjs.locale('es')

const employeeOptions = ref([])

const filters = ref({
    employee: null,
})

const searchEmployees = debounce(async (query) => {
    try {
        const result = await call('portal_rrhh.portal_rrhh.employee_data.get_employees_list', {
            search_term: query
        })

        employeeOptions.value = (result.employees || []).map(e => {
            const statusLabel = e.status || 'Sin estado'
            const dniLabel = e.custom_dninie || 'Sin DNI'
            const deviceLabel = e.attendance_device_id ? `[${e.attendance_device_id}]` : ''
            return {
                label: `${e.employee_name} (${dniLabel}) ${deviceLabel} [${statusLabel}]`,
                value: e.name
            }
        })
    } catch (e) {
        console.error("Search failed:", e)
    }
}, 300)

const downloadReport = () => {
    // Simplest: Alert user that export is not fully linked to calendar view in this refactor
    alert("Funcionalidad de exportación simplificada para esta vista.")
}

const __ = (text) => text

onMounted(() => {
    searchEmployees('')
})
</script>
