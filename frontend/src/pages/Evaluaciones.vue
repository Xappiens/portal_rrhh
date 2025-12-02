<template>
  <div class="h-full bg-gray-50 flex flex-col overflow-hidden">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200 px-6 py-4 flex-shrink-0">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Evaluaciones por Competencias</h1>
          <p class="text-sm text-gray-600 mt-1">Gestiona y realiza seguimiento de las evaluaciones de desempeño</p>
        </div>
        <div class="flex items-center space-x-3">
          <Button variant="outline" size="sm" @click="showCyclesModal = true">
            <template #prefix>
              <FeatherIcon name="calendar" class="h-4" />
            </template>
            Ciclos
          </Button>
          <Button variant="outline" size="sm" @click="showGapAnalysis = !showGapAnalysis">
            <template #prefix>
              <FeatherIcon name="trending-down" class="h-4" />
            </template>
            Análisis de Brechas
          </Button>
          <Button variant="solid" size="sm" @click="showCreateModal = true">
            <template #prefix>
              <FeatherIcon name="plus" class="h-4" />
            </template>
            Nueva Evaluación
          </Button>
        </div>
      </div>
    </div>

    <!-- Estadísticas -->
    <div class="px-6 py-4 flex-shrink-0">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card class="p-4">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <FeatherIcon name="clipboard" class="h-5 w-5 text-blue-600" />
              </div>
            </div>
            <div class="ml-3">
              <p class="text-xs font-medium text-gray-500">Total</p>
              <p class="text-xl font-semibold text-gray-900">{{ statistics.total_appraisals || 0 }}</p>
            </div>
          </div>
        </Card>

        <Card class="p-4">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                <FeatherIcon name="clock" class="h-5 w-5 text-yellow-600" />
              </div>
            </div>
            <div class="ml-3">
              <p class="text-xs font-medium text-gray-500">Pendientes</p>
              <p class="text-xl font-semibold text-gray-900">{{ statistics.pending_count || 0 }}</p>
            </div>
          </div>
        </Card>

        <Card class="p-4">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <FeatherIcon name="check-circle" class="h-5 w-5 text-green-600" />
              </div>
            </div>
            <div class="ml-3">
              <p class="text-xs font-medium text-gray-500">Completadas</p>
              <p class="text-xl font-semibold text-gray-900">{{ statistics.completed_count || 0 }}</p>
            </div>
          </div>
        </Card>

        <Card class="p-4">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <FeatherIcon name="trending-up" class="h-5 w-5 text-purple-600" />
              </div>
            </div>
            <div class="ml-3">
              <p class="text-xs font-medium text-gray-500">Puntuación Promedio</p>
              <p class="text-xl font-semibold text-gray-900">
                {{ statistics.average_score ? statistics.average_score.toFixed(1) : '0.0' }}
              </p>
            </div>
          </div>
        </Card>

        <Card class="p-4">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                <FeatherIcon name="alert-triangle" class="h-5 w-5 text-red-600" />
              </div>
            </div>
            <div class="ml-3">
              <p class="text-xs font-medium text-gray-500">Brechas Críticas</p>
              <p class="text-xl font-semibold text-gray-900">{{ statistics.critical_gaps_count || 0 }}</p>
            </div>
          </div>
        </Card>
      </div>
    </div>

    <!-- Análisis de Brechas (Colapsable) -->
    <div v-if="showGapAnalysis" class="px-6 py-4 flex-shrink-0">
      <Card class="p-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Análisis de Brechas de Competencias</h3>
          <Button variant="ghost" size="sm" @click="loadGapAnalysis">
            <FeatherIcon name="refresh-cw" class="h-4" />
          </Button>
        </div>
        <div v-if="gapAnalysisLoading" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        </div>
        <div v-else-if="gapAnalysis.length === 0" class="text-center py-8 text-gray-500">
          No hay brechas identificadas
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="gap in gapAnalysis"
            :key="gap.competency"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
          >
            <div class="flex-1">
              <div class="flex items-center space-x-2">
                <span class="font-medium text-gray-900">{{ gap.competency_name }}</span>
                <Badge :label="gap.category" variant="subtle" />
                <span class="text-xs text-gray-500">({{ gap.competency_code }})</span>
              </div>
              <div class="mt-1 text-sm text-gray-600">
                Brecha promedio: <span class="font-semibold text-red-600">{{ gap.avg_gap?.toFixed(1) }}</span>
                | Evaluaciones: {{ gap.evaluation_count }} | Críticas: {{ gap.critical_count }}
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>

    <!-- Filtros -->
    <div class="bg-white border-b border-gray-200 px-6 py-4 flex-shrink-0">
      <div class="flex flex-wrap items-center gap-3">
        <div class="flex-1 min-w-[200px]">
          <Input
            v-model="filters.search"
            type="text"
            placeholder="Buscar por empleado o código..."
            variant="outline"
            size="sm"
            @input="debouncedSearch"
          >
            <template #prefix>
              <FeatherIcon name="search" class="h-4 text-gray-400" />
            </template>
          </Input>
        </div>

        <Input
          v-model="filters.status"
          type="select"
          variant="outline"
          size="sm"
          @change="loadAppraisals"
          class="w-48"
        >
          <option value="">Todos los estados</option>
          <option value="Borrador">Borrador</option>
          <option value="Auto-evaluado">Auto-evaluado</option>
          <option value="Enviado">Enviado</option>
          <option value="Completado">Completado</option>
          <option value="Cancelado">Cancelado</option>
        </Input>

        <Input
          v-model="filters.appraisal_cycle"
          type="select"
          variant="outline"
          size="sm"
          @change="loadAppraisals"
          class="w-48"
        >
          <option value="">Todos los ciclos</option>
          <option v-for="cycle in cycles" :key="cycle.name" :value="cycle.name">
            {{ cycle.cycle_name }}
          </option>
        </Input>

        <Input
          v-model="filters.department"
          type="select"
          variant="outline"
          size="sm"
          @change="loadAppraisals"
          class="w-48"
        >
          <option value="">Todos los departamentos</option>
          <option v-for="dept in departments" :key="dept.name" :value="dept.name">
            {{ dept.department_name }}
          </option>
        </Input>

        <Button variant="outline" size="sm" @click="resetFilters">
          <template #prefix>
            <FeatherIcon name="x" class="h-4" />
          </template>
          Limpiar
        </Button>
      </div>
    </div>

    <!-- Lista de Evaluaciones -->
    <div class="flex-1 overflow-y-auto px-6 py-4">
      <Card>
        <div v-if="appraisalsLoading" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
          <p class="text-gray-600">Cargando evaluaciones...</p>
        </div>

        <div v-else-if="appraisals.length === 0" class="text-center py-12">
          <FeatherIcon name="clipboard" class="h-12 w-12 mx-auto text-gray-300 mb-4" />
          <p class="text-gray-600">No se encontraron evaluaciones</p>
          <Button variant="solid" size="sm" class="mt-4" @click="showCreateModal = true">
            Crear primera evaluación
          </Button>
        </div>

        <div v-else class="divide-y divide-gray-200">
          <div
            v-for="appraisal in appraisals"
            :key="appraisal.name"
            class="p-4 hover:bg-gray-50 transition-colors cursor-pointer"
            @click="viewAppraisal(appraisal.name)"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center space-x-3 mb-2">
                  <div>
                    <h3 class="text-base font-semibold text-gray-900">{{ appraisal.employee_name }}</h3>
                    <p class="text-sm text-gray-500 font-mono">{{ appraisal.name }}</p>
                  </div>
                  <Badge :label="appraisal.status" :variant="getStatusVariant(appraisal.status)" />
                  <Badge v-if="appraisal.cycle_name" :label="appraisal.cycle_name" variant="subtle" />
                </div>

                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-3">
                  <div>
                    <p class="text-xs text-gray-500">Puesto</p>
                    <p class="text-sm font-medium text-gray-900">{{ appraisal.designation || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500">Departamento</p>
                    <p class="text-sm font-medium text-gray-900">{{ appraisal.department || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500">Puntuación</p>
                    <p class="text-sm font-medium text-gray-900">
                      {{ appraisal.total_score ? appraisal.total_score.toFixed(1) : '-' }}
                      <span v-if="appraisal.self_appraisal_score" class="text-xs text-gray-500">
                        (Auto: {{ appraisal.self_appraisal_score.toFixed(1) }})
                      </span>
                    </p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500">Fecha Evaluación</p>
                    <p class="text-sm font-medium text-gray-900">
                      {{ appraisal.evaluation_date_formatted || '-' }}
                    </p>
                  </div>
                </div>

                <div v-if="appraisal.competency_count" class="mt-2">
                  <p class="text-xs text-gray-500">
                    {{ appraisal.competency_count }} competencia(s) evaluada(s)
                  </p>
                </div>
              </div>

              <div class="flex items-center space-x-2 ml-4" @click.stop>
                <Button
                  variant="ghost"
                  size="sm"
                  @click.stop="viewAppraisal(appraisal.name)"
                >
                  <FeatherIcon name="eye" class="h-4" />
                </Button>
                <Button
                  v-if="appraisal.status === 'Borrador' || appraisal.status === 'Auto-evaluado'"
                  variant="ghost"
                  size="sm"
                  @click.stop="editAppraisal(appraisal.name)"
                >
                  <FeatherIcon name="edit" class="h-4" />
                </Button>
                <Button
                  v-if="appraisal.status === 'Borrador' || appraisal.status === 'Auto-evaluado'"
                  variant="ghost"
                  size="sm"
                  @click.stop="submitAppraisal(appraisal.name)"
                >
                  <FeatherIcon name="send" class="h-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>

        <!-- Paginación -->
        <div v-if="totalCount > limit" class="bg-gray-50 px-6 py-4 border-t border-gray-200">
          <div class="flex items-center justify-between">
            <div class="text-sm text-gray-700">
              Mostrando {{ offset + 1 }} a {{ Math.min(offset + limit, totalCount) }} de {{ totalCount }} evaluaciones
            </div>
            <div class="flex space-x-2">
              <Button
                variant="outline"
                size="sm"
                :disabled="offset === 0"
                @click="changePage(-1)"
              >
                <FeatherIcon name="chevron-left" class="h-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                :disabled="offset + limit >= totalCount"
                @click="changePage(1)"
              >
                <FeatherIcon name="chevron-right" class="h-4" />
              </Button>
            </div>
          </div>
        </div>
      </Card>
    </div>

    <!-- Modal de Crear Evaluación -->
    <Dialog v-model="showCreateModal" :options="{ title: 'Nueva Evaluación', size: 'lg' }">
      <template #body>
        <div class="space-y-4">
          <Input
            v-model="formData.employee"
            type="select"
            label="Empleado"
            :options="employeeOptions"
            required
          />
          <Input
            v-model="formData.appraisal_cycle"
            type="select"
            label="Ciclo de Evaluación"
            :options="cycleOptions"
            required
            @change="onCycleChange"
          />
          <Input
            v-model="formData.competency_profile"
            type="select"
            label="Perfil de Competencias"
            :options="profileOptions"
            required
          />
          <Input
            v-model="formData.self_appraisal_enabled"
            type="checkbox"
            label="Habilitar Auto-evaluación"
          />
        </div>
      </template>
      <template #actions>
        <Button variant="outline" @click="showCreateModal = false">Cancelar</Button>
        <Button variant="solid" @click="createAppraisal" :loading="creating">
          Crear
        </Button>
      </template>
    </Dialog>

    <!-- Modal de Detalles -->
    <Dialog v-model="showDetailsModal" :options="{ title: 'Detalles de Evaluación', size: '2xl' }">
      <template #body>
        <div v-if="selectedAppraisal" class="space-y-6">
          <!-- Información General -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-sm font-medium text-gray-700">Empleado</label>
              <p class="text-sm text-gray-900 mt-1">{{ selectedAppraisal.employee?.employee_name }}</p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700">Estado</label>
              <p class="text-sm mt-1">
                <Badge :label="selectedAppraisal.appraisal?.status" :variant="getStatusVariant(selectedAppraisal.appraisal?.status)" />
              </p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700">Ciclo</label>
              <p class="text-sm text-gray-900 mt-1">{{ selectedAppraisal.cycle?.cycle_name || '-' }}</p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700">Puntuación Total</label>
              <p class="text-sm text-gray-900 font-semibold mt-1">
                {{ selectedAppraisal.appraisal?.total_score?.toFixed(1) || '-' }}
              </p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700">Fecha de Evaluación</label>
              <p class="text-sm text-gray-900 mt-1">
                {{ selectedAppraisal.appraisal?.evaluation_date ? formatDate(selectedAppraisal.appraisal.evaluation_date) : '-' }}
              </p>
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700">Evaluado por</label>
              <p class="text-sm text-gray-900 mt-1">
                {{ selectedAppraisal.evaluator?.full_name || selectedAppraisal.appraisal?.evaluated_by || '-' }}
              </p>
            </div>
          </div>

          <!-- Estadísticas -->
          <div v-if="selectedAppraisal.statistics" class="bg-gray-50 rounded-lg p-4">
            <h4 class="text-sm font-semibold text-gray-900 mb-3">Estadísticas</h4>
            <div class="grid grid-cols-4 gap-4">
              <div>
                <p class="text-xs text-gray-500">Total Competencias</p>
                <p class="text-lg font-semibold">{{ selectedAppraisal.statistics.total_competencies }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Evaluadas</p>
                <p class="text-lg font-semibold">{{ selectedAppraisal.statistics.competencies_evaluated }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Con Brecha</p>
                <p class="text-lg font-semibold text-yellow-600">{{ selectedAppraisal.statistics.competencies_with_gap }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Brecha Crítica</p>
                <p class="text-lg font-semibold text-red-600">{{ selectedAppraisal.statistics.competencies_critical_gap }}</p>
              </div>
            </div>
          </div>

          <!-- Evaluaciones por Competencia -->
          <div>
            <h4 class="text-lg font-semibold text-gray-900 mb-4">Evaluaciones por Competencia</h4>
            <div class="space-y-4">
              <Card
                v-for="eval_item in selectedAppraisal.competency_evaluations"
                :key="eval_item.competency"
                class="p-4"
              >
                <div class="flex items-start justify-between mb-3">
                  <div class="flex-1">
                    <div class="flex items-center space-x-2">
                      <h5 class="font-medium text-gray-900">{{ eval_item.competency_name }}</h5>
                      <Badge :label="eval_item.category" variant="subtle" />
                      <span class="text-xs text-gray-500">({{ eval_item.competency_code }})</span>
                    </div>
                    <p v-if="eval_item.description" class="text-sm text-gray-600 mt-1">
                      {{ eval_item.description }}
                    </p>
                  </div>
                  <div class="text-right">
                    <p class="text-xs text-gray-500">Puntuación</p>
                    <p class="text-lg font-semibold">{{ eval_item.score?.toFixed(1) || '-' }}</p>
                  </div>
                </div>

                <div class="grid grid-cols-4 gap-4 mt-4">
                  <div>
                    <p class="text-xs text-gray-500">Nivel Esperado</p>
                    <p class="text-sm font-medium">{{ eval_item.expected_level }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500">Nivel Alcanzado</p>
                    <p class="text-sm font-medium">{{ eval_item.achieved_level || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500">Brecha</p>
                    <p :class="eval_item.level_gap > 0 ? 'text-red-600' : 'text-green-600'" class="text-sm font-semibold">
                      {{ eval_item.level_gap || 0 }}
                    </p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500">Ponderación</p>
                    <p class="text-sm font-medium">{{ eval_item.weightage ? `${eval_item.weightage}%` : '-' }}</p>
                  </div>
                </div>

                <div v-if="eval_item.comments" class="mt-3 pt-3 border-t border-gray-200">
                  <p class="text-xs font-medium text-gray-700 mb-1">Comentarios del Evaluador</p>
                  <p class="text-sm text-gray-700">{{ eval_item.comments }}</p>
                </div>

                <div v-if="eval_item.employee_comments" class="mt-3 pt-3 border-t border-gray-200">
                  <p class="text-xs font-medium text-gray-700 mb-1">Comentarios del Empleado</p>
                  <p class="text-sm text-gray-700">{{ eval_item.employee_comments }}</p>
                </div>
              </Card>
            </div>
          </div>

          <!-- Notas de Entrevista -->
          <div v-if="selectedAppraisal.appraisal?.interview_notes">
            <h4 class="text-lg font-semibold text-gray-900 mb-2">Notas de Entrevista</h4>
            <div class="bg-gray-50 rounded-lg p-4">
              <div v-html="selectedAppraisal.appraisal.interview_notes"></div>
            </div>
          </div>

          <!-- Sugerencias de Mejora -->
          <div v-if="selectedAppraisal.appraisal?.improvement_suggestions">
            <h4 class="text-lg font-semibold text-gray-900 mb-2">Sugerencias de Mejora</h4>
            <div class="bg-gray-50 rounded-lg p-4">
              <div v-html="selectedAppraisal.appraisal.improvement_suggestions"></div>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <Button variant="outline" @click="showDetailsModal = false">Cerrar</Button>
        <Button
          v-if="selectedAppraisal?.appraisal?.status === 'Borrador' || selectedAppraisal?.appraisal?.status === 'Auto-evaluado'"
          variant="solid"
          @click="editAppraisal(selectedAppraisal.appraisal.name)"
        >
          Editar
        </Button>
      </template>
    </Dialog>

    <!-- Modal de Ciclos -->
    <Dialog v-model="showCyclesModal" :options="{ title: 'Ciclos de Evaluación', size: 'lg' }">
      <template #body>
        <div v-if="cyclesLoading" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        </div>
        <div v-else-if="cycles.length === 0" class="text-center py-8 text-gray-500">
          No hay ciclos disponibles
        </div>
        <div v-else class="space-y-3">
          <Card
            v-for="cycle in cycles"
            :key="cycle.name"
            class="p-4 cursor-pointer hover:bg-gray-50"
            @click="selectCycle(cycle)"
          >
            <div class="flex items-center justify-between">
              <div>
                <h4 class="font-medium text-gray-900">{{ cycle.cycle_name }}</h4>
                <p class="text-sm text-gray-500">
                  {{ formatDate(cycle.start_date) }} - {{ formatDate(cycle.end_date) }}
                </p>
                <p class="text-xs text-gray-500 mt-1">
                  {{ cycle.appraisal_count }} evaluaciones | {{ cycle.completed_count }} completadas
                </p>
              </div>
              <Badge :label="cycle.status" :variant="getStatusVariant(cycle.status)" />
            </div>
          </Card>
        </div>
      </template>
      <template #actions>
        <Button variant="outline" @click="showCyclesModal = false">Cerrar</Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { FeatherIcon, Button, Input, Dialog, Badge, Card, createResource, call } from 'frappe-ui'

// Estado
const appraisals = ref([])
const statistics = ref({})
const cycles = ref([])
const profiles = ref([])
const departments = ref([])
const employees = ref([])
const gapAnalysis = ref([])

const filters = ref({
  search: '',
  status: '',
  appraisal_cycle: '',
  department: '',
  company: ''
})

const showCreateModal = ref(false)
const showDetailsModal = ref(false)
const showCyclesModal = ref(false)
const showGapAnalysis = ref(false)
const selectedAppraisal = ref(null)
const creating = ref(false)
const appraisalsLoading = ref(false)
const gapAnalysisLoading = ref(false)
const cyclesLoading = ref(false)

const formData = ref({
  employee: '',
  appraisal_cycle: '',
  competency_profile: '',
  self_appraisal_enabled: false
})

const limit = ref(20)
const offset = ref(0)
const totalCount = ref(0)

// Resources
const appraisalsResource = createResource({
  url: 'portal_rrhh.api.evaluaciones.get_appraisals',
  auto: false,
  makeParams() {
    return {
      filters: JSON.stringify(filters.value),
      limit: limit.value,
      offset: offset.value,
      order_by: 'creation desc'
    }
  },
  transform(data) {
    return data
  }
})

const statisticsResource = createResource({
  url: 'portal_rrhh.api.evaluaciones.get_appraisal_statistics',
  auto: false,
  makeParams() {
    return {
      filters: JSON.stringify(filters.value)
    }
  }
})

const cyclesResource = createResource({
  url: 'portal_rrhh.api.evaluaciones.get_appraisal_cycles',
  auto: true,
  transform(data) {
    return data || []
  }
})

// Computed
const employeeOptions = computed(() => {
  return employees.value.map(emp => ({
    label: emp.employee_name,
    value: emp.name
  }))
})

const cycleOptions = computed(() => {
  return cycles.value.map(cycle => ({
    label: cycle.cycle_name,
    value: cycle.name
  }))
})

const profileOptions = computed(() => {
  return profiles.value.map(profile => ({
    label: profile.profile_name,
    value: profile.name
  }))
})

// Debounced search
let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadAppraisals()
  }, 500)
}

// Methods
const loadAppraisals = async () => {
  appraisalsLoading.value = true
  try {
    await appraisalsResource.reload()
    appraisals.value = appraisalsResource.data?.appraisals || []
    totalCount.value = appraisalsResource.data?.total_count || 0
  } catch (error) {
    console.error('Error loading appraisals:', error)
  } finally {
    appraisalsLoading.value = false
  }
}

const loadStatistics = async () => {
  try {
    await statisticsResource.reload()
    statistics.value = statisticsResource.data || {}
  } catch (error) {
    console.error('Error loading statistics:', error)
  }
}

const loadCycles = async () => {
  cyclesLoading.value = true
  try {
    await cyclesResource.reload()
    cycles.value = cyclesResource.data || []
  } catch (error) {
    console.error('Error loading cycles:', error)
  } finally {
    cyclesLoading.value = false
  }
}

const loadProfiles = async () => {
  try {
    const data = await call('portal_rrhh.api.evaluaciones.get_competency_profiles')
    profiles.value = data || []
  } catch (error) {
    console.error('Error loading profiles:', error)
  }
}

const loadEmployees = async () => {
  try {
    const data = await call('portal_rrhh.api.employee.get_employees', {
      filters: JSON.stringify({ status: 'Active' })
    })
    employees.value = data || []
  } catch (error) {
    console.error('Error loading employees:', error)
  }
}

const loadDepartments = async () => {
  try {
    const data = await call('portal_rrhh.api.evaluaciones.get_departments')
    departments.value = data || []
  } catch (error) {
    console.error('Error loading departments:', error)
  }
}

const loadGapAnalysis = async () => {
  gapAnalysisLoading.value = true
  try {
    const data = await call('portal_rrhh.api.evaluaciones.get_gap_analysis', {
      filters: JSON.stringify(filters.value)
    })
    gapAnalysis.value = data || []
  } catch (error) {
    console.error('Error loading gap analysis:', error)
  } finally {
    gapAnalysisLoading.value = false
  }
}

const createAppraisal = async () => {
  creating.value = true
  try {
    await call('portal_rrhh.api.evaluaciones.create_appraisal', {
      data: JSON.stringify(formData.value)
    })
    showCreateModal.value = false
    formData.value = {
      employee: '',
      appraisal_cycle: '',
      competency_profile: '',
      self_appraisal_enabled: false
    }
    loadAppraisals()
    loadStatistics()
  } catch (error) {
    console.error('Error creating appraisal:', error)
    alert(error.message || 'Error al crear la evaluación')
  } finally {
    creating.value = false
  }
}

const viewAppraisal = async (name) => {
  try {
    const data = await call('portal_rrhh.api.evaluaciones.get_appraisal_details', { name })
    selectedAppraisal.value = data
    showDetailsModal.value = true
  } catch (error) {
    console.error('Error loading appraisal details:', error)
    alert('Error al cargar los detalles de la evaluación')
  }
}

const editAppraisal = async (name) => {
  // Por ahora, abrir vista de detalles
  // En el futuro, se puede abrir un modal de edición
  viewAppraisal(name)
}

const submitAppraisal = async (name) => {
  if (confirm('¿Estás seguro de enviar esta evaluación?')) {
    try {
      await call('portal_rrhh.api.evaluaciones.submit_appraisal', { name })
      loadAppraisals()
      loadStatistics()
      if (selectedAppraisal.value?.appraisal?.name === name) {
        viewAppraisal(name)
      }
    } catch (error) {
      console.error('Error submitting appraisal:', error)
      alert(error.message || 'Error al enviar la evaluación')
    }
  }
}

const resetFilters = () => {
  filters.value = {
    search: '',
    status: '',
    appraisal_cycle: '',
    department: '',
    company: ''
  }
  offset.value = 0
  loadAppraisals()
}

const changePage = (direction) => {
  if (direction === -1 && offset.value > 0) {
    offset.value -= limit.value
  } else if (direction === 1 && offset.value + limit.value < totalCount.value) {
    offset.value += limit.value
  }
  loadAppraisals()
}

const onCycleChange = async () => {
  // Cargar perfiles cuando cambia el ciclo
  if (formData.value.appraisal_cycle) {
    await loadProfiles()
  }
}

const selectCycle = (cycle) => {
  filters.value.appraisal_cycle = cycle.name
  showCyclesModal.value = false
  loadAppraisals()
}

const getStatusVariant = (status) => {
  const variants = {
    'Borrador': 'subtle',
    'Auto-evaluado': 'yellow',
    'Enviado': 'blue',
    'Completado': 'green',
    'Cancelado': 'red',
    'Activo': 'green',
    'Draft': 'subtle'
  }
  return variants[status] || 'subtle'
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// Watch filters
watch(() => filters.value.status, () => {
  offset.value = 0
  loadAppraisals()
})

watch(() => filters.value.appraisal_cycle, () => {
  offset.value = 0
  loadAppraisals()
})

watch(() => filters.value.department, () => {
  offset.value = 0
  loadAppraisals()
})

watch(showGapAnalysis, (val) => {
  if (val) {
    loadGapAnalysis()
  }
})

// Initialize
onMounted(() => {
  loadAppraisals()
  loadStatistics()
  loadCycles()
  loadProfiles()
  loadEmployees()
  loadDepartments()
})
</script>
