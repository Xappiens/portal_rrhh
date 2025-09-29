<template>
  <div class="flex-1 p-6 bg-gray-50">
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
          <Input
            v-model="selectedDepartment"
            type="select"
            variant="outline"
            size="sm"
          >
            <option value="">Todos los departamentos</option>
            <option v-for="dept in departamentos" :key="dept.name" :value="dept.department_name">
              {{ dept.department_name }}
            </option>
          </Input>
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
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-if="loading" class="text-center">
                <td colspan="6" class="px-6 py-4">
                  <div class="flex items-center justify-center">
                    <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    <span class="ml-2">Cargando empleados...</span>
                  </div>
                </td>
              </tr>
              <tr v-else-if="filteredEmpleados.length === 0" class="text-center">
                <td colspan="6" class="px-6 py-4 text-gray-500">
                  No se encontraron empleados
                </td>
              </tr>
              <tr v-else v-for="empleado in filteredEmpleados" :key="empleado.id" class="hover:bg-gray-50">
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
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div class="flex items-center justify-end space-x-2">
                    <Button variant="ghost" size="sm" theme="blue">
                      <FeatherIcon name="edit" class="h-4" />
                    </Button>
                    <Button variant="ghost" size="sm" theme="gray">
                      <FeatherIcon name="eye" class="h-4" />
                    </Button>
                    <Button variant="ghost" size="sm" theme="red">
                      <FeatherIcon name="trash-2" class="h-4" />
                    </Button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'
import { ref, onMounted, computed } from 'vue'

const empleados = ref([])
const departamentos = ref([])
const loading = ref(false)
const searchQuery = ref('')
const selectedDepartment = ref('')

// Load employees data
const loadEmployees = async () => {
  loading.value = true
  try {
    const result = await frappe.call('portal_rrhh.portal_rrhh.employee_data.get_employees_list', {
      filters: {
        status: 'Active'
      },
      limit: 50,
      offset: 0
    })

    if (result.message) {
      empleados.value = result.message.employees.map(emp => ({
        id: emp.name,
        nombre: emp.employee_name,
        email: emp.email,
        departamento: emp.department || 'Sin departamento',
        cargo: emp.designation || 'Sin cargo',
        estado: emp.status === 'Active' ? 'Activo' : 'Inactivo',
        fechaIngreso: emp.date_of_joining_formatted || 'N/A',
        avatar: emp.avatar
      }))
    }
  } catch (error) {
    console.error('Error loading employees:', error)
  } finally {
    loading.value = false
  }
}

// Load departments
const loadDepartments = async () => {
  try {
    const result = await frappe.call('portal_rrhh.portal_rrhh.employee_data.get_departments_list')

    if (result.message) {
      departamentos.value = result.message
    }
  } catch (error) {
    console.error('Error loading departments:', error)
  }
}

// Filter employees
const filteredEmpleados = computed(() => {
  let filtered = empleados.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(emp =>
      emp.nombre.toLowerCase().includes(query) ||
      emp.email.toLowerCase().includes(query) ||
      emp.departamento.toLowerCase().includes(query)
    )
  }

  if (selectedDepartment.value) {
    filtered = filtered.filter(emp => emp.departamento === selectedDepartment.value)
  }

  return filtered
})

onMounted(() => {
  loadEmployees()
  loadDepartments()
})
</script>
