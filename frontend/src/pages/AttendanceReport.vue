<template>
  <div class="flex flex-col h-full overflow-hidden bg-white">
    <div class="flex-1 overflow-y-auto p-5">
      <div class="mb-6 flex items-center justify-between">
        <h1 class="text-2xl font-bold text-gray-900">{{ __('Reporte de Asistencia') }}</h1>
        <div class="flex items-center space-x-2">
            <Button
                v-if="reportData.length"
                variant="outline"
                @click="downloadReport"
            >
                {{ __('Imprimir / PDF') }}
            </Button>
            <Button
                v-if="reportData.length"
                variant="outline"
                @click="downloadExcel"
            >
                {{ __('Exportar Excel') }}
            </Button>
        </div>
      </div>

      <!-- Filters -->
      <div class="bg-gray-50 rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div class="grid grid-cols-12 gap-4 items-end">
            <!-- Employee Search -->
            <div class="col-span-12 md:col-span-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __('Empleado') }}</label>
                <Autocomplete
                    v-model="filters.employee"
                    :options="employeeOptions"
                    placeholder="Buscar por nombre, DNI o ID..."
                    @update:query="searchEmployees"
                />
            </div>
            <!-- From Date -->
             <div class="col-span-6 md:col-span-3">
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __('Desde') }}</label>
                <DatePicker 
                    v-model="filters.from_date"
                    class="w-full"
                />
            </div>
            <!-- To Date -->
             <div class="col-span-6 md:col-span-3">
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __('Hasta') }}</label>
                <DatePicker 
                    v-model="filters.to_date"
                    class="w-full"
                />
            </div>
             <!-- Button -->
            <div class="col-span-12 md:col-span-2">
                 <Button
                    variant="solid"
                    theme="gray"
                    class="w-full justify-center !bg-black !text-white hover:!bg-gray-800"
                    :loading="loading"
                    :disabled="!isValidFilter"
                    @click="fetchReport"
                >
                    {{ __('Generar Reporte') }}
                </Button>
            </div>
        </div>
      </div>

      <!-- Report View -->
      <div v-if="hasRunReport && employeeDetails" class="bg-white rounded-lg border border-gray-200 shadow-sm p-6" id="printable-area">
          
          <!-- Header -->
          <div class="border-b border-gray-200 pb-4 mb-4 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
              <div>
                  <h2 class="text-xl font-bold text-gray-900">{{ employeeDetails.employee_name }}</h2>
                  <div class="flex flex-wrap gap-4 mt-2 text-sm text-gray-600">
                      <div v-if="employeeDetails.dni">
                          <span class="font-semibold">DNI/NIE:</span> {{ employeeDetails.dni }}
                      </div>
                      <div>
                          <span class="font-semibold">Periodo:</span> 
                          {{ formatDate(filters.from_date) }} - {{ formatDate(filters.to_date) }}
                      </div>
                  </div>
              </div>
              
              <!-- Calculation Explanation -->
              <div class="bg-blue-50 text-blue-800 text-xs p-3 rounded-md max-w-md">
                   <div class="font-semibold mb-1 flex items-center">
                       <FeatherIcon name="info" class="w-3 h-3 mr-1" />
                       {{ __('Cálculo de Horas') }}
                   </div>
                   {{ __('El "Total Horas" representa la suma real de tiempo trabajado (suma de intervalos Entrada-Salida), excluyendo descansos no fichados.') }}
              </div>
          </div>

          <!-- Table -->
          <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                      <tr>
                          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ __('Fecha') }}</th>
                          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ __('Hora Entrada') }}</th>
                          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ __('Hora Salida') }}</th>
                          <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">{{ __('Tiempo Descanso') }}</th>
                          <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">{{ __('Total Horas') }}</th>
                          <th scope="col" class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider no-print">
                            {{ __('Acciones') }}
                          </th>
                      </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                      <tr v-for="day in reportData" :key="day.date" :class="getRowClass(day)">
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              <div class="flex items-center gap-2">
                                {{ formatDateLong(day.date) }}
                                <div v-if="day.status && day.hours === 0" class="text-xs text-orange-600 font-medium">
                                    {{ day.status }}
                                </div>
                                <div v-if="day.is_verified" class="no-print">
                                    <Badge theme="blue" size="sm">
                                        {{ __('Verificado') }}
                                    </Badge>
                                </div>
                              </div>
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              <span :class="{'text-red-500 text-xs': getFirstIn(day.logs).includes('Usuario')}">
                                {{ getFirstIn(day.logs) }}
                              </span>
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                               <span :class="{'text-red-500 text-xs': getLastOut(day.logs).includes('Usuario')}">
                                {{ getLastOut(day.logs) }}
                               </span>
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-right">
                              <!-- Show verified rest time if available, else calc -->
                                {{ formatRestTimeDisplay(day.verified_rest_time || calculateRestTime(day.logs)) }}
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right font-medium">
                              {{ formatDecimalToTime(day.hours) }}
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap text-center text-sm font-medium no-print">
                               <Button 
                                    icon="edit-2" 
                                    variant="ghost" 
                                    @click="openVerifyDialog(day)"
                               />
                          </td>
                      </tr>
                  </tbody>
                  <tfoot class="bg-gray-50">
                      <tr>
                          <td colspan="3" class="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900 text-right">
                              {{ __('Total Periodo:') }}
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-500 text-right">
                              <!-- Optional Total Rest -->
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900 text-right">
                              {{ formatDecimalToTime(totalPeriodHours) }}
                          </td>
                          <td></td>
                      </tr>
                  </tfoot>
              </table>
          </div>

      </div>
      
      <div v-else-if="!hasRunReport" class="text-center py-10 text-gray-500">
          {{ __('Selecciona un empleado y un rango de fechas para generar el reporte.') }}
      </div>
      
      <!-- Verify Dialog -->
      <Dialog 
        v-model="showVerifyDialog"
        :options="{
            title: __('Verificar / Corregir Asistencia'),
            actions: [
                {
                    label: __('Guardar'),
                    variant: 'solid',
                    loading: verifyLoading,
                    onClick: submitVerification
                }
            ]
        }"
      >
        <template #body-content>
            <div class="space-y-4" v-if="currentDay">
                <div class="text-sm text-gray-600 mb-4">
                    {{ __('Editando registro del:') }} <span class="font-bold">{{ formatDateLong(currentDay.date) }}</span>
                </div>
                
                <div class="grid grid-cols-2 gap-4">
                     <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">{{ __('Total Horas') }} *</label>
                        <Input type="number" step="0.01" v-model="editForm.total_hours" placeholder="0.00" />
                     </div>
                     <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">{{ __('Tiempo Descanso') }}</label>
                        <Input type="text" v-model="editForm.rest_time" placeholder="Ej: 01:30" />
                     </div>
                     <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">{{ __('Hora Entrada (Visual)') }}</label>
                         <Input type="time" v-model="editForm.verified_in_time" />
                     </div>
                     <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">{{ __('Hora Salida (Visual)') }}</label>
                        <Input type="time" v-model="editForm.verified_out_time" />
                     </div>
                </div>
            </div>
        </template>
      </Dialog>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Button, Autocomplete, DatePicker, call, debounce, Dialog, Input, Badge, createResource } from 'frappe-ui'
import dayjs from 'dayjs'
import customParseFormat from 'dayjs/plugin/customParseFormat'
import 'dayjs/locale/es'

dayjs.extend(customParseFormat)
dayjs.locale('es')

const employeeOptions = ref([])
const loading = ref(false)
const hasRunReport = ref(false)
const reportData = ref([])
const employeeDetails = ref(null)

// Dialog State
const showVerifyDialog = ref(false)
const verifyLoading = ref(false)
const currentDay = ref(null)
const editForm = ref({
    total_hours: 0,
    rest_time: '',
    verified_in_time: '',
    verified_out_time: ''
})

// Smart Calculation Watcher
watch(() => [editForm.value.total_hours, editForm.value.verified_in_time, editForm.value.verified_out_time], ([newHours, newIn, newOut]) => {
    if (!showVerifyDialog.value) return
    
    // Only proceed if we have valid times
    if (!newIn || !newOut) return

    const inTime = dayjs(newIn, 'HH:mm')
    const outTime = dayjs(newOut, 'HH:mm')
    
    if (!inTime.isValid() || !outTime.isValid()) return
    
    const totalSpanMinutes = outTime.diff(inTime, 'minute')
    if (totalSpanMinutes <= 0) return

    // Prevent negative rest
    const workedMinutes = Math.min(parseFloat(newHours || 0) * 60, totalSpanMinutes)
    
    const restMinutes = totalSpanMinutes - workedMinutes
    
    if (restMinutes >= 0) {
        const h = Math.floor(restMinutes / 60)
        const m = Math.round(restMinutes % 60)
        editForm.value.rest_time = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
    }
})

const filters = ref({
    employee: null,
    from_date: dayjs().startOf('month').format('YYYY-MM-DD'),
    to_date: dayjs().endOf('month').format('YYYY-MM-DD')
})

const isValidFilter = computed(() => {
    return filters.value.employee && filters.value.from_date && filters.value.to_date
})

const totalPeriodHours = computed(() => {
    return reportData.value.reduce((sum, day) => sum + (day.hours || 0), 0)
})

const searchEmployees = debounce(async (query) => {
    try {
        const result = await call('portal_rrhh.portal_rrhh.employee_data.get_employees_list', {
            search_term: query
        })

        employeeOptions.value = (result.employees || []).map(e => {
            const statusLabel = e.status || 'Sin estado'
            const dniLabel = e.custom_dninie || 'Sin DNI'
            return {
                label: `${e.employee_name} (${dniLabel})`,
                value: e.name,
                original: e 
            }
        })
    } catch (e) {
        console.error("Search failed:", e)
    }
}, 300)

const fetchReport = async () => {
    if (!isValidFilter.value) return
    
    loading.value = true
    hasRunReport.value = false
    try {
        // Update Details
        let empLabel = filters.value.employee.label || ''
        // If employee was set programmatically or missing label, try to find it
        if (!empLabel && employeeOptions.value.length) {
             const found = employeeOptions.value.find(e => e.value === filters.value.employee.value)
             if (found) empLabel = found.label
        }

        employeeDetails.value = {
            employee_name: empLabel.split('(')[0]?.trim() || 'Empleado',
            dni: empLabel.match(/\((.*?)\)/)?.[1] || ''
        }

        const result = await call('portal_rrhh.api.attendance.get_attendance_report', {
            employee: filters.value.employee.value,
            from_date: filters.value.from_date,
            to_date: filters.value.to_date
        })
        
        if (result && result.success && result.data) {
            reportData.value = result.data
            hasRunReport.value = true
        } else {
             reportData.value = []
        }
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

const downloadReport = () => {
    window.print()
}

const downloadExcel = () => {
    const args = new URLSearchParams({
        employee: filters.value.employee.value,
        from_date: filters.value.from_date,
        to_date: filters.value.to_date
    })
    window.open(`/api/method/portal_rrhh.api.attendance.export_attendance_report?${args.toString()}`, '_blank')
}

// Dialog Logic
const openVerifyDialog = (day) => {
    currentDay.value = day
    // Pre-fill form
    // Check if logs exist to fill visual times
    const firstIn = getFirstIn(day.logs)
    const lastOut = getLastOut(day.logs)
    
    editForm.value = {
        total_hours: day.hours,
        rest_time: day.verified_rest_time || (calculateRestTime(day.logs) !== '-' ? calculateRestTime(day.logs) : ''),
        verified_in_time: firstIn !== '-' ? firstIn : '',
        verified_out_time: lastOut !== '-' ? lastOut : ''
    }
    
    showVerifyDialog.value = true
}

const submitVerification = async () => {
    if (!currentDay.value) return
    
    verifyLoading.value = true
    try {
        const result = await call('portal_rrhh.api.attendance.save_verified_attendance', {
            employee: filters.value.employee.value,
            date: currentDay.value.date,
            total_hours: editForm.value.total_hours,
            in_time: editForm.value.verified_in_time,
            out_time: editForm.value.verified_out_time,
            rest_time: editForm.value.rest_time
        })
        
        if (result && result.success) {
            showVerifyDialog.value = false
            // Refresh report
            fetchReport()
        } else {
            console.error(result.message)
            alert(result.message || "Error al guardar")
        }
    } catch (e) {
       console.error(e) 
       alert("Error al guardar")
    } finally {
        verifyLoading.value = false
    }
}

// Helpers
const formatDate = (d) => d ? dayjs(d).format('DD/MM/YYYY') : ''
const formatDateLong = (d) => dayjs(d).format('DD MMMM YYYY (dddd)')
const formatNumber = (n) => n ? Number(n).toFixed(2) : '0.00'

const getFirstIn = (logs) => {
    if (!logs || !logs.length) return '-'
    const ins = logs.filter(l => l.type === 'IN')
    if (!ins.length) return 'Usuario no registró hora de entrada'
    return ins[0].time
}

const getLastOut = (logs) => {
    if (!logs || !logs.length) return '-'
    const outs = logs.filter(l => l.type === 'OUT')
    if (!outs.length) return 'Usuario no registró hora de salida'
    return outs[outs.length - 1].time
}

const calculateRestTime = (logs) => {
    if (!logs || logs.length < 2) return '-'
    
    let totalMinutes = 0
    // Logs are sorted by time from backend
    // Iterate to find OUT followed by IN
    for (let i = 0; i < logs.length - 1; i++) {
        const current = logs[i]
        const next = logs[i+1]
        
        if (current.type === 'OUT' && next.type === 'IN') {
            const outTime = dayjs(current.time, 'HH:mm')
            const inTime = dayjs(next.time, 'HH:mm')
            
            if (inTime.isValid() && outTime.isValid()) {
                const diff = inTime.diff(outTime, 'minute')
                if (diff > 0) {
                    totalMinutes += diff
                }
            }
        }
    }
    
    if (totalMinutes === 0) return '-'
    
    const h = Math.floor(Math.abs(totalMinutes) / 60)
    const m = Math.round(Math.abs(totalMinutes) % 60)
    const sign = totalMinutes < 0 ? '-' : ''
    return `${sign}${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
}

const formatRestTimeDisplay = (val) => {
    if (!val || val === '-') return '-'
    // Check if Xh Ym format
    const match = val.match(/(\d+)h\s*(\d+)m/)
    if (match) {
        const h = parseInt(match[1]) || 0
        const m = parseInt(match[2]) || 0
        return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
    }
    return val
}

const formatDecimalToTime = (hours) => {
    if (!hours) return '00:00'
    const h = Math.floor(hours)
    const m = Math.round((hours - h) * 60)
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`
}

const getRowClass = (day) => {
    if (day.is_verified) return 'bg-blue-50/50'
    if (day.hours > 0) return ''
    if (day.status) return 'bg-orange-50'
    // Weekend check
    const d = dayjs(day.date).day()
    if (d === 0 || d === 6) return 'bg-gray-50 text-gray-400'
    return 'bg-red-50' // Absent workday
}

const __ = (text) => text

onMounted(() => {
    searchEmployees('')
})
</script>

<style scoped>
@media print {
    /* Hide everything except printable area */
    body * {
        visibility: hidden;
    }
    #printable-area, #printable-area * {
        visibility: visible;
    }
    .no-print {
        display: none !important;
    }
    #printable-area {
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        border: none;
        box-shadow: none;
        margin: 0;
        padding: 0;
    }
}
</style>
