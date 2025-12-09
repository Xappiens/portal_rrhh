<template>
  <div class="flex flex-col h-full overflow-hidden">
    <div class="flex-1 overflow-y-auto p-5">
      <div class="mb-6 flex items-center justify-between">
        <h1 class="text-2xl font-bold text-gray-900">{{ __('Registro de Horas') }}</h1>
        <div class="flex space-x-2">
          <Button
            v-if="viewMode === 'edit'"
            variant="outline"
            @click="viewMode = 'list'"
          >
            {{ __('Volver al listado') }}
          </Button>
          <Button
            v-if="viewMode === 'list'"
            variant="solid"
            theme="gray"
            size="md"
            label="Nuevo Registro Semanal"
            :loading="loading"
            @click="createNewTimesheet"
            class="!bg-gray-900 !text-white hover:!bg-gray-800"
          >
            {{ __('Nuevo Registro Semanal') }}
          </Button>
        </div>
      </div>

      <CheckInWidget />

      <!-- LIST VIEW -->
      <div v-if="viewMode === 'list'" class="bg-white rounded shadow p-4">
        <div v-if="loading" class="text-center py-4">{{ __('Cargando...') }}</div>
        <div v-else-if="timesheets.length === 0" class="text-center py-4 text-gray-500">
          {{ __('No hay registros de horas. Crea uno nuevo.') }}
        </div>
        <table v-else class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b">
              <th class="p-2">{{ __('Semana') }}</th>
              <th class="p-2">{{ __('Horas Totales') }}</th>
              <th class="p-2">{{ __('Estado') }}</th>
              <th class="p-2">{{ __('Acciones') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="ts in timesheets"
              :key="ts.name"
              class="border-b hover:bg-gray-50"
            >
              <td class="p-2">
                {{ formatDate(ts.start_date) }} - {{ formatDate(ts.end_date) }}
              </td>
              <td class="p-2">{{ ts.total_hours }} h</td>
              <td class="p-2">
                <Badge :variant="getStatusVariant(ts.status)">{{ ts.status }}</Badge>
              </td>
              <td class="p-2">
                <Button size="sm" variant="ghost" @click="editTimesheet(ts.name)">
                  {{ __('Ver / Editar') }}
                </Button>
              </td>
            </tr>
          </tbody>
        </table>
        
        <!-- Pagination / Load More -->
        <div class="mt-4 text-center" v-if="hasMoreTimesheets">
            <Button
                variant="subtle"
                :loading="loadingMore"
                @click="loadMoreTimesheets"
            >
                {{ __('Cargar anteriores') }}
            </Button>
        </div>
      </div>

      <!-- EDIT VIEW -->
      <div v-else class="bg-white rounded shadow p-4">
        <div class="mb-4 flex items-center justify-between bg-gray-50 p-3 rounded">
          <div class="flex items-center space-x-4">
            <Button icon="chevron-left" variant="ghost" @click="changeWeek(-1)" :disabled="!isNew" />
            <div class="text-lg font-medium">
              {{ __('Semana del') }} {{ formatDate(currentStartDate) }} {{ __('al') }} {{ formatDate(currentEndDate) }}
            </div>
             <Button icon="chevron-right" variant="ghost" @click="changeWeek(1)" :disabled="!isNew" />
          </div>
          <div>
            <Badge size="lg" :variant="getStatusVariant(currentTimesheet.status)">
              {{ currentTimesheet.status || 'Borrador' }}
            </Badge>
          </div>
        </div>

        <div class="mb-4">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
             <div class="bg-blue-50 p-3 rounded border border-blue-100">
               <span class="block text-xs uppercase text-blue-500 font-bold tracking-wider">{{ __('Total Horas') }}</span>
               <span class="text-2xl font-bold text-blue-700">{{ totalHours }} h</span>
             </div>
          </div>
        </div>
        
        <!-- Logs Editor -->
        <h3 class="text-lg font-semibold mb-2">{{ __('Detalle de Actividad') }}</h3>
        
        <div class="space-y-4">
            <!-- Headers -->
            <div class="grid grid-cols-12 gap-2 text-sm font-medium text-gray-500 border-b pb-2">
                <div class="col-span-2">{{ __('Fecha') }}</div>
                <div class="col-span-3">{{ __('Sede') }}</div>
                <div class="col-span-2">{{ __('Expediente') }}</div>
                <div class="col-span-3">{{ __('Curso') }}</div>
                <div class="col-span-1">{{ __('Horas') }}</div>
                <div class="col-span-1 text-right">{{ __('Acciones') }}</div>
            </div>

            <!-- Rows -->
            <div 
                v-for="(log, index) in logs" 
                :key="index" 
                class="grid grid-cols-12 gap-2 items-start border-b py-2"
            >
                <!-- Date -->
                <div class="col-span-2">
                    <select
                        v-model="log.date"
                        class="form-select w-full text-sm border-gray-300 rounded focus:ring-blue-500 py-1.5"
                        :disabled="isReadOnly"
                    >
                        <option 
                            v-for="d in weekDays.map(d => ({ label: d.label + ' (' + formatDateShort(d.date) + ')', value: d.date }))" 
                            :key="d.value" 
                            :value="d.value"
                        >
                            {{ d.label }}
                        </option>
                    </select>
                </div>
                <!-- Sede -->
                <div class="col-span-3">
                    <Autocomplete
                        v-model="log.sede"
                        :options="sedes.map(s => ({ label: s.room_name, value: s.name }))"
                        :disabled="isReadOnly"
                        placeholder="Seleccionar Sede"
                    />
                </div>
                <!-- Expediente -->
                 <div class="col-span-2">
                    <Autocomplete
                        v-model="log.expediente"
                        :options="programs.map(p => ({ label: p.custom_num_de_expediente, value: p.name }))"
                        :disabled="isReadOnly"
                        placeholder="Buscar Exp..."
                        @update:query="(q) => searchPrograms(q)"
                        @update:modelValue="() => { log.course = null; }"
                    />
                </div>
                <!-- Curso -->
                 <div class="col-span-3" @click.capture="searchCourses('', log.expediente)">
                     <Autocomplete
                        v-model="log.course"
                        :options="courses.map(c => ({ label: c.custom_display_identifier || c.course_name, value: c.name }))"
                        :disabled="isReadOnly || !log.expediente"
                        placeholder="Buscar Curso..."
                        @update:query="(q) => searchCourses(q, log.expediente)"
                    />
                </div>
                <!-- Hours -->
                 <div class="col-span-1">
                    <Input
                        type="number"
                        v-model.number="log.hours"
                        :disabled="isReadOnly"
                        min="0"
                        step="0.5"
                    />
                </div>
                <!-- Actions -->
                <div class="col-span-1 text-right pt-1">
                    <Button 
                        v-if="!isReadOnly"
                        icon="trash-2" 
                        variant="ghost" 
                        class="text-red-500 hover:text-red-700"
                        @click="removeLog(index)"
                    />
                </div>
            </div>

            <!-- Add Row Button -->
            <div v-if="!isReadOnly" class="pt-2">
                <Button variant="outline" icon="plus" class="w-full" @click="addLog">
                    {{ __('Añadir Registro') }}
                </Button>
            </div>
        </div>

        <!-- Footer Actions -->
        <div class="mt-8 flex justify-end space-x-3 pt-4 border-t">
             <Button 
                v-if="!isReadOnly"
                variant="subtle" 
                @click="save(false)"
                :loading="saving"
            >
                {{ __('Guardar Borrador') }}
            </Button>
             <Button 
                v-if="!isReadOnly"
                variant="solid" 
                @click="attemptSubmit"
                :loading="saving"
            >
                {{ __('Validar y Enviar') }}
            </Button>
        </div>

      </div>
    </div>
    
    <!-- Warning Dialog -->
    <Dialog 
        v-model="showWarningDialog"
        :title="__('Advertencia de Envío')"
    >
        <template #body-content>
            <p>{{ warningMessage }}</p>
            <p class="mt-2">{{ __('¿Estás seguro de que quieres validar este registro ahora? Ya no podrás editarlo después.') }}</p>
        </template>
        <template #actions>
            <Button variant="outline" @click="showWarningDialog = false">{{ __('Cancelar') }}</Button>
            <Button variant="solid" theme="red" @click="confirmSubmit">{{ __('Sí, Validar') }}</Button>
        </template>
    </Dialog>

  </div>
</template>

<script setup>
import CheckInWidget from '@/components/CheckInWidget.vue'
import { ref, computed, onMounted } from 'vue'
import { createResource, Button, Badge, call, Dialog, FeatherIcon, Autocomplete, Input } from 'frappe-ui'
import dayjs from 'dayjs'
import 'dayjs/locale/es'

dayjs.locale('es')

// State
const viewMode = ref('list') // 'list' or 'edit'
const loading = ref(false)
const loadingMore = ref(false)
const saving = ref(false)
const timesheets = ref([])
const hasMoreTimesheets = ref(true)
const start = ref(0)
const PAGE_LENGTH = 20
const sedes = ref([])
const courses = ref([])
const programs = ref([])
const userSettings = ref({})

// Current Edit State
const currentTimesheet = ref({})
const currentStartDate = ref(dayjs().startOf('week').format('YYYY-MM-DD'))
const logs = ref([])
const isNew = ref(false)
const showWarningDialog = ref(false)
const warningMessage = ref('')

// Computed
const currentEndDate = computed(() => {
    return dayjs(currentStartDate.value).endOf('week').format('YYYY-MM-DD')
})

const weekDays = computed(() => {
    const days = []
    let start = dayjs(currentStartDate.value)
    for (let i = 0; i < 7; i++) {
        days.push({
            date: start.add(i, 'day').format('YYYY-MM-DD'),
            label: start.add(i, 'day').format('dddd') // lunes, martes...
        })
    }
    return days
})

const totalHours = computed(() => {
    return logs.value.reduce((sum, log) => sum + (parseFloat(log.hours) || 0), 0)
})

const isReadOnly = computed(() => {
    return currentTimesheet.value.docstatus === 1
})

// Resources
const fetchTimesheets = async (reset = true) => {
    if (reset) {
        loading.value = true
        start.value = 0
        timesheets.value = []
        hasMoreTimesheets.value = true
    } else {
        loadingMore.value = true
    }
    
    try {
        const data = await call('portal_rrhh.api.timesheets.get_timesheets', {
            start: start.value,
            page_length: PAGE_LENGTH
        })
        
        if (data && data.length > 0) {
            timesheets.value = reset ? data : [...timesheets.value, ...data]
            start.value += PAGE_LENGTH
            if (data.length < PAGE_LENGTH) {
                hasMoreTimesheets.value = false
            }
        } else {
            hasMoreTimesheets.value = false
        }
    } catch (error) {
        console.error(error)
    } finally {
        loading.value = false
        loadingMore.value = false
    }
}

const loadMoreTimesheets = () => {
    fetchTimesheets(false)
}

const fetchMetadata = async () => {
    try {
        const [sedesData, coursesData, programsData, settingsData] = await Promise.all([
            call('portal_rrhh.api.timesheets.get_sedes'),
            call('portal_rrhh.api.timesheets.get_courses'),
            call('portal_rrhh.api.timesheets.get_programs'),
            call('portal_rrhh.api.timesheets.get_user_settings')
        ])
        sedes.value = sedesData || []
        courses.value = coursesData || []
        programs.value = programsData || []
        userSettings.value = settingsData || {}
    } catch (error) {
        console.error(error)
    }
}

// Methods
const debounce = (fn, delay) => {
    let timeoutId
    return (...args) => {
        clearTimeout(timeoutId)
        timeoutId = setTimeout(() => fn(...args), delay)
    }
}

const searchCourses = debounce(async (query, program) => {
    // Force allow empty query if we have a program filter? Maybe, to show initial list? 
    // But usually user types. If they focus without typing, Autocomplete might trigger query=''
    // Let's allow empty query if program is set to fetch initial filtered list.
    if (!query && !program) return
    
    // Autocomplete usually sends string or object? 'query' is string text.
    // 'program' is passed from template as log.expediente (which might be object {label, value} or value string depending on v-model state)
    // IMPORTANT: log.expediente v-model value. Frappe-UI Autocomplete v-model is usually value.
    // However, if we bound objects in `options`, it might return object.
    // But in my replace block, options are `.map(p => ({ label: ..., value: ... }))`
    // So v-model should be the `value` (which is name).
    // EXCEPT if `search` event doesn't have access to row context easily... oh wait, I passed `log.expediente` in the template call.
    // So 'program' here is the v-model value (string name).
    // BUT what if log.expediente is the object because of initial load mapping?
    // In editTimesheet I mapped: `expediente: programs.value.find...?.name || l.expediente` which is name string.
    // So it should be string.
    
    const programName = (typeof program === 'object' && program !== null) ? program.value : program

    try {
        const data = await call('portal_rrhh.api.timesheets.get_courses', { txt: query, program: programName })
        courses.value = data || []
    } catch (e) {
        console.error(e)
    }
}, 300)

const searchPrograms = debounce(async (query) => {
    if (!query) return
    try {
        const data = await call('portal_rrhh.api.timesheets.get_programs', { txt: query })
        programs.value = data || []
    } catch (e) {
        console.error(e)
    }
}, 300)

const formatDate = (date) => dayjs(date).format('DD/MM/YYYY')
const formatDateShort = (date) => dayjs(date).format('DD/MM')

const getStatusVariant = (status) => {
    if (status === 'Submitted' || status === 'Aprobado') return 'green'
    if (status === 'Draft' || status === 'Borrador') return 'gray'
    if (status === 'Rejected' || status === 'Rechazado') return 'red'
    return 'blue'
}

const createNewTimesheet = () => {
    currentTimesheet.value = { status: 'Borrador' }
    // Set to current week
    currentStartDate.value = dayjs().startOf('week').format('YYYY-MM-DD')
    logs.value = []
    // Add one empty row for Monday
    logs.value.push({ 
        date: currentStartDate.value, 
        hours: 0, 
        sede: userSettings.value.default_sede ? { label: userSettings.value.default_sede_name, value: userSettings.value.default_sede } : null,
        course: null, 
        expediente: null 
    })
    isNew.value = true
    viewMode.value = 'edit'
}

const editTimesheet = async (name) => {
    loading.value = true
    try {
        const data = await call('portal_rrhh.api.timesheets.get_timesheet_details', { name })
        currentTimesheet.value = data
        currentStartDate.value = data.start_date
        // Populate logs from custom_sede_time_logs
        logs.value = (data.custom_sede_time_logs || []).map(l => ({
            date: l.date,
            hours: l.hours,
            sede: l.sede && sedes.value.find(s => s.name === l.sede) ? { label: sedes.value.find(s => s.name === l.sede).room_name, value: l.sede } : l.sede,
            course: courses.value.find(oc => oc.name === l.course) ? { label: courses.value.find(oc => oc.name === l.course).custom_display_identifier || courses.value.find(oc => oc.name === l.course).course_name, value: l.course } : l.course,
            expediente: programs.value.find(op => op.name === l.expediente) ? { label: programs.value.find(op => op.name === l.expediente).custom_num_de_expediente, value: l.expediente } : l.expediente
        }))
        
        isNew.value = false
        viewMode.value = 'edit'
    } catch (error) {
        console.error(error)
    } finally {
        loading.value = false
    }
}

const changeWeek = (offset) => {
    currentStartDate.value = dayjs(currentStartDate.value).add(offset, 'week').format('YYYY-MM-DD')
}

const addLog = () => {
    // Default to first day of week or last used date
    const lastLog = logs.value[logs.value.length - 1]
    const date = lastLog ? lastLog.date : currentStartDate.value
    logs.value.push({ 
        date, 
        hours: 0, 
        sede: userSettings.value.default_sede ? { label: userSettings.value.default_sede_name, value: userSettings.value.default_sede } : null,
        course: null, 
        expediente: null 
    })
}

const removeLog = (index) => {
    logs.value.splice(index, 1)
}

const save = async (isSubmitting = false) => {
    saving.value = true
    try {
        const payload = {
            name: currentTimesheet.value.name,
            start_date: currentStartDate.value,
            end_date: currentEndDate.value,
            logs: logs.value.map(l => ({
                ...l,
                sede: l.sede?.value || l.sede,
                course: l.course?.value || l.course,
                expediente: l.expediente?.value || l.expediente
            }))
        }
        
        const result = await call('portal_rrhh.api.timesheets.save_timesheet', { data: JSON.stringify(payload) })
        currentTimesheet.value = result
        isNew.value = false 
        
        return result
    } catch (e) {
        console.error(e)
    } finally {
        saving.value = false
    }
}

const attemptSubmit = async () => {
    const now = dayjs()
    const weekEnd = dayjs(currentEndDate.value)
    
    let warnings = []
    
    if (now.isBefore(weekEnd) && totalHours.value < 40) {
        warnings.push("La semana aún no ha terminado y/o parece que no has completado una jornada completa.")
    }

    warningMessage.value = warnings.length > 0 
        ? warnings.join("\n") + "\n" + __('Recuerda: El timesheet debe validarse al final de la semana o con todas las horas registradas.')
        : __('Vas a cerrar y validar este registro de horas.')
        
    showWarningDialog.value = true
}

const confirmSubmit = async () => {
    showWarningDialog.value = false
    saving.value = true
    
    try {
        const saved = await save(true)
        if (saved) {
             await call('portal_rrhh.api.timesheets.submit_timesheet', { name: saved.name })
             await editTimesheet(saved.name)
        }
    } catch (e) {
        console.error(e)
    } finally {
        saving.value = false
    }
}

const __ = (text) => text 

// Init
onMounted(() => {
    fetchTimesheets()
    fetchMetadata()
})
</script>
