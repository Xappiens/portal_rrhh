<template>
  <div class="h-full bg-gray-50 flex flex-col overflow-hidden">
    <!-- Header con Estadísticas -->
    <div class="bg-white border-b border-gray-200 px-6 py-4 flex-shrink-0">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Gestión de Incentivos</h1>
          <p class="text-sm text-gray-600 mt-1">Administra y visualiza los incentivos de empleados</p>
        </div>
        <Button
          variant="primary"
          @click="openCreateDialog"
          :disabled="isLoading"
        >
          <FeatherIcon name="plus" class="h-4 w-4 mr-2" />
          Nuevo Incentivo
        </Button>
      </div>

      <!-- Tarjetas de Estadísticas -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card class="p-4">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <FeatherIcon name="file-text" class="h-5 w-5 text-blue-600" />
              </div>
            </div>
            <div class="ml-3">
              <p class="text-xs font-medium text-gray-500">Total</p>
              <p class="text-xl font-semibold text-gray-900">
                {{ stats.total || 0 }}
              </p>
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
              <p class="text-xs font-medium text-gray-500">Enviados</p>
              <p class="text-xl font-semibold text-gray-900">
                {{ stats.submitted || 0 }}
              </p>
            </div>
          </div>
        </Card>

        <Card class="p-4">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                <FeatherIcon name="edit" class="h-5 w-5 text-yellow-600" />
              </div>
            </div>
            <div class="ml-3">
              <p class="text-xs font-medium text-gray-500">Borradores</p>
              <p class="text-xl font-semibold text-gray-900">
                {{ stats.draft || 0 }}
              </p>
            </div>
          </div>
        </Card>

        <Card class="p-4">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <FeatherIcon name="dollar-sign" class="h-5 w-5 text-purple-600" />
              </div>
            </div>
            <div class="ml-3">
              <p class="text-xs font-medium text-gray-500">Total Monto</p>
              <p class="text-xl font-semibold text-gray-900">
                {{ formatCurrency(stats.total_amount) }}
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>

    <!-- Filtros -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 mx-6 mt-4 mb-4 flex-shrink-0">
      <div class="px-4 py-3">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          <!-- Búsqueda de texto -->
          <div class="lg:col-span-2">
            <Input
              v-model="searchFilters.search_text"
              type="text"
              placeholder="Buscar por empleado, ID de incentivo..."
              variant="outline"
              size="sm"
            >
              <template #prefix>
                <FeatherIcon name="search" class="h-4 text-gray-400" />
              </template>
            </Input>
          </div>

          <!-- Filtro por estado -->
          <div>
            <select
              v-model="searchFilters.status"
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todos los estados</option>
              <option value="Draft">Borrador</option>
              <option value="Submitted">Enviado</option>
              <option value="Cancelled">Cancelado</option>
            </select>
          </div>

          <!-- Filtro por fecha -->
          <div>
            <Input
              v-model="searchFilters.payroll_date_from"
              type="date"
              placeholder="Fecha desde"
              variant="outline"
              size="sm"
              label="Fecha desde"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mt-3">
          <!-- Filtro por fecha hasta -->
          <div>
            <Input
              v-model="searchFilters.payroll_date_to"
              type="date"
              placeholder="Fecha hasta"
              variant="outline"
              size="sm"
              label="Fecha hasta"
            />
          </div>

          <!-- Botón limpiar filtros -->
          <div class="flex items-end">
            <Button
              variant="outline"
              size="sm"
              @click="clearFilters"
              :disabled="!hasActiveFilters"
            >
              <FeatherIcon name="x" class="h-4 w-4 mr-2" />
              Limpiar Filtros
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Lista de Incentivos -->
    <div class="flex-1 overflow-hidden px-6 pb-6">
      <Card class="h-full flex flex-col overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200 flex-shrink-0 flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-900">
            Incentivos ({{ incentivesList.length }})
          </h3>
          <div class="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              @click="reloadIncentives"
              :loading="isLoading"
            >
              <FeatherIcon name="refresh-cw" class="h-4 w-4 mr-2" />
              Actualizar
            </Button>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto p-6">
          <!-- Loading State -->
          <div v-if="isLoading && incentivesList.length === 0" class="text-center py-12">
            <FeatherIcon name="loader" class="h-8 w-8 animate-spin mx-auto mb-4 text-gray-400" />
            <p class="text-sm text-gray-500">Cargando incentivos...</p>
          </div>

          <!-- Empty State -->
          <div v-else-if="!isLoading && incentivesList.length === 0" class="text-center py-12">
            <FeatherIcon name="inbox" class="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p class="text-sm font-medium text-gray-900 mb-1">No hay incentivos</p>
            <p class="text-xs text-gray-500 mb-4">
              {{ hasActiveFilters ? 'Intenta ajustar los filtros' : 'Crea tu primer incentivo' }}
            </p>
            <Button
              v-if="!hasActiveFilters"
              variant="primary"
              size="sm"
              @click="openCreateDialog"
            >
              <FeatherIcon name="plus" class="h-4 w-4 mr-2" />
              Crear Incentivo
            </Button>
          </div>

          <!-- Lista de Incentivos -->
          <div v-else class="space-y-4">
            <div
              v-for="incentive in incentivesList"
              :key="incentive.name"
              class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
              @click="openIncentiveDetails(incentive)"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <!-- Header con empleado y estado -->
                  <div class="flex items-center space-x-3 mb-3">
                    <div class="flex-shrink-0">
                      <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                        <span class="text-sm font-semibold text-blue-700">
                          {{ getInitials(incentive.employee_name) }}
                        </span>
                      </div>
                    </div>
                    <div class="flex-1 min-w-0">
                      <h4 class="text-base font-semibold text-gray-900 truncate">
                        {{ incentive.employee_name || 'Sin nombre' }}
                      </h4>
                      <p class="text-xs text-gray-500 truncate">
                        {{ incentive.department || 'Sin departamento' }} • {{ incentive.company || 'Sin compañía' }}
                      </p>
                    </div>
                    <Badge
                      :variant="getStatusVariant(incentive.status)"
                      size="md"
                    >
                      {{ incentive.status_label || incentive.status }}
                    </Badge>
                  </div>

                  <!-- Información del incentivo -->
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                    <div class="space-y-2">
                      <div class="flex items-center space-x-2 text-sm">
                        <FeatherIcon name="dollar-sign" class="h-4 w-4 text-gray-400" />
                        <span class="text-gray-600">Monto:</span>
                        <span class="font-semibold text-gray-900">
                          {{ formatCurrency(incentive.incentive_amount) }} {{ incentive.currency || '' }}
                        </span>
                      </div>
                      <div class="flex items-center space-x-2 text-sm">
                        <FeatherIcon name="calendar" class="h-4 w-4 text-gray-400" />
                        <span class="text-gray-600">Fecha de nómina:</span>
                        <span class="font-medium text-gray-900">
                          {{ incentive.payroll_date_formatted || formatDate(incentive.payroll_date) }}
                        </span>
                      </div>
                    </div>
                    <div class="space-y-2">
                      <div class="flex items-center space-x-2 text-sm">
                        <FeatherIcon name="briefcase" class="h-4 w-4 text-gray-400" />
                        <span class="text-gray-600">Componente:</span>
                        <span class="font-medium text-gray-900 truncate">
                          {{ incentive.salary_component || 'Sin componente' }}
                        </span>
                      </div>
                      <div v-if="incentive.custom_provincia" class="flex items-center space-x-2 text-sm">
                        <FeatherIcon name="map-pin" class="h-4 w-4 text-gray-400" />
                        <span class="text-gray-600">Provincia:</span>
                        <span class="font-medium text-gray-900">
                          {{ incentive.custom_provincia }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- Información adicional -->
                  <div v-if="incentive.custom_by_hours || incentive.custom_justificación" class="flex flex-wrap gap-2 mt-3">
                    <Badge
                      v-if="incentive.custom_by_hours"
                      variant="info"
                      size="sm"
                    >
                      <FeatherIcon name="clock" class="h-3 w-3 mr-1" />
                      Por horas: {{ formatDuration(incentive.custom_incentive_hours) }}
                    </Badge>
                    <div
                      v-if="incentive.custom_justificación"
                      class="text-xs text-gray-600 bg-gray-50 rounded px-2 py-1 max-w-md truncate"
                      :title="incentive.custom_justificación"
                    >
                      {{ incentive.custom_justificación }}
                    </div>
                  </div>

                  <!-- Footer con ID y fecha de modificación -->
                  <div class="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
                    <a
                      @click.stop="openFormInNewTab('Employee Incentive', incentive.name, $event)"
                      class="text-xs text-blue-600 hover:text-blue-800 hover:underline font-mono cursor-pointer"
                      title="Ver detalle del incentivo"
                    >
                      ID: {{ incentive.name }}
                    </a>
                    <span class="text-xs text-gray-500">
                      Modificado: {{ formatDate(incentive.modified) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>

    <!-- Dialog para crear/editar incentivo -->
    <Dialog
      v-model="showCreateDialog"
      :options="{
        title: 'Nuevo Incentivo',
        size: 'lg'
      }"
    >
      <template #body>
        <div class="space-y-4">
          <Alert
            variant="info"
            title="Información"
          >
            Serás redirigido al formulario de Frappe para crear el incentivo.
          </Alert>
          <div class="text-sm text-gray-600">
            <p>Al hacer clic en "Crear", se abrirá el formulario de Employee Incentive en una nueva pestaña.</p>
          </div>
        </div>
      </template>
      <template #actions>
        <div class="flex justify-end space-x-2">
          <Button
            variant="outline"
            @click="showCreateDialog = false"
          >
            Cancelar
          </Button>
          <Button
            variant="primary"
            @click="createIncentive"
          >
            Crear Incentivo
          </Button>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { FeatherIcon, Button, Badge, Card, Input, Dialog, Alert, createResource } from 'frappe-ui'
import { ref, computed, watch, onMounted } from 'vue'
import { call } from 'frappe-ui'

// Estado
const isLoading = ref(false)
const incentivesList = ref([])
const stats = ref({
  total: 0,
  submitted: 0,
  draft: 0,
  total_amount: 0
})
const showCreateDialog = ref(false)

// Filtros
const searchFilters = ref({
  search_text: '',
  status: '',
  payroll_date_from: '',
  payroll_date_to: '',
  employee: '',
  company: '',
  custom_provincia: '',
  salary_component: ''
})

// Resource para cargar incentivos
const incentivesResource = createResource({
  url: 'portal_rrhh.api.incentive.get_incentives',
  params: () => ({
    filters: JSON.stringify(searchFilters.value)
  }),
  onSuccess(data) {
    incentivesList.value = data.data || []
  }
})

// Resource para estadísticas
const statsResource = createResource({
  url: 'portal_rrhh.api.incentive.get_incentive_stats',
  params: () => ({
    filters: JSON.stringify(searchFilters.value)
  }),
  onSuccess(data) {
    stats.value = data || {}
  }
})

// Computed
const hasActiveFilters = computed(() => {
  return !!(
    searchFilters.value.search_text ||
    searchFilters.value.status ||
    searchFilters.value.payroll_date_from ||
    searchFilters.value.payroll_date_to ||
    searchFilters.value.employee ||
    searchFilters.value.company ||
    searchFilters.value.custom_provincia ||
    searchFilters.value.salary_component
  )
})

// Métodos
const reloadIncentives = async () => {
  isLoading.value = true
  try {
    await Promise.all([
      incentivesResource.reload(),
      statsResource.reload()
    ])
  } finally {
    isLoading.value = false
  }
}

const clearFilters = () => {
  searchFilters.value = {
    search_text: '',
    status: '',
    payroll_date_from: '',
    payroll_date_to: '',
    employee: '',
    company: '',
    custom_provincia: '',
    salary_component: ''
  }
}

const openCreateDialog = () => {
  showCreateDialog.value = true
}

const createIncentive = () => {
  const url = '/app/employee-incentive/new-employee-incentive'
  window.open(url, '_blank')
  showCreateDialog.value = false
}

const openIncentiveDetails = (incentive) => {
  openFormInNewTab('Employee Incentive', incentive.name)
}

const openFormInNewTab = (doctype, docname, event) => {
  if (event) {
    event.stopPropagation()
  }
  const doctypeSlug = doctype.toLowerCase().replace(/\s+/g, '-')
  const url = `/app/${doctypeSlug}/${encodeURIComponent(docname)}`
  window.open(url, '_blank')
}

const getInitials = (name) => {
  if (!name) return 'E'
  const words = name.trim().split(' ')
  if (words.length >= 2) {
    return (words[0].charAt(0) + words[words.length - 1].charAt(0)).toUpperCase()
  }
  return name.charAt(0).toUpperCase()
}

const getStatusVariant = (status) => {
  const variants = {
    'Draft': 'warning',
    'Submitted': 'success',
    'Cancelled': 'danger',
    'Borrador': 'warning',
    'Enviado': 'success',
    'Cancelado': 'danger'
  }
  return variants[status] || 'default'
}

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return new Intl.NumberFormat('es-ES', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatDuration = (seconds) => {
  if (!seconds) return '0h'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  if (hours > 0 && minutes > 0) {
    return `${hours}h ${minutes}m`
  } else if (hours > 0) {
    return `${hours}h`
  } else {
    return `${minutes}m`
  }
}

// Watchers
watch(
  searchFilters,
  () => {
    // Debounce para búsqueda de texto
    const delay = searchFilters.value.search_text ? 500 : 200
    const timeout = setTimeout(() => {
      reloadIncentives()
    }, delay)
    return () => clearTimeout(timeout)
  },
  { deep: true }
)

// Lifecycle
onMounted(() => {
  reloadIncentives()
})
</script>
