<template>
  <div class="flex-1 p-6 bg-gray-50">
      <!-- Dashboard de Estadísticas -->
      <div class="mb-6">
        <div class="mb-4">
          <h2 class="text-2xl font-bold text-gray-900">Dashboard RRHH</h2>
          <p class="text-sm text-gray-600 mt-1">Estadísticas e indicadores importantes del departamento</p>
        </div>

        <!-- Tarjetas de Estadísticas -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Card 
            class="p-4 cursor-pointer hover:shadow-lg transition-shadow"
            :class="{ 'ring-2 ring-red-500': selectedIndicator === 'missing_data' }"
            @click="selectedIndicator = 'missing_data'"
          >
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                  <FeatherIcon name="alert-triangle" class="h-6 w-6 text-red-600" />
                </div>
              </div>
              <div class="ml-4">
                <p class="text-xs font-medium text-gray-500">Empleados sin Datos</p>
                <p class="text-2xl font-semibold text-gray-900">
                  {{ dashboardStats.summary?.employees_missing_data_count || 0 }}
                </p>
                <p class="text-xs text-gray-500 mt-1">
                  de {{ dashboardStats.summary?.total_employees || 0 }} empleados
                </p>
              </div>
            </div>
          </Card>

          <Card 
            class="p-4 cursor-pointer hover:shadow-lg transition-shadow"
            :class="{ 'ring-2 ring-orange-500': selectedIndicator === 'job_offers_expired' }"
            @click="selectedIndicator = 'job_offers_expired'"
          >
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                  <FeatherIcon name="file-text" class="h-6 w-6 text-orange-600" />
                </div>
              </div>
              <div class="ml-4">
                <p class="text-xs font-medium text-gray-500">Job Offers Vencidos</p>
                <p class="text-2xl font-semibold text-gray-900">
                  {{ dashboardStats.summary?.job_offers_expired_active_count || 0 }}
                </p>
                <p class="text-xs text-gray-500 mt-1">Estado Alta con fecha vencida</p>
              </div>
            </div>
          </Card>

          <Card 
            class="p-4 cursor-pointer hover:shadow-lg transition-shadow"
            :class="{ 'ring-2 ring-yellow-500': selectedIndicator === 'modificaciones_expired' }"
            @click="selectedIndicator = 'modificaciones_expired'"
          >
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                  <FeatherIcon name="edit" class="h-6 w-6 text-yellow-600" />
                </div>
              </div>
              <div class="ml-4">
                <p class="text-xs font-medium text-gray-500">Modificaciones Vencidas</p>
                <p class="text-2xl font-semibold text-gray-900">
                  {{ dashboardStats.summary?.modificaciones_expired_active_count || 0 }}
                </p>
                <p class="text-xs text-gray-500 mt-1">Estado Alta con fecha vencida</p>
              </div>
            </div>
          </Card>

          <Card 
            class="p-4 cursor-pointer hover:shadow-lg transition-shadow"
            :class="{ 'ring-2 ring-purple-500': selectedIndicator === 'inconsistencies' }"
            @click="selectedIndicator = 'inconsistencies'"
          >
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                  <FeatherIcon name="alert-circle" class="h-6 w-6 text-purple-600" />
                </div>
              </div>
              <div class="ml-4">
                <p class="text-xs font-medium text-gray-500">Incoherencias</p>
                <p class="text-2xl font-semibold text-gray-900">
                  {{ dashboardStats.summary?.job_offers_baja_modificaciones_alta_count || 0 }}
                </p>
                <p class="text-xs text-gray-500 mt-1">Job Offer Baja / Mod. Alta</p>
              </div>
            </div>
          </Card>
        </div>

        <!-- Cuadro de Detalles del Indicador Seleccionado -->
        <div v-if="selectedIndicator" class="mb-6">
          <!-- Empleados sin datos -->
          <Card v-if="selectedIndicator === 'missing_data' && dashboardStats.employees_missing_data?.length > 0" class="p-4">
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center space-x-2">
                <FeatherIcon name="user-x" class="h-5 w-5 text-red-600" />
                <h3 class="text-lg font-semibold text-gray-900">
                  Empleados con Datos Faltantes ({{ dashboardStats.employees_missing_data.length }})
                </h3>
              </div>
              <Button variant="ghost" size="sm" @click="selectedIndicator = null">
                <FeatherIcon name="x" class="h-4" />
              </Button>
            </div>
            <div class="max-h-96 overflow-y-auto space-y-2 pr-2">
              <div
                v-for="emp in dashboardStats.employees_missing_data"
                :key="emp.employee_name"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div class="flex-1">
                  <div class="flex items-center space-x-2 flex-wrap">
                    <span class="font-medium text-gray-900">{{ emp.employee_display_name }}</span>
                    <Badge :label="emp.department" variant="subtle" />
                    <Badge :label="emp.designation" variant="subtle" />
                  </div>
                  <div class="mt-1 text-sm text-gray-600">
                    Faltan: <span class="font-semibold text-red-600">{{ emp.missing_fields.join(', ') }}</span>
                  </div>
                </div>
                <Badge :label="`${emp.missing_count} campos`" variant="error" />
              </div>
            </div>
          </Card>

          <!-- Job Offers vencidos -->
          <Card v-if="selectedIndicator === 'job_offers_expired' && dashboardStats.job_offers_expired_active?.length > 0" class="p-4">
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center space-x-2">
                <FeatherIcon name="file-text" class="h-5 w-5 text-orange-600" />
                <h3 class="text-lg font-semibold text-gray-900">
                  Job Offers Vencidos en Estado Alta ({{ dashboardStats.job_offers_expired_active.length }})
                </h3>
              </div>
              <Button variant="ghost" size="sm" @click="selectedIndicator = null">
                <FeatherIcon name="x" class="h-4" />
              </Button>
            </div>
            <div class="max-h-96 overflow-y-auto space-y-2 pr-2">
              <div
                v-for="jo in dashboardStats.job_offers_expired_active"
                :key="jo.job_offer_name"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div class="flex-1">
                  <div class="flex items-center space-x-2 flex-wrap">
                    <span class="font-medium text-gray-900">{{ jo.job_offer_name }}</span>
                    <Badge :label="jo.applicant_name" variant="subtle" />
                    <Badge :label="jo.designation" variant="subtle" />
                  </div>
                  <div class="mt-1 text-sm text-gray-600">
                    Fecha fin: <span class="font-semibold">{{ jo.fecha_fin }}</span> | 
                    Vencido hace: <span class="font-semibold text-orange-600">{{ jo.dias_vencido }} días</span>
                  </div>
                </div>
                <Badge :label="`${jo.dias_vencido} días`" variant="warning" />
              </div>
            </div>
          </Card>

          <!-- Modificaciones vencidas -->
          <Card v-if="selectedIndicator === 'modificaciones_expired' && dashboardStats.modificaciones_expired_active?.length > 0" class="p-4">
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center space-x-2">
                <FeatherIcon name="edit" class="h-5 w-5 text-yellow-600" />
                <h3 class="text-lg font-semibold text-gray-900">
                  Modificaciones RRHH Vencidas en Estado Alta ({{ dashboardStats.modificaciones_expired_active.length }})
                </h3>
              </div>
              <Button variant="ghost" size="sm" @click="selectedIndicator = null">
                <FeatherIcon name="x" class="h-4" />
              </Button>
            </div>
            <div class="max-h-96 overflow-y-auto space-y-2 pr-2">
              <div
                v-for="mod in dashboardStats.modificaciones_expired_active"
                :key="mod.modificacion_name"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div class="flex-1">
                  <div class="flex items-center space-x-2 flex-wrap">
                    <span class="font-medium text-gray-900">{{ mod.modificacion_name }}</span>
                    <Badge :label="mod.employee_display_name" variant="subtle" />
                    <Badge :label="mod.tipo_actualizacion" variant="subtle" />
                  </div>
                  <div class="mt-1 text-sm text-gray-600">
                    Fecha fin: <span class="font-semibold">{{ mod.end_date }}</span> | 
                    Vencido hace: <span class="font-semibold text-yellow-600">{{ mod.dias_vencido }} días</span>
                  </div>
                </div>
                <Badge :label="`${mod.dias_vencido} días`" variant="warning" />
              </div>
            </div>
          </Card>

          <!-- Incoherencias Job Offer Baja / Modificaciones Alta -->
          <Card v-if="selectedIndicator === 'inconsistencies' && dashboardStats.job_offers_baja_modificaciones_alta?.length > 0" class="p-4">
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center space-x-2">
                <FeatherIcon name="alert-circle" class="h-5 w-5 text-purple-600" />
                <h3 class="text-lg font-semibold text-gray-900">
                  Incoherencias Detectadas ({{ dashboardStats.job_offers_baja_modificaciones_alta.length }})
                </h3>
              </div>
              <Button variant="ghost" size="sm" @click="selectedIndicator = null">
                <FeatherIcon name="x" class="h-4" />
              </Button>
            </div>
            <div class="max-h-96 overflow-y-auto space-y-2 pr-2">
              <div
                v-for="inc in dashboardStats.job_offers_baja_modificaciones_alta"
                :key="inc.job_offer_name"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div class="flex-1">
                  <div class="flex items-center space-x-2 flex-wrap">
                    <span class="font-medium text-gray-900">{{ inc.job_offer_name }}</span>
                    <Badge :label="inc.job_offer_state" variant="error" />
                    <Badge :label="inc.employee_display_name" variant="subtle" />
                  </div>
                  <div class="mt-1 text-sm text-gray-600">
                    Job Offer en <span class="font-semibold text-red-600">Baja</span> pero tiene 
                    <span class="font-semibold text-purple-600">{{ inc.modificaciones_count }} modificación(es)</span> en estado Alta
                  </div>
                </div>
                <Badge :label="`${inc.modificaciones_count} mods`" variant="info" />
              </div>
            </div>
          </Card>

          <!-- Mensaje cuando no hay problemas en el indicador seleccionado -->
          <Card v-if="selectedIndicator && getSelectedIndicatorCount() === 0 && !dashboardLoading" class="p-4">
            <Alert variant="info" title="Sin problemas">
              No se encontraron problemas para este indicador.
            </Alert>
          </Card>
        </div>

        <!-- Mensaje cuando no hay problemas -->
        <Card v-if="totalProblems === 0 && !dashboardLoading && !selectedIndicator" class="p-4 mb-6">
          <Alert variant="success" title="¡Todo en orden!">
            No se han detectado problemas en los datos del departamento de RRHH.
          </Alert>
        </Card>
      </div>

      <!-- Filtros y búsqueda -->
      <div class="bg-white rounded-lg shadow p-4 mb-6">
        <div class="flex items-center space-x-4">
          <div class="flex-1">
            <Input
              v-model="searchQuery"
              type="text"
              placeholder="Buscar empleados..."
              variant="outline"
              size="sm"
            >
              <template #prefix>
                <FeatherIcon name="search" class="h-4 text-gray-400" />
              </template>
            </Input>
          </div>
          <select
            v-model="selectedDepartment"
            class="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Todos los departamentos</option>
            <option v-for="dept in departamentos" :key="dept.name" :value="dept.department_name">
              {{ dept.department_name }}
            </option>
          </select>
          <Button variant="outline" size="sm">
            <template #prefix>
              <FeatherIcon name="filter" class="h-4" />
            </template>
            Filtrar
          </Button>
        </div>
      </div>

      <!-- Tabla de empleados -->
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Empleado
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Departamento
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cargo
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fecha de Ingreso
                </th>

              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-if="loading && empleados.length === 0" class="text-center">
                <td colspan="6" class="px-6 py-4">
                  <div class="flex items-center justify-center">
                    <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    <span class="ml-2">Cargando empleados...</span>
                  </div>
                </td>
              </tr>
              <tr v-else-if="empleados.length === 0" class="text-center">
                <td colspan="6" class="px-6 py-4 text-gray-500">
                  No se encontraron empleados
                </td>
              </tr>
              <tr v-else v-for="empleado in empleados" :key="empleado.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10">
                      <img v-if="empleado.avatar" :src="empleado.avatar" :alt="empleado.nombre" class="h-10 w-10 rounded-full object-cover">
                      <div v-else class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                        <span class="text-sm font-medium text-gray-700">{{ empleado.nombre.charAt(0) }}</span>
                      </div>
                    </div>
                    <div class="ml-4">
                      <div class="text-sm font-medium text-gray-900">{{ empleado.nombre }}</div>
                      <div class="text-sm text-gray-500">{{ empleado.email }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ empleado.departamento }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ empleado.cargo }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <Badge
                    :theme="empleado.estado === 'Activo' ? 'green' : 'red'"
                    variant="subtle"
                  >
                    {{ empleado.estado }}
                  </Badge>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ empleado.fechaIngreso }}
                </td>

              </tr>
            </tbody>
          </table>
        </div>
        <div class="px-6 py-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
          <Button @click="prevPage" :disabled="loading || offset === 0" variant="outline">
            <template #prefix>
              <FeatherIcon name="chevron-left" class="h-4" />
            </template>
            Anterior
          </Button>
          <span class="text-sm text-gray-500">
            Página {{ currentPage }}
          </span>
          <Button @click="nextPage" :disabled="loading || !hasMore" variant="outline">
            Siguiente
            <template #suffix>
              <FeatherIcon name="chevron-right" class="h-4" />
            </template>
          </Button>
        </div>
      </div>
    </div>
</template>

<script setup>
import { FeatherIcon, Card, Badge, Button, Alert, call } from 'frappe-ui'
import { ref, onMounted, computed } from 'vue'

const empleados = ref([])
const departamentos = ref([]) // Inicializado como array vacío
const loading = ref(false)
const searchQuery = ref('')
const selectedDepartment = ref('')
const offset = ref(0)
const hasMore = ref(false)
const limit = 6

// Dashboard stats
const dashboardStats = ref({
  employees_missing_data: [],
  job_offers_expired_active: [],
  modificaciones_expired_active: [],
  job_offers_baja_modificaciones_alta: [],
  summary: {
    total_employees: 0,
    employees_missing_data_count: 0,
    job_offers_expired_active_count: 0,
    modificaciones_expired_active_count: 0,
    job_offers_baja_modificaciones_alta_count: 0
  }
})
const dashboardLoading = ref(false)
const selectedIndicator = ref(null) // 'missing_data', 'job_offers_expired', 'modificaciones_expired', 'inconsistencies', o null

const totalProblems = computed(() => {
  return (dashboardStats.value.summary?.employees_missing_data_count || 0) +
         (dashboardStats.value.summary?.job_offers_expired_active_count || 0) +
         (dashboardStats.value.summary?.modificaciones_expired_active_count || 0) +
         (dashboardStats.value.summary?.job_offers_baja_modificaciones_alta_count || 0)
})

// Función para obtener el conteo del indicador seleccionado
const getSelectedIndicatorCount = () => {
  switch (selectedIndicator.value) {
    case 'missing_data':
      return dashboardStats.value.employees_missing_data?.length || 0
    case 'job_offers_expired':
      return dashboardStats.value.job_offers_expired_active?.length || 0
    case 'modificaciones_expired':
      return dashboardStats.value.modificaciones_expired_active?.length || 0
    case 'inconsistencies':
      return dashboardStats.value.job_offers_baja_modificaciones_alta?.length || 0
    default:
      return 0
  }
}

// Load dashboard stats
const loadDashboardStats = async () => {
  dashboardLoading.value = true
  try {
    const result = await call('portal_rrhh.portal_rrhh.employee_data.get_rrhh_dashboard_stats')
    if (result) {
      dashboardStats.value = result
    }
  } catch (error) {
    console.error('Error loading dashboard stats:', error)
  } finally {
    dashboardLoading.value = false
  }
}

// Load employees data
// Load employees data
const loadEmployees = async (direction = 'init') => {
  let newOffset = offset.value

  if (direction === 'next') {
    newOffset += limit
  } else if (direction === 'prev') {
    newOffset = Math.max(0, newOffset - limit)
  } else if (direction === 'init') {
    newOffset = 0
  }

  loading.value = true
  
  const filters = {
    status: 'Active'
  }
  
  if (selectedDepartment.value) {
    filters.department = selectedDepartment.value
  }

  try {
    const result = await call('portal_rrhh.portal_rrhh.employee_data.get_employees_list', {
      filters: filters,
      limit: limit,
      offset: newOffset,
      search_term: searchQuery.value
    })

    if (result && result.employees) {
      const newEmployees = result.employees.map(emp => ({
        id: emp.name,
        nombre: emp.employee_name,
        email: emp.email,
        departamento: emp.department || 'Sin departamento',
        cargo: emp.designation || 'Sin cargo',
        estado: emp.status === 'Active' ? 'Activo' : 'Inactivo',
        fechaIngreso: emp.date_of_joining_formatted || 'N/A',
        avatar: emp.avatar
      }))
      
      // Always replace employees list
      empleados.value = newEmployees
      
      hasMore.value = result.has_more
      offset.value = newOffset
    }
  } catch (error) {
    console.error('Error loading employees:', error)
  } finally {
    loading.value = false
  }
}

const nextPage = () => {
  loadEmployees('next')
}

const prevPage = () => {
  loadEmployees('prev')
}

const currentPage = computed(() => {
  return Math.floor(offset.value / limit) + 1
})

// Load departments
const loadDepartments = async () => {
  try {
    const result = await call('portal_rrhh.portal_rrhh.employee_data.get_departments_list')

    if (result) {
      departamentos.value = result
    }
  } catch (error) {
    console.error('Error loading departments:', error)
  }
}

// Watch for filter changes
import { watch } from 'vue'
import { debounce } from 'frappe-ui'

watch(selectedDepartment, () => {
  loadEmployees('init')
})

watch(searchQuery, debounce(() => {
  loadEmployees('init')
}, 300))

onMounted(() => {
  loadEmployees()
  loadDepartments()
  loadDashboardStats()
})
</script>
