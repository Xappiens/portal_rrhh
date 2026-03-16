<template>
  <div class="h-full bg-gray-50 flex overflow-hidden">
    <!-- Left Panel: List -->
    <div class="flex-1 flex flex-col overflow-hidden" :class="selectedCourse ? 'border-r' : ''">
      <!-- Header -->
      <div class="px-6 py-4 bg-white border-b flex items-center justify-between flex-shrink-0">
        <div>
          <h2 class="text-lg font-semibold text-gray-900">Previsión de Contratación</h2>
          <p class="text-xs text-gray-500">Cursos sin instructor asignado que requieren contratación</p>
        </div>
        <div class="flex items-center gap-2">
          <Badge theme="orange" variant="subtle">
            {{ stats.sinInstructor }} sin instructor
          </Badge>
          <Button variant="outline" size="sm" @click="loadCourses">
            <template #prefix>
              <FeatherIcon name="refresh-cw" class="h-3.5" />
            </template>
            Actualizar
          </Button>
        </div>
      </div>

      <!-- Stats -->
      <div class="px-6 py-3 bg-white border-b flex-shrink-0">
        <div class="flex gap-3">
          <Card 
            class="flex-1 p-3 cursor-pointer"
            :class="stateFilter === 'Previsto' ? 'ring-2 ring-orange-500' : ''"
            @click="toggleStateFilter('Previsto')"
          >
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-orange-500"></div>
              <span class="text-xs text-gray-600">Previsto</span>
              <span class="text-sm font-semibold text-gray-900 ml-auto">{{ stats.previsto }}</span>
            </div>
          </Card>
          <Card 
            class="flex-1 p-3 cursor-pointer"
            :class="stateFilter === 'Planificado' ? 'ring-2 ring-blue-500' : ''"
            @click="toggleStateFilter('Planificado')"
          >
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-blue-500"></div>
              <span class="text-xs text-gray-600">Planificado</span>
              <span class="text-sm font-semibold text-gray-900 ml-auto">{{ stats.planificado }}</span>
            </div>
          </Card>
          <Card class="flex-1 p-3">
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-green-500"></div>
              <span class="text-xs text-gray-600">Con fecha inicio</span>
              <span class="text-sm font-semibold text-gray-900 ml-auto">{{ stats.conFecha }}</span>
            </div>
          </Card>
          <Card class="flex-1 p-3">
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-purple-500"></div>
              <span class="text-xs text-gray-600">Próximos 30 días</span>
              <span class="text-sm font-semibold text-gray-900 ml-auto">{{ stats.proximos30 }}</span>
            </div>
          </Card>
        </div>
      </div>

      <!-- Filters -->
      <div class="px-6 py-3 bg-white border-b flex-shrink-0">
        <div class="flex items-center gap-2 flex-wrap">
          <div class="flex-1 min-w-[180px]">
            <Input v-model="searchQuery" type="text" placeholder="Buscar curso..." size="sm">
              <template #prefix>
                <FeatherIcon name="search" class="h-4 text-gray-400" />
              </template>
            </Input>
          </div>
          <select v-model="comunidadFilter" class="text-xs border border-gray-300 rounded px-2 py-1.5">
            <option value="">Comunidad Autónoma</option>
            <option v-for="c in comunidades" :key="c" :value="c">{{ c }}</option>
          </select>
          <select v-model="provinciaFilter" class="text-xs border border-gray-300 rounded px-2 py-1.5">
            <option value="">Provincia</option>
            <option v-for="p in provincias" :key="p" :value="p">{{ p }}</option>
          </select>
          <select v-model="modalidadFilter" class="text-xs border border-gray-300 rounded px-2 py-1.5">
            <option value="">Modalidad</option>
            <option v-for="m in modalidades" :key="m" :value="m">{{ m }}</option>
          </select>
          <select v-model="expedienteFilter" class="text-xs border border-gray-300 rounded px-2 py-1.5">
            <option value="">Expediente</option>
            <option v-for="e in expedientes" :key="e" :value="e">{{ e }}</option>
          </select>
          <select v-model="urgencyFilter" class="text-xs border border-gray-300 rounded px-2 py-1.5">
            <option value="">Urgencia</option>
            <option value="urgent">Urgente (&lt; 15 días)</option>
            <option value="soon">Próximo (15-30 días)</option>
            <option value="planned">Planificado (&gt; 30 días)</option>
            <option value="nodate">Sin fecha</option>
          </select>
          <Button v-if="hasFilters" variant="ghost" size="sm" @click="clearFilters">
            <FeatherIcon name="x" class="h-4" />
          </Button>
        </div>
      </div>

      <!-- List -->
      <div class="flex-1 overflow-y-auto">
        <div v-if="loading" class="p-8 text-center">
          <LoadingIndicator class="h-6 w-6 mx-auto text-gray-500" />
          <p class="text-sm text-gray-500 mt-2">Cargando cursos...</p>
        </div>

        <div v-else-if="filteredCourses.length === 0" class="p-8 text-center">
          <FeatherIcon name="check-circle" class="h-12 w-12 text-green-300 mx-auto mb-3" />
          <p class="text-sm text-gray-500">No hay cursos pendientes de asignar instructor</p>
        </div>

        <div v-else class="divide-y divide-gray-100">
          <div
            v-for="course in paginatedCourses"
            :key="course.name"
            class="px-6 py-3 hover:bg-gray-50 cursor-pointer"
            :class="{ 'bg-blue-50': selectedCourse?.name === course.name }"
            @click="selectCourse(course)"
          >
            <div class="flex items-start gap-3">
              <div class="flex-shrink-0 mt-1">
                <div 
                  class="w-2 h-2 rounded-full"
                  :class="getUrgencyColor(course)"
                ></div>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <span class="text-sm font-medium text-gray-900 truncate">{{ course.course_name || course.name }}</span>
                </div>
                <div class="text-xs text-gray-500 mt-0.5">
                  <span v-if="course.expediente">{{ course.expediente }}</span>
                  <span v-if="course.expediente && course.custom_modalidad"> · </span>
                  <span v-if="course.custom_modalidad">{{ course.custom_modalidad }}</span>
                  <span v-if="course.hours"> · {{ course.hours }}h</span>
                </div>
                <div v-if="course.start_date" class="text-xs mt-1">
                  <span :class="isUrgent(course.start_date) ? 'text-red-600 font-medium' : 'text-gray-500'">
                    Inicio: {{ formatDate(course.start_date) }}
                    <span v-if="getDaysUntil(course.start_date) !== null">
                      ({{ getDaysUntilText(course.start_date) }})
                    </span>
                  </span>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <Badge :theme="course.state === 'Previsto' ? 'orange' : 'blue'" variant="subtle" size="sm">
                  {{ course.state }}
                </Badge>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="px-6 py-2 bg-white border-t flex items-center justify-center gap-2 flex-shrink-0">
        <Button variant="ghost" size="sm" :disabled="currentPage === 1" @click="currentPage--">
          <FeatherIcon name="chevron-left" class="h-4" />
        </Button>
        <span class="text-xs text-gray-500">{{ currentPage }} / {{ totalPages }}</span>
        <Button variant="ghost" size="sm" :disabled="currentPage >= totalPages" @click="currentPage++">
          <FeatherIcon name="chevron-right" class="h-4" />
        </Button>
      </div>
    </div>

    <!-- Right Panel: Detail -->
    <div v-if="selectedCourse" class="w-1/2 bg-white flex flex-col overflow-hidden">
      <!-- Detail Header -->
      <div class="px-6 py-4 border-b flex items-start justify-between flex-shrink-0">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-1">
            <Badge :theme="selectedCourse.state === 'Previsto' ? 'orange' : 'blue'" variant="subtle" size="sm">
              {{ selectedCourse.state }}
            </Badge>
            <span class="text-xs text-gray-400 font-mono">{{ selectedCourse.name }}</span>
          </div>
          <h3 class="text-base font-semibold text-gray-900">{{ selectedCourse.course_name || 'Sin nombre' }}</h3>
        </div>
        <div class="flex items-center gap-1">
          <Button variant="ghost" size="sm" @click="openInDesk(selectedCourse.name, 'Course')">
            <FeatherIcon name="external-link" class="h-4" />
          </Button>
          <Button variant="ghost" size="sm" @click="selectedCourse = null">
            <FeatherIcon name="x" class="h-4" />
          </Button>
        </div>
      </div>

      <!-- Urgency Alert -->
      <div v-if="selectedCourse.start_date && isUrgent(selectedCourse.start_date)" class="px-6 py-3 bg-red-50 border-b">
        <div class="flex items-center gap-2 text-red-700">
          <FeatherIcon name="alert-circle" class="h-4" />
          <span class="text-sm font-medium">
            ¡Urgente! El curso comienza en {{ getDaysUntilText(selectedCourse.start_date) }}
          </span>
        </div>
      </div>

      <!-- Detail Info -->
      <div class="px-6 py-4 border-b flex-shrink-0">
        <h4 class="text-xs font-medium text-gray-500 uppercase mb-3">Información del Curso</h4>
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="text-xs text-gray-500">Expediente</span>
            <p class="text-gray-900">{{ selectedCourse.expediente || '-' }}</p>
          </div>
          <div>
            <span class="text-xs text-gray-500">Código</span>
            <p class="text-gray-900">{{ selectedCourse.code || '-' }}</p>
          </div>
          <div>
            <span class="text-xs text-gray-500">Modalidad</span>
            <p class="text-gray-900">{{ selectedCourse.custom_modalidad || '-' }}</p>
          </div>
          <div>
            <span class="text-xs text-gray-500">Horas Totales</span>
            <p class="text-gray-900">{{ selectedCourse.hours || '-' }}</p>
          </div>
          <div>
            <span class="text-xs text-gray-500">Centro</span>
            <p class="text-gray-900">{{ selectedCourse.center || '-' }}</p>
          </div>
          <div>
            <span class="text-xs text-gray-500">Provincia</span>
            <p class="text-gray-900">{{ selectedCourse.custom_pronvincia || '-' }}</p>
          </div>
        </div>
      </div>

      <!-- Dates -->
      <div class="px-6 py-4 border-b flex-shrink-0">
        <h4 class="text-xs font-medium text-gray-500 uppercase mb-3">Fechas</h4>
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="text-xs text-gray-500">Fecha Inicio</span>
            <p :class="selectedCourse.start_date ? (isUrgent(selectedCourse.start_date) ? 'text-red-600 font-medium' : 'text-gray-900') : 'text-gray-400 italic'">
              {{ selectedCourse.start_date ? formatDate(selectedCourse.start_date) : 'Sin definir' }}
            </p>
          </div>
          <div>
            <span class="text-xs text-gray-500">Fecha Fin</span>
            <p class="text-gray-900">{{ selectedCourse.end_date ? formatDate(selectedCourse.end_date) : '-' }}</p>
          </div>
          <div v-if="selectedCourse.custom_fecha_fin_teoria">
            <span class="text-xs text-gray-500">Fin Teoría</span>
            <p class="text-gray-900">{{ formatDate(selectedCourse.custom_fecha_fin_teoria) }}</p>
          </div>
          <div v-if="selectedCourse.custom_fecha_inicio_practicas">
            <span class="text-xs text-gray-500">Inicio Prácticas</span>
            <p class="text-gray-900">{{ formatDate(selectedCourse.custom_fecha_inicio_practicas) }}</p>
          </div>
          <div v-if="selectedCourse.custom_fecha_fin_practicas">
            <span class="text-xs text-gray-500">Fin Prácticas</span>
            <p class="text-gray-900">{{ formatDate(selectedCourse.custom_fecha_fin_practicas) }}</p>
          </div>
        </div>
      </div>

      <!-- Hours breakdown -->
      <div v-if="selectedCourse.custom_horas_practicas" class="px-6 py-4 border-b flex-shrink-0">
        <h4 class="text-xs font-medium text-gray-500 uppercase mb-3">Desglose de Horas</h4>
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div v-if="selectedCourse.custom_horas_practicas">
            <span class="text-xs text-gray-500">Horas Prácticas</span>
            <p class="text-gray-900">{{ selectedCourse.custom_horas_practicas }}</p>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="px-6 py-4 border-b flex-shrink-0">
        <h4 class="text-xs font-medium text-gray-500 uppercase mb-3">Acciones de Contratación</h4>
        <div class="flex gap-2">
          <Button variant="solid" size="sm" @click="goToVacantes">
            <template #prefix>
              <FeatherIcon name="briefcase" class="h-4" />
            </template>
            Buscar en Vacantes
          </Button>
          <Button variant="outline" size="sm" @click="createJobOpening">
            <template #prefix>
              <FeatherIcon name="plus" class="h-4" />
            </template>
            Crear Vacante
          </Button>
        </div>
      </div>

      <!-- Perfil requerido -->
      <div class="flex-1 overflow-y-auto px-6 py-4">
        <h4 class="text-xs font-medium text-gray-500 uppercase mb-3">Perfil Docente Requerido</h4>
        <Card class="p-4">
          <div class="space-y-3 text-sm">
            <div>
              <span class="text-xs text-gray-500">Curso</span>
              <p class="text-gray-900 font-medium">{{ selectedCourse.course_name }}</p>
            </div>
            <div v-if="selectedCourse.custom_modalidad">
              <span class="text-xs text-gray-500">Modalidad requerida</span>
              <p class="text-gray-900">{{ selectedCourse.custom_modalidad }}</p>
            </div>
            <div v-if="selectedCourse.hours">
              <span class="text-xs text-gray-500">Disponibilidad requerida</span>
              <p class="text-gray-900">{{ selectedCourse.hours }} horas</p>
            </div>
            <div v-if="selectedCourse.custom_pronvincia || selectedCourse.center">
              <span class="text-xs text-gray-500">Ubicación</span>
              <p class="text-gray-900">{{ [selectedCourse.custom_pronvincia, selectedCourse.center].filter(Boolean).join(' - ') || 'A determinar' }}</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { FeatherIcon, Button, Card, Badge, Input, LoadingIndicator, call, debounce } from 'frappe-ui'

const router = useRouter()

const loading = ref(true)
const courses = ref([])
const selectedCourse = ref(null)

const searchQuery = ref('')
const stateFilter = ref('')
const modalidadFilter = ref('')
const expedienteFilter = ref('')
const urgencyFilter = ref('')
const comunidadFilter = ref('')
const provinciaFilter = ref('')
const currentPage = ref(1)
const itemsPerPage = 25

const stats = computed(() => {
  const all = courses.value
  const today = new Date()
  const in30Days = new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000)
  
  return {
    sinInstructor: all.length,
    previsto: all.filter(c => c.state === 'Previsto').length,
    planificado: all.filter(c => c.state === 'Planificado').length,
    conFecha: all.filter(c => c.start_date).length,
    proximos30: all.filter(c => {
      if (!c.start_date) return false
      const startDate = new Date(c.start_date)
      return startDate >= today && startDate <= in30Days
    }).length
  }
})

const modalidades = computed(() => {
  return [...new Set(courses.value.map(c => c.custom_modalidad).filter(Boolean))].sort()
})

const expedientes = computed(() => {
  return [...new Set(courses.value.map(c => c.expediente).filter(Boolean))].sort()
})

const comunidades = computed(() => {
  return [...new Set(courses.value.map(c => c.comunidad_autonoma).filter(Boolean))].sort()
})

const provincias = computed(() => {
  let provinciasList = courses.value.map(c => c.custom_pronvincia).filter(Boolean)
  // Si hay filtro de comunidad, filtrar provincias por esa comunidad
  if (comunidadFilter.value) {
    provinciasList = courses.value
      .filter(c => c.comunidad_autonoma === comunidadFilter.value)
      .map(c => c.custom_pronvincia)
      .filter(Boolean)
  }
  return [...new Set(provinciasList)].sort()
})

const hasFilters = computed(() => 
  searchQuery.value || stateFilter.value || modalidadFilter.value || 
  expedienteFilter.value || urgencyFilter.value || comunidadFilter.value || provinciaFilter.value
)

const filteredCourses = computed(() => {
  let result = [...courses.value]
  
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(c => 
      c.course_name?.toLowerCase().includes(q) ||
      c.name?.toLowerCase().includes(q) ||
      c.expediente?.toLowerCase().includes(q)
    )
  }
  
  if (stateFilter.value) {
    result = result.filter(c => c.state === stateFilter.value)
  }
  
  if (modalidadFilter.value) {
    result = result.filter(c => c.custom_modalidad === modalidadFilter.value)
  }
  
  if (expedienteFilter.value) {
    result = result.filter(c => c.expediente === expedienteFilter.value)
  }
  
  if (comunidadFilter.value) {
    result = result.filter(c => c.comunidad_autonoma === comunidadFilter.value)
  }
  
  if (provinciaFilter.value) {
    result = result.filter(c => c.custom_pronvincia === provinciaFilter.value)
  }
  
  if (urgencyFilter.value) {
    const today = new Date()
    result = result.filter(c => {
      if (urgencyFilter.value === 'nodate') return !c.start_date
      if (!c.start_date) return false
      
      const days = getDaysUntil(c.start_date)
      if (days === null || days < 0) return false
      
      if (urgencyFilter.value === 'urgent') return days < 15
      if (urgencyFilter.value === 'soon') return days >= 15 && days <= 30
      if (urgencyFilter.value === 'planned') return days > 30
      return true
    })
  }
  
  // Sort by start_date (urgents first, then by date, nulls last)
  result.sort((a, b) => {
    if (!a.start_date && !b.start_date) return 0
    if (!a.start_date) return 1
    if (!b.start_date) return -1
    return new Date(a.start_date) - new Date(b.start_date)
  })
  
  return result
})

const totalPages = computed(() => Math.ceil(filteredCourses.value.length / itemsPerPage))

const paginatedCourses = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredCourses.value.slice(start, start + itemsPerPage)
})

async function loadCourses() {
  loading.value = true
  try {
    const result = await call('portal_rrhh.api.prevision.get_courses_without_instructor')
    courses.value = result || []
  } catch (error) {
    console.error('Error loading courses:', error)
  } finally {
    loading.value = false
  }
}

function toggleStateFilter(state) {
  stateFilter.value = stateFilter.value === state ? '' : state
  currentPage.value = 1
}

function clearFilters() {
  searchQuery.value = ''
  stateFilter.value = ''
  modalidadFilter.value = ''
  expedienteFilter.value = ''
  urgencyFilter.value = ''
  comunidadFilter.value = ''
  provinciaFilter.value = ''
  currentPage.value = 1
}

function selectCourse(course) {
  selectedCourse.value = course
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })
}

function getDaysUntil(dateStr) {
  if (!dateStr) return null
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const target = new Date(dateStr)
  target.setHours(0, 0, 0, 0)
  const diff = Math.ceil((target - today) / (1000 * 60 * 60 * 24))
  return diff
}

function getDaysUntilText(dateStr) {
  const days = getDaysUntil(dateStr)
  if (days === null) return ''
  if (days < 0) return `hace ${Math.abs(days)} días`
  if (days === 0) return 'hoy'
  if (days === 1) return 'mañana'
  return `en ${days} días`
}

function isUrgent(dateStr) {
  const days = getDaysUntil(dateStr)
  return days !== null && days >= 0 && days < 15
}

function getUrgencyColor(course) {
  if (!course.start_date) return 'bg-gray-300'
  const days = getDaysUntil(course.start_date)
  if (days === null || days < 0) return 'bg-gray-300'
  if (days < 15) return 'bg-red-500'
  if (days <= 30) return 'bg-orange-500'
  return 'bg-green-500'
}

function openInDesk(name, doctype) {
  window.open(`/app/${doctype.toLowerCase()}/${name}`, '_blank')
}

function goToVacantes() {
  router.push({ name: 'Vacantes' })
}

function createJobOpening() {
  if (!selectedCourse.value) return
  
  // Open Frappe desk to create a new Job Opening with pre-filled data
  const course = selectedCourse.value
  const title = `Docente - ${course.course_name || course.name}`
  window.open(`/app/job-opening/new-job-opening-1?job_title=${encodeURIComponent(title)}`, '_blank')
}

watch(searchQuery, debounce(() => { currentPage.value = 1 }, 300))

// Limpiar provincia si cambia comunidad
watch(comunidadFilter, () => {
  provinciaFilter.value = ''
  currentPage.value = 1
})

onMounted(() => {
  loadCourses()
})
</script>
