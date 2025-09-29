<template>
  <div class="h-full bg-gray-50 flex flex-col">
    <!-- Stats Cards Section -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 m-6 relative flex-shrink-0">
      <!-- Toggle Button -->
      <Button
        variant="ghost"
        size="sm"
        @click="isStatsExpanded = !isStatsExpanded"
        class="absolute top-2 right-2 z-10 p-1 h-8 w-8"
      >
        <FeatherIcon
          :name="isStatsExpanded ? 'x' : 'menu'"
          class="h-4 w-4"
        />
      </Button>

      <!-- Cards Content -->
      <div v-show="isStatsExpanded" class="p-4">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          <Card class="p-3">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xs font-medium text-gray-600">Bajas esta Semana</p>
                <p class="text-xl font-bold text-gray-900">{{ bajasEstaSemana }}</p>
              </div>
              <div class="p-1.5 rounded-full bg-red-100 text-red-600">
                <FeatherIcon name="user-minus" class="h-4 w-4" />
              </div>
            </div>
          </Card>

          <Card class="p-3">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xs font-medium text-gray-600">Altas esta Semana</p>
                <p class="text-xl font-bold text-gray-900">{{ altasEstaSemana }}</p>
              </div>
              <div class="p-1.5 rounded-full bg-green-100 text-green-600">
                <FeatherIcon name="user-plus" class="h-4 w-4" />
              </div>
            </div>
          </Card>

          <Card class="p-3">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xs font-medium text-gray-600">Anexos que terminan</p>
                <p class="text-xl font-bold text-gray-900">{{ contratosPendientes }}</p>
              </div>
              <div class="p-1.5 rounded-full bg-yellow-100 text-yellow-600">
                <FeatherIcon name="file-minus" class="h-4 w-4" />
              </div>
            </div>
          </Card>

          <Card class="p-3">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xs font-medium text-gray-600">Nuevos anexos</p>
                <p class="text-xl font-bold text-gray-900">{{ contratosFirmados }}</p>
              </div>
              <div class="p-1.5 rounded-full bg-blue-100 text-blue-600">
                <FeatherIcon name="file-plus" class="h-4 w-4" />
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>

    <!-- Employee Management Section -->
    <div class="flex gap-6 px-6 pb-6 flex-1 min-h-0">
      <!-- Left Column: Employee List -->
      <div class="w-1/3 bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden flex flex-col h-full">
        <div class="px-4 py-3 border-b border-gray-200 flex-shrink-0">
          <h3 class="text-sm font-medium text-gray-900">Empleados</h3>
        </div>
        <div class="overflow-y-auto flex-1">
          <div v-if="loadingEmployees" class="p-4 text-center text-gray-500">
            <FeatherIcon name="loader" class="h-6 w-6 animate-spin mx-auto mb-2" />
            Cargando empleados...
          </div>
          <div v-else-if="!employees.data || employees.data.length === 0" class="p-4 text-center text-gray-500">
            No hay empleados disponibles
          </div>
          <div v-else class="divide-y divide-gray-200">
            <div
              v-for="employee in employees.data"
              :key="employee.name"
              @click="selectEmployee(employee)"
              class="p-3 cursor-pointer hover:bg-gray-50 transition-colors"
              :class="{ 'bg-blue-50 border-r-2 border-blue-500': selectedEmployee?.name === employee.name }"
            >
              <div class="flex items-start justify-between">
                <div class="flex items-center space-x-3 flex-1 min-w-0">
                  <div class="flex-shrink-0 h-10 w-10">
                    <div class="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                      <span class="text-sm font-semibold text-blue-700">
                        {{ getInitials(employee.employee_name) }}
                      </span>
                    </div>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 truncate">
                      {{ employee.employee_name || 'Sin nombre' }}
                    </p>
                    <p class="text-xs text-gray-600 truncate">
                      <span class="font-medium">DNI:</span> {{ employee.custom_dninie || employee.name || 'Sin DNI' }}
                    </p>
                    <p class="text-xs text-gray-500 truncate">
                      {{ employee.designation || 'Sin puesto' }}
                    </p>
                  </div>
                </div>

                <!-- Empresas en la parte superior derecha -->
                <div class="flex-shrink-0 ml-3">
                  <div class="flex flex-col gap-1 max-w-48">
                    <div
                      v-for="company in employee.companies"
                      :key="company"
                      class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 truncate"
                      :title="company"
                    >
                      {{ company }}
                    </div>
                    <div
                      v-if="!employee.companies || employee.companies.length === 0"
                      class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600"
                    >
                      Sin empresas
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Job Offers -->
      <div class="flex-1 bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden flex flex-col h-full">
        <div class="px-4 py-3 border-b border-gray-200 flex-shrink-0">
          <h3 class="text-sm font-medium text-gray-900">
            {{ selectedEmployee ? `Job Offers - ${selectedEmployee.employee_name}` : 'Selecciona un empleado' }}
          </h3>
        </div>
        <div class="overflow-y-auto flex-1">
          <div v-if="!selectedEmployee" class="p-8 text-center text-gray-500">
            <FeatherIcon name="user" class="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>Selecciona un empleado para ver sus Job Offers</p>
          </div>
          <div v-else-if="loadingJobOffers" class="p-4 text-center text-gray-500">
            <FeatherIcon name="loader" class="h-6 w-6 animate-spin mx-auto mb-2" />
            Cargando Job Offers...
          </div>
          <div v-else-if="!jobOffers.data || jobOffers.data.length === 0" class="p-4 text-center text-gray-500">
            <FeatherIcon name="file-text" class="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>No hay Job Offers para este empleado</p>
          </div>
          <div v-else class="divide-y divide-gray-200">
            <div
              v-for="jobOffer in jobOffers.data"
              :key="jobOffer.name"
              class="p-4 hover:bg-gray-50 transition-colors"
            >
              <div class="flex items-center justify-between">
                <div class="flex-1">
                  <div class="flex items-center space-x-3 mb-2">
                    <h4 class="text-sm font-medium text-gray-900">{{ jobOffer.designation || 'Sin título' }}</h4>
                    <Badge
                      :theme="getJobOfferStatusTheme(jobOffer.status)"
                      variant="subtle"
                      class="text-xs"
                    >
                      {{ jobOffer.status || 'Sin estado' }}
                    </Badge>
                  </div>
                  <div class="grid grid-cols-2 gap-4 text-xs text-gray-500">
                    <div>
                      <span class="font-medium">Fecha Inicio:</span>
                      <span class="ml-1">{{ formatDate(jobOffer.custom_fecha_inicio) }}</span>
                    </div>
                    <div>
                      <span class="font-medium">Fecha Fin:</span>
                      <span class="ml-1">{{ formatDate(jobOffer.custom_fecha_fin) }}</span>
                    </div>
                    <div>
                      <span class="font-medium">Salario:</span>
                      <span class="ml-1">{{ jobOffer.offer_date || 'No especificado' }}</span>
                    </div>
                    <div>
                      <span class="font-medium">Creado:</span>
                      <span class="ml-1">{{ formatDate(jobOffer.creation) }}</span>
                    </div>
                  </div>
                </div>
                <div class="flex items-center space-x-2 ml-4">
                  <Button variant="ghost" size="sm" theme="blue">
                    <FeatherIcon name="eye" class="h-4" />
                  </Button>
                  <Button variant="ghost" size="sm" theme="green">
                    <FeatherIcon name="edit" class="h-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { FeatherIcon, Button, Badge, Card, createResource } from 'frappe-ui'
import { ref, computed } from 'vue'

// Variables reactivas para los indicadores
const isStatsExpanded = ref(true)

// Employee management
const selectedEmployee = ref(null)

// Resources using CRM pattern
const contratacionStats = createResource({
  url: 'portal_rrhh.api.job_offer.get_contratacion_stats',
  cache: 'contratacion-stats',
  auto: true
})

const employees = createResource({
  url: 'portal_rrhh.api.employee.get_employees',
  cache: 'employees',
  auto: true
})

const jobOffers = createResource({
  url: 'portal_rrhh.api.job_offer.get_job_offers_by_employee',
  cache: ['job-offers', () => selectedEmployee.value?.name],
  auto: false
})

// Computed properties for stats
const bajasEstaSemana = computed(() => contratacionStats.data?.bajas_esta_semana || 0)
const altasEstaSemana = computed(() => contratacionStats.data?.altas_esta_semana || 0)
const contratosPendientes = computed(() => contratacionStats.data?.contratos_pendientes || 0)
const contratosFirmados = computed(() => contratacionStats.data?.contratos_firmados || 0)

// Loading states
const loadingEmployees = computed(() => employees.loading)
const loadingJobOffers = computed(() => jobOffers.loading)

// Función para seleccionar empleado
const selectEmployee = (employee) => {
  selectedEmployee.value = employee
  jobOffers.params = { employee_name: employee.name }
  jobOffers.reload()
}

// Función para obtener iniciales del nombre
const getInitials = (name) => {
  if (!name) return 'E'
  const words = name.trim().split(' ')
  if (words.length >= 2) {
    return (words[0].charAt(0) + words[words.length - 1].charAt(0)).toUpperCase()
  }
  return name.charAt(0).toUpperCase()
}


// Función para formatear fechas
const formatDate = (dateString) => {
  if (!dateString) return 'No especificado'
  const date = new Date(dateString)
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// Función para obtener el tema del estado del Job Offer
const getJobOfferStatusTheme = (status) => {
  const statusMap = {
    'Accepted': 'green',
    'Rejected': 'red',
    'Pending': 'yellow',
    'Alta': 'blue',
    'Baja': 'gray'
  }
  return statusMap[status] || 'gray'
}


</script>
