<template>
  <div class="gantt-container bg-white rounded-lg border shadow-sm overflow-hidden">
    <!-- Header con controles de navegación -->
    <div class="flex items-center justify-between px-4 py-3 border-b bg-gray-50">
      <div class="flex items-center gap-4">
        <h3 class="text-lg font-semibold text-gray-900">Vista Gantt - Licencias del Equipo</h3>
        <span class="text-sm text-gray-500">
          {{ formatDateRange(startDate, endDate) }}
        </span>
      </div>
      <div class="flex items-center gap-2">
        <Button icon="chevron-left" variant="ghost" @click="previousPeriod" title="Período anterior" />
        <Button variant="subtle" @click="goToToday">Hoy</Button>
        <Button icon="chevron-right" variant="ghost" @click="nextPeriod" title="Período siguiente" />
      </div>
    </div>

    <!-- Contenedor principal con scroll horizontal -->
    <div class="flex overflow-hidden" style="height: 500px;">
      <!-- Columna fija de empleados -->
      <div class="flex-shrink-0 w-48 border-r bg-gray-50 overflow-y-auto" ref="employeeColumn">
        <!-- Header vacío para alinear con días -->
        <div class="h-16 border-b bg-gray-100 flex items-end justify-center pb-2">
          <span class="text-xs font-medium text-gray-500 uppercase">Empleado</span>
        </div>
        <!-- Lista de empleados -->
        <div 
          v-for="employee in employeesList" 
          :key="employee.name"
          class="h-7 px-3 flex items-center border-b border-gray-100 hover:bg-gray-100 transition"
        >
          <div class="truncate">
            <div class="text-xs font-medium text-gray-900 truncate" :title="employee.employee_name">
              {{ employee.employee_name }}
            </div>
          </div>
        </div>
        <!-- Mensaje si no hay empleados con licencias -->
        <div v-if="!employeesList.length" class="p-6 text-sm text-gray-500 text-center">
          <div class="text-gray-400 mb-1">No hay licencias</div>
          <div class="text-xs">en este período</div>
        </div>
      </div>

      <!-- Área de scroll horizontal para el Gantt -->
      <div class="flex-1 overflow-x-auto overflow-y-auto" ref="ganttArea" @scroll="syncScroll">
        <!-- Header de días/semanas -->
        <div class="sticky top-0 z-10 bg-white border-b">
          <!-- Fila de semanas -->
          <div class="flex h-8 border-b bg-gray-50">
            <div 
              v-for="week in weeks" 
              :key="week.start"
              class="flex-shrink-0 flex items-center justify-center border-r border-gray-200 text-xs font-medium text-gray-600"
              :style="{ width: `${week.days * dayWidth}px` }"
            >
              Semana {{ week.weekNum }} - {{ week.label }}
            </div>
          </div>
          <!-- Fila de días -->
          <div class="flex h-8">
            <div 
              v-for="day in days" 
              :key="day.date"
              class="flex-shrink-0 flex items-center justify-center border-r text-xs"
              :class="getDayHeaderClass(day)"
              :style="{ width: `${dayWidth}px` }"
            >
              <div class="flex flex-col items-center leading-tight">
                <span class="font-medium">{{ day.dayNum }}</span>
                <span class="text-[10px] uppercase">{{ day.dayName }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Filas de empleados con barras Gantt -->
        <div class="relative">
          <div 
            v-for="employee in employeesList" 
            :key="employee.name"
            class="h-7 flex items-center border-b border-gray-50 relative"
            :style="{ width: `${totalWidth}px` }"
          >
            <!-- Grid de fondo para los días -->
            <div class="absolute inset-0 flex">
              <div 
                v-for="day in days" 
                :key="day.date"
                class="flex-shrink-0 border-r border-gray-50 h-full"
                :class="getDayBackgroundClass(day)"
                :style="{ width: `${dayWidth}px` }"
              ></div>
            </div>

            <!-- Barras de licencias -->
            <template v-for="leave in getEmployeeLeaves(employee.name)" :key="leave.name">
              <Popover 
                placement="bottom" 
                :hover-delay="100"
                trigger="click"
              >
                <template #target="{ open, close, isOpen }">
                  <div 
                    class="absolute h-6 rounded cursor-pointer hover:brightness-110 transition-all flex items-center px-1.5 overflow-hidden"
                    :class="[getBarClass(leave), isOpen ? 'ring-2 ring-white ring-offset-1' : '']"
                    :style="getBarStyle(leave)"
                    @click.stop="isOpen ? close() : open()"
                  >
                    <span class="text-[10px] font-medium text-white truncate">
                      {{ leave.leave_type }}
                    </span>
                  </div>
                </template>
                <template #body="{ close }">
                  <div class="p-3 bg-white rounded-lg shadow-xl border text-sm min-w-[240px] max-w-[300px]" @click.stop>
                    <!-- Empleado -->
                    <div class="font-semibold text-gray-900">{{ leave.employee_name }}</div>
                    
                    <!-- Tipo de licencia -->
                    <div class="text-gray-600 mt-1">{{ leave.leave_type }}</div>
                    
                    <!-- Fechas -->
                    <div class="text-gray-500 text-xs mt-1">
                      {{ formatLeaveDate(leave) }}
                    </div>
                    
                    <!-- Estado -->
                    <div v-if="leave.status" class="mt-2">
                      <span 
                        class="inline-block px-2 py-0.5 text-xs rounded font-medium"
                        :class="getStatusClass(leave.status)"
                      >
                        {{ leave.status }}
                      </span>
                    </div>
                    
                    <!-- Descripción si existe -->
                    <div v-if="leave.description" class="mt-2 text-xs text-gray-500 border-t pt-2">
                      {{ leave.description }}
                    </div>
                    
                    <!-- Botones de acción para solicitudes pendientes -->
                    <div v-if="leave.status === 'Abierta' && canApprove" class="mt-3 pt-3 border-t flex gap-2">
                      <Button 
                        variant="subtle" 
                        theme="red"
                        size="sm"
                        class="flex-1"
                        @click.stop="handleProcess(leave.name, 'reject', close)"
                      >
                        Rechazar
                      </Button>
                      <Button 
                        variant="solid" 
                        theme="green"
                        size="sm"
                        class="flex-1"
                        @click.stop="handleProcess(leave.name, 'approve', close)"
                      >
                        Aprobar
                      </Button>
                    </div>
                  </div>
                </template>
              </Popover>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- Leyenda -->
    <div class="px-4 py-3 border-t bg-gray-50 flex items-center gap-6">
      <span class="text-xs font-medium text-gray-500 uppercase">Leyenda:</span>
      <div class="flex items-center gap-4 flex-wrap">
        <div v-for="type in leaveTypesWithColors" :key="type.name" class="flex items-center gap-1.5">
          <div class="w-3 h-3 rounded" :class="getBarColorClass(type.color)"></div>
          <span class="text-xs text-gray-600">{{ type.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/es'
import weekOfYear from 'dayjs/plugin/weekOfYear'
import isSameOrAfter from 'dayjs/plugin/isSameOrAfter'
import isSameOrBefore from 'dayjs/plugin/isSameOrBefore'
import { Tooltip, Button, Popover } from 'frappe-ui'

dayjs.extend(weekOfYear)
dayjs.extend(isSameOrAfter)
dayjs.extend(isSameOrBefore)
dayjs.locale('es')

const props = defineProps({
  leaves: {
    type: Array,
    default: () => []
  },
  employees: {
    type: Array,
    default: () => []
  },
  leaveTypes: {
    type: Array,
    default: () => []
  },
  canApprove: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['process'])

// Configuración
const dayWidth = 36 // Ancho de cada día en píxeles
const daysToShow = 42 // 6 semanas

// Estado
const currentStart = ref(dayjs().startOf('week'))

// Refs para sincronizar scroll
const employeeColumn = ref(null)
const ganttArea = ref(null)

// Computed
const startDate = computed(() => currentStart.value)
const endDate = computed(() => currentStart.value.add(daysToShow - 1, 'day'))

const days = computed(() => {
  const result = []
  let current = startDate.value
  for (let i = 0; i < daysToShow; i++) {
    result.push({
      date: current.format('YYYY-MM-DD'),
      dayNum: current.format('D'),
      dayName: current.format('dd'),
      isWeekend: current.day() === 0 || current.day() === 6,
      isToday: current.isSame(dayjs(), 'day'),
      dayjs: current
    })
    current = current.add(1, 'day')
  }
  return result
})

const weeks = computed(() => {
  const result = []
  let weekStart = startDate.value
  
  while (weekStart.isSameOrBefore(endDate.value)) {
    const weekEnd = weekStart.endOf('week')
    const actualEnd = weekEnd.isAfter(endDate.value) ? endDate.value : weekEnd
    const daysInWeek = actualEnd.diff(weekStart, 'day') + 1
    
    result.push({
      start: weekStart.format('YYYY-MM-DD'),
      weekNum: weekStart.week(),
      label: weekStart.format('D MMM'),
      days: daysInWeek
    })
    
    weekStart = weekStart.add(1, 'week').startOf('week')
  }
  
  return result
})

const totalWidth = computed(() => daysToShow * dayWidth)

// Obtener IDs de empleados que tienen licencias en el período visible
const employeesWithLeaves = computed(() => {
  const employeeIds = new Set()
  
  props.leaves.forEach(l => {
    const leaveStart = dayjs(l.from_date || l.request_date)
    const leaveEnd = dayjs(l.to_date || l.request_date)
    
    // Verificar si la licencia está dentro del rango visible
    if (leaveEnd.isSameOrAfter(startDate.value) && leaveStart.isSameOrBefore(endDate.value)) {
      employeeIds.add(l.employee)
    }
  })
  
  return employeeIds
})

const employeesList = computed(() => {
  // Filtrar solo empleados que tienen licencias en el período visible
  if (props.employees.length) {
    return props.employees.filter(emp => employeesWithLeaves.value.has(emp.name))
  }
  
  // Si no hay lista de empleados, extraer de las licencias visibles
  const seen = new Set()
  return props.leaves
    .filter(l => {
      if (seen.has(l.employee)) return false
      
      const leaveStart = dayjs(l.from_date || l.request_date)
      const leaveEnd = dayjs(l.to_date || l.request_date)
      
      // Solo incluir si está en el período visible
      if (!leaveEnd.isSameOrAfter(startDate.value) || !leaveStart.isSameOrBefore(endDate.value)) {
        return false
      }
      
      seen.add(l.employee)
      return true
    })
    .map(l => ({
      name: l.employee,
      employee_name: l.employee_name
    }))
})

const leaveTypesWithColors = computed(() => {
  const PALETTE = ['blue', 'purple', 'teal', 'orange', 'pink', 'indigo', 'yellow', 'red', 'green']
  return props.leaveTypes.map((lt, idx) => ({
    name: lt.name,
    label: lt.leave_type_name,
    color: PALETTE[idx % PALETTE.length]
  }))
})

// Funciones
function previousPeriod() {
  currentStart.value = currentStart.value.subtract(2, 'week')
}

function nextPeriod() {
  currentStart.value = currentStart.value.add(2, 'week')
}

function goToToday() {
  currentStart.value = dayjs().startOf('week')
}

function formatDateRange(start, end) {
  return `${start.format('D MMM')} - ${end.format('D MMM YYYY')}`
}

function getEmployeeLeaves(employeeId) {
  return props.leaves.filter(l => {
    if (l.employee !== employeeId) return false
    
    // Verificar que la licencia está dentro del rango visible
    const leaveStart = dayjs(l.from_date || l.request_date)
    const leaveEnd = dayjs(l.to_date || l.request_date)
    
    return leaveEnd.isSameOrAfter(startDate.value) && leaveStart.isSameOrBefore(endDate.value)
  })
}

function getBarStyle(leave) {
  const leaveStart = dayjs(leave.from_date || leave.request_date)
  const leaveEnd = dayjs(leave.to_date || leave.request_date)
  
  // Calcular posición inicial
  let startOffset = leaveStart.diff(startDate.value, 'day')
  if (startOffset < 0) startOffset = 0
  
  // Calcular ancho
  let endOffset = leaveEnd.diff(startDate.value, 'day')
  if (endOffset >= daysToShow) endOffset = daysToShow - 1
  
  const width = (endOffset - startOffset + 1) * dayWidth - 2 // -2 para pequeño margen
  const left = startOffset * dayWidth + 1 // +1 para centrar
  
  return {
    left: `${left}px`,
    width: `${Math.max(width, dayWidth - 2)}px`,
    top: '2px'
  }
}

function getBarClass(leave) {
  const type = leaveTypesWithColors.value.find(t => t.name === leave.leave_type)
  const color = type?.color || 'gray'
  const colorClass = getBarColorClass(color)
  
  // Si es solicitud pendiente, añadir borde discontinuo y opacidad reducida
  if (leave.status === 'Abierta') {
    return `${colorClass} border-2 border-dashed border-white/70 opacity-75`
  }
  
  // Aprobadas: borde sólido sutil
  return `${colorClass} border border-white/30`
}

function getBarColorClass(color) {
  const map = {
    blue: 'bg-blue-500',
    purple: 'bg-purple-500',
    teal: 'bg-teal-500',
    orange: 'bg-orange-500',
    pink: 'bg-pink-500',
    indigo: 'bg-indigo-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
    green: 'bg-green-500',
    gray: 'bg-gray-500'
  }
  return map[color] || map.gray
}

function getStatusClass(status) {
  const map = {
    'Aprobada': 'bg-green-100 text-green-700',
    'Abierta': 'bg-orange-100 text-orange-700',
    'Rechazada': 'bg-red-100 text-red-700',
    'Cancelada': 'bg-gray-100 text-gray-700'
  }
  return map[status] || 'bg-gray-100 text-gray-700'
}

function getDayHeaderClass(day) {
  if (day.isToday) return 'bg-blue-100 text-blue-700 font-semibold border-blue-200'
  if (day.isWeekend) return 'bg-orange-50 text-orange-600 border-orange-100'
  return 'bg-white text-gray-600 border-gray-100'
}

function getDayBackgroundClass(day) {
  if (day.isToday) return 'bg-blue-50/50'
  if (day.isWeekend) return 'bg-orange-50/30'
  return 'bg-white'
}

function formatLeaveDate(leave) {
  const start = dayjs(leave.from_date || leave.request_date)
  const end = dayjs(leave.to_date || leave.request_date)
  
  if (start.isSame(end, 'day')) {
    return start.format('D [de] MMMM YYYY')
  }
  return `${start.format('D MMM')} - ${end.format('D MMM YYYY')}`
}

function syncScroll(e) {
  if (employeeColumn.value) {
    employeeColumn.value.scrollTop = e.target.scrollTop
  }
}

// Manejar aprobar/rechazar
function handleProcess(name, action, closePopover) {
  emit('process', { name, action })
  if (closePopover) closePopover()
}

// Sincronizar scroll vertical de la columna de empleados
watch(() => ganttArea.value?.scrollTop, (val) => {
  if (employeeColumn.value && val !== undefined) {
    employeeColumn.value.scrollTop = val
  }
})
</script>

<style scoped>
.gantt-container {
  min-height: 400px;
}

/* Sincronizar scroll de columna empleados con área gantt */
.gantt-container > div:nth-child(2) > div:first-child::-webkit-scrollbar {
  display: none;
}
.gantt-container > div:nth-child(2) > div:first-child {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
