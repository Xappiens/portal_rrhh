<template>
  <div class="px-5 py-6 sm:px-8">
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
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { Card, Badge, createResource, FeatherIcon, LoadingIndicator } from 'frappe-ui'
import { sessionStore } from '@/stores/session'
import { usersStore } from '@/stores/users'

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
</script>
