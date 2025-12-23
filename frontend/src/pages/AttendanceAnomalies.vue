<template>
  <div class="flex flex-col h-full overflow-hidden bg-white">
    <div class="flex-1 overflow-y-auto p-5">
      <div class="mb-6 flex items-center justify-between">
        <h1 class="text-2xl font-bold text-gray-900">{{ __('Anomalías de Asistencia') }}</h1>
      </div>

      <!-- Filters -->
      <div class="bg-gray-50 rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div class="grid grid-cols-12 gap-4 items-end">
            <!-- From Date -->
             <div class="col-span-6 md:col-span-5">
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __('Desde') }}</label>
                <DatePicker 
                    v-model="filters.from_date"
                    class="w-full"
                />
            </div>
            <!-- To Date -->
             <div class="col-span-6 md:col-span-5">
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __('Hasta') }}</label>
                <DatePicker 
                    v-model="filters.to_date"
                    class="w-full"
                />
            </div>
             <!-- Button -->
            <div class="col-span-12 md:col-span-2">
                 <Button
                    variant="solid"
                    theme="gray"
                    class="w-full justify-center !bg-black !text-white hover:!bg-gray-800"
                    :loading="loading"
                    @click="fetchAnomalies"
                >
                    {{ __('Actualizar') }}
                </Button>
            </div>
        </div>
      </div>

      <!-- Dashboard Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div 
            class="cursor-pointer p-4 rounded-lg border shadow-sm transition-all duration-200 flex flex-col"
            :class="selectedCategory === 'Ghost Employee' ? 'bg-purple-50 border-purple-200 ring-2 ring-purple-100' : 'bg-white border-gray-200 hover:border-purple-200'"
            @click="selectCategory('Ghost Employee')"
          >
              <span class="text-xs text-gray-500 font-medium uppercase">{{ __('Sin Fichajes (Job Offer)') }}</span>
              <span class="text-3xl font-bold text-gray-900 mt-2">{{ stats.ghost }}</span>
              <span class="text-xs text-gray-400 mt-1" v-if="stats.ghost > 0">{{ __('Empleados sin actividad') }}</span>
          </div>

          <div 
            class="cursor-pointer p-4 rounded-lg border shadow-sm transition-all duration-200 flex flex-col"
            :class="selectedCategory === 'Missing Punch' ? 'bg-orange-50 border-orange-200 ring-2 ring-orange-100' : 'bg-white border-gray-200 hover:border-orange-200'"
             @click="selectCategory('Missing Punch')"
          >
              <span class="text-xs text-gray-500 font-medium uppercase">{{ __('Fichajes Faltantes') }}</span>
              <span class="text-3xl font-bold text-gray-900 mt-2">{{ stats.missing }}</span>
              <span class="text-xs text-gray-400 mt-1" v-if="stats.missing > 0">{{ __('Entradas sin Salida (o viceversa)') }}</span>
          </div>

          <div 
            class="cursor-pointer p-4 rounded-lg border shadow-sm transition-all duration-200 flex flex-col"
            :class="selectedCategory === 'Time Issue' ? 'bg-blue-50 border-blue-200 ring-2 ring-blue-100' : 'bg-white border-gray-200 hover:border-blue-200'"
             @click="selectCategory('Time Issue')"
          >
              <span class="text-xs text-gray-500 font-medium uppercase">{{ __('Jornada > 6h sin descanso') }}</span>
              <span class="text-3xl font-bold text-gray-900 mt-2">{{ stats.time }}</span>
              <span class="text-xs text-gray-400 mt-1" v-if="stats.time > 0">{{ __('Sesiones largas o sin pausa') }}</span>
          </div>
          
           <div 
            class="cursor-pointer p-4 rounded-lg border shadow-sm transition-all duration-200 flex flex-col"
            :class="selectedCategory === 'Absent' ? 'bg-red-50 border-red-200 ring-2 ring-red-100' : 'bg-white border-gray-200 hover:border-red-200'"
             @click="selectCategory('Absent')"
          >
              <span class="text-xs text-gray-500 font-medium uppercase">{{ __('Ausencias') }}</span>
              <span class="text-3xl font-bold text-gray-900 mt-2">{{ stats.absent }}</span>
              <span class="text-xs text-gray-400 mt-1" v-if="stats.absent > 0">{{ __('Sin justificar') }}</span>
          </div>
      </div>

      <!-- Filtered List Title -->
      <div v-if="selectedCategory" class="mb-4 flex items-center gap-2">
           <h2 class="text-lg font-semibold text-gray-800">{{ getCategoryLabel(selectedCategory) }}</h2>
           <Badge :theme="getCategoryTheme(selectedCategory)" size="lg">{{ groupedAnomalies.length }} {{ __('Empleados') }}</Badge>
           <Button v-if="selectedCategory" variant="ghost" class="ml-auto" @click="selectedCategory = null">
               {{ __('Cerrar') }}
           </Button>
      </div>

      <!-- Grouped by Employee Table -->
      <div v-if="selectedCategory && groupedAnomalies.length > 0" class="bg-white rounded-lg border border-gray-200 shadow-sm">
          <div class="overflow-hidden">
               <!-- Iterating Employees -->
               <div v-for="(group, idx) in groupedAnomalies" :key="idx" class="border-b last:border-b-0 border-gray-100">
                    <div 
                        class="p-4 flex items-center justify-between cursor-pointer hover:bg-gray-50 transition-colors"
                        @click="toggleEmployee(group.employee)"
                    >
                        <div class="flex items-center gap-3">
                            <div class="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center text-xs font-bold text-gray-600">
                                {{ getInitials(group.employee) }}
                            </div>
                            <div>
                                <div class="text-sm font-semibold text-gray-900">{{ group.employee }}</div>
                                <div class="text-xs text-gray-500">{{ group.items.length }} {{ group.items.length === 1 ? __('anomalía') : __('anomalías') }}</div>
                            </div>
                        </div>
                        <div class="transform transition-transform duration-200" :class="{ 'rotate-180': expandedEmployees.includes(group.employee) }">
                             <FeatherIcon name="chevron-down" class="w-4 h-4 text-gray-400" />
                        </div>
                    </div>

                    <!-- Details Row -->
                    <div v-if="expandedEmployees.includes(group.employee)" class="bg-gray-50/50 p-4 border-t border-gray-100 pl-14">
                        <table class="w-full">
                            <thead>
                                <tr class="text-left text-xs text-gray-500 uppercase">
                                    <th class="pb-2 font-medium">{{ __('Fecha') }}</th>
                                    <th class="pb-2 font-medium">{{ __('Tipo') }}</th>
                                    <th class="pb-2 font-medium">{{ __('Detalle') }}</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-100">
                                <tr v-for="(item, i) in group.items" :key="i">
                                    <td class="py-2 text-sm text-gray-900 font-medium w-32 whitespace-nowrap">{{ formatDateLong(item.date) }}</td>
                                    <td class="py-2 w-48">
                                        <Badge :theme="getBadgeTheme(item.type)" size="sm">
                                            {{ __(item.type) }}
                                        </Badge>
                                    </td>
                                    <td class="py-2 text-sm text-gray-600">{{ item.description }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
               </div>
          </div>
      </div>
      
       <!-- Empty State for Details -->
       <div v-else-if="selectedCategory" class="text-center py-12 bg-white rounded-lg border border-dashed border-gray-300">
            <div class="text-gray-400 mb-2">
                <FeatherIcon name="check-circle" class="w-8 h-8 mx-auto" />
            </div>
            <p class="text-gray-500 font-medium">{{ __('No hay anomalías de este tipo en el período seleccionado.') }}</p>
       </div>

       <!-- Initial State -->
       <div v-else class="text-center py-20">
            <h3 class="text-lg font-medium text-gray-900 mb-2">{{ __('Selecciona una categoría') }}</h3>
            <p class="text-gray-500 max-w-sm mx-auto">{{ __('Haz clic en una de las tarjetas de arriba para ver los empleados afectados y los detalles.') }}</p>
       </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Button, DatePicker, call, Badge, FeatherIcon } from 'frappe-ui'
import dayjs from 'dayjs'
import 'dayjs/locale/es'

dayjs.locale('es')

const loading = ref(false)
const anomalies = ref([])
const selectedCategory = ref(null)
const expandedEmployees = ref([])

const filters = ref({
    // Default last 30 days
    from_date: dayjs().subtract(30, 'days').format('YYYY-MM-DD'),
    to_date: dayjs().format('YYYY-MM-DD')
})

const stats = computed(() => {
    return {
        total: anomalies.value.length,
        ghost: anomalies.value.filter(a => a.type === 'Ghost Employee').length,
        missing: anomalies.value.filter(a => a.type === 'Missing Punch').length,
        time: anomalies.value.filter(a => ['Excessive Continuous Work', 'No Break'].includes(a.type)).length,
        absent: anomalies.value.filter(a => a.type === 'Absent').length
    }
})

// Returns array of { employee: "Name", items: [...] }
const groupedAnomalies = computed(() => {
    if (!selectedCategory.value) return []
    
    let filtered = []
    
    if (selectedCategory.value === 'Ghost Employee') {
        filtered = anomalies.value.filter(a => a.type === 'Ghost Employee')
    } else if (selectedCategory.value === 'Missing Punch') {
        filtered = anomalies.value.filter(a => a.type === 'Missing Punch')
    } else if (selectedCategory.value === 'Time Issue') {
        filtered = anomalies.value.filter(a => ['Excessive Continuous Work', 'No Break'].includes(a.type))
    } else if (selectedCategory.value === 'Absent') {
        filtered = anomalies.value.filter(a => a.type === 'Absent')
    }
    
    // Group by Employee
    const groups = {}
    filtered.forEach(item => {
        if (!groups[item.employee]) {
            groups[item.employee] = []
        }
        groups[item.employee].push(item)
    })
    
    // Sort employees by count (desc) then name (asc)
    return Object.keys(groups).map(name => {
        return {
            employee: name,
            items: groups[name].sort((a, b) => new Date(b.date) - new Date(a.date)) // newest first
        }
    }).sort((a, b) => {
        // High severity first? Or just count.
        if (b.items.length !== a.items.length) return b.items.length - a.items.length
        return a.employee.localeCompare(b.employee)
    })
})

const fetchAnomalies = async () => {
    loading.value = true
    try {
        const result = await call('portal_rrhh.api.attendance.get_attendance_anomalies', {
            employee: null, // explicit null
            from_date: filters.value.from_date,
            to_date: filters.value.to_date
        })
        
        if (result && result.success) {
            anomalies.value = result.data
        } else {
            anomalies.value = []
        }
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
        // Reset expanded, but keep category selected if it makes sense contextually
        expandedEmployees.value = []
    }
}

const selectCategory = (cat) => {
    if (selectedCategory.value === cat) {
        selectedCategory.value = null
    } else {
        selectedCategory.value = cat
    }
    expandedEmployees.value = []
}

const toggleEmployee = (emp) => {
    if (expandedEmployees.value.includes(emp)) {
        expandedEmployees.value = expandedEmployees.value.filter(e => e !== emp)
    } else {
        expandedEmployees.value.push(emp)
    }
}

const getInitials = (name) => {
    if (!name) return '?'
    return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
}

const getCategoryLabel = (cat) => {
     if (cat === 'Ghost Employee') return __('Sin Fichajes (Job Offer)')
     if (cat === 'Missing Punch') return __('Fichajes Faltantes')
     if (cat === 'Time Issue') return __('Jornada > 6h sin descanso')
     if (cat === 'Absent') return __('Ausencias')
     return cat
}
const getCategoryTheme = (cat) => {
     if (cat === 'Ghost Employee') return 'purple'
     if (cat === 'Missing Punch') return 'orange'
     if (cat === 'Time Issue') return 'blue'
     if (cat === 'Absent') return 'red'
     return 'gray'
}

const formatDateLong = (d) => dayjs(d).format('DD MMM (ddd)')
const __ = (text) => text

const getBadgeTheme = (type) => {
    if (type === 'Missing Punch') return 'orange'
    if (type === 'Absent' || type === 'Ghost Employee') return 'red'
    if (['Late Entry', 'Early Exit', 'No Break'].includes(type) || type.includes('Excessive')) return 'yellow'
    return 'gray'
}

onMounted(() => {
    // Initial fetch
    fetchAnomalies()
})
</script>
