<template>
  <div class="flex flex-col h-full overflow-hidden bg-white">
    <div class="flex-1 overflow-y-auto p-5">
      <div class="mb-6 flex items-center justify-between">
        <h1 class="text-2xl font-bold text-gray-900">{{ __('Reporte de Asistencia') }}</h1>
        <div class="flex items-center space-x-2">
            <Button
                v-if="reportData.length > 0"
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
            
            <div class="flex justify-end">
                 <!-- Navigation Controls -->
                 <div class="flex items-center bg-white rounded-md shadow-sm border border-gray-300">
                    <button @click="changeMonth(-1)" class="p-2 hover:bg-gray-50 border-r border-gray-300 text-gray-600">
                        <FeatherIcon name="chevron-left" class="h-5 w-5" />
                    </button>
                    <button @click="jumpToToday" class="px-4 py-2 text-sm font-medium hover:bg-gray-50 text-gray-700 border-r border-gray-300">
                        {{ __('Hoy') }}
                    </button>
                    <button @click="changeMonth(1)" class="p-2 hover:bg-gray-50 text-gray-600">
                        <FeatherIcon name="chevron-right" class="h-5 w-5" />
                    </button>
                 </div>
            </div>
        </div>
      </div>

      <!-- Report View -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Month 1 -->
        <div class="bg-white">
            <h3 class="text-lg font-bold text-gray-900 mb-4 capitalize text-center">
                {{ formatMonthTitle(currentMonth) }}
            </h3>
            <div class="grid grid-cols-7 gap-px bg-gray-200 border border-gray-200 rounded-lg overflow-hidden">
                <!-- Headers -->
                <div v-for="day in weekDays" :key="day" class="bg-gray-50 py-2 text-center text-xs font-semibold text-gray-500 uppercase">
                    {{ day }}
                </div>
                <!-- Days -->
                <div v-for="(day, idx) in calendar1" :key="idx" 
                    class="bg-white min-h-[100px] p-2 flex flex-col items-center justify-start relative group transition-colors hover:bg-blue-50"
                    :class="{'bg-gray-50': !day.inMonth, 'bg-blue-50': day.isToday}"
                >
                    <span class="text-xs font-medium mb-1" :class="day.isToday ? 'text-blue-600' : 'text-gray-400'">
                        {{ day.dayNum }}
                    </span>
                    
                    <!-- Data content -->
                    <div v-if="day.inMonth && day.data" class="w-full text-center">
                        <div v-if="day.data.hours > 0" class="mt-1">
                            <span class="text-lg font-bold text-gray-900">{{ day.data.hours }}h</span>
                        </div>
                        <div v-if="day.data.status" class="mt-1">
                             <Badge v-for="(s, i) in formatStatus(day.data.status)" :key="i" size="sm" variant="subtle" theme="orange" class="mb-0.5 mx-auto block max-w-full truncate">
                                {{ s }}
                             </Badge>
                        </div>
                        <div v-if="day.data.hours === 0 && !day.data.status && isWeekday(day.date)" class="mt-2">
                             <span class="h-1.5 w-1.5 rounded-full bg-red-400 inline-block"></span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Month 2 -->
        <div class="bg-white">
            <h3 class="text-lg font-bold text-gray-900 mb-4 capitalize text-center">
                {{ formatMonthTitle(nextMonthObj) }}
            </h3>
            <div class="grid grid-cols-7 gap-px bg-gray-200 border border-gray-200 rounded-lg overflow-hidden">
                <!-- Headers -->
                <div v-for="day in weekDays" :key="day" class="bg-gray-50 py-2 text-center text-xs font-semibold text-gray-500 uppercase">
                    {{ day }}
                </div>
                <!-- Days -->
                <div v-for="(day, idx) in calendar2" :key="idx" 
                    class="bg-white min-h-[100px] p-2 flex flex-col items-center justify-start relative group transition-colors hover:bg-blue-50"
                    :class="{'bg-gray-50': !day.inMonth, 'bg-blue-50': day.isToday}"
                >
                     <span class="text-xs font-medium mb-1" :class="day.isToday ? 'text-blue-600' : 'text-gray-400'">
                        {{ day.dayNum }}
                    </span>

                     <!-- Data content -->
                    <div v-if="day.inMonth && day.data" class="w-full text-center">
                        <div v-if="day.data.hours > 0" class="mt-1">
                            <span class="text-lg font-bold text-gray-900">{{ day.data.hours }}h</span>
                        </div>
                        <div v-if="day.data.status" class="mt-1">
                             <Badge v-for="(s, i) in formatStatus(day.data.status)" :key="i" size="sm" variant="subtle" theme="orange" class="mb-0.5 mx-auto block max-w-full truncate">
                                {{ s }}
                             </Badge>
                        </div>
                         <div v-if="day.data.hours === 0 && !day.data.status && isWeekday(day.date)" class="mt-2">
                             <span class="h-1.5 w-1.5 rounded-full bg-red-400 inline-block"></span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
      </div>

       <div v-if="loading" class="fixed inset-0 bg-white/50 z-50 flex items-center justify-center">
            <div class="bg-white p-4 rounded shadow-lg flex items-center space-x-3">
                <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                <span>{{ __('Cargando datos...') }}</span>
            </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Button, Autocomplete, Badge, call, FeatherIcon, debounce } from 'frappe-ui'
import dayjs from 'dayjs'
import 'dayjs/locale/es'
import isBetween from 'dayjs/plugin/isBetween'

dayjs.extend(isBetween)
dayjs.locale('es')

const loading = ref(false)
const reportData = ref([]) // Array of daily data objects from API
const employeeOptions = ref([])
const reportDataMap = ref({}) // Map date -> data object

const filters = ref({
    employee: null,
})

// Calendar State
const currentMonth = ref(dayjs().startOf('month'))

// Computed
const nextMonthObj = computed(() => currentMonth.value.add(1, 'month'))

const weekDays = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

const calendar1 = computed(() => generateCalendarDays(currentMonth.value))
const calendar2 = computed(() => generateCalendarDays(nextMonthObj.value))

// Helpers
const formatMonthTitle = (d) => d.format('MMMM YYYY')
const formatStatus = (statusStr) => statusStr ? statusStr.split(',').map(s => s.trim()) : []
const isWeekday = (date) => {
    const d = dayjs(date).day()
    return d !== 0 && d !== 6 
}

function generateCalendarDays(monthStart) {
    const startOfMonth = monthStart.startOf('month')
    const endOfMonth = monthStart.endOf('month')
    const daysInMonth = monthStart.daysInMonth()
    
    const days = []
    
    // Previous month padding
    // day() returns 0 (Sun) to 6 (Sat). We want Monday 0.
    // Sunday (0) -> 6, Mon(1) -> 0.
    let startDay = startOfMonth.day()
    if (startDay === 0) startDay = 7
    startDay -= 1 // Make 0-indexed for Monday
    
    for (let i = 0; i < startDay; i++) {
        days.push({ inMonth: false, dayNum: '', date: null })
    }
    
    // Current month days
    for (let i = 1; i <= daysInMonth; i++) {
        const date = startOfMonth.date(i).format('YYYY-MM-DD')
        days.push({
            inMonth: true,
            dayNum: i,
            date: date,
            isToday: date === dayjs().format('YYYY-MM-DD'),
            data: reportDataMap.value[date] || null
        })
    }
    
    // Next month padding to fill 6 rows (42 cells) or just fill last row
    const remaining = 42 - days.length
    if (remaining > 0 && remaining < 7) { 
         // Optional: just pad to end of week
    }
    // Let's just Pad to end of week for cleaner look
    const endDay = endOfMonth.day() // 0-6
    let padEnds = 0
    if (endDay !== 0) {
        padEnds = 7 - endDay
    }
    
    for(let i=0; i<padEnds; i++) {
         days.push({ inMonth: false, dayNum: '', date: null })
    }

    return days
}

// Actions
const changeMonth = (delta) => {
    currentMonth.value = currentMonth.value.add(delta, 'month')
    fetchReport()
}

const jumpToToday = () => {
    currentMonth.value = dayjs().startOf('month')
    fetchReport()
}

const searchEmployees = debounce(async (query) => {
    // if (!query) return // Allow empty query for initial load
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

const fetchReport = async () => {
    if (!filters.value.employee) return
    
    loading.value = true
    try {
        // Range: From start of Month 1 to End of Month 2
        const from_date = currentMonth.value.format('YYYY-MM-DD')
        const to_date = nextMonthObj.value.endOf('month').format('YYYY-MM-DD')

        const result = await call('portal_rrhh.api.attendance.get_attendance_report', {
            employee: filters.value.employee.value,
            from_date: from_date,
            to_date: to_date
        })
        
        if (result && result.success) {
            reportData.value = result.data
            // Map to dict for easier access O(1)
            const map = {}
            if(result.data) {
                result.data.forEach(d => {
                    map[d.date] = d
                })
            }
            reportDataMap.value = map
        }
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

watch(() => filters.value.employee, () => {
    if (filters.value.employee) {
        fetchReport()
    } else {
        reportData.value = []
        reportDataMap.value = {}
    }
})

const downloadReport = () => {
   // Simple XLS export for calendar view is hard. 
   // Maybe export list data for the selected period?
   // Let's reuse legacy logic but just dump the data we have.
   // Or better, just alert user this exports raw data.
   
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "Fecha,Horas,Estado,Logs\n";
    
    reportData.value.forEach(row => {
        const logsStr = (row.logs || []).map(l => `${l.type} ${l.time}`).join(' | ')
        csvContent += `${row.date},${row.hours},"${row.status || ''}","${logsStr}"\n`;
    });
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `Reporte_${filters.value.employee.label}_${currentMonth.value.format('MM-YYYY')}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

const __ = (text) => text

onMounted(() => {
    searchEmployees('')
})
</script>
