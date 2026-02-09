<template>
  <div class="px-5 py-6 sm:px-8 h-full overflow-y-auto">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Gestión de Nóminas</h1>
      <p class="text-base text-gray-500">Sistema de liquidación de nóminas para docentes</p>
    </div>

    <!-- Filtros -->
    <Card class="mb-6">
      <template #header>
        <div class="flex items-center gap-2">
          <FeatherIcon name="filter" class="h-5 w-5 text-gray-500" />
          <span class="text-lg font-medium">Filtros</span>
        </div>
      </template>
      <div class="p-4 space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Mes</label>
            <select 
              v-model="filters.mes" 
              @change="cargarDatos" 
              class="form-select w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="Enero">Enero</option>
              <option value="Febrero">Febrero</option>
              <option value="Marzo">Marzo</option>
              <option value="Abril">Abril</option>
              <option value="Mayo">Mayo</option>
              <option value="Junio">Junio</option>
              <option value="Julio">Julio</option>
              <option value="Agosto">Agosto</option>
              <option value="Septiembre">Septiembre</option>
              <option value="Octubre">Octubre</option>
              <option value="Noviembre">Noviembre</option>
              <option value="Diciembre">Diciembre</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Año</label>
            <Input 
              type="number" 
              v-model="filters.año" 
              @change="cargarDatos"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Docente (Opcional)</label>
            <Input 
              type="text" 
              v-model="filters.employee" 
              placeholder="Buscar docente..."
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Course (Opcional)</label>
            <Input 
              type="text" 
              v-model="filters.course" 
              placeholder="Buscar course..."
            />
          </div>
        </div>

        <div class="flex gap-2">
          <Button @click="cargarDatos" icon-left="search">
            Buscar
          </Button>
          <Button @click="limpiarFiltros" appearance="white">
            Limpiar
          </Button>
        </div>
      </div>
    </Card>

    <!-- Resumen -->
    <div v-if="resumen" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <Card>
        <div class="p-4 flex items-center gap-4">
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
            <FeatherIcon name="users" class="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <div class="text-xs font-medium text-gray-500 uppercase">Total Docentes</div>
            <div class="text-2xl font-bold text-gray-900">{{ resumen.total_docentes }}</div>
          </div>
        </div>
      </Card>

      <Card>
        <div class="p-4 flex items-center gap-4">
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-green-100">
            <FeatherIcon name="clock" class="h-6 w-6 text-green-600" />
          </div>
          <div>
            <div class="text-xs font-medium text-gray-500 uppercase">Total Horas</div>
            <div class="text-2xl font-bold text-gray-900">{{ formatNumber(resumen.total_horas) }}h</div>
          </div>
        </div>
      </Card>

      <Card>
        <div class="p-4 flex items-center gap-4">
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-yellow-100">
            <FeatherIcon name="dollar-sign" class="h-6 w-6 text-yellow-600" />
          </div>
          <div>
            <div class="text-xs font-medium text-gray-500 uppercase">Total Bruto</div>
            <div class="text-2xl font-bold text-gray-900">{{ formatCurrency(resumen.total_bruto) }}</div>
          </div>
        </div>
      </Card>

      <Card class="bg-gradient-to-br from-blue-500 to-blue-600">
        <div class="p-4 flex items-center gap-4">
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-white bg-opacity-20">
            <FeatherIcon name="trending-up" class="h-6 w-6 text-white" />
          </div>
          <div>
            <div class="text-xs font-medium text-blue-100 uppercase">Total a Pagar</div>
            <div class="text-2xl font-bold text-white">{{ formatCurrency(resumen.total_pagar) }}</div>
          </div>
        </div>
      </Card>
    </div>

    <!-- Acciones -->
    <Card class="mb-6">
      <div class="p-4 flex flex-wrap gap-2">
        <Button 
          @click="generarPrevisiones" 
          icon-left="calculator"
          :loading="loading"
        >
          Generar Previsiones
        </Button>

        <Button 
          @click="liquidarSeleccionadas" 
          icon-left="check"
          :disabled="seleccionadas.length === 0 || loading"
        >
          Liquidar Seleccionadas ({{ seleccionadas.length }})
        </Button>

        <Button 
          @click="marcarComoEnviado" 
          icon-left="send"
          appearance="white"
          :disabled="seleccionadasLiquidaciones.length === 0 || loading"
        >
          Marcar como Enviado
        </Button>

        <Button 
          @click="generarReporteExcel" 
          icon-left="file-text"
          appearance="white"
          :disabled="liquidaciones.length === 0 || loading"
        >
          Generar Reporte Excel
        </Button>
      </div>
    </Card>

    <!-- Tabs -->
    <Card>
      <div class="border-b border-gray-200">
        <nav class="flex -mb-px">
          <button 
            @click="activeTab = 'previsiones'" 
            :class="[
              'flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === 'previsiones' 
                ? 'border-blue-500 text-blue-600' 
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            <FeatherIcon name="eye" class="h-4 w-4" />
            Previsiones
          </button>
          <button 
            @click="activeTab = 'liquidaciones'" 
            :class="[
              'flex items-center gap-2 px-6 py-3 text-sm font-medium border-b-2 transition-colors',
              activeTab === 'liquidaciones' 
                ? 'border-blue-500 text-blue-600' 
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            <FeatherIcon name="file-text" class="h-4 w-4" />
            Liquidaciones
          </button>
        </nav>
      </div>

      <!-- Tabla de Previsiones -->
      <div v-if="activeTab === 'previsiones'" class="p-4">
        <LoadingIndicator v-if="loading" class="py-12" />

        <div v-else-if="previsiones.length === 0" class="text-center py-12">
          <FeatherIcon name="inbox" class="h-12 w-12 text-gray-400 mx-auto mb-3" />
          <p class="text-gray-500 mb-4">No hay previsiones para este mes</p>
          <Button @click="generarPrevisiones" icon-left="plus">
            Generar Previsiones
          </Button>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left">
                  <input 
                    type="checkbox" 
                    @change="toggleSelectAll" 
                    class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Docente</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">DNI/NIE</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Course</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Horas</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Bruto</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Vacaciones</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">SS</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="prev in previsiones" :key="`prev-${prev.employee}-${prev.course}`" class="hover:bg-gray-50">
                <td class="px-4 py-3">
                  <input 
                    type="checkbox" 
                    :value="`${prev.employee}-${prev.course}`"
                    v-model="seleccionadas"
                    class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                </td>
                <td class="px-4 py-3 text-sm text-gray-900">{{ prev.employee_name }}</td>
                <td class="px-4 py-3 text-sm text-gray-500">{{ prev.dni_nie }}</td>
                <td class="px-4 py-3 text-sm text-gray-500">{{ prev.course }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 text-right">{{ formatNumber(prev.total_horas) }}h</td>
                <td class="px-4 py-3 text-sm text-gray-900 text-right">{{ formatCurrency(prev.bruto) }}</td>
                <td class="px-4 py-3 text-sm text-gray-500 text-right">{{ formatCurrency(prev.vacaciones_mes) }}</td>
                <td class="px-4 py-3 text-sm text-gray-500 text-right">{{ formatCurrency(prev.importe_ss) }}</td>
                <td class="px-4 py-3 text-sm font-semibold text-gray-900 text-right">{{ formatCurrency(prev.total) }}</td>
                <td class="px-4 py-3 text-center">
                  <div class="flex items-center justify-center gap-1">
                    <Button 
                      @click="verDetalle(prev)" 
                      appearance="minimal"
                      icon="eye"
                      class="!p-1"
                    />
                    <Button 
                      @click="agregarHorasExtras(prev)" 
                      appearance="minimal"
                      icon="clock"
                      class="!p-1"
                    />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Tabla de Liquidaciones -->
      <div v-if="activeTab === 'liquidaciones'" class="p-4">
        <LoadingIndicator v-if="loading" class="py-12" />

        <div v-else-if="liquidaciones.length === 0" class="text-center py-12">
          <FeatherIcon name="inbox" class="h-12 w-12 text-gray-400 mx-auto mb-3" />
          <p class="text-gray-500">No hay liquidaciones creadas para este mes</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left">
                  <input 
                    type="checkbox" 
                    @change="toggleSelectAllLiquidaciones" 
                    class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Docente</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">DNI/NIE</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Course</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Horas N</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Horas E</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total H</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Bruto</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">SS</th>
                <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="liq in liquidaciones" :key="liq.name" class="hover:bg-gray-50">
                <td class="px-4 py-3">
                  <input 
                    type="checkbox" 
                    :value="liq.name"
                    v-model="seleccionadasLiquidaciones"
                    class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                </td>
                <td class="px-4 py-3 text-sm text-gray-900">{{ liq.employee_name }}</td>
                <td class="px-4 py-3 text-sm text-gray-500">{{ liq.dni_nie }}</td>
                <td class="px-4 py-3 text-sm text-gray-500">{{ liq.course }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 text-right">{{ formatNumber(liq.horas_normales) }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 text-right">{{ formatNumber(liq.horas_extras) }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 text-right">{{ formatNumber(liq.total_horas) }}</td>
                <td class="px-4 py-3 text-sm text-gray-900 text-right">{{ formatCurrency(liq.bruto) }}</td>
                <td class="px-4 py-3 text-sm text-gray-500 text-right">{{ formatCurrency(liq.importe_ss) }}</td>
                <td class="px-4 py-3 text-sm font-semibold text-gray-900 text-right">{{ formatCurrency(liq.total) }}</td>
                <td class="px-4 py-3 text-center">
                  <Badge :theme="getEstadoBadgeTheme(liq.estado)">
                    {{ liq.estado }}
                  </Badge>
                </td>
                <td class="px-4 py-3 text-center">
                  <Button 
                    @click="abrirLiquidacion(liq.name)" 
                    appearance="minimal"
                    icon="external-link"
                    class="!p-1"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </Card>

    <!-- Dialog: Detalle de Previsión -->
    <Dialog 
      v-model="showDetalleModal"
      :options="{
        title: 'Detalle de Liquidación',
        size: '3xl'
      }"
    >
      <template #body-content>
        <div v-if="detalleActual" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Información Básica -->
            <div class="bg-gray-50 rounded-lg p-4">
              <h4 class="text-sm font-semibold text-gray-900 mb-3">Información Básica</h4>
              <div class="space-y-2">
                <div class="flex justify-between text-sm">
                  <span class="text-gray-500">Empleado:</span>
                  <span class="font-medium text-gray-900">{{ detalleActual.employee_name }}</span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-gray-500">DNI/NIE:</span>
                  <span class="font-medium text-gray-900">{{ detalleActual.dni_nie }}</span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-gray-500">Designation:</span>
                  <span class="font-medium text-gray-900">{{ detalleActual.designation }}</span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-gray-500">Course:</span>
                  <span class="font-medium text-gray-900">{{ detalleActual.course }}</span>
                </div>
              </div>
            </div>

            <!-- Horas Trabajadas -->
            <div class="bg-gray-50 rounded-lg p-4">
              <h4 class="text-sm font-semibold text-gray-900 mb-3">Horas Trabajadas</h4>
              <div class="space-y-2">
                <div class="flex justify-between text-sm">
                  <span class="text-gray-500">Horas Normales:</span>
                  <span class="font-medium text-gray-900">{{ formatNumber(detalleActual.horas_normales) }}h</span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-gray-500">Horas Extras:</span>
                  <span class="font-medium text-gray-900">{{ formatNumber(detalleActual.horas_extras) }}h</span>
                </div>
                <div class="flex justify-between text-sm border-t pt-2">
                  <span class="text-gray-500 font-medium">Total Horas:</span>
                  <span class="font-semibold text-gray-900">{{ formatNumber(detalleActual.total_horas) }}h</span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-gray-500">Días Trabajados:</span>
                  <span class="font-medium text-gray-900">{{ detalleActual.dias_trabajados }} días</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Cálculo de Importes -->
          <div class="bg-white border border-gray-200 rounded-lg p-4">
            <h4 class="text-sm font-semibold text-gray-900 mb-4">Cálculo de Importes</h4>
            <div class="space-y-2">
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">Precio por Hora:</span>
                <span class="text-gray-900">{{ formatCurrency(detalleActual.precio_hora) }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">Importe Horas Normales:</span>
                <span class="text-gray-900">{{ formatCurrency(detalleActual.importe_horas_normales) }}</span>
              </div>
              <div v-if="detalleActual.horas_extras > 0" class="flex justify-between text-sm">
                <span class="text-gray-600">Importe Horas Extras:</span>
                <span class="text-gray-900">{{ formatCurrency(detalleActual.importe_horas_extras) }}</span>
              </div>
              <div class="flex justify-between text-sm font-semibold border-t border-b py-2">
                <span class="text-gray-900">BRUTO TOTAL:</span>
                <span class="text-gray-900">{{ formatCurrency(detalleActual.bruto) }}</span>
              </div>
              <div class="flex justify-between text-sm text-red-600">
                <span>Vacaciones (8.33%):</span>
                <span>-{{ formatCurrency(detalleActual.vacaciones_mes) }}</span>
              </div>
              <div class="flex justify-between text-sm border-t pt-2">
                <span class="text-gray-600">Bruto - Vacaciones:</span>
                <span class="text-gray-900">{{ formatCurrency(detalleActual.bruto_menos_vacaciones) }}</span>
              </div>
              <div v-if="detalleActual.vacaciones_acumuladas > 0" class="flex justify-between text-sm">
                <span class="text-gray-600">Vacaciones Acumuladas:</span>
                <span class="text-gray-900">{{ formatCurrency(detalleActual.vacaciones_acumuladas) }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">Base para SS:</span>
                <span class="text-gray-900">{{ formatCurrency(detalleActual.base_ss) }}</span>
              </div>
              <div class="flex justify-between text-sm">
                <span class="text-gray-600">Seguridad Social (32.07%):</span>
                <span class="text-gray-900">{{ formatCurrency(detalleActual.importe_ss) }}</span>
              </div>
              <div class="flex justify-between text-lg font-bold bg-blue-50 p-3 rounded-lg mt-3">
                <span class="text-blue-900">TOTAL A PAGAR:</span>
                <span class="text-blue-900">{{ formatCurrency(detalleActual.total) }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>
      <template #actions>
        <Button appearance="white" @click="showDetalleModal = false">
          Cerrar
        </Button>
      </template>
    </Dialog>

    <!-- Dialog: Agregar Horas Extras -->
    <Dialog 
      v-model="showHorasExtrasModal"
      :options="{
        title: 'Agregar Horas Extras',
        size: 'md'
      }"
    >
      <template #body-content>
        <div v-if="horasExtrasData" class="space-y-4">
          <div class="bg-gray-50 rounded-lg p-3">
            <p class="text-sm"><strong>Docente:</strong> {{ horasExtrasData.employee_name }}</p>
            <p class="text-sm"><strong>Course:</strong> {{ horasExtrasData.course }}</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Horas Extras</label>
            <Input 
              type="number" 
              v-model="horasExtrasData.horas_extras" 
              step="0.5"
              min="0"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Precio Hora Extra (opcional)</label>
            <Input 
              type="number" 
              v-model="horasExtrasData.precio_hora_extra" 
              step="0.01"
              min="0"
              :placeholder="`Por defecto: ${formatCurrency(horasExtrasData.precio_hora * 1.2)}`"
            />
            <p class="text-xs text-gray-500 mt-1">Si no se especifica, se usa 120% del precio normal</p>
          </div>
        </div>
      </template>
      <template #actions>
        <Button appearance="white" @click="showHorasExtrasModal = false">
          Cancelar
        </Button>
        <Button @click="guardarHorasExtras">
          Guardar
        </Button>
      </template>
    </Dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { Card, Badge, Button, FeatherIcon, LoadingIndicator, Input, Dialog, call } from 'frappe-ui'

export default {
  name: 'Nominas',
  components: {
    Card,
    Badge,
    Button,
    FeatherIcon,
    LoadingIndicator,
    Input,
    Dialog
  },
  setup() {
    // Estado
    const loading = ref(false)
    const activeTab = ref('previsiones')
    
    // Filtros
    const filters = ref({
      mes: getMesActual(),
      año: new Date().getFullYear(),
      employee: '',
      course: ''
    })
    
    // Datos
    const previsiones = ref([])
    const liquidaciones = ref([])
    const resumen = ref(null)
    const seleccionadas = ref([])
    const seleccionadasLiquidaciones = ref([])
    
    // Modals
    const showDetalleModal = ref(false)
    const detalleActual = ref(null)
    const showHorasExtrasModal = ref(false)
    const horasExtrasData = ref(null)
    
    // Métodos
    const cargarDatos = async () => {
      loading.value = true
      
      try {
        // Cargar previsiones
        const respPrevisiones = await call('portal_rrhh.api.nominas.get_prevision_mes', {
          mes: filters.value.mes,
          año: filters.value.año,
          employee: filters.value.employee || null,
          course: filters.value.course || null
        })
        
        if (respPrevisiones) {
          previsiones.value = respPrevisiones.previsiones || []
          resumen.value = respPrevisiones.resumen || {}
        }
        
        // Cargar liquidaciones existentes
        const respLiquidaciones = await call('portal_rrhh.api.nominas.get_liquidaciones_mes', {
          mes: filters.value.mes,
          año: filters.value.año,
          employee: filters.value.employee || null,
          course: filters.value.course || null
        })
        
        if (respLiquidaciones) {
          liquidaciones.value = respLiquidaciones.liquidaciones || []
          if (respLiquidaciones.resumen) {
            resumen.value = respLiquidaciones.resumen
          }
        }
        
      } catch (error) {
        console.error('Error cargando datos:', error)
      } finally {
        loading.value = false
      }
    }
    
    const limpiarFiltros = () => {
      filters.value.employee = ''
      filters.value.course = ''
      cargarDatos()
    }
    
    const generarPrevisiones = async () => {
      await cargarDatos()
    }
    
    const liquidarSeleccionadas = async () => {
      if (seleccionadas.value.length === 0) return
      
      if (!confirm(`¿Está seguro de liquidar ${seleccionadas.value.length} nóminas?`)) {
        return
      }
      
      loading.value = true
      
      try {
        const liquidaciones_data = previsiones.value.filter(p => 
          seleccionadas.value.includes(`${p.employee}-${p.course}`)
        )
        
        await call('portal_rrhh.api.nominas.crear_liquidaciones_mes', {
          mes: filters.value.mes,
          año: filters.value.año,
          liquidaciones_data: liquidaciones_data
        })
        
        seleccionadas.value = []
        await cargarDatos()
        activeTab.value = 'liquidaciones'
        
      } catch (error) {
        console.error('Error liquidando nóminas:', error)
      } finally {
        loading.value = false
      }
    }
    
    const marcarComoEnviado = async () => {
      if (seleccionadasLiquidaciones.value.length === 0) return
      
      if (!confirm(`¿Marcar ${seleccionadasLiquidaciones.value.length} liquidaciones como enviadas?`)) {
        return
      }
      
      loading.value = true
      
      try {
        await call('portal_rrhh.api.nominas.marcar_como_enviado', {
          liquidaciones_ids: seleccionadasLiquidaciones.value
        })
        
        seleccionadasLiquidaciones.value = []
        await cargarDatos()
        
      } catch (error) {
        console.error('Error:', error)
      } finally {
        loading.value = false
      }
    }
    
    const generarReporteExcel = async () => {
      loading.value = true
      
      try {
        await call('portal_rrhh.api.nominas.generar_reporte_excel', {
          mes: filters.value.mes,
          año: filters.value.año,
          liquidaciones_ids: seleccionadasLiquidaciones.value.length > 0 
            ? seleccionadasLiquidaciones.value 
            : null
        })
        
      } catch (error) {
        console.error('Error generando reporte:', error)
      } finally {
        loading.value = false
      }
    }
    
    const verDetalle = (prevision) => {
      detalleActual.value = prevision
      showDetalleModal.value = true
    }
    
    const agregarHorasExtras = (prevision) => {
      horasExtrasData.value = {
        ...prevision,
        horas_extras: prevision.horas_extras || 0,
        precio_hora_extra: prevision.precio_hora_extra || (prevision.precio_hora * 1.2)
      }
      showHorasExtrasModal.value = true
    }
    
    const guardarHorasExtras = () => {
      const index = previsiones.value.findIndex(p => 
        p.employee === horasExtrasData.value.employee && 
        p.course === horasExtrasData.value.course
      )
      
      if (index !== -1) {
        const prev = previsiones.value[index]
        prev.horas_extras = horasExtrasData.value.horas_extras
        prev.precio_hora_extra = horasExtrasData.value.precio_hora_extra
        
        // Recalcular importes
        prev.total_horas = prev.horas_normales + prev.horas_extras
        prev.importe_horas_extras = prev.horas_extras * prev.precio_hora_extra
        prev.bruto = prev.importe_horas_normales + prev.importe_horas_extras
        prev.vacaciones_mes = Math.round(prev.bruto * 0.0833 * 100) / 100
        prev.bruto_menos_vacaciones = prev.bruto - prev.vacaciones_mes
        prev.base_ss = prev.bruto_menos_vacaciones
        prev.importe_ss = Math.round(prev.base_ss * 0.3207 * 100) / 100
        prev.total = prev.base_ss + prev.importe_ss
      }
      
      showHorasExtrasModal.value = false
    }
    
    const toggleSelectAll = (event) => {
      if (event.target.checked) {
        seleccionadas.value = previsiones.value.map(p => `${p.employee}-${p.course}`)
      } else {
        seleccionadas.value = []
      }
    }
    
    const toggleSelectAllLiquidaciones = (event) => {
      if (event.target.checked) {
        seleccionadasLiquidaciones.value = liquidaciones.value.map(l => l.name)
      } else {
        seleccionadasLiquidaciones.value = []
      }
    }
    
    const abrirLiquidacion = (name) => {
      window.open(`/app/liquidacion-nomina/${name}`, '_blank')
    }
    
    // Utilidades
    const formatCurrency = (value) => {
      return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR'
      }).format(value || 0)
    }
    
    const formatNumber = (value) => {
      return new Intl.NumberFormat('es-ES', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value || 0)
    }
    
    const getEstadoBadgeTheme = (estado) => {
      const map = {
        'Borrador': 'gray',
        'Previsión': 'blue',
        'Liquidado': 'orange',
        'Enviado a Asesoría': 'purple',
        'Pagado': 'green'
      }
      return map[estado] || 'gray'
    }
    
    function getMesActual() {
      const meses = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
      ]
      return meses[new Date().getMonth()]
    }
    
    // Lifecycle
    onMounted(() => {
      cargarDatos()
    })
    
    return {
      loading,
      activeTab,
      filters,
      previsiones,
      liquidaciones,
      resumen,
      seleccionadas,
      seleccionadasLiquidaciones,
      showDetalleModal,
      detalleActual,
      showHorasExtrasModal,
      horasExtrasData,
      cargarDatos,
      limpiarFiltros,
      generarPrevisiones,
      liquidarSeleccionadas,
      marcarComoEnviado,
      generarReporteExcel,
      verDetalle,
      agregarHorasExtras,
      guardarHorasExtras,
      toggleSelectAll,
      toggleSelectAllLiquidaciones,
      abrirLiquidacion,
      formatCurrency,
      formatNumber,
      getEstadoBadgeTheme
    }
  }
}
</script>

<style scoped>
.form-select {
  @apply block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm;
}
</style>
