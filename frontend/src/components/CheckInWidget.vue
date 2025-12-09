<template>
  <div v-if="employee.data" class="bg-white rounded-lg shadow-sm border border-gray-100 p-4 mb-6">
    <div class="flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
            <h2 class="text-lg font-bold text-gray-900">
                {{ __('Hola, {0} 👋', [employee.data.first_name]) }}
            </h2> 
            <div class="font-medium text-sm text-gray-500 mt-1" v-if="lastLog">
                <div v-if="lastLogType === 'check-in'" class="flex items-center space-x-2 text-green-600">
                     <span class="relative flex h-3 w-3">
                      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                      <span class="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                    </span>
                    <span>{{ __('En curso: {0}', [elapsedTime]) }}</span>
                </div>
                 <div v-else class="text-gray-500">
                    <span>{{ __('Total hoy: {0}', [dailyTotal]) }}</span>
                    <span class="mx-1">&middot;</span>
                    <span>{{ __('Último check-out: {0}', [formatTimestamp(lastLog.time)]) }}</span>
                </div>
            </div>
            <div v-else class="font-medium text-sm text-gray-500 mt-1">
                 {{ dayjs().format("D MMMM, YYYY") }}
            </div>
        </div>

        <div v-if="settings.data?.allow_employee_checkin_from_mobile_app">
            <Button
                size="lg"
                variant="solid"
                :theme="nextAction.action === 'IN' ? 'green' : 'gray'"
                @click="openCheckinModal"
                class="!px-6 !py-2 !text-base shadow-sm"
            >
                <template #prefix>
                    <FeatherIcon
                        :name="nextAction.action === 'IN' ? 'log-in' : 'log-out'"
                        class="w-5 h-5 mr-1"
                    />
                </template>
                {{ nextAction.label }}
            </Button>
        </div>
    </div>

    <!-- Check-in Dialog -->
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
dayjs.extend(duration)

// Utility formatters
const formatTimestamp = (time) => {
    return dayjs(time).format("HH:mm")
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
const elapsedTime = ref("00:00:00")
const dailyTotal = ref("0h 0m")
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

const updateTimer = () => {
    if (lastLog.value && lastLog.value.log_type === 'IN') {
        const start = dayjs(lastLog.value.time)
        const now = dayjs()
        const diff = now.diff(start)
        elapsedTime.value = dayjs.duration(diff).format("HH:mm:ss")
    }
}

const calculateDailyTotal = () => {
    if (!checkins.data) return
    
    // Sort ascending for calculation
    const logs = [...checkins.data].sort((a, b) => new Date(a.time) - new Date(b.time))
    let totalMs = 0
    let lastIn = null
    
    logs.forEach(log => {
        if (log.log_type === 'IN') {
            lastIn = dayjs(log.time)
        } else if (log.log_type === 'OUT' && lastIn) {
            totalMs += dayjs(log.time).diff(lastIn)
            lastIn = null
        }
    })
    
    // If still checked in, add time until now? Usually daily total implies "completed" time, 
    // but user might want to see accumulation. Let's keep it strictly completed pairs to avoid confusion with "Elapsed".
    // Or we could show "Completed: Xh Ym". 
    // The request said "indicator of total time of the day" when checking out.
    // So usually sum of completed sessions.
    
    const d = dayjs.duration(totalMs)
    dailyTotal.value = `${Math.floor(d.asHours())}h ${d.minutes()}m`
}

watch(lastLog, (newVal) => {
    if (timerInterval) clearInterval(timerInterval)
    
    if (newVal && newVal.log_type === 'IN') {
        updateTimer()
        timerInterval = setInterval(updateTimer, 1000)
    } else {
        elapsedTime.value = "00:00:00"
    }
    calculateDailyTotal()
}, { immediate: true })

onBeforeUnmount(() => {
    if (timerInterval) clearInterval(timerInterval)
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
