<template>
  <div class="px-5 py-6 sm:px-8 h-full overflow-y-auto">
    <div class="mb-6 flex flex-col justify-between sm:flex-row sm:items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Mi Perfil</h1>
        <p class="text-base text-gray-500">
          Detalles de tu cuenta y perfil de empleado
        </p>
      </div>
      <div v-if="employee.data && employee.data.status" class="mt-4 sm:mt-0">
        <Badge
          :theme="
            employee.data.status === 'Active'
              ? 'green'
              : employee.data.status === 'Left'
              ? 'red'
              : 'orange'
          "
          size="lg"
        >
          {{ employee.data.status }}
        </Badge>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <!-- User Account Details -->
      <Card class="h-full">
        <template #header>
          <div class="flex items-center gap-2">
            <FeatherIcon name="user" class="h-5 w-5 text-gray-500" />
            <span class="text-lg font-medium">Cuenta de Usuario</span>
          </div>
        </template>
        <div class="space-y-4 p-4">
          <div class="flex items-center gap-4">
            <div
              class="flex h-20 w-20 items-center justify-center rounded-full bg-gray-100 text-2xl font-semibold text-gray-600"
            >
              {{ userInitials }}
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-900">
                {{ sessionStore().user }}
              </h3>
              <p class="text-sm text-gray-500">
                {{
                  usersStore().getUser('sessionUser').full_name || 'Sin nombre'
                }}
              </p>
            </div>
          </div>
          <div class="border-t pt-4">
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label class="block text-xs font-medium uppercase text-gray-500"
                  >Email</label
                >
                <div class="mt-1 text-sm text-gray-900">
                  {{
                    usersStore().getUser('sessionUser').email || 'No disponible'
                  }}
                </div>
              </div>
              <div>
                <label class="block text-xs font-medium uppercase text-gray-500"
                  >Roles</label
                >
                <div class="mt-1 flex flex-wrap gap-1">
                  <Badge
                    v-for="role in (
                      usersStore().getUser('sessionUser').roles || []
                    ).slice(0, 3)"
                    :key="role"
                    theme="gray"
                  >
                    {{ role }}
                  </Badge>
                  <span
                    v-if="
                      (usersStore().getUser('sessionUser').roles || []).length >
                      3
                    "
                    class="text-xs text-gray-500"
                    >+{{
                      usersStore().getUser('sessionUser').roles.length - 3
                    }}</span
                  >
                </div>
              </div>
            </div>
          </div>
        </div>
      </Card>

      <!-- Employee Details -->
      <Card class="h-full">
        <template #header>
          <div class="flex items-center gap-2">
            <FeatherIcon name="briefcase" class="h-5 w-5 text-gray-500" />
            <span class="text-lg font-medium">Información de Empleado</span>
          </div>
        </template>
        <div class="p-4">
          <div v-if="employee.loading" class="flex justify-center py-8">
            <LoadingIndicator />
          </div>
          <div
            v-else-if="employee.error"
            class="rounded-md bg-red-50 p-4 text-red-700"
          >
            <p>No se pudo cargar la información del empleado.</p>
            <p v-if="employee.error.message" class="text-xs mt-1">{{ employee.error.message }}</p>
          </div>
          <div v-else-if="!employee.data" class="py-8 text-center text-gray-500">
            <FeatherIcon
              name="alert-circle"
              class="mx-auto mb-2 h-8 w-8 text-gray-400"
            />
            <p>Este usuario no tiene un perfil de empleado asociado.</p>
          </div>
          <div v-else class="space-y-4">
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label class="block text-xs font-medium uppercase text-gray-500"
                  >Nombre Completo</label
                >
                <div class="mt-1 text-sm font-medium text-gray-900">
                  {{ employee.data.employee_name }}
                </div>
              </div>
              <div>
                <label class="block text-xs font-medium uppercase text-gray-500"
                  >Número de Empleado</label
                >
                <div class="mt-1 text-sm text-gray-900">
                  {{ employee.data.employee_number || '-' }}
                </div>
              </div>
              <div>
                <label class="block text-xs font-medium uppercase text-gray-500"
                  >Departamento</label
                >
                <div class="mt-1 text-sm text-gray-900">
                  {{ employee.data.department || '-' }}
                </div>
              </div>
              <div>
                <label class="block text-xs font-medium uppercase text-gray-500"
                  >Puesto</label
                >
                <div class="mt-1 text-sm text-gray-900">
                  {{ employee.data.designation || '-' }}
                </div>
              </div>
              <div>
                <label class="block text-xs font-medium uppercase text-gray-500"
                  >Reporta a</label
                >
                <div class="mt-1 text-sm text-gray-900">
                  {{ employee.data.reports_to || '-' }}
                </div>
              </div>
              <div>
                <label class="block text-xs font-medium uppercase text-gray-500"
                  >Fecha de Ingreso</label
                >
                <div class="mt-1 text-sm text-gray-900">
                  {{ employee.data.date_of_joining || '-' }}
                </div>
              </div>
              <div>
                <label class="block text-xs font-medium uppercase text-gray-500"
                  >Empresa</label
                >
                <div class="mt-1 text-sm text-gray-900">
                  {{ employee.data.company || '-' }}
                </div>
              </div>
              <div>
                <label class="block text-xs font-medium uppercase text-gray-500"
                  >Email Empresa</label
                >
                <div class="mt-1 text-sm text-gray-900">
                  {{ employee.data.company_email || '-' }}
                </div>
              </div>
              <div>
                <label class="block text-xs font-medium uppercase text-gray-500"
                  >IBAN</label
                >
                <div class="mt-1 text-sm text-gray-900 font-mono">
                  {{ formatIban(employee.data.iban) || '-' }}
                </div>
              </div>
              <div>
                <label class="block text-xs font-medium uppercase text-gray-500"
                  >Retención IRPF</label
                >
                <div class="mt-1 text-sm text-gray-900">
                  {{ employee.data.custom_irpf ? employee.data.custom_irpf + '%' : '-' }}
                </div>
              </div>
            </div>
            
            <!-- Botones de solicitudes -->
            <div class="border-t pt-4 mt-4 space-y-3">
              <Button
                @click="showIbanDialog = true"
                class="w-full !bg-blue-600 hover:!bg-blue-700 !text-white"
              >
                <template #prefix>
                  <FeatherIcon name="credit-card" class="h-4 w-4" />
                </template>
                Solicitar Cambio de IBAN
              </Button>
              <Button
                @click="showIrpfDialog = true"
                class="w-full !bg-emerald-600 hover:!bg-emerald-700 !text-white"
              >
                <template #prefix>
                  <FeatherIcon name="percent" class="h-4 w-4" />
                </template>
                Solicitar Modificación de Retención IRPF
              </Button>
            </div>
            
            <div v-if="employee.data.companies && employee.data.companies.length > 0" class="border-t pt-4 mt-4">
               <label class="block text-xs font-medium uppercase text-gray-500 mb-2">
                  {{ employee.data.status_text }}
               </label>
               <div class="flex flex-wrap gap-2">
                 <Badge v-for="comp in employee.data.companies" :key="comp" theme="blue">
                   {{ comp }}
                 </Badge>
               </div>
            </div>
          </div>
        </div>
      </Card>

      <!-- Solicitudes de Cambio de IBAN -->
      <Card class="h-full" v-if="employee.data">
        <template #header>
          <div class="flex items-center gap-2">
            <FeatherIcon name="credit-card" class="h-5 w-5 text-gray-500" />
            <span class="text-lg font-medium">Solicitudes de Cambio de IBAN</span>
          </div>
        </template>
        <div class="p-4">
          <div v-if="ibanRequests.loading" class="flex justify-center py-8">
            <LoadingIndicator />
          </div>
          <div
            v-else-if="ibanRequests.error"
            class="rounded-md bg-red-50 p-4 text-red-700"
          >
            <p>No se pudieron cargar las solicitudes.</p>
          </div>
          <div v-else-if="!ibanRequests.data || ibanRequests.data.length === 0" class="py-8 text-center text-gray-500">
            <FeatherIcon
              name="inbox"
              class="mx-auto mb-2 h-8 w-8 text-gray-400"
            />
            <p>No tienes solicitudes de cambio de IBAN.</p>
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="request in ibanRequests.data"
              :key="request.name"
              class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
            >
              <div class="flex items-start justify-between mb-2">
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-sm font-semibold text-gray-900">
                      {{ request.name }}
                    </span>
                    <Badge
                      :theme="getStatusTheme(request.status)"
                      size="sm"
                    >
                      {{ getStatusLabel(request.status) }}
                    </Badge>
                  </div>
                  <p class="text-xs text-gray-500">
                    Fecha de solicitud: {{ formatDate(request.posting_date || request.creation) }}
                  </p>
                </div>
              </div>
              
              <div class="grid grid-cols-1 gap-2 mt-3 text-sm">
                <div v-if="request.current_iban" class="flex items-center gap-2">
                  <span class="text-gray-500 min-w-[100px]">IBAN Actual:</span>
                  <span class="font-mono text-gray-900">{{ formatIban(request.current_iban) }}</span>
                </div>
                <div v-if="request.new_iban" class="flex items-center gap-2">
                  <span class="text-gray-500 min-w-[100px]">Nuevo IBAN:</span>
                  <span class="font-mono text-gray-900">{{ formatIban(request.new_iban) }}</span>
                </div>
                <div v-if="request.bank_entity" class="flex items-center gap-2">
                  <span class="text-gray-500 min-w-[100px]">Entidad:</span>
                  <span class="text-gray-900">{{ request.bank_entity }}</span>
                </div>
                <div v-if="request.approval_notes" class="flex items-start gap-2 mt-2 pt-2 border-t">
                  <span class="text-gray-500 min-w-[100px]">Notas:</span>
                  <span class="text-gray-900">{{ request.approval_notes }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Card>

      <!-- Solicitudes de Retención IRPF -->
      <Card class="h-full" v-if="employee.data">
        <template #header>
          <div class="flex items-center gap-2">
            <FeatherIcon name="percent" class="h-5 w-5 text-gray-500" />
            <span class="text-lg font-medium">Solicitudes de Retención IRPF</span>
          </div>
        </template>
        <div class="p-4">
          <div v-if="irpfRequests.loading" class="flex justify-center py-8">
            <LoadingIndicator />
          </div>
          <div
            v-else-if="irpfRequests.error"
            class="rounded-md bg-red-50 p-4 text-red-700"
          >
            <p>No se pudieron cargar las solicitudes.</p>
          </div>
          <div v-else-if="!irpfRequests.data || irpfRequests.data.length === 0" class="py-8 text-center text-gray-500">
            <FeatherIcon
              name="inbox"
              class="mx-auto mb-2 h-8 w-8 text-gray-400"
            />
            <p>No tienes solicitudes de retención IRPF.</p>
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="request in irpfRequests.data"
              :key="request.name"
              class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
            >
              <div class="flex items-start justify-between mb-2">
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <span class="text-sm font-semibold text-gray-900">
                      {{ request.name }}
                    </span>
                    <Badge
                      :theme="getStatusTheme(request.status)"
                      size="sm"
                    >
                      {{ getStatusLabel(request.status) }}
                    </Badge>
                  </div>
                  <p class="text-xs text-gray-500">
                    Fecha de solicitud: {{ formatDate(request.posting_date || request.creation) }}
                  </p>
                </div>
              </div>
              
              <div class="grid grid-cols-1 gap-2 mt-3 text-sm">
                <div class="flex items-center gap-2">
                  <span class="text-gray-500 min-w-[120px]">IRPF Actual:</span>
                  <span class="text-gray-900">{{ request.current_irpf || 0 }}%</span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-gray-500 min-w-[120px]">IRPF Solicitado:</span>
                  <span class="font-semibold text-gray-900">{{ request.requested_irpf }}%</span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-gray-500 min-w-[120px]">Tipo:</span>
                  <span class="text-gray-900">{{ request.irpf_type }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-gray-500 min-w-[120px]">Fecha de Efecto:</span>
                  <span class="text-gray-900">{{ formatDate(request.effective_date) }}</span>
                </div>
                <div v-if="request.approval_notes" class="flex items-start gap-2 mt-2 pt-2 border-t">
                  <span class="text-gray-500 min-w-[120px]">Notas:</span>
                  <span class="text-gray-900">{{ request.approval_notes }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>

    <!-- Diálogo de cambio de IBAN -->
    <IbanChangeDialog
      v-model="showIbanDialog"
      :current-iban="employee.data?.iban || ''"
      :employee-id="employee.data?.name || ''"
      @success="handleIbanRequestSuccess"
    />

    <!-- Diálogo de retención IRPF -->
    <IrpfRetentionDialog
      v-model="showIrpfDialog"
      :current-irpf="parseFloat(employee.data?.custom_irpf || '0')"
      :employee-id="employee.data?.name || ''"
      @success="handleIrpfRequestSuccess"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { Card, Badge, createResource, FeatherIcon, LoadingIndicator, Button } from 'frappe-ui'
import { sessionStore } from '@/stores/session'
import { usersStore } from '@/stores/users'
import IbanChangeDialog from '@/components/IbanChangeDialog.vue'
import IrpfRetentionDialog from '@/components/IrpfRetentionDialog.vue'

const userInitials = computed(() => {
  const fullName = usersStore().getUser('sessionUser').full_name
  if (!fullName) return '?'
  return fullName
    .split(' ')
    .map((n) => n[0])
    .join('')
    .substring(0, 2)
    .toUpperCase()
})

const employee = createResource({
  url: 'portal_rrhh.api.employee.get_current_employee',
  auto: true,
})

const ibanRequests = createResource({
  url: 'portal_rrhh.api.iban.get_my_iban_requests',
  auto: false, // Se cargará cuando haya un empleado
})

const irpfRequests = createResource({
  url: 'portal_rrhh.api.irpf.get_my_irpf_requests',
  auto: false, // Se cargará cuando haya un empleado
})

const showIbanDialog = ref(false)
const showIrpfDialog = ref(false)

// Cargar solicitudes cuando haya un empleado
watch(() => employee.data, (newData) => {
  if (newData && newData.name) {
    ibanRequests.reload()
    irpfRequests.reload()
  }
}, { immediate: true })

// Formatear IBAN para mostrar
function formatIban(iban) {
  if (!iban) return ''
  const clean = iban.replace(/\s/g, '')
  return clean.match(/.{1,4}/g)?.join(' ') || clean
}

// Formatear fecha
function formatDate(date) {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// Obtener tema del badge según el estado
function getStatusTheme(status) {
  const themes = {
    'Open': 'orange',
    'Approved': 'green',
    'Rejected': 'red'
  }
  return themes[status] || 'gray'
}

// Obtener etiqueta del estado en español
function getStatusLabel(status) {
  const labels = {
    'Open': 'Pendiente',
    'Approved': 'Aprobada',
    'Rejected': 'Rechazada'
  }
  return labels[status] || status
}

// Manejar éxito al crear solicitud de IBAN
function handleIbanRequestSuccess() {
  employee.reload()
  ibanRequests.reload()
}

// Manejar éxito al crear solicitud de IRPF
function handleIrpfRequestSuccess() {
  employee.reload()
  irpfRequests.reload()
}
</script>
