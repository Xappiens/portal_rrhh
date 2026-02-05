<template>
  <div class="calendar-container select-none">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-gray-900 capitalize" :class="compact ? 'text-sm' : ''">
        {{ currentMonthName }} {{ currentYear }}
      </h2>
      <div v-if="!hideControls" class="flex gap-1">
        <Button icon="chevron-left" variant="ghost" @click="prevMonth" />
        <Button icon="chevron-right" variant="ghost" @click="nextMonth" />
      </div>
    </div>

    <!-- Days Header -->
    <div class="grid grid-cols-7 mb-2 border-b border-gray-100 pb-2">
      <div
        v-for="day in weekDays"
        :key="day"
        class="text-xs font-medium text-gray-500 text-center uppercase tracking-wide"
      >
        {{ day }}
      </div>
    </div>

    <!-- Calendar Grid -->
    <div class="grid grid-cols-7 gap-1">
      <!-- Empty cells for padding -->
      <div
        v-for="n in paddingDays"
        :key="`pad-${n}`"
        class="bg-gray-50/50 rounded-md"
        :class="compact ? 'h-8' : (selectable ? 'h-10' : 'h-24')"
      ></div>

      <!-- Days -->
      <!-- Wrapper for tooltip if compact and has events -->
      <component
        :is="compact && getDayEvents(date.fullDate).length ? Tooltip : 'div'"
        v-for="date in daysInMonth"
        :key="date.fullDate"
        :text="compact ? getDayEventsTooltip(date.fullDate) : ''"
        class="contents"
      >
          <div
            class="relative border rounded-lg p-1 transition flex flex-col gap-1 cursor-pointer"
            :class="[
                compact ? 'h-8 justify-center items-center' : (selectable ? 'h-10 justify-center items-center' : 'h-24'),
                getDayClasses(date.fullDate)
            ]"
            @click="handleDayClick(date.fullDate)"
          >
            <span
              class="font-medium"
              :class="[
                  getDayTextClasses(date.fullDate),
                  compact ? 'text-xs' : 'text-sm'
              ]"
            >
              {{ date.day }}
            </span>
            
            <!-- Holidays Label (Full Mode) -->
            <div v-if="!compact && isHoliday(date.fullDate)" class="text-[10px] leading-tight text-red-600 font-medium bg-red-50 px-1 py-0.5 rounded truncate w-full text-center">
                Festivo
            </div>

            <!-- Events/Leaves (Full Mode) -->
            <div v-if="!compact" class="flex flex-col gap-1 overflow-hidden w-full flex-1">
                <!-- Mostrar máximo 2 eventos visibles -->
                <template v-for="(event, idx) in getVisibleEvents(date.fullDate)" :key="event.id">
                    <Tooltip :text="event.tooltip">
                        <div
                            class="text-xs px-1.5 py-0.5 rounded truncate font-medium cursor-help"
                            :class="getEventClassWithStatus(event)"
                        >
                            {{ event.title }}
                        </div>
                    </Tooltip>
                </template>
                
                <!-- Botón "+N más" si hay más eventos -->
                <Popover v-if="getHiddenEventsCount(date.fullDate) > 0">
                    <template #target="{ toggle }">
                        <button 
                            @click.stop="toggle"
                            class="text-xs px-1.5 py-0.5 rounded bg-gray-100 text-gray-600 hover:bg-gray-200 font-medium text-center w-full"
                        >
                            +{{ getHiddenEventsCount(date.fullDate) }} más
                        </button>
                    </template>
                    <template #body>
                        <div class="p-3 w-64 max-h-64 overflow-y-auto bg-white rounded-lg shadow-xl border border-gray-100">
                            <div class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                                {{ formatDateForPopover(date.fullDate) }}
                            </div>
                            <div class="flex flex-col gap-1.5">
                                <div 
                                    v-for="event in getEvents(date.fullDate)" 
                                    :key="event.id"
                                    class="text-xs px-2 py-1.5 rounded font-medium"
                                    :class="getEventClassWithStatus(event)"
                                >
                                    {{ event.title }}
                                    <div v-if="event.tooltip" class="text-[10px] opacity-75 mt-0.5">
                                        {{ event.tooltip }}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </template>
                </Popover>
            </div>
          </div>
      </component>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import dayjs from 'dayjs'
import 'dayjs/locale/es'
import isSameOrAfter from 'dayjs/plugin/isSameOrAfter'
import isSameOrBefore from 'dayjs/plugin/isSameOrBefore'
import isBetween from 'dayjs/plugin/isBetween'
import { Tooltip, Button, Popover } from 'frappe-ui'

dayjs.extend(isSameOrAfter)
dayjs.extend(isSameOrBefore)
dayjs.extend(isBetween)
dayjs.locale('es')

const props = defineProps({
  events: {
    type: Array,
    default: () => []
  },
  // If provided, the calendar is controlled
  modelDate: {
    type: [String, Date, Object], // dayjs object or date
    default: null
  },
  hideControls: {
    type: Boolean,
    default: false
  },
  compact: {
    type: Boolean,
    default: false
  },
  // Selection Props
  selectable: {
      type: Boolean,
      default: false
  },
  selection: {
      type: Object, // { from: 'YYYY-MM-DD', to: 'YYYY-MM-DD' }
      default: () => ({ from: null, to: null })
  },
  holidays: {
      type: Array, // ['YYYY-MM-DD', ...]
      default: () => []
  }
})

const emit = defineEmits(['update:selection'])

const today = dayjs()
const internalCursor = ref(dayjs())

const currentCursor = computed({
    get: () => props.modelDate ? dayjs(props.modelDate) : internalCursor.value,
    set: (val) => {
        if (!props.modelDate) {
            internalCursor.value = val
        }
    }
})

const currentMonthName = computed(() => currentCursor.value.format('MMMM'))
const currentYear = computed(() => currentCursor.value.format('YYYY'))
const weekDays = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sá', 'Do']

const daysInMonth = computed(() => {
  const start = currentCursor.value.startOf('month')
  const days = currentCursor.value.daysInMonth()
  const arr = []
  for (let i = 1; i <= days; i++) {
    const d = start.date(i)
    arr.push({
      day: i,
      fullDate: d.format('YYYY-MM-DD')
    })
  }
  return arr
})

const paddingDays = computed(() => {
  let startDay = currentCursor.value.startOf('month').day()
  if (startDay === 0) startDay = 7
  return startDay - 1
})

function prevMonth() {
  if (!props.modelDate) {
      internalCursor.value = internalCursor.value.subtract(1, 'month')
  }
}

function nextMonth() {
  if (!props.modelDate) {
      internalCursor.value = internalCursor.value.add(1, 'month')
  }
}

function isToday(dateStr) {
  return dateStr === today.format('YYYY-MM-DD')
}

// --- Holiday Logic ---
function isHoliday(dateStr) {
    if (!props.holidays) return false
    return props.holidays.includes(dateStr)
}

function isWeekend(dateStr) {
    const d = dayjs(dateStr)
    return d.day() === 0 || d.day() === 6
}

// --- Selection Logic ---
function handleDayClick(dateStr) {
    if (!props.selectable) return

    let { from, to } = props.selection || {}
    
    // Logic:
    // 1. If nothing selected, set from
    // 2. If from selected but no to:
    //    - If clicked before from, set as new from (and clear old from)
    //    - If clicked after from, set as to
    // 3. If both selected, clear and start new from
    
    if (!from && !to) {
        emit('update:selection', { from: dateStr, to: null })
    } else if (from && !to) {
        if (dayjs(dateStr).isBefore(from)) {
            emit('update:selection', { from: dateStr, to: null }) // Swap/Reset
        } else {
            emit('update:selection', { from, to: dateStr })
        }
    } else {
        // Reset
        emit('update:selection', { from: dateStr, to: null })
    }
}

function isSelected(dateStr) {
    if (!props.selection?.from) return false
    if (props.selection.from === dateStr) return true
    if (props.selection.to === dateStr) return true
    return false
}

function isInRange(dateStr) {
    if (!props.selection?.from || !props.selection?.to) return false
    return dayjs(dateStr).isBetween(props.selection.from, props.selection.to, 'day', '()')
}

// --- Styling ---
function getDayClasses(dateStr) {
    const base = 'border-gray-100 hover:bg-gray-50'
    
    // Selection Mode Styles
    if (props.selectable) {
        if (isSelected(dateStr)) return 'bg-blue-600 border-blue-600 shadow-sm z-10'
        if (isInRange(dateStr)) return 'bg-blue-50 border-blue-100'
        if (isHoliday(dateStr)) return 'bg-red-50 border-red-100'
        if (isWeekend(dateStr)) return 'bg-orange-50/50' // DISTINCT COLOR for weekends
        return base
    }

    // Normal Mode Styles (Dashboard)
    if (isToday(dateStr)) return 'bg-blue-50 border-blue-100'
    if (props.compact && getDayEvents(dateStr).length) {
        return getEventBgClass(getDayEvents(dateStr)[0])
    }
    
    // Highlights for Holidays and Weekends in View Mode
    if (isHoliday(dateStr)) return 'bg-red-50 border-red-100'
    if (isWeekend(dateStr)) return 'bg-orange-50/50'
    
    return base
}

function getDayTextClasses(dateStr) {
    if (props.selectable) {
        if (isSelected(dateStr)) return 'text-white'
        if (isHoliday(dateStr)) return 'text-red-600 font-bold'
        if (isWeekend(dateStr)) return 'text-orange-400'
        return 'text-gray-700'
    }

    if (isToday(dateStr)) return 'text-blue-600'
    if (props.compact && getDayEvents(dateStr).length) return 'text-white'
    
    if (isHoliday(dateStr)) return 'text-red-600 font-bold'
    if (isWeekend(dateStr)) return 'text-orange-400'
    
    return 'text-gray-700'
}


// --- Events Logic (Existing) ---
const MAX_VISIBLE_EVENTS = 2

function getEvents(dateStr) {
  return props.events.filter(e => {
      if (e.from_date && e.to_date) {
          return dayjs(dateStr).isSameOrAfter(e.from_date, 'day') && dayjs(dateStr).isSameOrBefore(e.to_date, 'day')
      }
      return e.date === dateStr
  })
}

// Obtener solo los eventos visibles (máximo MAX_VISIBLE_EVENTS)
function getVisibleEvents(dateStr) {
    return getEvents(dateStr).slice(0, MAX_VISIBLE_EVENTS)
}

// Obtener cantidad de eventos ocultos
function getHiddenEventsCount(dateStr) {
    const total = getEvents(dateStr).length
    return Math.max(0, total - MAX_VISIBLE_EVENTS)
}

// Formatear fecha para el popover
function formatDateForPopover(dateStr) {
    return dayjs(dateStr).format('dddd, D [de] MMMM')
}

// Alias for template readability
const getDayEvents = getEvents

function getDayEventsTooltip(dateStr) {
    const events = getEvents(dateStr)
    if (!events.length) return ''
    return events.map(e => e.tooltip).join('\n')
}

function getEventBgClass(event) {
    if (!event) return ''
    const map = {
        green: 'bg-green-500 border-green-600',
        orange: 'bg-orange-500 border-orange-600',
        red: 'bg-red-500 border-red-600',
        blue: 'bg-blue-500 border-blue-600',
        purple: 'bg-purple-500 border-purple-600',
        pink: 'bg-pink-500 border-pink-600',
        yellow: 'bg-yellow-500 border-yellow-600',
        teal: 'bg-teal-500 border-teal-600',
        indigo: 'bg-indigo-500 border-indigo-600',
        gray: 'bg-gray-500 border-gray-600',
    }
    return map[event.color] || map['gray']
}

function getEventClass(color) {
    const map = {
        green: 'bg-green-100 text-green-700',
        orange: 'bg-orange-100 text-orange-700',
        red: 'bg-red-100 text-red-700',
        blue: 'bg-blue-100 text-blue-700',
        purple: 'bg-purple-100 text-purple-700',
        pink: 'bg-pink-100 text-pink-700',
        yellow: 'bg-yellow-100 text-yellow-700',
        teal: 'bg-teal-100 text-teal-700',
        indigo: 'bg-indigo-100 text-indigo-700',
        gray: 'bg-gray-100 text-gray-700',
    }
    return map[color] || map['gray']
}

// Clase de evento con distinción para solicitudes pendientes
function getEventClassWithStatus(event) {
    const baseClass = getEventClass(event.color)
    
    // Si es solicitud pendiente, añadir borde discontinuo
    if (event.status === 'Abierta') {
        return `${baseClass} border border-dashed border-current opacity-70`
    }
    
    return baseClass
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 2px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e5e7eb;
  border-radius: 10px;
}
</style>
