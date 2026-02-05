<template>
  <div class="attendance-calendar">
      <!-- Controls -->
       <div class="flex justify-end mb-4">
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

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 relative">
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
                        <!-- Hours worked -->
                        <div v-if="day.data.hours > 0" class="mt-1">
                            <span class="text-lg font-bold text-gray-900">{{ day.data.hours }}h</span>
                        </div>
                        
                        <!-- Leave/Holiday status -->
                        <div v-if="day.data.status" class="mt-1">
                            <Badge v-for="(s, i) in formatStatus(day.data.status)" :key="i" size="sm" variant="subtle" theme="orange" class="mb-0.5 mx-auto block max-w-full truncate">
                                {{ s }}
                            </Badge>
                        </div>
                        
                        <!-- Anomaly indicator -->
                        <div v-if="day.data.anomaly" class="mt-2">
                            <Tooltip :text="day.data.anomaly_desc || getAnomalyText(day.data.anomaly)">
                                <span 
                                    class="h-2.5 w-2.5 rounded-full inline-block cursor-help"
                                    :class="getAnomalyColor(day.data.anomaly)"
                                ></span>
                            </Tooltip>
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
                        <!-- Hours worked -->
                        <div v-if="day.data.hours > 0" class="mt-1">
                            <span class="text-lg font-bold text-gray-900">{{ day.data.hours }}h</span>
                        </div>
                        
                        <!-- Leave/Holiday status -->
                        <div v-if="day.data.status" class="mt-1">
                            <Badge v-for="(s, i) in formatStatus(day.data.status)" :key="i" size="sm" variant="subtle" theme="orange" class="mb-0.5 mx-auto block max-w-full truncate">
                                {{ s }}
                            </Badge>
                        </div>
                        
                        <!-- Anomaly indicator -->
                        <div v-if="day.data.anomaly" class="mt-2">
                            <Tooltip :text="day.data.anomaly_desc || getAnomalyText(day.data.anomaly)">
                                <span 
                                    class="h-2.5 w-2.5 rounded-full inline-block cursor-help"
                                    :class="getAnomalyColor(day.data.anomaly)"
                                ></span>
                            </Tooltip>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="loading" class="absolute inset-0 bg-white/50 z-50 flex items-center justify-center rounded-lg">
             <div class="bg-white p-3 rounded shadow border flex items-center space-x-3">
                 <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                 <span class="text-sm font-medium">{{ __('Cargando...') }}</span>
             </div>
        </div>
      </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Badge, call, FeatherIcon, Tooltip } from 'frappe-ui'
import dayjs from 'dayjs'
import 'dayjs/locale/es'

dayjs.locale('es')

const props = defineProps({
    employeeId: {
        type: String,
        default: null
    }
})

const loading = ref(false)
const reportDataMap = ref({})

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

// Anomaly helpers
const getAnomalyColor = (anomaly) => {
    const colors = {
        'missing_out': 'bg-orange-400',   // Falta salida
        'missing_in': 'bg-orange-400',    // Falta entrada
        'no_break': 'bg-yellow-400',      // Sin descanso
        'no_checkin': 'bg-red-400'        // Sin fichaje
    }
    return colors[anomaly] || 'bg-red-400'
}

const getAnomalyText = (anomaly) => {
    const texts = {
        'missing_out': 'Falta fichaje de salida',
        'missing_in': 'Falta fichaje de entrada',
        'no_break': 'Jornada > 6h sin descanso',
        'no_checkin': 'Sin fichaje ni justificación'
    }
    return texts[anomaly] || 'Anomalía detectada'
}

function generateCalendarDays(monthStart) {
    const startOfMonth = monthStart.startOf('month')
    const endOfMonth = monthStart.endOf('month')
    const daysInMonth = monthStart.daysInMonth()
    
    const days = []
    
    let startDay = startOfMonth.day()
    if (startDay === 0) startDay = 7
    startDay -= 1 
    
    for (let i = 0; i < startDay; i++) {
        days.push({ inMonth: false, dayNum: '', date: null })
    }
    
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
    
    const endDay = endOfMonth.day()
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

const fetchReport = async () => {
    if (!props.employeeId) {
        reportDataMap.value = {}
        return
    }
    
    loading.value = true
    try {
        const from_date = currentMonth.value.format('YYYY-MM-DD')
        const to_date = nextMonthObj.value.endOf('month').format('YYYY-MM-DD')

        const result = await call('portal_rrhh.api.attendance.get_attendance_report', {
            employee: props.employeeId,
            from_date: from_date,
            to_date: to_date
        })
        
        if (result && result.success && result.data) {
            const map = {}
            result.data.forEach(d => {
                map[d.date] = d
            })
            reportDataMap.value = map
        } else {
             reportDataMap.value = {}
        }
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

watch(() => props.employeeId, () => {
    fetchReport()
}, { immediate: true })

const __ = (text) => text
</script>
