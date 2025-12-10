<template>
  <div v-if="employee.data" class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 mb-4">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        
        <!-- LEFT COLUMN: Greeting & Actions -->
        <div class="flex flex-col justify-center items-start space-y-4">
             <div>
                <h2 class="text-xl font-bold text-gray-900 leading-tight">
                    {{ __('Hola, {0} 👋', [employee.data.first_name]) }}
                </h2>
                <p class="text-sm text-gray-500 mt-1">
                    {{ __('Registra tu jornada laboral') }}
                </p>
             </div>

             <div v-if="settings.data?.allow_employee_checkin_from_mobile_app" class="w-full">
                <Button
                    size="lg"
                    variant="solid"
                    :theme="nextAction.action === 'IN' ? 'green' : 'gray'"
                    @click="openCheckinModal"
                    class="!px-6 !py-2 !text-base shadow-md w-full md:w-auto justify-center"
                >
                    <template #prefix>
                        <FeatherIcon
                            :name="nextAction.action === 'IN' ? 'log-in' : 'log-out'"
                            class="w-6 h-6 mr-2"
                        />
                    </template>
                    {{ nextAction.label }}
                </Button>
                <!-- Status Badge -->
                 <div class="mt-4 flex items-center space-x-2">
                    <div v-if="lastLogType === 'check-in'" class="flex items-center text-green-600 font-medium">
                        <span class="relative flex h-3 w-3 mr-2">
                          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                          <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                        </span>
                        {{ __('Actualmente Trabajando') }}
                    </div>
                     <div v-else class="flex items-center text-gray-500 font-medium">
                        <span class="h-3 w-3 rounded-full bg-gray-300 mr-2"></span>
                        {{ __('Jornada Pausada / No iniciada') }}
                    </div>
                 </div>
            </div>
        </div>

        <!-- RIGHT COLUMN: Stats & Timers -->
        <div class="bg-gray-50 rounded-lg p-4 border border-gray-100 flex flex-col justify-center space-y-4">
            <!-- Date -->
            <div class="text-right border-b border-gray-200 pb-2">
                 <div class="text-2xl font-bold text-gray-800">{{ dayjs().format("D") }}</div>
                 <div class="text-base text-gray-500 uppercase tracking-wide">{{ dayjs().format("MMMM YYYY") }}</div>
                 <div class="text-xs text-gray-400 mt-1">{{ dayjs().format("dddd") }}</div>
            </div>

            <!-- Counters -->
            <div class="grid grid-cols-2 gap-3">
                <!-- Work Timer -->
                <div class="bg-white p-3 rounded shadow-sm border border-gray-100">
                    <div class="text-[10px] uppercase font-bold text-gray-400 tracking-wider mb-1">{{ __('Tiempo Trabajado') }}</div>
                    <div class="text-xl font-mono font-semibold text-gray-800">
                        {{ formatDuration(totalWorkSeconds) }}
                    </div>
                </div>

                 <!-- Rest Timer -->
                <div class="bg-white p-3 rounded shadow-sm border border-gray-100">
                    <div class="text-[10px] uppercase font-bold text-gray-400 tracking-wider mb-1">{{ __('Tiempo Descanso') }}</div>
                    <div class="text-xl font-mono font-semibold text-gray-500">
                         {{ formatDuration(totalRestSeconds) }}
                    </div>
                </div>
            </div>
            
            <div class="text-xs text-center text-gray-400">
                 {{ __('Último registro: {0}', [lastLog ? formatTimestamp(lastLog.time) : '--:--']) }}
            </div>
        </div>

    </div>

    <!-- Check-in Dialog (Same as before) -->
    <Dialog
        v-model="showModal"
        :options="{
            title: nextAction.label,
            size: 'md'
        }"
    >
        <template #body-content>
            <div class="flex flex-col items-center justify-center gap-4 py-6">
                <div class="text-center">
                    <div class="font-bold text-3xl mb-1">
                        {{ dayjs(checkinTimestamp).format("HH:mm:ss") }}
                    </div>
                    <div class="font-medium text-gray-500">
                        {{ dayjs().format("D MMM, YYYY") }}
                    </div>
                </div>

                <div v-if="settings.data?.allow_geolocation_tracking" class="w-full">
                    <div v-if="locationStatus" class="font-medium text-gray-500 text-sm mb-2 text-center">
                        {{ locationStatus }}
                    </div>
                    
                    <div v-if="latitude && longitude" class="rounded overflow-hidden w-full h-48 border bg-gray-50">
                        <iframe
                            width="100%"
                            height="100%"
                            frameborder="0"
                            scrolling="no"
                            marginheight="0"
                            marginwidth="0"
                            style="border: 0"
                            :src="`https://maps.google.com/maps?q=${latitude},${longitude}&hl=es&z=15&amp;output=embed`"
                        >
                        </iframe>
                    </div>
                    <div v-else class="h-48 bg-gray-100 flex items-center justify-center text-gray-400 rounded">
                        {{ __('Obteniendo ubicación...') }}
                    </div>
                </div>
            </div>
        </template>
        <template #actions>
            <Button
                variant="solid"
                class="w-full"
                size="lg"
                :loading="submitting"
                @click="submitLog(nextAction.action)"
            >
                {{ __('Confirmar {0}', [nextAction.label]) }}
            </Button>
        </template>
    </Dialog>

  </div>
</template>

<script setup>
import { createResource, createListResource, toast, FeatherIcon, Button, Dialog } from "frappe-ui"
import { computed, ref, onMounted, onBeforeUnmount, watch } from "vue"
import dayjs from "dayjs"
import duration from "dayjs/plugin/duration"
import 'dayjs/locale/es' 
dayjs.locale('es')
dayjs.extend(duration)

// Utility formatters
const formatTimestamp = (time) => {
    return dayjs(time).format("HH:mm")
}

const formatDuration = (seconds) => {
    const d = dayjs.duration(seconds, 'seconds')
    const h = Math.floor(d.asHours())
    const m = d.minutes()
    const s = d.seconds()
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

const __ = (text, args) => {
  if (!text) return "";
  let translated = text;
  if (args && args.length) {
      args.forEach((arg, i) => {
          translated = translated.replace(`{${i}}`, arg);
      });
  }
  return translated;
}

const DOCTYPE = "Employee Checkin"

const checkinTimestamp = ref(null)
const latitude = ref(0)
const longitude = ref(0)
const locationStatus = ref("")
const showModal = ref(false)
const submitting = ref(false)

const totalWorkSeconds = ref(0)
const totalRestSeconds = ref(0)
let timerInterval = null

// Fetch Employee Info
const employee = createResource({
    url: "hrms.api.get_current_employee_info",
    auto: true,
})

// Settings
const settings = createResource({
    url: "hrms.api.get_hr_settings",
    auto: true,
})

// Checkins List - Fetch today's logs
const checkins = createListResource({
    doctype: DOCTYPE,
    fields: ["name", "log_type", "time"],
    orderBy: "time desc",
    pageLength: 50,
    auto: false
})

// Watch for employee load to fetch checkins
watch(() => employee.data, (newVal) => {
    if (newVal && newVal.name) {
        checkins.filters = {
            employee: newVal.name,
             time: [">=", dayjs().startOf('day').format("YYYY-MM-DD HH:mm:ss")]
        }
        checkins.reload()
    }
})

const lastLog = computed(() => {
    if (checkins.list.loading || !checkins.data || checkins.data.length === 0) return null
    return checkins.data[0]
})

const lastLogType = computed(() => {
    if (!lastLog.value) return "check-out"
    return lastLog.value.log_type === "IN" ? "check-in" : "check-out"
})

const nextAction = computed(() => {
    if (!lastLog.value || lastLog.value.log_type === "OUT") {
        return { action: "IN", label: __("Entrar") }
    }
    return { action: "OUT", label: __("Salir") }
})

// Main Logic for Counting
const calculateTimers = () => {
    if (!checkins.data) return

    // Sort ascending: Earliest first
    const logs = [...checkins.data].sort((a, b) => new Date(a.time) - new Date(b.time))
    
    let workSec = 0
    let restSec = 0
    let lastIn = null
    let lastOut = null

    // Iterate through logs to build completed intervals
    logs.forEach((log, index) => {
        if (log.log_type === 'IN') {
             // If we had a previous OUT, the gap between that OUT and this IN is rest
             if (lastOut) {
                 restSec += dayjs(log.time).diff(lastOut, 'second')
                 lastOut = null // Consumed
             }
             lastIn = dayjs(log.time)
        } else if (log.log_type === 'OUT') {
            if (lastIn) {
                // Completed work session
                workSec += dayjs(log.time).diff(lastIn, 'second')
                lastIn = null // Consumed
            }
            lastOut = dayjs(log.time)
        }
    })

    // Handle "Active" states (Live Ticking)
    const now = dayjs()
    
    // If currently checked IN (lastIn is set and not null because we exhausted logs)
    // Actually, based on logic: if last log was IN, lastIn will be set.
    if (lastIn) {
        workSec += now.diff(lastIn, 'second')
    }



    totalWorkSeconds.value = workSec
    totalRestSeconds.value = restSec
}

onMounted(() => {
    timerInterval = setInterval(() => {
        calculateTimers()
    }, 1000)
})

onBeforeUnmount(() => {
    if (timerInterval) clearInterval(timerInterval)
})

// Watch checkins reload to recalc immediately
watch(() => checkins.data, () => {
    calculateTimers()
})


const handleLocationSuccess = (position) => {
    latitude.value = position.coords.latitude
    longitude.value = position.coords.longitude

    locationStatus.value = [
        __("Latitud: {0}°", [Number(latitude.value).toFixed(5)]),
        __("Longitud: {0}°", [Number(longitude.value).toFixed(5)]),
    ].join(", ")
}

const handleLocationError = (error) => {
    locationStatus.value = "No se pudo obtener tu ubicación"
    if (error) locationStatus.value += `: ERROR(${error.code}): ${error.message}`
}

const fetchLocation = () => {
    if (!navigator.geolocation) {
        locationStatus.value = __("Geolocalización no soportada por tu navegador")
    } else {
        locationStatus.value = __("Localizando...")
        navigator.geolocation.getCurrentPosition(handleLocationSuccess, handleLocationError)
    }
}

const openCheckinModal = () => {
    checkinTimestamp.value = dayjs().format("YYYY-MM-DD HH:mm:ss")
    showModal.value = true
    if (settings.data?.allow_geolocation_tracking) {
        fetchLocation()
    }
}

const submitLog = async (logType) => {
    const actionLabel = logType === "IN" ? __("Entrada") : __("Salida")
    submitting.value = true

    try {
        await checkins.insert.submit({
            employee: employee.data.name,
            log_type: logType,
            time: checkinTimestamp.value,
            latitude: latitude.value,
            longitude: longitude.value,
        })
        
        toast({
            title: __("Éxito"),
            text: __("¡{0} registrada correctamente!", [actionLabel]),
            icon: "check-circle",
            position: "bottom-center",
            iconClasses: "text-green-500",
        })
        
        showModal.value = false
        checkins.reload()
        
    } catch (error) {
        toast({
            title: __("Error"),
            text: __("¡Fallo al registrar {0}!", [actionLabel]),
            icon: "alert-circle",
            position: "bottom-center",
            iconClasses: "text-red-500",
        })
        console.error(error)
    } finally {
        submitting.value = false
    }
}

</script>
