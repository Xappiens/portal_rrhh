<template>
  <div class="flex flex-col h-full overflow-hidden">
    <div class="flex-1 overflow-y-auto p-5">
      <div class="mb-6 flex items-center justify-between">
        <h1 class="text-2xl font-bold text-gray-900">{{ __('Registro de Horas') }}</h1>
        <div class="flex space-x-2">
          <Button
            v-if="viewMode === 'edit'"
            appearance="white"
            @click="goBackToList"
          >
            {{ __('Volver al listado') }}
          </Button>
          <Button
            v-if="viewMode === 'list'"
            appearance="primary"
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



      <!-- LIST VIEW -->
      <div v-if="viewMode === 'list'" class="bg-white rounded shadow p-4">
        <div v-if="loading" class="text-center py-4">{{ __('Cargando...') }}</div>
        <div v-else-if="timesheets.length === 0" class="text-center py-4 text-gray-500">
          {{ __('No hay registros de horas. Crea uno nuevo.') }}
        </div>
        <div v-else class="divide-y">
            <ListItem
              v-for="ts in timesheets"
              :key="ts.name"
              :title="`Semana #${dayjs(ts.start_date).week()} • ${formatDate(ts.start_date)} - ${formatDate(dayjs(ts.start_date).add(4, 'day').format('YYYY-MM-DD'))}`"
            >
                <template #actions>
                    <div class="flex items-center space-x-4">
                        <div class="flex items-center space-x-3">
                             <span class="text-gray-900 font-medium">{{ ts.total_hours }} h</span>
                             <Badge :color="getStatusColor(ts.status)">{{ getStatusLabel(ts.status) }}</Badge>
                        </div>
                        
                        <div class="flex items-center space-x-1">
                          <Button 
                            v-if="ts.status === 'Draft' || ts.status === 'Borrador'"
                            size="sm" 
                            appearance="minimal" 
                            class="text-red-500 hover:text-red-700"
                            @click="deleteTimesheet(ts.name)" 
                            :title="__('Eliminar')"
                          >
                            <FeatherIcon name="trash-2" class="w-4 h-4" />
                          </Button>
                          <Button size="sm" appearance="minimal" @click="duplicateTimesheet(ts.name)" :title="__('Duplicar')">
                            <FeatherIcon name="copy" class="w-4 h-4" />
                          </Button>
                          <Button size="sm" appearance="minimal" @click="editTimesheet(ts.name)">
                            {{ __('Ver / Editar') }}
                          </Button>
                        </div>
                    </div>
                </template>
            </ListItem>
        </div>
        
        <!-- Pagination / Load More -->
        <div class="mt-4 text-center border-t pt-4" v-if="hasMoreTimesheets">
            <Button
                appearance="secondary"
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
            <Button icon="chevron-left" appearance="minimal" @click="changeWeek(-1)" :disabled="!isNew" />
            <div class="text-lg font-medium">
              {{ __('Semana del') }} {{ formatDate(currentStartDate) }} {{ __('al') }} {{ formatDate(currentEndDate) }}
            </div>
             <Button icon="chevron-right" appearance="minimal" @click="changeWeek(1)" :disabled="!isNew" />
          </div>
          <div class="flex items-center space-x-4">
            <div class="flex items-center space-x-2">
                <span class="text-xs uppercase text-gray-500 font-bold tracking-wider">{{ __('Total') }}:</span>
                <span class="text-lg font-bold" :class="totalHours > 39 ? 'text-red-600' : 'text-blue-700'">{{ totalHours }} h</span>
            </div>
            <Badge size="lg" :color="getStatusColor(currentTimesheet.status)">
              {{ getStatusLabel(currentTimesheet.status || 'Borrador') }}
            </Badge>
          </div>
        </div>
        
        <!-- Logs Editor -->
        <h3 class="text-lg font-semibold mb-2">{{ __('Detalle de Actividad') }}</h3>
        
        <div class="space-y-4">
            <!-- Headers -->
            <div class="grid grid-cols-12 gap-2 text-sm font-medium text-gray-500 border-b pb-2">
                <div class="col-span-2">{{ __('Fecha') }}</div>
                <div class="col-span-3">{{ __('Plan Formativo') }} <span class="text-xs text-gray-400">({{ planes.length }})</span></div>
                <div class="col-span-2">{{ __('Expediente') }} <span class="text-xs text-gray-400">({{ programs.length }})</span></div>
                <div class="col-span-3">{{ __('Curso') }} <span class="text-xs text-gray-400">({{ courses.length }})</span></div>
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
                    <Input
                        type="select"
                        v-model="log.date"
                        :options="weekDays"
                        :disabled="isReadOnly"
                    />
                </div>
                <!-- Plan Formativo -->
                <div class="col-span-3">
                    <SearchableAutocomplete
                        v-model="log.plan"
                        :options="[
                            { label: '📋 Todos (General)', value: '__todos__' },
                            ...planes.map(p => ({ 
                                label: (p.n_plan_formativo ? `[${p.n_plan_formativo}] ` : '') + (p.custom_descripción_del_plan || p.name), 
                                value: p.name 
                            }))
                        ]"
                        :disabled="isReadOnly"
                        placeholder="Buscar Plan..."
                        @update:query="(q) => searchPlanes(q)"
                        @update:modelValue="(val) => updatePlan(log, val)"
                    />
                </div>
                <!-- Expediente -->
                 <div class="col-span-2" @click.capture="searchPrograms('', log.plan)">
                    <SearchableAutocomplete
                        v-model="log.expediente"
                        :options="[
                            { label: '📋 Todos', value: '__todos__' },
                            ...programs.map(p => ({ 
                                label: (p.custom_num_de_expediente ? `[${p.custom_num_de_expediente}] ` : '') + (p.program_name || p.name), 
                                value: p.name, 
                                link_plan: p.custom_plan 
                            }))
                        ]"
                        :disabled="isReadOnly"
                        placeholder="Buscar Exp..."
                        @update:query="(q) => searchPrograms(q, log.plan)"
                        @update:modelValue="(val) => updateProgram(log, val)"
                    />
                </div>
                <!-- Curso -->
                 <div class="col-span-3" @click.capture="searchCourses('', log.expediente, log.plan)">
                     <SearchableAutocomplete
                        v-model="log.course"
                        :options="[
                            { label: '📋 Todos', value: '__todos__' },
                            ...courses.map(c => ({ 
                                label: (c.custom_display_identifier ? `[${c.custom_display_identifier}] ` : '') + (c.course_name || c.name), 
                                value: c.name,
                                link_program: c.expediente,
                                link_plan: c.custom_plan
                            }))
                        ]"
                        :disabled="isReadOnly"
                        placeholder="Buscar Curso..."
                        @update:query="(q) => searchCourses(q, log.expediente, log.plan)"
                        @update:modelValue="(val) => updateCourse(log, val)"
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
                        appearance="minimal" 
                        class="text-red-500 hover:text-red-700"
                        @click="removeLog(index)"
                    />
                </div>
            </div>

            <!-- Add Row Button -->
            <div v-if="!isReadOnly" class="pt-2">
                <Button appearance="white" icon="plus" class="w-full" @click="addLog">
                    {{ __('Añadir Registro') }}
                </Button>
            </div>
        </div>

        <!-- Footer Actions -->
        <div class="mt-8 flex justify-end space-x-3 pt-4 border-t">
             <Button 
                v-if="!isReadOnly"
                appearance="secondary" 
                @click="save(false)"
                :loading="saving"
            >
                {{ __('Guardar Borrador') }}
            </Button>
             <Button 
                v-if="!isReadOnly && !isNew"
                appearance="primary" 
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
            <Button appearance="white" @click="showWarningDialog = false">{{ __('Cancelar') }}</Button>
            <Button appearance="danger" @click="confirmSubmit">{{ __('Sí, Validar') }}</Button>
        </template>
    </Dialog>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import SearchableAutocomplete from '../components/SearchableAutocomplete.vue'
import { createResource, Button, Badge, call, Dialog, FeatherIcon, Input, ListItem } from 'frappe-ui'
import { useDebounceFn } from '@vueuse/core'
import dayjs from 'dayjs'
import 'dayjs/locale/es'
import weekOfYear from 'dayjs/plugin/weekOfYear'

const debounce = useDebounceFn

dayjs.extend(weekOfYear)
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
const planes = ref([])
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
            value: start.add(i, 'day').format('YYYY-MM-DD'),
            label: start.add(i, 'day').format('dddd') + ' (' + formatDateShort(start.add(i, 'day')) + ')'
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
        const [sedesData, settingsData, coursesData, programsData, planesData] = await Promise.all([
            call('portal_rrhh.api.timesheets.get_sedes'),
            call('portal_rrhh.api.timesheets.get_user_settings'),
            call('portal_rrhh.api.timesheets.get_courses', { limit: 50 }),
            call('portal_rrhh.api.timesheets.get_programs', { limit: 50 }),
            call('portal_rrhh.api.timesheets.get_planes', { limit: 50 })
        ])
        sedes.value = sedesData || []
        userSettings.value = settingsData || {}
        courses.value = coursesData || []
        programs.value = programsData || []
        planes.value = planesData || []
    } catch (error) {
        console.error(error)
    }
}

// Methods


const searchCourses = debounce(async (query, program, plan) => {
    // If just searching, we allow it. But we respect filters if present.
    const programName = (typeof program === 'object' && program !== null) ? program.value : program
    const planName = (typeof plan === 'object' && plan !== null) ? plan.value : plan

    try {
        const data = await call('portal_rrhh.api.timesheets.get_courses', { 
            txt: query, 
            program: programName,
            plan: planName,
            limit: 50
        })
        courses.value = data || []
    } catch (e) {
        console.error(e)
    }
}, 300)

const searchPrograms = debounce(async (query, plan) => {
    const planName = (typeof plan === 'object' && plan !== null) ? plan.value : plan

    try {
        const data = await call('portal_rrhh.api.timesheets.get_programs', { 
            txt: query,
            plan: planName,
            limit: 50
        })
        programs.value = data || []
    } catch (e) {
        console.error(e)
    }
}, 300)

const searchPlanes = debounce(async (query) => {
    try {
        const data = await call('portal_rrhh.api.timesheets.get_planes', { txt: query, limit: 50 })
        planes.value = data || []
    } catch (e) {
        console.error(e)
    }
}, 300)

const updatePlan = (log, val) => {
    // Si selecciona "Todos", limpiar el valor y los hijos
    if (val?.value === '__todos__' || val === '__todos__') {
        log.plan = { label: '📋 Todos (General)', value: '__todos__' }
        log.expediente = { label: '📋 Todos', value: '__todos__' }
        log.course = { label: '📋 Todos', value: '__todos__' }
        return
    }
    // Reset children if plan changes
    log.expediente = null
    log.course = null
}

const updateProgram = async (log, val) => {
    // Si selecciona "Todos", limpiar el valor y el curso
    if (val?.value === '__todos__' || val === '__todos__') {
        log.expediente = { label: '📋 Todos', value: '__todos__' }
        log.course = { label: '📋 Todos', value: '__todos__' }
        return
    }
    
    // Clear course because program changed
    log.course = null
    
    if (!val) return

    const programValue = (typeof val === 'object' && val?.value) ? val.value : val
    
    // Attempt to find in currently loaded programs (from search)
    let found = programs.value.find(p => p.name === programValue)
    
    // If not found (unlikely if user just selected it, but possible if set programmatically), fetch it?
    // For now assume found if user selected it from autocomplete.
    
    if (found && found.custom_plan && !log.plan) {
         // Auto-fill Plan
         // Check if plan is already in 'planes' list
         let foundPlan = planes.value.find(pl => pl.name === found.custom_plan)
         
         if (!foundPlan) {
             // Fetch plan details to populate label correctly
             try {
                 const planData = await call('portal_rrhh.api.timesheets.get_planes', { txt: found.custom_plan })
                 if (planData && planData.length > 0) {
                     // Prefer exact match if possible, but search 'txt' acts as filter.
                     foundPlan = planData.find(p => p.name === found.custom_plan) || planData[0]
                     if (foundPlan) planes.value.push(foundPlan) // Cache it in the list
                 }
             } catch (e) {
                 console.error(e)
             }
         }

         if (foundPlan) {
             log.plan = { label: (foundPlan.n_plan_formativo ? `[${foundPlan.n_plan_formativo}] ` : '') + (foundPlan.custom_descripción_del_plan || foundPlan.name), value: foundPlan.name }
         } else {
             log.plan = found.custom_plan // Fallback to ID
         }
    }
}

const updateCourse = (log, val) => {
    // Si selecciona "Todos", solo establecer el valor
    if (val?.value === '__todos__' || val === '__todos__') {
        log.course = { label: '📋 Todos', value: '__todos__' }
        return
    }
    
    if (!val) return

    const courseValue = (typeof val === 'object' && val?.value) ? val.value : val
    const found = courses.value.find(c => c.name === courseValue)
    
    if (found) {
        // Auto-fill Program
        if (found.expediente) {
             const foundProgram = programs.value.find(p => p.name === found.expediente)
             // Set program
             log.expediente = foundProgram 
                ? { label: foundProgram.custom_num_de_expediente, value: foundProgram.name } 
                : found.expediente
             
             // Auto-fill Plan (Recursive logic basically)
             // If we found the program in list, we know its plan
             // OR we look at course.custom_plan directly
             
             const planName = found.custom_plan || (foundProgram ? foundProgram.custom_plan : null)
             
             if (planName) {
                 const foundPlan = planes.value.find(pl => pl.name === planName)
                 log.plan = foundPlan 
                    ? { label: foundPlan.custom_descripción_del_plan || foundPlan.name, value: foundPlan.name } 
                    : planName
             }
        }
    }
}

const formatDate = (date) => dayjs(date).format('DD/MM/YYYY')
const formatDateShort = (date) => dayjs(date).format('DD/MM')

// ... (This tool call is complex due to multiple distributed changes. I will use multi_replace for safety if I can, or replace_file_content if I am confident with ranges. Since it's scattered, I will use `replace_file_content` with a large range or `multi_replace`. I'll use `replace_file_content` to rewrite the script section for `getStatusColor` and `multi_replace` for the template parts or just `replace_file_content` for specific chunks. I will do script first.)

// Script update
const getStatusColor = (status) => {
    if (status === 'Submitted' || status === 'Aprobado') return 'green'
    if (status === 'Draft' || status === 'Borrador') return 'yellow' // Use yellow for Draft
    if (status === 'Rejected' || status === 'Rechazado') return 'red'
    return 'gray'
}


const deleteTimesheet = async (name) => {
    if (!confirm(__('¿Estás seguro de que quieres eliminar este borrador?'))) return

    try {
        await call('portal_rrhh.api.timesheets.delete_timesheet', { name })
        fetchTimesheets(true)
    } catch (error) {
        console.error(error)
    }
}

const getStatusLabel = (status) => {
    const map = {
        'Draft': 'Borrador',
        'Submitted': 'Validado', // Or 'Enviado' per user request, but Validado is common for Submitted
        'Cancelled': 'Cancelado',
        'Borrador': 'Borrador' // In case it's already translated
    }
    return map[status] || status
}

const createNewTimesheet = () => {
    currentTimesheet.value = { status: 'Borrador' }
    // Set to current week Monday
    const startOfWeek = dayjs().startOf('week')
    currentStartDate.value = startOfWeek.format('YYYY-MM-DD')
    logs.value = []
    
    // Auto-fill Mon-Fri (0 is Sunday, 1 is Monday... 6 is Saturday)
    // dayjs().day(1) is Monday.
    // Loop 0 to 4 (Mon to Fri) relative to start (which in dayjs 'week' start depends on locale, but let's be explicit)
    // Spanish locale starts week on Monday.
    
    // Let's iterate 0 to 4 (5 days) starting from currentStartDate (Monday)
    for (let i = 0; i < 5; i++) {
        logs.value.push({ 
            date: startOfWeek.add(i, 'day').format('YYYY-MM-DD'), 
            hours: 0, 
            sede: userSettings.value.default_sede ? { label: userSettings.value.default_sede_name, value: userSettings.value.default_sede } : null,
            course: null, 
            expediente: null,
            plan: null
        })
    }

    isNew.value = true
    viewMode.value = 'edit'
}

const editTimesheet = async (name) => {
    loading.value = true
    try {
        const data = await call('portal_rrhh.api.timesheets.get_timesheet_details', { name })
        currentTimesheet.value = data
        currentStartDate.value = data.start_date
        
        // Extract unique IDs to fetch metadata for
        const planIds = [...new Set((data.custom_sede_time_logs || []).map(l => l.plan).filter(Boolean))]
        const progIds = [...new Set((data.custom_sede_time_logs || []).map(l => l.expediente).filter(Boolean))]
        const courseIds = [...new Set((data.custom_sede_time_logs || []).map(l => l.course).filter(Boolean))]

        // Helper to fetch details in parallel
        // We can reuse get_planes/programs/courses but with ID filter? NO, they filter by txt/name match.
        // We can just loop and fetch or use valid search.
        // To be efficient, we might want a new backend method 'get_names' but let's stick to what we have. 
        // We'll use the search endpoints. It's fine for a few items.
        // Or better: Assume we need their full objects for the Autocomplete options.
        
        // FETCH METADATA for existing items so they display correctly
        const fetchPromises = []
        
        // Fetches for Plans
        if (planIds.length > 0) {
             // Ideally we pass a list of names, but our API takes 'txt'.
             // We'll just fetch each one? No, that's N requests.
             // We'll assume the user isn't editing a massive timesheet with 50 different plans. Usually 1 or 2.
             planIds.forEach(id => {
                 fetchPromises.push(call('portal_rrhh.api.timesheets.get_planes', { txt: id }).then(res => {
                     return res ? res.find(i => i.name === id) : null
                 }))
             })
        }
        
        // Fetches for Programs
        if (progIds.length > 0) {
             progIds.forEach(id => {
                 fetchPromises.push(call('portal_rrhh.api.timesheets.get_programs', { txt: id }).then(res => {
                     return res ? res.find(i => i.name === id) : null
                 }))
             })
        }
        
        // Fetches for Courses
        if (courseIds.length > 0) {
             courseIds.forEach(id => {
                 fetchPromises.push(call('portal_rrhh.api.timesheets.get_courses', { txt: id }).then(res => {
                     return res ? res.find(i => i.name === id) : null
                 }))
             })
        }

        const stats = await Promise.all(fetchPromises)
        // Add unique non-null items to our lists
        stats.filter(Boolean).forEach(item => {
            if (item.n_plan_formativo !== undefined) { // Is Plan
                if (!planes.value.find(p => p.name === item.name)) planes.value.push(item)
            } else if (item.program_name !== undefined) { // Is Program
                if (!programs.value.find(p => p.name === item.name)) programs.value.push(item)
            } else if (item.course_name !== undefined) { // Is Course
                 if (!courses.value.find(c => c.name === item.name)) courses.value.push(item)
            }
        })

        // Populate logs from custom_sede_time_logs
        logs.value = (data.custom_sede_time_logs || []).map(l => {
            const foundSede = l.sede ? sedes.value.find(s => s.name === l.sede) : null
            const foundCourse = l.course ? courses.value.find(c => c.name === l.course) : null
            const foundProgram = l.expediente ? programs.value.find(p => p.name === l.expediente) : null
            const foundPlan = l.plan ? planes.value.find(p => p.name === l.plan) : null
            
            // Helper para mostrar "Todos" cuando el campo está vacío
            const todosOption = (label) => ({ label: `📋 ${label}`, value: '__todos__' })
            
            return {
                date: l.date,
                hours: l.hours,
                sede: foundSede ? { label: foundSede.room_name, value: l.sede } : l.sede,
                course: l.course 
                    ? (foundCourse ? { label: (foundCourse.custom_display_identifier ? `[${foundCourse.custom_display_identifier}] ` : '') + (foundCourse.course_name || foundCourse.name), value: l.course, link_program: foundCourse.expediente } : l.course)
                    : todosOption('Todos'),
                expediente: l.expediente 
                    ? (foundProgram ? { label: (foundProgram.custom_num_de_expediente ? `[${foundProgram.custom_num_de_expediente}] ` : '') + (foundProgram.program_name || foundProgram.name), value: l.expediente, link_plan: foundProgram.custom_plan } : l.expediente)
                    : todosOption('Todos'),
                plan: l.plan 
                    ? (foundPlan ? { label: (foundPlan.n_plan_formativo ? `[${foundPlan.n_plan_formativo}] ` : '') + (foundPlan.custom_descripción_del_plan || foundPlan.name), value: l.plan } : l.plan)
                    : todosOption('Todos (General)')
            }
        })
        
        isNew.value = false
        viewMode.value = 'edit'
    } catch (error) {
        console.error(error)
    } finally {
        loading.value = false
    }
}

const duplicateTimesheet = async (name) => {
    loading.value = true
    try {
        const data = await call('portal_rrhh.api.timesheets.get_timesheet_details', { name })
        
        // Set new state
        currentTimesheet.value = { status: 'Borrador' }
        isNew.value = true
        
        // Calculate date shift (Old Monday -> Current Monday)
        const oldStart = dayjs(data.start_date)
        const newStart = dayjs().startOf('week')
        const diffDays = newStart.diff(oldStart, 'day')
        
        currentStartDate.value = newStart.format('YYYY-MM-DD')

        // Extract unique IDs to fetch metadata for
        const planIds = [...new Set((data.custom_sede_time_logs || []).map(l => l.plan).filter(Boolean))]
        const progIds = [...new Set((data.custom_sede_time_logs || []).map(l => l.expediente).filter(Boolean))]
        const courseIds = [...new Set((data.custom_sede_time_logs || []).map(l => l.course).filter(Boolean))]

        // FETCH METADATA for existing items so they display correctly
        const fetchPromises = []
        
        if (planIds.length > 0) {
             planIds.forEach(id => {
                 fetchPromises.push(call('portal_rrhh.api.timesheets.get_planes', { txt: id }).then(res => {
                     return res ? res.find(i => i.name === id) : null
                 }))
             })
        }
        
        if (progIds.length > 0) {
             progIds.forEach(id => {
                 fetchPromises.push(call('portal_rrhh.api.timesheets.get_programs', { txt: id }).then(res => {
                     return res ? res.find(i => i.name === id) : null
                 }))
             })
        }
        
        if (courseIds.length > 0) {
             courseIds.forEach(id => {
                 fetchPromises.push(call('portal_rrhh.api.timesheets.get_courses', { txt: id }).then(res => {
                     return res ? res.find(i => i.name === id) : null
                 }))
             })
        }

        const stats = await Promise.all(fetchPromises)
        // Add unique non-null items to our lists
        stats.filter(Boolean).forEach(item => {
            if (item.n_plan_formativo !== undefined) { 
                if (!planes.value.find(p => p.name === item.name)) planes.value.push(item)
            } else if (item.program_name !== undefined) { 
                if (!programs.value.find(p => p.name === item.name)) programs.value.push(item)
            } else if (item.course_name !== undefined) { 
                 if (!courses.value.find(c => c.name === item.name)) courses.value.push(item)
            }
        })

        // Populate logs with shifted dates
        logs.value = (data.custom_sede_time_logs || []).map(l => {
            const newDate = dayjs(l.date).add(diffDays, 'day').format('YYYY-MM-DD')
            const foundSede = l.sede ? sedes.value.find(s => s.name === l.sede) : null
            const foundCourse = l.course ? courses.value.find(c => c.name === l.course) : null
            const foundProgram = l.expediente ? programs.value.find(p => p.name === l.expediente) : null
            const foundPlan = l.plan ? planes.value.find(p => p.name === l.plan) : null
            
            // Helper para mostrar "Todos" cuando el campo está vacío
            const todosOption = (label) => ({ label: `📋 ${label}`, value: '__todos__' })
            
            return {
                date: newDate,
                hours: l.hours,
                sede: foundSede ? { label: foundSede.room_name, value: l.sede } : l.sede,
                course: l.course 
                    ? (foundCourse ? { label: (foundCourse.custom_display_identifier ? `[${foundCourse.custom_display_identifier}] ` : '') + (foundCourse.course_name || foundCourse.name), value: l.course, link_program: foundCourse.expediente } : l.course)
                    : todosOption('Todos'),
                expediente: l.expediente 
                    ? (foundProgram ? { label: (foundProgram.custom_num_de_expediente ? `[${foundProgram.custom_num_de_expediente}] ` : '') + (foundProgram.program_name || foundProgram.name), value: l.expediente, link_plan: foundProgram.custom_plan } : l.expediente)
                    : todosOption('Todos'),
                plan: l.plan 
                    ? (foundPlan ? { label: (foundPlan.n_plan_formativo ? `[${foundPlan.n_plan_formativo}] ` : '') + (foundPlan.custom_descripción_del_plan || foundPlan.name), value: l.plan } : l.plan)
                    : todosOption('Todos (General)')
            }
        })
        
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
        expediente: null,
        plan: null
    })
}

const removeLog = (index) => {
    logs.value.splice(index, 1)
}

const save = async (isSubmitting = false) => {
    // Validation: Max 39 hours
    if (totalHours.value > 39) {
        alert(__('No se pueden registrar más de 39 horas semanales. Por favor, ajusta tus horas.'))
        return false
    }

    // Validation: No empty rows (0 hours)
    // We allow deleting rows, so if it's there, it must have hours.
    const hasEmptyRows = logs.value.some(l => !l.hours || parseFloat(l.hours) <= 0)
    if (hasEmptyRows) {
        alert(__('No puedes guardar líneas con 0 horas. Por favor, elimina las líneas vacías o añade horas.'))
        return false
    }

    saving.value = true
    try {
        // Helper para convertir __todos__ a null
        const convertTodos = (val) => {
            const v = val?.value || val
            return v === '__todos__' ? null : v
        }
        
        const payload = {
            name: currentTimesheet.value.name,
            start_date: currentStartDate.value,
            end_date: currentEndDate.value,
            logs: logs.value.map(l => ({
                ...l,
                sede: l.sede?.value || l.sede,
                course: convertTodos(l.course),
                expediente: convertTodos(l.expediente),
                plan: convertTodos(l.plan)
            }))
        }
        
        const result = await call('portal_rrhh.api.timesheets.save_timesheet', { data: JSON.stringify(payload) })
        currentTimesheet.value = result
        isNew.value = false 
        
        return result
    } catch (e) {
        console.error(e)
        const errorMsg = e.messages?.[0] || e.message || e
        alert(errorMsg)
    } finally {
        saving.value = false
    }
}

const attemptSubmit = async () => {
    const now = dayjs()
    const weekEnd = dayjs(currentEndDate.value)
    
    let warnings = []
    
    if (now.isBefore(weekEnd) && totalHours.value < 39) {
        warnings.push("La semana aún no ha terminado y/o parece que no has completado una jornada completa.")
    }

    warningMessage.value = warnings.length > 0 
        ? warnings.join("\n") + "\n" + __('Recuerda: El timesheet debe validarse al final de la semana o con todas las horas registradas.')
        : __('Vas a cerrar y validar este registro de horas.')
        
    showWarningDialog.value = true
}

const goBackToList = () => {
    viewMode.value = 'list'
    fetchTimesheets(true)
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

<style scoped>
:deep(input) {
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
}
</style>
