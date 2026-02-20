<template>
  <div class="h-full flex flex-col overflow-hidden">
    <div class="flex-1 overflow-y-auto px-5 py-4 sm:px-8">
      
      <!-- Pestañas Principales -->
      <div class="mb-4">
        <nav class="flex space-x-1 bg-gray-100 p-1 rounded-lg">
          <button 
            @click="mainTab = 'nominas'" 
            :class="[
              'flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-colors',
              mainTab === 'nominas' 
                ? 'bg-white text-blue-600 shadow-sm' 
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            ]"
          >
            <FeatherIcon name="file-text" class="h-4 w-4" />
            Nóminas
          </button>
          <button 
            @click="mainTab = 'incentivos'; cargarIncentivos()" 
            :class="[
              'flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-colors',
              mainTab === 'incentivos' 
                ? 'bg-white text-green-600 shadow-sm' 
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            ]"
          >
            <FeatherIcon name="award" class="h-4 w-4" />
            Incentivos
            <span v-if="incentivos.length > 0" class="ml-1 bg-green-100 text-green-600 px-2 py-0.5 rounded-full text-xs">
              {{ incentivos.length }}
            </span>
          </button>
          <button 
            @click="mainTab = 'gastos'; cargarGastos()" 
            :class="[
              'flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-md transition-colors',
              mainTab === 'gastos' 
                ? 'bg-white text-orange-600 shadow-sm' 
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
            ]"
          >
            <FeatherIcon name="credit-card" class="h-4 w-4" />
            Dietas y KM
            <span v-if="gastos.length > 0" class="ml-1 bg-orange-100 text-orange-600 px-2 py-0.5 rounded-full text-xs">
              {{ gastos.length }}
            </span>
          </button>
        </nav>
      </div>

      <!-- ============================================ -->
      <!-- PESTAÑA: NÓMINAS -->
      <!-- ============================================ -->
      <div v-show="mainTab === 'nominas'">
      
      <!-- Filtros Compactos -->
      <Card class="mb-4">
        <div class="p-2">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mb-2">
            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">Mes</label>
              <select 
                v-model="filters.mes" 
                @change="cargarDatos" 
                class="form-select w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm py-1.5"
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
              <label class="block text-xs font-medium text-gray-700 mb-1">Año</label>
              <Input 
                type="number" 
                v-model="filters.año" 
                @change="cargarDatos"
                class="text-sm"
              />
            </div>

            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">Docente (Opcional)</label>
              <Input 
                type="text" 
                v-model="filters.employee" 
                placeholder="Buscar docente..."
                class="text-sm"
              />
            </div>

            <div>
              <label class="block text-xs font-medium text-gray-700 mb-1">Course (Opcional)</label>
              <Input 
                type="text" 
                v-model="filters.course" 
                placeholder="Buscar course..."
                class="text-sm"
              />
            </div>
          </div>

          <div class="flex flex-wrap gap-2">
            <Button @click="cargarDatos" icon-left="search" class="!py-1 !text-sm">
              Buscar
            </Button>
            <Button @click="limpiarFiltros" appearance="white" class="!py-1 !text-sm">
              Limpiar
            </Button>
            
            <div class="border-l border-gray-300 mx-1"></div>
            
            <Button 
              @click="generarPrevisiones" 
              icon-left="refresh-cw"
              :loading="loading"
              class="!py-1 !text-sm"
            >
              Actualizar Previsiones
            </Button>

            <Button 
              @click="liquidarSeleccionadas" 
              icon-left="check"
              :disabled="seleccionadas.length === 0 || loading"
              class="!py-1 !text-sm bg-blue-600 hover:bg-blue-700 text-white"
            >
              Liquidar {{ seleccionadas.length }} Seleccionadas
            </Button>

            <Button 
              @click="generarTodasLiquidaciones" 
              icon-left="alert-triangle"
              :disabled="previsiones.length === 0 || loading || generandoMasivo"
              :loading="generandoMasivo"
              class="!py-1 !text-sm bg-orange-600 hover:bg-orange-700 text-white"
            >
              ⚠️ Generar TODAS ({{ previsiones.length }})
            </Button>

            <Button 
              @click="validarSeleccionadas" 
              icon-left="check-circle"
              :disabled="borradoresSeleccionados.length === 0 || loading"
              class="!py-1 !text-sm bg-blue-600 hover:bg-blue-700 text-white"
            >
              Validar Seleccionadas ({{ borradoresSeleccionados.length }})
            </Button>

            <Button 
              @click="abrirEnvioAsesoria" 
              icon-left="mail"
              :disabled="liquidacionesValidadas.length === 0 || loading"
              class="!py-1 !text-sm bg-purple-600 hover:bg-purple-700 text-white"
            >
              Enviar a Asesoría ({{ liquidacionesValidadas.length }})
            </Button>

            <Button 
              @click="marcarComoPagado" 
              icon-left="dollar-sign"
              appearance="white"
              :disabled="seleccionadasLiquidaciones.length === 0 || loading"
              class="!py-1 !text-sm"
            >
              Marcar como Pagado
            </Button>

            <Button 
              @click="generarReporteExcel" 
              icon-left="download"
              appearance="white"
              :disabled="liquidaciones.length === 0 || loading"
              :loading="generandoExcel"
              class="!py-1 !text-sm"
            >
              Descargar Excel
            </Button>
          </div>
        </div>
      </Card>

      <!-- Notificación Toast -->
      <transition name="fade">
        <div 
          v-if="toast.show" 
          :class="[
            'fixed top-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg flex items-center gap-2 max-w-md',
            toast.type === 'success' ? 'bg-green-500 text-white' : '',
            toast.type === 'error' ? 'bg-red-500 text-white' : '',
            toast.type === 'warning' ? 'bg-yellow-500 text-white' : '',
            toast.type === 'info' ? 'bg-blue-500 text-white' : ''
          ]"
        >
          <FeatherIcon :name="toastIcon" class="h-5 w-5 flex-shrink-0" />
          <span class="text-sm">{{ toast.message }}</span>
          <button @click="toast.show = false" class="ml-2 hover:opacity-70">
            <FeatherIcon name="x" class="h-4 w-4" />
          </button>
        </div>
      </transition>

      <!-- Resumen Compacto -->
      <div v-if="resumen" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
        <Card>
          <div class="p-2.5 flex items-center gap-2.5">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-100 flex-shrink-0">
              <FeatherIcon name="users" class="h-4 w-4 text-blue-600" />
            </div>
            <div class="min-w-0">
              <div class="text-[10px] font-medium text-gray-500 uppercase leading-tight">Total Docentes</div>
              <div class="text-lg font-bold text-gray-900 leading-tight">{{ resumen.total_docentes }}</div>
            </div>
          </div>
        </Card>

        <Card>
          <div class="p-2.5 flex items-center gap-2.5">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-green-100 flex-shrink-0">
              <FeatherIcon name="clock" class="h-4 w-4 text-green-600" />
            </div>
            <div class="min-w-0">
              <div class="text-[10px] font-medium text-gray-500 uppercase leading-tight">Total Horas</div>
              <div class="text-lg font-bold text-gray-900 leading-tight">{{ formatNumber(resumen.total_horas) }}h</div>
            </div>
          </div>
        </Card>

        <Card>
          <div class="p-2.5 flex items-center gap-2.5">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-yellow-100 flex-shrink-0">
              <FeatherIcon name="dollar-sign" class="h-4 w-4 text-yellow-600" />
            </div>
            <div class="min-w-0">
              <div class="text-[10px] font-medium text-gray-500 uppercase leading-tight">Total Bruto</div>
              <div class="text-lg font-bold text-gray-900 leading-tight">{{ formatCurrency(resumen.total_bruto) }}</div>
            </div>
          </div>
        </Card>

        <Card class="bg-gradient-to-br from-blue-500 to-blue-600">
          <div class="p-2.5 flex items-center gap-2.5">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-white bg-opacity-20 flex-shrink-0">
              <FeatherIcon name="trending-up" class="h-4 w-4 text-white" />
            </div>
            <div class="min-w-0">
              <div class="text-[10px] font-medium text-blue-100 uppercase leading-tight">Total a Pagar</div>
              <div class="text-lg font-bold text-white leading-tight">{{ formatCurrency(resumen.total_pagar) }}</div>
            </div>
          </div>
        </Card>
      </div>

      <!-- Tabs -->
      <Card>
        <div class="border-b border-gray-200">
          <nav class="flex -mb-px">
            <button 
              @click="activeTab = 'previsiones'" 
              :class="[
                'flex items-center gap-2 px-5 py-2.5 text-sm font-medium border-b-2 transition-colors',
                activeTab === 'previsiones' 
                  ? 'border-blue-500 text-blue-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              <FeatherIcon name="eye" class="h-4 w-4" />
              Previsiones
              <span v-if="previsiones.length > 0" class="ml-1 bg-blue-100 text-blue-600 px-2 py-0.5 rounded-full text-xs">
                {{ previsiones.length }}
              </span>
            </button>
            <button 
              @click="activeTab = 'liquidaciones'" 
              :class="[
                'flex items-center gap-2 px-5 py-2.5 text-sm font-medium border-b-2 transition-colors',
                activeTab === 'liquidaciones' 
                  ? 'border-blue-500 text-blue-600' 
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              <FeatherIcon name="file-text" class="h-4 w-4" />
              Liquidaciones
              <span v-if="liquidaciones.length > 0" class="ml-1 bg-green-100 text-green-600 px-2 py-0.5 rounded-full text-xs">
                {{ liquidaciones.length }}
              </span>
            </button>
          </nav>
        </div>

        <!-- Tabla de Previsiones -->
        <div v-if="activeTab === 'previsiones'" class="p-3">
          <LoadingIndicator v-if="loading" class="py-12" />

          <div v-else-if="previsiones.length === 0" class="text-center py-12">
            <FeatherIcon name="inbox" class="h-12 w-12 text-gray-400 mx-auto mb-3" />
            <p class="text-gray-500 mb-4">No hay previsiones pendientes para este mes</p>
            <p class="text-gray-400 text-sm mb-4">Las previsiones se generan automáticamente desde Job Offers y Modificaciones RRHH activos</p>
            <Button @click="cargarDatos" icon-left="refresh-cw">
              Actualizar
            </Button>
          </div>

          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-3 py-2 text-left">
                    <input 
                      type="checkbox" 
                      :checked="allPrevisionesSelected"
                      @change="toggleSelectAll" 
                      class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                  </th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <span class="cursor-help" @click="mostrarAyuda('docente')">Docente <FeatherIcon name="help-circle" class="h-3 w-3 inline text-gray-400" /></span>
                  </th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">DNI/NIE</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <span class="cursor-help" @click="mostrarAyuda('course')">Course <FeatherIcon name="help-circle" class="h-3 w-3 inline text-gray-400" /></span>
                  </th>
                  <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <span class="cursor-help" @click="mostrarAyuda('horas')">Horas <FeatherIcon name="help-circle" class="h-3 w-3 inline text-gray-400" /></span>
                  </th>
                  <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <span class="cursor-help" @click="mostrarAyuda('brutoV')">Bruto+V <FeatherIcon name="help-circle" class="h-3 w-3 inline text-gray-400" /></span>
                  </th>
                  <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <span class="cursor-help" @click="mostrarAyuda('vacaciones')">Vacaciones <FeatherIcon name="help-circle" class="h-3 w-3 inline text-gray-400" /></span>
                  </th>
                  <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <span class="cursor-help" @click="mostrarAyuda('bruto')">Bruto <FeatherIcon name="help-circle" class="h-3 w-3 inline text-gray-400" /></span>
                  </th>
                  <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <span class="cursor-help" @click="mostrarAyuda('ss')">SS <FeatherIcon name="help-circle" class="h-3 w-3 inline text-gray-400" /></span>
                  </th>
                  <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <span class="cursor-help" @click="mostrarAyuda('total')">Total <FeatherIcon name="help-circle" class="h-3 w-3 inline text-gray-400" /></span>
                  </th>
                  <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Origen</th>
                  <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <span class="cursor-help" @click="mostrarAyuda('estado')">Estado <FeatherIcon name="help-circle" class="h-3 w-3 inline text-gray-400" /></span>
                  </th>
                  <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="prev in previsiones" :key="`prev-${prev.employee}-${prev.course}`" class="hover:bg-gray-50">
                  <td class="px-3 py-2">
                    <input 
                      type="checkbox" 
                      :value="`${prev.employee}-${prev.course}`"
                      v-model="seleccionadas"
                      class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                  </td>
                  <td class="px-3 py-2 text-sm text-gray-900">
                    <span 
                      class="cursor-pointer hover:text-blue-600 hover:underline" 
                      @click="mostrarExplicacion(prev, 'docente')"
                      :title="`Designation: ${prev.designation}`"
                    >{{ prev.employee_name }}</span>
                  </td>
                  <td class="px-3 py-2 text-sm text-gray-500">{{ prev.dni_nie }}</td>
                  <td class="px-3 py-2 text-sm text-gray-500 max-w-[200px] truncate">
                    <span 
                      class="cursor-pointer hover:text-blue-600 hover:underline"
                      @click="mostrarExplicacion(prev, 'course')"
                      :title="prev.course"
                    >{{ prev.course_display || prev.course }}</span>
                  </td>
                  <td class="px-3 py-2 text-sm text-gray-900 text-right">
                    <span 
                      class="cursor-pointer hover:text-blue-600 hover:underline"
                      @click="mostrarExplicacion(prev, 'horas')"
                      :title="`${prev.dias_trabajados} días × horas/día del calendario`"
                    >{{ formatNumber(prev.total_horas) }}h</span>
                  </td>
                  <!-- Bruto+V (con vacaciones incluidas) -->
                  <td class="px-3 py-2 text-sm text-gray-900 text-right">
                    <span 
                      class="cursor-pointer hover:text-blue-600 hover:underline"
                      @click="mostrarExplicacion(prev, 'brutoV')"
                      :title="`${formatNumber(prev.horas_normales)}h × ${formatCurrency(prev.precio_hora)}/h`"
                    >{{ formatCurrency(prev.bruto) }}</span>
                  </td>
                  <!-- Vacaciones -->
                  <td class="px-3 py-2 text-sm text-gray-500 text-right">
                    <span 
                      class="cursor-pointer hover:text-blue-600 hover:underline"
                      @click="mostrarExplicacion(prev, 'vacaciones')"
                      :title="`${formatCurrency(prev.bruto)} × 8.33%`"
                    >{{ formatCurrency(prev.vacaciones_mes) }}</span>
                  </td>
                  <!-- Bruto (sin vacaciones) -->
                  <td class="px-3 py-2 text-sm text-gray-900 text-right">
                    <span 
                      class="cursor-pointer hover:text-blue-600 hover:underline"
                      @click="mostrarExplicacion(prev, 'bruto')"
                      :title="`Bruto+V - Vacaciones`"
                    >{{ formatCurrency(prev.bruto_menos_vacaciones) }}</span>
                  </td>
                  <!-- SS -->
                  <td class="px-3 py-2 text-sm text-gray-500 text-right">
                    <span 
                      class="cursor-pointer hover:text-blue-600 hover:underline"
                      @click="mostrarExplicacion(prev, 'ss')"
                      :title="`Bruto × 32.07%`"
                    >{{ formatCurrency(prev.importe_ss) }}</span>
                  </td>
                  <td class="px-3 py-2 text-sm font-semibold text-gray-900 text-right">
                    <span 
                      class="cursor-pointer hover:text-blue-600 hover:underline"
                      @click="mostrarExplicacion(prev, 'total')"
                      :title="`Base SS + Importe SS`"
                    >{{ formatCurrency(prev.total) }}</span>
                  </td>
                  <!-- Enlace al documento origen -->
                  <td class="px-3 py-2 text-center">
                    <a 
                      :href="getSourceDocUrl(prev.source_type, prev.source_doc)"
                      target="_blank"
                      class="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 hover:underline"
                      :title="`Abrir ${prev.source_type}: ${prev.source_doc}`"
                    >
                      <FeatherIcon :name="prev.source_type === 'Job Offer' ? 'briefcase' : 'edit-3'" class="h-3 w-3" />
                      {{ prev.source_type === 'Job Offer' ? 'JO' : 'Mod' }}
                    </a>
                  </td>
                  <td class="px-3 py-2 text-center">
                    <span 
                      class="cursor-pointer"
                      @click="mostrarExplicacion(prev, 'estado')"
                      :title="`Estado del ${prev.source_type}`"
                    >
                      <Badge :theme="getWorkflowBadgeTheme(prev.workflow_state)">
                        {{ prev.workflow_state || 'N/A' }}
                      </Badge>
                    </span>
                  </td>
                  <td class="px-3 py-2 text-center">
                    <div class="flex items-center justify-center gap-1">
                      <Button 
                        @click="verDetalle(prev)" 
                        appearance="minimal"
                        icon="eye"
                        class="!p-1"
                        title="Ver detalle"
                      />
                      <Button 
                        @click="agregarHorasExtras(prev)" 
                        appearance="minimal"
                        icon="clock"
                        class="!p-1"
                        title="Agregar horas extras"
                      />
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Tabla de Liquidaciones -->
        <div v-if="activeTab === 'liquidaciones'" class="p-3">
          <LoadingIndicator v-if="loading" class="py-12" />

          <div v-else-if="liquidaciones.length === 0" class="text-center py-12">
            <FeatherIcon name="inbox" class="h-12 w-12 text-gray-400 mx-auto mb-3" />
            <p class="text-gray-500">No hay liquidaciones creadas para este mes</p>
            <p class="text-gray-400 text-sm mt-2">Selecciona previsiones y haz clic en "Liquidar Seleccionadas"</p>
          </div>

          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-3 py-2 text-left">
                    <input 
                      type="checkbox" 
                      :checked="allLiquidacionesSelected"
                      @change="toggleSelectAllLiquidaciones" 
                      class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                  </th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Docente</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">DNI/NIE</th>
                  <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Course</th>
                  <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Origen</th>
                  <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Horas N</th>
                  <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Horas E</th>
                  <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total H</th>
                  <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Bruto+V</th>
                  <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Vacaciones</th>
                  <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Bruto</th>
                  <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">SS</th>
                  <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                  <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                  <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr 
                  v-for="liq in liquidaciones" 
                  :key="liq.name" 
                  :class="[
                    'hover:bg-gray-50',
                    liq.docstatus === 0 ? 'bg-yellow-50' : ''
                  ]"
                >
                  <td class="px-3 py-2">
                    <input 
                      type="checkbox" 
                      :value="liq.name"
                      v-model="seleccionadasLiquidaciones"
                      class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                  </td>
                  <td class="px-3 py-2 text-sm text-gray-900">{{ liq.employee_name }}</td>
                  <td class="px-3 py-2 text-sm text-gray-500">{{ liq.dni_nie }}</td>
                  <td class="px-3 py-2 text-sm text-gray-500 max-w-[200px] truncate" :title="liq.course">{{ liq.course_display || liq.course }}</td>
                  <!-- Enlace al documento origen -->
                  <td class="px-3 py-2 text-center">
                    <a 
                      :href="getSourceDocUrl(liq.source_document_type, liq.source_document)"
                      target="_blank"
                      class="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 hover:underline"
                      :title="`Abrir ${liq.source_document_type}: ${liq.source_document}`"
                    >
                      <FeatherIcon :name="liq.source_document_type === 'Job Offer' ? 'briefcase' : 'edit-3'" class="h-3 w-3" />
                      {{ liq.source_document_type === 'Job Offer' ? 'JO' : 'Mod' }}
                    </a>
                  </td>
                  
                  <!-- Horas Normales - Editable si es borrador -->
                  <td class="px-3 py-2 text-sm text-right">
                    <input 
                      v-if="liq.docstatus === 0"
                      type="number"
                      :value="liq.horas_normales"
                      @change="editarCampoLiquidacion(liq, 'horas_normales', $event.target.value)"
                      class="w-16 text-right border rounded px-1 py-0.5 text-sm"
                      step="0.5"
                    />
                    <span v-else>{{ formatNumber(liq.horas_normales) }}</span>
                  </td>
                  
                  <!-- Horas Extras - Editable si es borrador -->
                  <td class="px-3 py-2 text-sm text-right">
                    <input 
                      v-if="liq.docstatus === 0"
                      type="number"
                      :value="liq.horas_extras"
                      @change="editarCampoLiquidacion(liq, 'horas_extras', $event.target.value)"
                      class="w-16 text-right border rounded px-1 py-0.5 text-sm"
                      step="0.5"
                    />
                    <span v-else>{{ formatNumber(liq.horas_extras) }}</span>
                  </td>
                  
                  <td class="px-3 py-2 text-sm text-gray-900 text-right">{{ formatNumber(liq.total_horas) }}</td>
                  <td class="px-3 py-2 text-sm text-gray-900 text-right">{{ formatCurrency(liq.bruto) }}</td>
                  <td class="px-3 py-2 text-sm text-gray-500 text-right">{{ formatCurrency(liq.vacaciones_mes) }}</td>
                  <td class="px-3 py-2 text-sm text-gray-900 text-right">{{ formatCurrency(liq.bruto_menos_vacaciones) }}</td>
                  <td class="px-3 py-2 text-sm text-gray-500 text-right">{{ formatCurrency(liq.importe_ss) }}</td>
                  <td class="px-3 py-2 text-sm font-semibold text-gray-900 text-right">{{ formatCurrency(liq.total) }}</td>
                  
                  <!-- Estado con indicador de borrador -->
                  <td class="px-3 py-2 text-center">
                    <Badge :theme="getEstadoBadgeTheme(liq.estado)">
                      {{ liq.estado }}
                    </Badge>
                    <div v-if="liq.docstatus === 0" class="text-xs text-yellow-600 mt-0.5">
                      (editable)
                    </div>
                  </td>
                  
                  <td class="px-3 py-2 text-center">
                    <div class="flex items-center justify-center gap-1">
                      <!-- Botón editar para borradores -->
                      <Button 
                        v-if="liq.docstatus === 0"
                        @click="abrirEdicionLiquidacion(liq)" 
                        appearance="minimal"
                        icon="edit-2"
                        class="!p-1"
                        title="Editar liquidación"
                      />
                      <Button 
                        @click="abrirLiquidacion(liq.name)" 
                        appearance="minimal"
                        icon="external-link"
                        class="!p-1"
                        title="Abrir en Frappe"
                      />
                    </div>
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
                    <span class="font-medium text-gray-900 text-right max-w-[200px]">{{ detalleActual.course_display || detalleActual.course }}</span>
                  </div>
                  <div class="flex justify-between text-sm pt-2 border-t mt-2">
                    <span class="text-gray-500">Documento Origen:</span>
                    <a 
                      :href="getSourceDocUrl(detalleActual.source_type, detalleActual.source_doc)"
                      target="_blank"
                      class="font-medium text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1"
                    >
                      <FeatherIcon :name="detalleActual.source_type === 'Job Offer' ? 'briefcase' : 'edit-3'" class="h-3 w-3" />
                      {{ detalleActual.source_type === 'Job Offer' ? 'Job Offer' : 'Modificación RRHH' }}
                      <FeatherIcon name="external-link" class="h-3 w-3" />
                    </a>
                  </div>
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-500">ID Documento:</span>
                    <span class="font-medium text-gray-900">{{ detalleActual.source_doc }}</span>
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
                  <span class="text-gray-900">BRUTO+V (con vacaciones):</span>
                  <span class="text-gray-900">{{ formatCurrency(detalleActual.bruto) }}</span>
                </div>
                <div class="flex justify-between text-sm text-red-600">
                  <span>Vacaciones (8.33%):</span>
                  <span>-{{ formatCurrency(detalleActual.vacaciones_mes) }}</span>
                </div>
                <div class="flex justify-between text-sm border-t pt-2 font-semibold">
                  <span class="text-gray-900">BRUTO (sin vacaciones):</span>
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

      <!-- Dialog: Marcar como Pagado -->
      <Dialog 
        v-model="showPagoModal"
        :options="{
          title: 'Marcar como Pagado',
          size: 'sm'
        }"
      >
        <template #body-content>
          <div class="space-y-4">
            <p class="text-sm text-gray-600">
              Se marcarán <strong>{{ seleccionadasLiquidaciones.length }}</strong> liquidaciones como pagadas.
            </p>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Fecha de Pago</label>
              <Input 
                type="date" 
                v-model="fechaPago"
              />
            </div>
          </div>
        </template>
        <template #actions>
          <Button appearance="white" @click="showPagoModal = false">
            Cancelar
          </Button>
          <Button @click="confirmarPago" :loading="loading">
            Confirmar Pago
          </Button>
        </template>
      </Dialog>

      <!-- Dialog: Editar Liquidación -->
      <Dialog 
        v-model="showEdicionModal"
        :options="{
          title: 'Editar Liquidación',
          size: 'lg'
        }"
      >
        <template #body-content>
          <div v-if="edicionData" class="space-y-4">
            <!-- Info del docente -->
            <div class="bg-gray-50 rounded-lg p-3">
              <div class="grid grid-cols-2 gap-2 text-sm">
                <div><strong>Docente:</strong> {{ edicionData.employee_name }}</div>
                <div><strong>DNI/NIE:</strong> {{ edicionData.dni_nie }}</div>
                <div class="col-span-2"><strong>Curso:</strong> {{ edicionData.course }}</div>
              </div>
            </div>

            <!-- Campos editables -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Horas Normales</label>
                <Input 
                  type="number" 
                  v-model="edicionData.horas_normales"
                  step="0.5"
                  min="0"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Horas Extras</label>
                <Input 
                  type="number" 
                  v-model="edicionData.horas_extras"
                  step="0.5"
                  min="0"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Precio/Hora (€)</label>
                <Input 
                  type="number" 
                  v-model="edicionData.precio_hora"
                  step="0.01"
                  min="0"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Precio/Hora Extra (€)</label>
                <Input 
                  type="number" 
                  v-model="edicionData.precio_hora_extra"
                  step="0.01"
                  min="0"
                  :placeholder="`Por defecto: ${(edicionData.precio_hora * 1.2).toFixed(2)}`"
                />
              </div>
            </div>

            <!-- Último mes -->
            <div class="flex items-center gap-2 p-3 bg-yellow-50 rounded-lg">
              <input 
                type="checkbox" 
                v-model="edicionData.es_ultimo_mes"
                id="es_ultimo_mes"
                class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <label for="es_ultimo_mes" class="text-sm font-medium text-gray-700">
                Es el último mes (se liquidarán las vacaciones acumuladas)
              </label>
            </div>

            <!-- Vacaciones acumuladas si es último mes -->
            <div v-if="edicionData.es_ultimo_mes" class="bg-blue-50 rounded-lg p-3 space-y-3">
              <h4 class="text-sm font-semibold text-blue-900">Vacaciones Acumuladas</h4>
              
              <!-- Info de vacaciones calculadas del sistema -->
              <div v-if="vacacionesInfo" class="text-xs text-blue-600 bg-blue-100 rounded p-2">
                <p>Calculado del sistema: <strong>{{ formatCurrency(vacacionesInfo.total_acumulado) }}</strong></p>
                <p class="mt-1">{{ vacacionesInfo.meses_liquidados }} meses liquidados anteriormente</p>
              </div>
              
              <!-- Campo editable para vacaciones acumuladas -->
              <div>
                <label class="block text-sm font-medium text-blue-800 mb-1">
                  Importe de vacaciones acumuladas a liquidar:
                </label>
                <input 
                  type="number" 
                  v-model="edicionData.vacaciones_acumuladas_manual"
                  step="0.01"
                  min="0"
                  class="w-full rounded-md border-blue-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-lg font-bold text-blue-700"
                  placeholder="0.00"
                />
                <p class="text-xs text-blue-500 mt-1">
                  Introduce el importe total de vacaciones acumuladas que se pagarán este mes
                </p>
              </div>
            </div>

            <!-- Preview de cálculos -->
            <div class="border rounded-lg p-3 bg-gray-50">
              <h4 class="text-sm font-semibold text-gray-700 mb-2">Vista previa del cálculo</h4>
              <div class="grid grid-cols-2 gap-2 text-sm">
                <div>Total Horas:</div>
                <div class="text-right font-medium">{{ formatNumber(parseFloat(edicionData.horas_normales || 0) + parseFloat(edicionData.horas_extras || 0)) }}h</div>
                <div>Bruto+V estimado:</div>
                <div class="text-right font-medium">{{ formatCurrency(calcularBrutoPreview()) }}</div>
                <div>Vacaciones mes (8.33%):</div>
                <div class="text-right font-medium text-red-600">-{{ formatCurrency(calcularBrutoPreview() * 0.0833) }}</div>
                <div>Bruto estimado:</div>
                <div class="text-right font-medium">{{ formatCurrency(calcularBrutoPreview() * (1 - 0.0833)) }}</div>
                
                <!-- Si es último mes, mostrar vacaciones acumuladas y totales -->
                <template v-if="edicionData.es_ultimo_mes">
                  <div class="text-green-700">+ Vacaciones acumuladas:</div>
                  <div class="text-right font-medium text-green-700">+{{ formatCurrency(parseFloat(edicionData.vacaciones_acumuladas_manual) || 0) }}</div>
                  <div class="font-semibold border-t pt-1">Base SS:</div>
                  <div class="text-right font-semibold border-t pt-1">{{ formatCurrency(calcularBaseSS()) }}</div>
                  <div>SS Empresa (32.07%):</div>
                  <div class="text-right font-medium">{{ formatCurrency(calcularBaseSS() * 0.3207) }}</div>
                  <div class="font-bold text-lg border-t pt-1">TOTAL:</div>
                  <div class="text-right font-bold text-lg border-t pt-1">{{ formatCurrency(calcularBaseSS() + calcularBaseSS() * 0.3207) }}</div>
                </template>
                <template v-else>
                  <div class="font-semibold border-t pt-1">Base SS:</div>
                  <div class="text-right font-semibold border-t pt-1">{{ formatCurrency(calcularBrutoPreview() * (1 - 0.0833)) }}</div>
                  <div>SS Empresa (32.07%):</div>
                  <div class="text-right font-medium">{{ formatCurrency(calcularBrutoPreview() * (1 - 0.0833) * 0.3207) }}</div>
                  <div class="font-bold text-lg border-t pt-1">TOTAL:</div>
                  <div class="text-right font-bold text-lg border-t pt-1">{{ formatCurrency(calcularBrutoPreview() * (1 - 0.0833) * 1.3207) }}</div>
                </template>
              </div>
            </div>
          </div>
        </template>
        <template #actions>
          <Button appearance="white" @click="showEdicionModal = false">
            Cancelar
          </Button>
          <Button @click="guardarEdicionLiquidacion" :loading="guardandoEdicion">
            Guardar y Recalcular
          </Button>
        </template>
      </Dialog>

      <!-- Dialog: Resultado Generación Masiva -->
      <Dialog 
        v-model="showResultadoMasivoModal"
        :options="{
          title: 'Resultado de Generación Masiva',
          size: 'xl'
        }"
      >
        <template #body-content>
          <div v-if="resultadoMasivo" class="space-y-4">
            <!-- Resumen -->
            <div class="grid grid-cols-3 gap-4">
              <div class="bg-green-50 rounded-lg p-4 text-center">
                <div class="text-2xl font-bold text-green-600">{{ resultadoMasivo.creadas }}</div>
                <div class="text-sm text-green-800">Liquidaciones Creadas</div>
              </div>
              <div class="bg-yellow-50 rounded-lg p-4 text-center">
                <div class="text-2xl font-bold text-yellow-600">{{ resultadoMasivo.omitidas }}</div>
                <div class="text-sm text-yellow-800">Omitidas (ya existían)</div>
              </div>
              <div class="bg-red-50 rounded-lg p-4 text-center">
                <div class="text-2xl font-bold text-red-600">{{ resultadoMasivo.errores?.length || 0 }}</div>
                <div class="text-sm text-red-800">Errores</div>
              </div>
            </div>

            <!-- Detalle por docente -->
            <div v-if="resultadoMasivo.total_docentes > 0" class="border rounded-lg">
              <div class="bg-gray-50 px-4 py-2 border-b">
                <h4 class="font-medium text-gray-900">Detalle por Docente ({{ resultadoMasivo.total_docentes }})</h4>
              </div>
              <div class="max-h-64 overflow-y-auto">
                <div 
                  v-for="(datos, nombre) in resultadoMasivo.por_docente" 
                  :key="nombre"
                  class="px-4 py-2 border-b last:border-b-0 flex justify-between items-center"
                >
                  <span class="text-sm text-gray-900">{{ nombre }}</span>
                  <div class="flex items-center gap-2">
                    <span class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">
                      {{ datos.creadas }} creadas
                    </span>
                    <span v-if="datos.errores > 0" class="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded">
                      {{ datos.errores }} errores
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Errores -->
            <div v-if="resultadoMasivo.errores?.length > 0" class="border border-red-200 rounded-lg">
              <div class="bg-red-50 px-4 py-2 border-b border-red-200">
                <h4 class="font-medium text-red-900">Errores Detallados</h4>
              </div>
              <div class="max-h-32 overflow-y-auto p-2">
                <div 
                  v-for="(error, idx) in resultadoMasivo.errores" 
                  :key="idx"
                  class="text-xs text-red-700 py-1"
                >
                  {{ error }}
                </div>
              </div>
            </div>
          </div>
        </template>
        <template #actions>
          <Button @click="showResultadoMasivoModal = false">
            Cerrar
          </Button>
        </template>
      </Dialog>

      <!-- Dialog: Explicación de Campo -->
      <Dialog 
        v-model="showExplicacionModal"
        :options="{
          title: explicacionActual?.titulo || 'Explicación',
          size: 'md'
        }"
      >
        <template #body-content>
          <div v-if="explicacionActual" class="space-y-4">
            <!-- Descripción -->
            <div class="bg-blue-50 rounded-lg p-4">
              <p class="text-sm text-blue-800">{{ explicacionActual.descripcion }}</p>
            </div>

            <!-- Fórmula -->
            <div v-if="explicacionActual.formula" class="bg-gray-50 rounded-lg p-4">
              <h4 class="text-xs font-semibold text-gray-500 uppercase mb-2">Fórmula</h4>
              <code class="text-sm bg-white px-2 py-1 rounded border block">{{ explicacionActual.formula }}</code>
            </div>

            <!-- Valor actual -->
            <div v-if="explicacionActual.valor" class="bg-green-50 rounded-lg p-4">
              <h4 class="text-xs font-semibold text-gray-500 uppercase mb-2">Valor Actual</h4>
              <div class="text-2xl font-bold text-green-700">{{ explicacionActual.valor }}</div>
            </div>

            <!-- Desglose -->
            <div v-if="explicacionActual.desglose && explicacionActual.desglose.length > 0" class="border rounded-lg">
              <h4 class="text-xs font-semibold text-gray-500 uppercase px-4 py-2 bg-gray-50 border-b">Desglose del Cálculo</h4>
              <div class="divide-y">
                <div 
                  v-for="(item, idx) in explicacionActual.desglose" 
                  :key="idx"
                  class="px-4 py-2 flex justify-between items-center"
                >
                  <span class="text-sm text-gray-600">{{ item.concepto }}</span>
                  <span class="text-sm font-medium text-gray-900">{{ item.valor }}</span>
                </div>
              </div>
            </div>

            <!-- Origen de datos -->
            <div v-if="explicacionActual.origen" class="text-xs text-gray-500 border-t pt-3">
              <FeatherIcon name="database" class="h-3 w-3 inline mr-1" />
              <strong>Origen:</strong> {{ explicacionActual.origen }}
            </div>
          </div>
        </template>
        <template #actions>
          <Button appearance="white" @click="showExplicacionModal = false">
            Cerrar
          </Button>
        </template>
      </Dialog>

      <!-- Dialog: Ayuda General de Columna -->
      <Dialog 
        v-model="showAyudaModal"
        :options="{
          title: ayudaActual?.titulo || 'Ayuda',
          size: 'md'
        }"
      >
        <template #body-content>
          <div v-if="ayudaActual" class="space-y-4">
            <div class="bg-blue-50 rounded-lg p-4">
              <p class="text-sm text-blue-800">{{ ayudaActual.descripcion }}</p>
            </div>

            <div v-if="ayudaActual.formula" class="bg-gray-100 rounded-lg p-4">
              <h4 class="text-xs font-semibold text-gray-500 uppercase mb-2">Fórmula</h4>
              <code class="text-sm">{{ ayudaActual.formula }}</code>
            </div>

            <div v-if="ayudaActual.notas" class="text-sm text-gray-600">
              <h4 class="font-semibold mb-2">Notas:</h4>
              <ul class="list-disc list-inside space-y-1">
                <li v-for="(nota, idx) in ayudaActual.notas" :key="idx">{{ nota }}</li>
              </ul>
            </div>
          </div>
        </template>
        <template #actions>
          <Button @click="showAyudaModal = false">
            Entendido
          </Button>
        </template>
      </Dialog>

      <!-- Dialog: Enviar a Asesoría -->
      <Dialog 
        v-model="showEnvioAsesoriaModal"
        :options="{
          title: 'Enviar Liquidaciones a Asesoría',
          size: '4xl'
        }"
      >
        <template #body-content>
          <div class="space-y-4">
            <!-- Resumen -->
            <div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <div class="flex items-center gap-3">
                <div class="bg-purple-600 text-white p-2 rounded-lg">
                  <FeatherIcon name="mail" class="h-6 w-6" />
                </div>
                <div>
                  <h3 class="font-semibold text-purple-900">
                    {{ liquidacionesParaEnvio.length }} liquidaciones listas para enviar
                  </h3>
                  <p class="text-sm text-purple-700">
                    Se generará un Excel profesional y se enviará a los usuarios con rol Asesoría
                  </p>
                </div>
              </div>
            </div>

            <!-- Selector de liquidaciones -->
            <div class="border rounded-lg">
              <div class="bg-gray-50 px-4 py-2 border-b flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <input 
                    type="checkbox" 
                    :checked="todasSeleccionadasAsesoria"
                    @change="toggleSelectAllAsesoria"
                    class="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                  />
                  <span class="text-sm font-medium text-gray-700">Seleccionar todas</span>
                </div>
                <div class="text-sm text-gray-600">
                  {{ seleccionadasParaAsesoria.length }} de {{ liquidacionesParaEnvio.length }} seleccionadas
                </div>
              </div>
              
              <div class="max-h-64 overflow-y-auto">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50 sticky top-0">
                    <tr>
                      <th class="px-3 py-2 w-10"></th>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Docente</th>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">DNI/NIE</th>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Curso</th>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Empresa</th>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Provincia</th>
                      <th class="px-3 py-2 text-right text-xs font-medium text-gray-500">Total</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr 
                      v-for="liq in liquidacionesParaEnvio" 
                      :key="liq.name"
                      :class="seleccionadasParaAsesoria.includes(liq.name) ? 'bg-purple-50' : 'hover:bg-gray-50'"
                    >
                      <td class="px-3 py-2">
                        <input 
                          type="checkbox" 
                          :value="liq.name"
                          v-model="seleccionadasParaAsesoria"
                          class="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                        />
                      </td>
                      <td class="px-3 py-2 text-sm text-gray-900">{{ liq.employee_name }}</td>
                      <td class="px-3 py-2 text-sm text-gray-500">{{ liq.dni_nie }}</td>
                      <td class="px-3 py-2 text-sm text-gray-500 max-w-[200px] truncate" :title="liq.course">
                        {{ liq.course_display || liq.course }}
                      </td>
                      <td class="px-3 py-2 text-sm text-gray-500">{{ liq.company }}</td>
                      <td class="px-3 py-2 text-sm text-gray-500">{{ liq.provincia || '-' }}</td>
                      <td class="px-3 py-2 text-sm text-gray-900 text-right font-medium">
                        {{ formatCurrency(liq.total) }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Resumen de importes -->
            <div class="grid grid-cols-3 gap-4">
              <div class="bg-gray-50 rounded-lg p-3 text-center">
                <div class="text-2xl font-bold text-gray-900">{{ seleccionadasParaAsesoria.length }}</div>
                <div class="text-xs text-gray-500">Liquidaciones</div>
              </div>
              <div class="bg-gray-50 rounded-lg p-3 text-center">
                <div class="text-2xl font-bold text-gray-900">{{ formatNumber(calcularTotalHorasAsesoria()) }}h</div>
                <div class="text-xs text-gray-500">Total Horas</div>
              </div>
              <div class="bg-purple-100 rounded-lg p-3 text-center">
                <div class="text-2xl font-bold text-purple-700">{{ formatCurrency(calcularTotalAsesoria()) }}</div>
                <div class="text-xs text-purple-600">Importe Total</div>
              </div>
            </div>

            <!-- Info de destinatarios -->
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <div class="flex items-start gap-2">
                <FeatherIcon name="info" class="h-4 w-4 text-blue-600 mt-0.5" />
                <div class="text-sm text-blue-800">
                  <p class="font-medium">El Excel se enviará a los usuarios con rol "Asesoría"</p>
                  <p class="text-blue-600 mt-1">Las liquidaciones seleccionadas se marcarán como "Enviado a Asesoría"</p>
                </div>
              </div>
            </div>
          </div>
        </template>
        <template #actions>
          <Button appearance="white" @click="showEnvioAsesoriaModal = false">
            Cancelar
          </Button>
          <Button 
            @click="enviarAAsesoria" 
            :loading="enviandoAsesoria"
            :disabled="seleccionadasParaAsesoria.length === 0"
            class="bg-purple-600 hover:bg-purple-700 text-white"
          >
            <FeatherIcon name="send" class="h-4 w-4 mr-2" />
            Enviar {{ seleccionadasParaAsesoria.length }} Liquidaciones
          </Button>
        </template>
      </Dialog>

      </div><!-- Fin pestaña Nóminas -->

      <!-- ============================================ -->
      <!-- PESTAÑA: INCENTIVOS -->
      <!-- ============================================ -->
      <div v-show="mainTab === 'incentivos'">
        <!-- Filtros Incentivos -->
        <Card class="mb-4">
          <div class="p-3">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-3 mb-3">
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">Estado</label>
                <select 
                  v-model="filtrosIncentivos.estado" 
                  @change="cargarIncentivos"
                  class="form-select w-full rounded-md border-gray-300 shadow-sm text-sm py-1.5"
                >
                  <option value="">Todos</option>
                  <option value="Draft">Borrador</option>
                  <option value="Approved">Aprobado</option>
                  <option value="Rejected">Rechazado</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">Empleado</label>
                <Input 
                  type="text" 
                  v-model="filtrosIncentivos.employee" 
                  placeholder="Buscar empleado..."
                  class="text-sm"
                />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">Desde</label>
                <Input type="date" v-model="filtrosIncentivos.desde" class="text-sm" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">Hasta</label>
                <Input type="date" v-model="filtrosIncentivos.hasta" class="text-sm" />
              </div>
            </div>
            <div class="flex gap-2">
              <Button @click="cargarIncentivos" icon-left="search" class="!py-1 !text-sm">
                Buscar
              </Button>
              <Button @click="limpiarFiltrosIncentivos" appearance="white" class="!py-1 !text-sm">
                Limpiar
              </Button>
              <Button @click="nuevoIncentivo" icon-left="plus" class="!py-1 !text-sm bg-green-600 hover:bg-green-700 text-white">
                Nuevo Incentivo
              </Button>
            </div>
          </div>
        </Card>

        <!-- Resumen Incentivos -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
          <Card>
            <div class="p-2.5 flex items-center gap-2.5">
              <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-green-100 flex-shrink-0">
                <FeatherIcon name="award" class="h-4 w-4 text-green-600" />
              </div>
              <div>
                <div class="text-[10px] font-medium text-gray-500 uppercase">Total Incentivos</div>
                <div class="text-lg font-bold text-gray-900">{{ incentivos.length }}</div>
              </div>
            </div>
          </Card>
          <Card>
            <div class="p-2.5 flex items-center gap-2.5">
              <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-100 flex-shrink-0">
                <FeatherIcon name="dollar-sign" class="h-4 w-4 text-blue-600" />
              </div>
              <div>
                <div class="text-[10px] font-medium text-gray-500 uppercase">Importe Total</div>
                <div class="text-lg font-bold text-gray-900">{{ formatCurrency(resumenIncentivos.total_importe) }}</div>
              </div>
            </div>
          </Card>
          <Card>
            <div class="p-2.5 flex items-center gap-2.5">
              <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-yellow-100 flex-shrink-0">
                <FeatherIcon name="clock" class="h-4 w-4 text-yellow-600" />
              </div>
              <div>
                <div class="text-[10px] font-medium text-gray-500 uppercase">Pendientes</div>
                <div class="text-lg font-bold text-gray-900">{{ resumenIncentivos.pendientes }}</div>
              </div>
            </div>
          </Card>
        </div>

        <!-- Tabla Incentivos -->
        <Card>
          <div class="p-3">
            <LoadingIndicator v-if="loadingIncentivos" class="py-12" />
            
            <div v-else-if="incentivos.length === 0" class="text-center py-12">
              <FeatherIcon name="award" class="h-12 w-12 text-gray-400 mx-auto mb-3" />
              <p class="text-gray-500">No hay incentivos registrados</p>
              <Button @click="nuevoIncentivo" class="mt-4" icon-left="plus">
                Crear Primer Incentivo
              </Button>
            </div>

            <div v-else class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Empleado</th>
                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Provincia</th>
                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Componente</th>
                    <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Importe</th>
                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Fecha Nómina</th>
                    <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase">Estado</th>
                    <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase">Acciones</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="inc in incentivos" :key="inc.name" class="hover:bg-gray-50">
                    <td class="px-3 py-2">
                      <div class="text-sm font-medium text-gray-900">{{ inc.employee_name }}</div>
                      <div class="text-xs text-gray-500">{{ inc.employee }}</div>
                    </td>
                    <td class="px-3 py-2 text-sm text-gray-500">{{ inc.custom_provincia || '-' }}</td>
                    <td class="px-3 py-2 text-sm text-gray-500">{{ inc.salary_component }}</td>
                    <td class="px-3 py-2 text-sm text-right font-medium text-gray-900">
                      {{ inc.custom_by_hours ? formatDuration(inc.custom_incentive_hours) : formatCurrency(inc.incentive_amount) }}
                    </td>
                    <td class="px-3 py-2 text-sm text-gray-500">{{ formatDate(inc.payroll_date) }}</td>
                    <td class="px-3 py-2 text-center">
                      <Badge :theme="getIncentivoEstadoBadge(inc.docstatus, inc.workflow_state)">
                        {{ getIncentivoEstadoLabel(inc.docstatus, inc.workflow_state) }}
                      </Badge>
                    </td>
                    <td class="px-3 py-2 text-center">
                      <div class="flex items-center justify-center gap-1">
                        <Button 
                          @click="editarIncentivo(inc)" 
                          appearance="minimal"
                          icon="edit-2"
                          class="!p-1"
                          title="Editar"
                          :disabled="inc.docstatus === 1"
                        />
                        <Button 
                          @click="abrirIncentivo(inc.name)" 
                          appearance="minimal"
                          icon="external-link"
                          class="!p-1"
                          title="Abrir en Frappe"
                        />
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </Card>
      </div><!-- Fin pestaña Incentivos -->

      <!-- ============================================ -->
      <!-- PESTAÑA: DIETAS Y KM -->
      <!-- ============================================ -->
      <div v-show="mainTab === 'gastos'">
        <!-- Filtros Gastos -->
        <Card class="mb-4">
          <div class="p-3">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-3 mb-3">
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">Estado</label>
                <select 
                  v-model="filtrosGastos.estado" 
                  @change="cargarGastos"
                  class="form-select w-full rounded-md border-gray-300 shadow-sm text-sm py-1.5"
                >
                  <option value="">Todos</option>
                  <option value="Draft">Borrador</option>
                  <option value="Submitted">Enviado</option>
                  <option value="Approved">Aprobado</option>
                  <option value="Rejected">Rechazado</option>
                  <option value="Paid">Pagado</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">Empleado</label>
                <Input 
                  type="text" 
                  v-model="filtrosGastos.employee" 
                  placeholder="Buscar empleado..."
                  class="text-sm"
                />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">Desde</label>
                <Input type="date" v-model="filtrosGastos.desde" class="text-sm" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-700 mb-1">Hasta</label>
                <Input type="date" v-model="filtrosGastos.hasta" class="text-sm" />
              </div>
            </div>
            <div class="flex gap-2">
              <Button @click="cargarGastos" icon-left="search" class="!py-1 !text-sm">
                Buscar
              </Button>
              <Button @click="limpiarFiltrosGastos" appearance="white" class="!py-1 !text-sm">
                Limpiar
              </Button>
              <Button @click="nuevoGasto" icon-left="plus" class="!py-1 !text-sm bg-orange-600 hover:bg-orange-700 text-white">
                Nuevo Gasto
              </Button>
            </div>
          </div>
        </Card>

        <!-- Resumen Gastos -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-3 mb-4">
          <Card>
            <div class="p-2.5 flex items-center gap-2.5">
              <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-orange-100 flex-shrink-0">
                <FeatherIcon name="file-text" class="h-4 w-4 text-orange-600" />
              </div>
              <div>
                <div class="text-[10px] font-medium text-gray-500 uppercase">Total Gastos</div>
                <div class="text-lg font-bold text-gray-900">{{ gastos.length }}</div>
              </div>
            </div>
          </Card>
          <Card>
            <div class="p-2.5 flex items-center gap-2.5">
              <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-100 flex-shrink-0">
                <FeatherIcon name="dollar-sign" class="h-4 w-4 text-blue-600" />
              </div>
              <div>
                <div class="text-[10px] font-medium text-gray-500 uppercase">Total Reclamado</div>
                <div class="text-lg font-bold text-gray-900">{{ formatCurrency(resumenGastos.total_reclamado) }}</div>
              </div>
            </div>
          </Card>
          <Card>
            <div class="p-2.5 flex items-center gap-2.5">
              <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-green-100 flex-shrink-0">
                <FeatherIcon name="check-circle" class="h-4 w-4 text-green-600" />
              </div>
              <div>
                <div class="text-[10px] font-medium text-gray-500 uppercase">Total Aprobado</div>
                <div class="text-lg font-bold text-gray-900">{{ formatCurrency(resumenGastos.total_aprobado) }}</div>
              </div>
            </div>
          </Card>
          <Card>
            <div class="p-2.5 flex items-center gap-2.5">
              <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-yellow-100 flex-shrink-0">
                <FeatherIcon name="clock" class="h-4 w-4 text-yellow-600" />
              </div>
              <div>
                <div class="text-[10px] font-medium text-gray-500 uppercase">Pendientes</div>
                <div class="text-lg font-bold text-gray-900">{{ resumenGastos.pendientes }}</div>
              </div>
            </div>
          </Card>
        </div>

        <!-- Tabla Gastos -->
        <Card>
          <div class="p-3">
            <LoadingIndicator v-if="loadingGastos" class="py-12" />
            
            <div v-else-if="gastos.length === 0" class="text-center py-12">
              <FeatherIcon name="credit-card" class="h-12 w-12 text-gray-400 mx-auto mb-3" />
              <p class="text-gray-500">No hay gastos registrados</p>
              <Button @click="nuevoGasto" class="mt-4" icon-left="plus">
                Registrar Primer Gasto
              </Button>
            </div>

            <div v-else class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Empleado</th>
                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Fecha</th>
                    <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Reclamado</th>
                    <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">Aprobado</th>
                    <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase">Aprobación</th>
                    <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase">Estado</th>
                    <th class="px-3 py-2 text-center text-xs font-medium text-gray-500 uppercase">Acciones</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="gasto in gastos" :key="gasto.name" class="hover:bg-gray-50">
                    <td class="px-3 py-2 text-sm text-gray-500">{{ gasto.name }}</td>
                    <td class="px-3 py-2">
                      <div class="text-sm font-medium text-gray-900">{{ gasto.employee_name }}</div>
                      <div class="text-xs text-gray-500">{{ gasto.department }}</div>
                    </td>
                    <td class="px-3 py-2 text-sm text-gray-500">{{ formatDate(gasto.posting_date) }}</td>
                    <td class="px-3 py-2 text-sm text-right font-medium text-gray-900">
                      {{ formatCurrency(gasto.total_claimed_amount) }}
                    </td>
                    <td class="px-3 py-2 text-sm text-right font-medium text-green-600">
                      {{ formatCurrency(gasto.total_sanctioned_amount) }}
                    </td>
                    <td class="px-3 py-2 text-center">
                      <Badge :theme="getApprovalBadge(gasto.approval_status)">
                        {{ gasto.approval_status || 'Pendiente' }}
                      </Badge>
                    </td>
                    <td class="px-3 py-2 text-center">
                      <Badge :theme="getGastoEstadoBadge(gasto.status)">
                        {{ gasto.status }}
                      </Badge>
                    </td>
                    <td class="px-3 py-2 text-center">
                      <div class="flex items-center justify-center gap-1">
                        <Button 
                          @click="verDetalleGasto(gasto)" 
                          appearance="minimal"
                          icon="eye"
                          class="!p-1"
                          title="Ver detalle"
                        />
                        <Button 
                          @click="editarGasto(gasto)" 
                          appearance="minimal"
                          icon="edit-2"
                          class="!p-1"
                          title="Editar"
                          :disabled="gasto.docstatus === 1"
                        />
                        <Button 
                          @click="abrirGasto(gasto.name)" 
                          appearance="minimal"
                          icon="external-link"
                          class="!p-1"
                          title="Abrir en Frappe"
                        />
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </Card>
      </div><!-- Fin pestaña Gastos -->

      <!-- ============================================ -->
      <!-- MODALES INCENTIVOS -->
      <!-- ============================================ -->
      <Dialog 
        v-model="showIncentivoModal"
        :options="{
          title: incentivoEditando ? 'Editar Incentivo' : 'Nuevo Incentivo',
          size: 'lg'
        }"
      >
        <template #body-content>
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Empleado *</label>
                <Input 
                  type="text" 
                  v-model="incentivoForm.employee_search" 
                  placeholder="Buscar empleado..."
                  @input="buscarEmpleados"
                />
                <div v-if="empleadosSugeridos.length > 0" class="mt-1 bg-white border rounded-md shadow-sm max-h-40 overflow-y-auto">
                  <button 
                    v-for="emp in empleadosSugeridos" 
                    :key="emp.name"
                    @click="seleccionarEmpleadoIncentivo(emp)"
                    class="w-full text-left px-3 py-2 hover:bg-gray-100 text-sm"
                  >
                    {{ emp.employee_name }} ({{ emp.name }})
                  </button>
                </div>
                <div v-if="incentivoForm.employee" class="mt-1 text-xs text-green-600">
                  Seleccionado: {{ incentivoForm.employee_name }}
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Provincia</label>
                <Input type="text" v-model="incentivoForm.custom_provincia" placeholder="Provincia" />
              </div>
            </div>
            
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Componente Salarial *</label>
                <select 
                  v-model="incentivoForm.salary_component"
                  class="form-select w-full rounded-md border-gray-300 shadow-sm text-sm"
                >
                  <option value="">Seleccionar...</option>
                  <option v-for="comp in salaryComponents" :key="comp.name" :value="comp.name">
                    {{ comp.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Fecha Nómina *</label>
                <Input type="date" v-model="incentivoForm.payroll_date" />
              </div>
            </div>

            <div class="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
              <input 
                type="checkbox" 
                v-model="incentivoForm.custom_by_hours"
                id="by_hours"
                class="rounded border-gray-300"
              />
              <label for="by_hours" class="text-sm font-medium text-gray-700">Por Horas</label>
            </div>

            <div v-if="incentivoForm.custom_by_hours">
              <label class="block text-sm font-medium text-gray-700 mb-1">Horas de Incentivo *</label>
              <Input type="text" v-model="incentivoForm.custom_incentive_hours" placeholder="ej: 2:30" />
            </div>
            <div v-else>
              <label class="block text-sm font-medium text-gray-700 mb-1">Importe *</label>
              <Input type="number" v-model="incentivoForm.incentive_amount" step="0.01" min="0" />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Justificación</label>
              <textarea 
                v-model="incentivoForm.custom_justificación"
                rows="3"
                class="w-full rounded-md border-gray-300 shadow-sm text-sm"
                placeholder="Motivo del incentivo..."
              ></textarea>
            </div>
          </div>
        </template>
        <template #actions>
          <Button appearance="white" @click="showIncentivoModal = false">
            Cancelar
          </Button>
          <Button @click="guardarIncentivo" :loading="guardandoIncentivo">
            {{ incentivoEditando ? 'Guardar Cambios' : 'Crear Incentivo' }}
          </Button>
        </template>
      </Dialog>

      <!-- ============================================ -->
      <!-- MODALES GASTOS -->
      <!-- ============================================ -->
      <Dialog 
        v-model="showGastoModal"
        :options="{
          title: gastoEditando ? 'Editar Gasto' : 'Nuevo Gasto',
          size: 'xl'
        }"
      >
        <template #body-content>
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Empleado *</label>
                <Input 
                  type="text" 
                  v-model="gastoForm.employee_search" 
                  placeholder="Buscar empleado..."
                  @input="buscarEmpleadosGasto"
                />
                <div v-if="empleadosSugeridosGasto.length > 0" class="mt-1 bg-white border rounded-md shadow-sm max-h-40 overflow-y-auto">
                  <button 
                    v-for="emp in empleadosSugeridosGasto" 
                    :key="emp.name"
                    @click="seleccionarEmpleadoGasto(emp)"
                    class="w-full text-left px-3 py-2 hover:bg-gray-100 text-sm"
                  >
                    {{ emp.employee_name }} ({{ emp.name }})
                  </button>
                </div>
                <div v-if="gastoForm.employee" class="mt-1 text-xs text-green-600">
                  Seleccionado: {{ gastoForm.employee_name }}
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Fecha *</label>
                <Input type="date" v-model="gastoForm.posting_date" />
              </div>
            </div>

            <!-- Líneas de gasto -->
            <div>
              <div class="flex justify-between items-center mb-2">
                <label class="block text-sm font-medium text-gray-700">Líneas de Gasto</label>
                <Button @click="agregarLineaGasto" icon-left="plus" class="!py-1 !text-xs">
                  Añadir Línea
                </Button>
              </div>
              <div class="border rounded-lg overflow-hidden">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Tipo</th>
                      <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Descripción</th>
                      <th class="px-3 py-2 text-right text-xs font-medium text-gray-500">Importe</th>
                      <th class="px-3 py-2 w-10"></th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-200">
                    <tr v-for="(linea, idx) in gastoForm.expenses" :key="idx">
                      <td class="px-2 py-1">
                        <select 
                          v-model="linea.expense_type"
                          class="form-select w-full rounded border-gray-300 text-xs py-1"
                        >
                          <option value="">Seleccionar...</option>
                          <option v-for="tipo in expenseTypes" :key="tipo.name" :value="tipo.name">
                            {{ tipo.name }}
                          </option>
                        </select>
                      </td>
                      <td class="px-2 py-1">
                        <input 
                          v-model="linea.description"
                          class="w-full rounded border-gray-300 text-xs py-1"
                          placeholder="Descripción"
                        />
                      </td>
                      <td class="px-2 py-1">
                        <input 
                          v-model="linea.amount"
                          type="number"
                          step="0.01"
                          class="w-full rounded border-gray-300 text-xs py-1 text-right"
                        />
                      </td>
                      <td class="px-2 py-1">
                        <Button 
                          @click="eliminarLineaGasto(idx)" 
                          appearance="minimal"
                          icon="trash-2"
                          class="!p-0.5 text-red-500"
                        />
                      </td>
                    </tr>
                  </tbody>
                  <tfoot class="bg-gray-50">
                    <tr>
                      <td colspan="2" class="px-3 py-2 text-right text-sm font-medium">Total:</td>
                      <td class="px-3 py-2 text-right text-sm font-bold">{{ formatCurrency(calcularTotalGasto()) }}</td>
                      <td></td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Observaciones</label>
              <textarea 
                v-model="gastoForm.remark"
                rows="2"
                class="w-full rounded-md border-gray-300 shadow-sm text-sm"
                placeholder="Observaciones adicionales..."
              ></textarea>
            </div>
          </div>
        </template>
        <template #actions>
          <Button appearance="white" @click="showGastoModal = false">
            Cancelar
          </Button>
          <Button @click="guardarGasto" :loading="guardandoGasto">
            {{ gastoEditando ? 'Guardar Cambios' : 'Crear Gasto' }}
          </Button>
        </template>
      </Dialog>

      <!-- Dialog: Detalle de Gasto -->
      <Dialog 
        v-model="showDetalleGastoModal"
        :options="{
          title: 'Detalle del Gasto',
          size: 'xl'
        }"
      >
        <template #body-content>
          <div v-if="gastoDetalle" class="space-y-4">
            <div class="grid grid-cols-2 gap-4 bg-gray-50 rounded-lg p-4">
              <div>
                <div class="text-xs text-gray-500">Empleado</div>
                <div class="font-medium">{{ gastoDetalle.employee_name }}</div>
              </div>
              <div>
                <div class="text-xs text-gray-500">Fecha</div>
                <div class="font-medium">{{ formatDate(gastoDetalle.posting_date) }}</div>
              </div>
              <div>
                <div class="text-xs text-gray-500">Total Reclamado</div>
                <div class="font-medium">{{ formatCurrency(gastoDetalle.total_claimed_amount) }}</div>
              </div>
              <div>
                <div class="text-xs text-gray-500">Total Aprobado</div>
                <div class="font-medium text-green-600">{{ formatCurrency(gastoDetalle.total_sanctioned_amount) }}</div>
              </div>
            </div>

            <div class="border rounded-lg overflow-hidden">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Tipo</th>
                    <th class="px-3 py-2 text-left text-xs font-medium text-gray-500">Descripción</th>
                    <th class="px-3 py-2 text-right text-xs font-medium text-gray-500">Reclamado</th>
                    <th class="px-3 py-2 text-right text-xs font-medium text-gray-500">Aprobado</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                  <tr v-for="exp in gastoDetalle.expenses" :key="exp.name">
                    <td class="px-3 py-2 text-sm">{{ exp.expense_type }}</td>
                    <td class="px-3 py-2 text-sm text-gray-500">{{ exp.description || '-' }}</td>
                    <td class="px-3 py-2 text-sm text-right">{{ formatCurrency(exp.amount) }}</td>
                    <td class="px-3 py-2 text-sm text-right text-green-600">{{ formatCurrency(exp.sanctioned_amount) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div v-if="gastoDetalle.remark" class="bg-yellow-50 rounded-lg p-3">
              <div class="text-xs text-gray-500 mb-1">Observaciones</div>
              <p class="text-sm">{{ gastoDetalle.remark }}</p>
            </div>
          </div>
        </template>
        <template #actions>
          <Button @click="showDetalleGastoModal = false">
            Cerrar
          </Button>
        </template>
      </Dialog>

    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, reactive, watch } from 'vue'
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
    // Estado principal
    const mainTab = ref('nominas')
    const loading = ref(false)
    const generandoExcel = ref(false)
    const generandoMasivo = ref(false)
    const guardandoEdicion = ref(false)
    const activeTab = ref('previsiones')
    
    // Helper: Calcular fecha hace N meses
    const getFechaHaceMeses = (meses) => {
      const fecha = new Date()
      fecha.setMonth(fecha.getMonth() - meses)
      return fecha.toISOString().split('T')[0]
    }
    
    const getHoy = () => new Date().toISOString().split('T')[0]
    
    // Estado Incentivos
    const loadingIncentivos = ref(false)
    const guardandoIncentivo = ref(false)
    const incentivos = ref([])
    const filtrosIncentivos = ref({
      estado: '',
      employee: '',
      desde: getFechaHaceMeses(2),  // Últimos 2 meses
      hasta: getHoy()
    })
    const resumenIncentivos = ref({
      total_importe: 0,
      pendientes: 0
    })
    const showIncentivoModal = ref(false)
    const incentivoEditando = ref(null)
    const incentivoForm = ref({
      employee: '',
      employee_name: '',
      employee_search: '',
      custom_provincia: '',
      salary_component: '',
      payroll_date: new Date().toISOString().split('T')[0],
      incentive_amount: 0,
      custom_by_hours: false,
      custom_incentive_hours: '',
      custom_justificación: ''
    })
    const salaryComponents = ref([])
    const empleadosSugeridos = ref([])
    
    // Estado Gastos
    const loadingGastos = ref(false)
    const guardandoGasto = ref(false)
    const gastos = ref([])
    const filtrosGastos = ref({
      estado: '',
      employee: '',
      desde: getFechaHaceMeses(2),  // Últimos 2 meses
      hasta: getHoy()
    })
    const resumenGastos = ref({
      total_reclamado: 0,
      total_aprobado: 0,
      pendientes: 0
    })
    const showGastoModal = ref(false)
    const showDetalleGastoModal = ref(false)
    const gastoEditando = ref(null)
    const gastoDetalle = ref(null)
    const gastoForm = ref({
      employee: '',
      employee_name: '',
      employee_search: '',
      posting_date: new Date().toISOString().split('T')[0],
      expenses: [],
      remark: ''
    })
    const expenseTypes = ref([])
    const empleadosSugeridosGasto = ref([])
    
    // Toast notification
    const toast = reactive({
      show: false,
      message: '',
      type: 'info' // 'success', 'error', 'warning', 'info'
    })
    
    const toastIcon = computed(() => {
      const icons = {
        success: 'check-circle',
        error: 'alert-circle',
        warning: 'alert-triangle',
        info: 'info'
      }
      return icons[toast.type] || 'info'
    })
    
    const showToast = (message, type = 'info', duration = 4000) => {
      toast.message = message
      toast.type = type
      toast.show = true
      
      setTimeout(() => {
        toast.show = false
      }, duration)
    }
    
    // Filtros
    const filters = ref({
      mes: getMesActual(),
      año: new Date().getFullYear(),
      employee: '',
      course: ''
    })
    
    // Datos sin filtrar
    const previsionesRaw = ref([])
    const liquidacionesRaw = ref([])
    const resumen = ref(null)
    const seleccionadas = ref([])
    const seleccionadasLiquidaciones = ref([])
    
    // Datos filtrados (computed)
    const previsiones = computed(() => {
      let filtered = previsionesRaw.value
      
      if (filters.value.employee && filters.value.employee.trim() !== '') {
        const searchTerm = filters.value.employee.toLowerCase().trim()
        filtered = filtered.filter(p => 
          p.employee_name?.toLowerCase().includes(searchTerm) ||
          p.employee?.toLowerCase().includes(searchTerm) ||
          p.dni_nie?.toLowerCase().includes(searchTerm)
        )
      }
      
      if (filters.value.course && filters.value.course.trim() !== '') {
        const searchTerm = filters.value.course.toLowerCase().trim()
        filtered = filtered.filter(p => 
          p.course?.toLowerCase().includes(searchTerm)
        )
      }
      
      return filtered
    })
    
    const liquidaciones = computed(() => {
      let filtered = liquidacionesRaw.value
      
      if (filters.value.employee && filters.value.employee.trim() !== '') {
        const searchTerm = filters.value.employee.toLowerCase().trim()
        filtered = filtered.filter(l => 
          l.employee_name?.toLowerCase().includes(searchTerm) ||
          l.employee?.toLowerCase().includes(searchTerm) ||
          l.dni_nie?.toLowerCase().includes(searchTerm)
        )
      }
      
      if (filters.value.course && filters.value.course.trim() !== '') {
        const searchTerm = filters.value.course.toLowerCase().trim()
        filtered = filtered.filter(l => 
          l.course?.toLowerCase().includes(searchTerm)
        )
      }
      
      return filtered
    })
    
    // Computed para checkboxes "seleccionar todo"
    const allPrevisionesSelected = computed(() => {
      return previsiones.value.length > 0 && 
        previsiones.value.every(p => seleccionadas.value.includes(`${p.employee}-${p.course}`))
    })
    
    const allLiquidacionesSelected = computed(() => {
      return liquidaciones.value.length > 0 && 
        liquidaciones.value.every(l => seleccionadasLiquidaciones.value.includes(l.name))
    })
    
    // Modals
    const showDetalleModal = ref(false)
    const detalleActual = ref(null)
    const showHorasExtrasModal = ref(false)
    const horasExtrasData = ref(null)
    const showPagoModal = ref(false)
    const fechaPago = ref(new Date().toISOString().split('T')[0])
    const showResultadoMasivoModal = ref(false)
    const resultadoMasivo = ref(null)
    const showExplicacionModal = ref(false)
    const explicacionActual = ref(null)
    const showAyudaModal = ref(false)
    const ayudaActual = ref(null)
    const showEdicionModal = ref(false)
    const edicionData = ref(null)
    const vacacionesInfo = ref(null)
    
    // Computed: liquidaciones en borrador
    const liquidacionesBorrador = computed(() => {
      return liquidaciones.value.filter(l => l.docstatus === 0)
    })
    
    // Computed: borradores seleccionados (para validar)
    const borradoresSeleccionados = computed(() => {
      return liquidaciones.value.filter(l => 
        l.docstatus === 0 && seleccionadasLiquidaciones.value.includes(l.name)
      )
    })
    
    // Computed: liquidaciones validadas (pendientes de enviar a asesoría)
    const liquidacionesValidadas = computed(() => {
      return liquidaciones.value.filter(l => l.docstatus === 1 && l.estado === 'Liquidado')
    })
    
    // Modal envío a asesoría
    const showEnvioAsesoriaModal = ref(false)
    const liquidacionesParaEnvio = ref([])
    const seleccionadasParaAsesoria = ref([])
    const enviandoAsesoria = ref(false)
    
    const todasSeleccionadasAsesoria = computed(() => {
      return liquidacionesParaEnvio.value.length > 0 && 
        liquidacionesParaEnvio.value.every(l => seleccionadasParaAsesoria.value.includes(l.name))
    })
    
    // Watch para cargar vacaciones al marcar es_ultimo_mes
    watch(() => edicionData.value?.es_ultimo_mes, async (newVal, oldVal) => {
      if (newVal && !oldVal && edicionData.value) {
        await cargarVacacionesParaEdicion()
      } else if (!newVal) {
        vacacionesInfo.value = null
      }
    })
    
    const cargarVacacionesParaEdicion = async () => {
      if (!edicionData.value) return
      try {
        const liq = liquidaciones.value.find(l => l.name === edicionData.value.name)
        if (liq) {
          const result = await call('portal_rrhh.api.nominas.obtener_vacaciones_acumuladas', {
            employee: liq.employee,
            course: liq.course,
            año: filters.value.año
          })
          vacacionesInfo.value = result
        }
      } catch (error) {
        console.error('Error cargando vacaciones:', error)
        vacacionesInfo.value = null
      }
    }
    
    // Métodos
    const cargarDatos = async () => {
      loading.value = true
      
      try {
        // Cargar previsiones
        const respPrevisiones = await call('portal_rrhh.api.nominas.get_prevision_mes', {
          mes: filters.value.mes,
          año: filters.value.año,
          employee: null,
          course: null
        })
        
        if (respPrevisiones) {
          previsionesRaw.value = respPrevisiones.previsiones || []
          resumen.value = respPrevisiones.resumen || {}
        }
        
        // Cargar liquidaciones existentes
        const respLiquidaciones = await call('portal_rrhh.api.nominas.get_liquidaciones_mes', {
          mes: filters.value.mes,
          año: filters.value.año,
          employee: null,
          course: null
        })
        
        if (respLiquidaciones) {
          liquidacionesRaw.value = respLiquidaciones.liquidaciones || []
          // Si hay liquidaciones, usar su resumen (más preciso)
          if (respLiquidaciones.liquidaciones?.length > 0) {
            resumen.value = respLiquidaciones.resumen
          }
        }
        
      } catch (error) {
        console.error('Error cargando datos:', error)
        showToast('Error al cargar los datos', 'error')
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
      showToast('Previsiones actualizadas', 'success')
    }
    
    const liquidarSeleccionadas = async () => {
      if (seleccionadas.value.length === 0) return
      
      if (!confirm(`¿Crear ${seleccionadas.value.length} liquidaciones SOLO para las previsiones seleccionadas?`)) {
        return
      }
      
      loading.value = true
      
      try {
        const liquidaciones_data = previsiones.value.filter(p => 
          seleccionadas.value.includes(`${p.employee}-${p.course}`)
        )
        
        const result = await call('portal_rrhh.api.nominas.crear_liquidaciones_mes', {
          mes: filters.value.mes,
          año: filters.value.año,
          liquidaciones_data: liquidaciones_data
        })
        
        if (result.creadas > 0) {
          showToast(`Se crearon ${result.creadas} liquidaciones`, 'success')
        }
        
        if (result.errores?.length > 0) {
          console.warn('Errores al liquidar:', result.errores)
          showToast(`${result.errores.length} liquidaciones con errores`, 'warning')
        }
        
        seleccionadas.value = []
        await cargarDatos()
        activeTab.value = 'liquidaciones'
        
      } catch (error) {
        console.error('Error liquidando nóminas:', error)
        showToast('Error al liquidar las nóminas', 'error')
      } finally {
        loading.value = false
      }
    }
    
    const generarTodasLiquidaciones = async () => {
      if (previsiones.value.length === 0) return
      
      if (!confirm(`⚠️ ATENCIÓN: Esto generará ${previsiones.value.length} liquidaciones para TODAS las previsiones pendientes.\n\n¿Está seguro de continuar?`)) {
        return
      }
      
      generandoMasivo.value = true
      
      try {
        const result = await call('portal_rrhh.api.nominas.generar_liquidaciones_masivas', {
          mes: filters.value.mes,
          año: filters.value.año
        })
        
        resultadoMasivo.value = result
        showResultadoMasivoModal.value = true
        
        if (result.creadas > 0) {
          showToast(`Se crearon ${result.creadas} liquidaciones para ${result.total_docentes} docentes`, 'success')
        } else if (result.omitidas > 0) {
          showToast('Todas las liquidaciones ya existían', 'warning')
        }
        
        seleccionadas.value = []
        await cargarDatos()
        activeTab.value = 'liquidaciones'
        
      } catch (error) {
        console.error('Error en generación masiva:', error)
        showToast('Error al generar las liquidaciones', 'error')
      } finally {
        generandoMasivo.value = false
      }
    }
    
    const validarSeleccionadas = async () => {
      const borradores = borradoresSeleccionados.value
      if (borradores.length === 0) {
        showToast('Selecciona al menos una liquidación en borrador para validar', 'warning')
        return
      }
      
      if (!confirm(`¿Validar ${borradores.length} liquidación(es) seleccionada(s)? Una vez validadas no se podrán modificar.`)) {
        return
      }
      
      loading.value = true
      
      try {
        const ids = borradores.map(l => l.name)
        const result = await call('portal_rrhh.api.nominas.validar_liquidaciones', {
          liquidaciones_ids: ids
        })
        
        if (result.validadas > 0) {
          showToast(`Se validaron ${result.validadas} liquidaciones`, 'success')
        }
        
        if (result.errores?.length > 0) {
          console.warn('Errores al validar:', result.errores)
          showToast(`${result.errores.length} liquidaciones con errores`, 'warning')
        }
        
        seleccionadasLiquidaciones.value = []
        await cargarDatos()
        
      } catch (error) {
        console.error('Error validando:', error)
        showToast('Error al validar las liquidaciones', 'error')
      } finally {
        loading.value = false
      }
    }
    
    const abrirEdicionLiquidacion = async (liq) => {
      edicionData.value = {
        name: liq.name,
        employee: liq.employee,
        employee_name: liq.employee_name,
        dni_nie: liq.dni_nie,
        course: liq.course,
        horas_normales: liq.horas_normales,
        horas_extras: liq.horas_extras,
        precio_hora: liq.precio_hora,
        precio_hora_extra: liq.precio_hora_extra || (liq.precio_hora * 1.2),
        es_ultimo_mes: liq.es_ultimo_mes === 1,
        vacaciones_acumuladas_manual: liq.vacaciones_acumuladas || 0
      }
      
      // Cargar vacaciones acumuladas si es último mes
      if (edicionData.value.es_ultimo_mes) {
        await cargarVacacionesAcumuladas(liq)
      }
      
      showEdicionModal.value = true
    }
    
    const cargarVacacionesAcumuladas = async (liq) => {
      try {
        const result = await call('portal_rrhh.api.nominas.obtener_vacaciones_acumuladas', {
          employee: liq.employee,
          course: liq.course,
          año: filters.value.año
        })
        vacacionesInfo.value = result
      } catch (error) {
        console.error('Error cargando vacaciones:', error)
        vacacionesInfo.value = null
      }
    }
    
    const guardarEdicionLiquidacion = async () => {
      if (!edicionData.value) return
      
      guardandoEdicion.value = true
      
      try {
        const campos = {
          horas_normales: parseFloat(edicionData.value.horas_normales) || 0,
          horas_extras: parseFloat(edicionData.value.horas_extras) || 0,
          precio_hora: parseFloat(edicionData.value.precio_hora) || 0,
          precio_hora_extra: parseFloat(edicionData.value.precio_hora_extra) || 0,
          es_ultimo_mes: edicionData.value.es_ultimo_mes ? 1 : 0
        }
        
        // Si es último mes, incluir vacaciones acumuladas manuales
        if (edicionData.value.es_ultimo_mes) {
          campos.vacaciones_acumuladas = parseFloat(edicionData.value.vacaciones_acumuladas_manual) || 0
        }
        
        const result = await call('portal_rrhh.api.nominas.editar_liquidacion', {
          liquidacion_id: edicionData.value.name,
          campos: campos
        })
        
        showToast('Liquidación actualizada y recalculada', 'success')
        showEdicionModal.value = false
        await cargarDatos()
        
      } catch (error) {
        console.error('Error guardando:', error)
        showToast('Error al guardar la liquidación', 'error')
      } finally {
        guardandoEdicion.value = false
      }
    }
    
    const editarCampoLiquidacion = async (liq, campo, valor) => {
      try {
        const campos = {}
        campos[campo] = parseFloat(valor) || 0
        
        await call('portal_rrhh.api.nominas.editar_liquidacion', {
          liquidacion_id: liq.name,
          campos: campos
        })
        
        // Recargar datos para ver los recálculos
        await cargarDatos()
        showToast('Campo actualizado', 'success', 2000)
        
      } catch (error) {
        console.error('Error editando campo:', error)
        showToast('Error al actualizar', 'error')
      }
    }
    
    const calcularBrutoPreview = () => {
      if (!edicionData.value) return 0
      const horasN = parseFloat(edicionData.value.horas_normales) || 0
      const horasE = parseFloat(edicionData.value.horas_extras) || 0
      const precioN = parseFloat(edicionData.value.precio_hora) || 0
      const precioE = parseFloat(edicionData.value.precio_hora_extra) || (precioN * 1.2)
      return (horasN * precioN) + (horasE * precioE)
    }
    
    const calcularBaseSS = () => {
      if (!edicionData.value) return 0
      const brutoV = calcularBrutoPreview()
      const vacacionesMes = brutoV * 0.0833
      const bruto = brutoV - vacacionesMes
      const vacacionesAcumuladas = edicionData.value.es_ultimo_mes 
        ? (parseFloat(edicionData.value.vacaciones_acumuladas_manual) || 0)
        : 0
      return bruto + vacacionesAcumuladas
    }
    
    // Funciones para envío a asesoría
    const abrirEnvioAsesoria = async () => {
      loading.value = true
      try {
        // Cargar liquidaciones validadas con datos de provincia
        const result = await call('portal_rrhh.api.nominas.get_liquidaciones_validadas_mes', {
          mes: filters.value.mes,
          año: filters.value.año
        })
        
        liquidacionesParaEnvio.value = result.liquidaciones || []
        seleccionadasParaAsesoria.value = liquidacionesParaEnvio.value.map(l => l.name) // Seleccionar todas por defecto
        
        if (liquidacionesParaEnvio.value.length === 0) {
          showToast('No hay liquidaciones validadas pendientes de enviar', 'warning')
          return
        }
        
        showEnvioAsesoriaModal.value = true
        
      } catch (error) {
        console.error('Error cargando liquidaciones para asesoría:', error)
        showToast('Error al cargar liquidaciones', 'error')
      } finally {
        loading.value = false
      }
    }
    
    const toggleSelectAllAsesoria = () => {
      if (todasSeleccionadasAsesoria.value) {
        seleccionadasParaAsesoria.value = []
      } else {
        seleccionadasParaAsesoria.value = liquidacionesParaEnvio.value.map(l => l.name)
      }
    }
    
    const calcularTotalAsesoria = () => {
      return liquidacionesParaEnvio.value
        .filter(l => seleccionadasParaAsesoria.value.includes(l.name))
        .reduce((sum, l) => sum + (parseFloat(l.total) || 0), 0)
    }
    
    const calcularTotalHorasAsesoria = () => {
      return liquidacionesParaEnvio.value
        .filter(l => seleccionadasParaAsesoria.value.includes(l.name))
        .reduce((sum, l) => sum + (parseFloat(l.total_horas) || 0), 0)
    }
    
    const enviarAAsesoria = async () => {
      if (seleccionadasParaAsesoria.value.length === 0) {
        showToast('Seleccione al menos una liquidación', 'warning')
        return
      }
      
      if (!confirm(`¿Enviar ${seleccionadasParaAsesoria.value.length} liquidaciones a Asesoría?\n\nSe generará un Excel y se enviará por email a los usuarios con rol Asesoría.`)) {
        return
      }
      
      enviandoAsesoria.value = true
      
      try {
        const result = await call('portal_rrhh.api.nominas.enviar_liquidaciones_asesoria', {
          liquidaciones_ids: seleccionadasParaAsesoria.value,
          mes: filters.value.mes,
          año: filters.value.año
        })
        
        showToast(`${result.message}\nEnviado a: ${result.recipients.join(', ')}`, 'success', 5000)
        
        showEnvioAsesoriaModal.value = false
        seleccionadasParaAsesoria.value = []
        await cargarDatos()
        
      } catch (error) {
        console.error('Error enviando a asesoría:', error)
        showToast('Error al enviar a asesoría: ' + (error.message || 'Error desconocido'), 'error')
      } finally {
        enviandoAsesoria.value = false
      }
    }
    
    const marcarComoPagado = () => {
      if (seleccionadasLiquidaciones.value.length === 0) return
      showPagoModal.value = true
    }
    
    const confirmarPago = async () => {
      loading.value = true
      
      try {
        const result = await call('portal_rrhh.api.nominas.marcar_como_pagado', {
          liquidaciones_ids: seleccionadasLiquidaciones.value,
          fecha_pago: fechaPago.value
        })
        
        showToast(`Se marcaron ${result.actualizadas} liquidaciones como pagadas`, 'success')
        
        showPagoModal.value = false
        seleccionadasLiquidaciones.value = []
        await cargarDatos()
        
      } catch (error) {
        console.error('Error:', error)
        showToast('Error al marcar como pagadas', 'error')
      } finally {
        loading.value = false
      }
    }
    
    const generarReporteExcel = async () => {
      generandoExcel.value = true
      
      try {
        const result = await call('portal_rrhh.api.nominas.generar_reporte_excel', {
          mes: filters.value.mes,
          año: filters.value.año,
          liquidaciones_ids: seleccionadasLiquidaciones.value.length > 0 
            ? seleccionadasLiquidaciones.value 
            : null
        })
        
        if (result.success && result.file_url) {
          // Descargar el archivo
          window.open(result.file_url, '_blank')
          showToast('Reporte Excel generado correctamente', 'success')
        }
        
      } catch (error) {
        console.error('Error generando reporte:', error)
        showToast('Error al generar el reporte Excel', 'error')
      } finally {
        generandoExcel.value = false
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
      const index = previsionesRaw.value.findIndex(p => 
        p.employee === horasExtrasData.value.employee && 
        p.course === horasExtrasData.value.course
      )
      
      if (index !== -1) {
        const prev = previsionesRaw.value[index]
        prev.horas_extras = parseFloat(horasExtrasData.value.horas_extras) || 0
        prev.precio_hora_extra = parseFloat(horasExtrasData.value.precio_hora_extra) || (prev.precio_hora * 1.2)
        
        // Recalcular importes
        prev.total_horas = prev.horas_normales + prev.horas_extras
        prev.importe_horas_extras = prev.horas_extras * prev.precio_hora_extra
        prev.bruto = prev.importe_horas_normales + prev.importe_horas_extras
        prev.vacaciones_mes = Math.round(prev.bruto * 0.0833 * 100) / 100
        prev.bruto_menos_vacaciones = prev.bruto - prev.vacaciones_mes
        prev.base_ss = prev.bruto_menos_vacaciones
        prev.importe_ss = Math.round(prev.base_ss * 0.3207 * 100) / 100
        prev.total = prev.base_ss + prev.importe_ss
        
        showToast('Horas extras actualizadas', 'success')
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
    
    const getSourceDocUrl = (sourceType, sourceDoc) => {
      if (!sourceType || !sourceDoc) return '#'
      if (sourceType === 'Job Offer') {
        return `/app/job-offer/${sourceDoc}`
      } else if (sourceType === 'Modificaciones RRHH') {
        return `/app/modificaciones-rrhh/${sourceDoc}`
      }
      return '#'
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
    
    const getWorkflowBadgeTheme = (workflow_state) => {
      const map = {
        'Alta': 'green',
        'Baja': 'red',
        'Pendiente': 'yellow',
        'Accepted': 'blue'
      }
      return map[workflow_state] || 'gray'
    }
    
    // Definiciones de ayuda para cada columna
    const ayudaColumnas = {
      docente: {
        titulo: 'Docente',
        descripcion: 'Nombre del empleado que impartirá la formación. Se obtiene del Employee vinculado al Job Offer o Modificación RRHH.',
        notas: [
          'Solo se muestran empleados con designation de docente (Docente, Tutor/a, Profesor, Formador/a, etc.)',
          'El DNI/NIE se usa para vincular el Job Offer con el Employee'
        ]
      },
      course: {
        titulo: 'Curso',
        descripcion: 'Acción formativa asignada al docente. Se obtiene de la tabla de cursos del Job Offer o Modificación RRHH.',
        notas: [
          'Un Job Offer puede tener múltiples cursos asociados',
          'Se genera una liquidación por cada combinación docente + curso'
        ]
      },
      horas: {
        titulo: 'Horas Totales',
        descripcion: 'Total de horas lectivas del mes, calculadas automáticamente desde el calendario del curso.',
        formula: 'Σ (horas de cada día lectivo del mes)',
        notas: [
          'Las horas se obtienen del campo "Calendario Curso" del Course',
          'Solo se cuentan los días marcados como "Lectivo"',
          'Se suman todos los tramos horarios de cada día (hasta 6 tramos)'
        ]
      },
      brutoV: {
        titulo: 'Bruto+V (Bruto con Vacaciones)',
        descripcion: 'Importe total calculado por horas trabajadas. Incluye la parte proporcional de vacaciones.',
        formula: '(Horas Normales × Precio/Hora) + (Horas Extras × Precio/Hora Extra)',
        notas: [
          'El precio/hora se obtiene del Job Offer o Modificación RRHH',
          'El precio de hora extra es por defecto 120% del precio normal',
          'Incluye el importe de vacaciones que se retendrá mensualmente'
        ]
      },
      vacaciones: {
        titulo: 'Vacaciones del Mes',
        descripcion: 'Provisión mensual para vacaciones. Se retiene del Bruto+V y se acumula para el último mes.',
        formula: '(Días naturales × 30 / 360) × Bruto+V / Días naturales = 8.33%',
        notas: [
          '8.33% corresponde a 30/360 del salario (30 días de vacaciones / 360 días año)',
          'Se acumula y se paga al finalizar el contrato (último mes)',
          'Se descuenta del Bruto+V para obtener el Bruto real'
        ]
      },
      bruto: {
        titulo: 'Bruto (sin Vacaciones)',
        descripcion: 'Importe bruto real después de descontar las vacaciones. Es la base para calcular la SS.',
        formula: 'Bruto+V - Vacaciones',
        notas: [
          'Es el importe que se paga efectivamente al trabajador cada mes',
          'Las vacaciones se retienen y acumulan para el pago final',
          'Sirve como base de cotización para la Seguridad Social'
        ]
      },
      ss: {
        titulo: 'Seguridad Social',
        descripcion: 'Coste de la Seguridad Social a cargo de la empresa sobre el Bruto.',
        formula: 'Bruto × 32.07%',
        notas: [
          '32.07% incluye: contingencias comunes, desempleo, FOGASA y formación profesional',
          'Se calcula sobre el Bruto (sin vacaciones)',
          'Este es el coste adicional para la empresa sobre el salario'
        ]
      },
      total: {
        titulo: 'Total a Pagar',
        descripcion: 'Coste total de la liquidación para la empresa, incluyendo salario y cargas sociales.',
        formula: 'Bruto + Importe SS',
        notas: [
          'Representa el coste real para la empresa',
          'No incluye las vacaciones porque se pagan aparte al finalizar',
          'Es la suma del Bruto más la SS empresa'
        ]
      },
      estado: {
        titulo: 'Estado del Contrato',
        descripcion: 'Estado actual del workflow del Job Offer o Modificación RRHH.',
        notas: [
          'Alta: El contrato está activo actualmente',
          'Baja: El contrato ha finalizado',
          'Accepted: Job Offer aceptado pero sin procesar alta',
          'Los documentos en Baja se incluyen si su periodo coincide con el mes'
        ]
      }
    }
    
    const mostrarAyuda = (campo) => {
      ayudaActual.value = ayudaColumnas[campo] || null
      if (ayudaActual.value) {
        showAyudaModal.value = true
      }
    }
    
    const mostrarExplicacion = (item, campo) => {
      const explicaciones = {
        docente: {
          titulo: `Docente: ${item.employee_name}`,
          descripcion: 'Información del empleado asignado a esta formación.',
          valor: item.employee_name,
          desglose: [
            { concepto: 'ID Empleado', valor: item.employee },
            { concepto: 'DNI/NIE', valor: item.dni_nie },
            { concepto: 'Cargo', valor: item.designation },
            { concepto: 'Empresa', valor: item.company }
          ],
          origen: `Employee → ${item.employee}`
        },
        course: {
          titulo: `Curso`,
          descripcion: 'Acción formativa vinculada al docente para este periodo.',
          valor: item.course,
          desglose: [
            { concepto: 'Documento Origen', valor: item.source_type },
            { concepto: 'ID Documento', valor: item.source_doc },
            { concepto: 'Fecha Inicio', valor: item.fecha_inicio || 'N/A' },
            { concepto: 'Fecha Fin', valor: item.fecha_fin || 'N/A' }
          ],
          origen: `${item.source_type} → ${item.source_doc} → Tabla de Cursos`
        },
        horas: {
          titulo: 'Cálculo de Horas',
          descripcion: 'Las horas se calculan sumando los tramos horarios de cada día lectivo del calendario del curso.',
          formula: 'Σ (hora_fin - hora_inicio) por cada tramo de cada día lectivo',
          valor: `${formatNumber(item.total_horas)} horas`,
          desglose: [
            { concepto: 'Horas Normales', valor: `${formatNumber(item.horas_normales)}h` },
            { concepto: 'Horas Extras', valor: `${formatNumber(item.horas_extras)}h` },
            { concepto: 'Días Trabajados', valor: `${item.dias_trabajados} días` },
            { concepto: 'Media horas/día', valor: item.dias_trabajados > 0 ? `${formatNumber(item.horas_normales / item.dias_trabajados)}h` : 'N/A' }
          ],
          origen: `Course → ${item.course} → custom_calendario_curso`
        },
        brutoV: {
          titulo: 'Bruto+V (con Vacaciones)',
          descripcion: 'Importe total calculado por horas trabajadas. Incluye la parte proporcional de vacaciones que se retendrá.',
          formula: '(Horas × Precio/Hora) + (H.Extras × Precio H.Extra)',
          valor: formatCurrency(item.bruto),
          desglose: [
            { concepto: `${formatNumber(item.horas_normales)}h × ${formatCurrency(item.precio_hora)}`, valor: formatCurrency(item.importe_horas_normales) },
            { concepto: `${formatNumber(item.horas_extras)}h × ${formatCurrency(item.precio_hora_extra)}`, valor: formatCurrency(item.importe_horas_extras || 0) },
            { concepto: 'BRUTO+V', valor: formatCurrency(item.bruto) }
          ],
          origen: `Precio/hora del ${item.source_type}`
        },
        bruto: {
          titulo: 'Bruto (sin Vacaciones)',
          descripcion: 'Importe bruto real después de descontar las vacaciones. Es la base para calcular la SS y el pago mensual.',
          formula: 'Bruto+V - Vacaciones',
          valor: formatCurrency(item.bruto_menos_vacaciones),
          desglose: [
            { concepto: 'Bruto+V', valor: formatCurrency(item.bruto) },
            { concepto: '- Vacaciones (8.33%)', valor: `-${formatCurrency(item.vacaciones_mes)}` },
            { concepto: 'BRUTO', valor: formatCurrency(item.bruto_menos_vacaciones) }
          ],
          origen: 'Cálculo automático'
        },
        vacaciones: {
          titulo: 'Cálculo de Vacaciones',
          descripcion: 'Provisión mensual para vacaciones (8.33% del Bruto+V). Se acumula y se paga en el último mes.',
          formula: '(Días naturales × 30 / 360) × Bruto+V / Días naturales = 8.33%',
          valor: formatCurrency(item.vacaciones_mes),
          desglose: [
            { concepto: 'Bruto+V', valor: formatCurrency(item.bruto) },
            { concepto: 'Porcentaje Vacaciones', valor: '8.33%' },
            { concepto: `${formatCurrency(item.bruto)} × 0.0833`, valor: formatCurrency(item.vacaciones_mes) },
            { concepto: 'Vacaciones Acumuladas', valor: formatCurrency(item.vacaciones_acumuladas || 0) }
          ],
          origen: 'Cálculo automático (30/360 del salario)'
        },
        ss: {
          titulo: 'Cálculo Seguridad Social',
          descripcion: 'Coste de SS a cargo de la empresa sobre el Bruto (sin vacaciones).',
          formula: 'Bruto × 32.07%',
          valor: formatCurrency(item.importe_ss),
          desglose: [
            { concepto: 'Bruto (sin vacaciones)', valor: formatCurrency(item.bruto_menos_vacaciones || item.base_ss) },
            { concepto: 'Tipo SS Empresa', valor: '32.07%' },
            { concepto: 'Importe SS', valor: formatCurrency(item.importe_ss) }
          ],
          origen: 'Cálculo automático según legislación vigente'
        },
        total: {
          titulo: 'Total a Pagar',
          descripcion: 'Coste total de la liquidación: Bruto (sin vacaciones) más la Seguridad Social a cargo de la empresa.',
          formula: 'Bruto + Importe SS',
          valor: formatCurrency(item.total),
          desglose: [
            { concepto: 'Bruto (sin vacaciones)', valor: formatCurrency(item.bruto_menos_vacaciones || item.base_ss) },
            { concepto: '+ Seguridad Social Empresa', valor: formatCurrency(item.importe_ss) },
            { concepto: 'TOTAL A PAGAR', valor: formatCurrency(item.total) }
          ],
          origen: 'Cálculo automático'
        },
        estado: {
          titulo: 'Estado del Documento',
          descripcion: `Estado actual del ${item.source_type} en el sistema.`,
          valor: item.workflow_state || 'N/A',
          desglose: [
            { concepto: 'Tipo Documento', valor: item.source_type },
            { concepto: 'ID Documento', valor: item.source_doc },
            { concepto: 'Workflow State', valor: item.workflow_state || 'N/A' },
            { concepto: 'Fecha Inicio', valor: item.fecha_inicio || 'N/A' },
            { concepto: 'Fecha Fin', valor: item.fecha_fin || 'N/A' }
          ],
          origen: `${item.source_type} → workflow_state`
        }
      }
      
      explicacionActual.value = explicaciones[campo] || null
      if (explicacionActual.value) {
        showExplicacionModal.value = true
      }
    }
    
    function getMesActual() {
      const meses = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
      ]
      return meses[new Date().getMonth()]
    }
    
    // ============================================
    // MÉTODOS INCENTIVOS
    // ============================================
    
    const cargarIncentivos = async () => {
      loadingIncentivos.value = true
      try {
        // Construir filtros como array para soportar operadores
        const filters_array = []
        
        // Filtro por estado
        if (filtrosIncentivos.value.estado) {
          if (filtrosIncentivos.value.estado === 'Draft') {
            filters_array.push(['docstatus', '=', 0])
          } else if (filtrosIncentivos.value.estado === 'Approved') {
            filters_array.push(['docstatus', '=', 1])
          } else if (filtrosIncentivos.value.estado === 'Rejected') {
            filters_array.push(['workflow_state', '=', 'Rejected'])
          }
        }
        
        // Filtro por empleado (búsqueda parcial)
        if (filtrosIncentivos.value.employee && filtrosIncentivos.value.employee.trim()) {
          filters_array.push(['employee_name', 'like', `%${filtrosIncentivos.value.employee.trim()}%`])
        }
        
        // Filtro por fecha desde
        if (filtrosIncentivos.value.desde) {
          filters_array.push(['payroll_date', '>=', filtrosIncentivos.value.desde])
        }
        
        // Filtro por fecha hasta
        if (filtrosIncentivos.value.hasta) {
          filters_array.push(['payroll_date', '<=', filtrosIncentivos.value.hasta])
        }
        
        const result = await call('frappe.client.get_list', {
          doctype: 'Employee Incentive',
          filters: filters_array,
          fields: [
            'name', 'employee', 'employee_name', 'department', 'company',
            'salary_component', 'incentive_amount', 'payroll_date',
            'custom_provincia', 'custom_by_hours', 'custom_incentive_hours',
            'custom_justificación', 'docstatus', 'workflow_state'
          ],
          order_by: 'payroll_date desc',
          limit_page_length: 100
        })
        
        incentivos.value = result || []
        
        // Calcular resumen
        let totalImporte = 0
        let pendientes = 0
        for (const inc of incentivos.value) {
          if (!inc.custom_by_hours) {
            totalImporte += inc.incentive_amount || 0
          }
          if (inc.docstatus === 0) {
            pendientes++
          }
        }
        resumenIncentivos.value = {
          total_importe: totalImporte,
          pendientes: pendientes
        }
        
      } catch (error) {
        console.error('Error cargando incentivos:', error)
        showToast('Error al cargar incentivos', 'error')
      } finally {
        loadingIncentivos.value = false
      }
    }
    
    const cargarSalaryComponents = async () => {
      try {
        const result = await call('frappe.client.get_list', {
          doctype: 'Salary Component',
          filters: { type: 'Earning' },
          fields: ['name'],
          limit_page_length: 0
        })
        salaryComponents.value = result || []
      } catch (error) {
        console.error('Error cargando componentes:', error)
      }
    }
    
    const nuevoIncentivo = async () => {
      await cargarSalaryComponents()
      incentivoEditando.value = null
      incentivoForm.value = {
        employee: '',
        employee_name: '',
        employee_search: '',
        custom_provincia: '',
        salary_component: '',
        payroll_date: new Date().toISOString().split('T')[0],
        incentive_amount: 0,
        custom_by_hours: false,
        custom_incentive_hours: '',
        custom_justificación: ''
      }
      empleadosSugeridos.value = []
      showIncentivoModal.value = true
    }
    
    const editarIncentivo = async (inc) => {
      await cargarSalaryComponents()
      incentivoEditando.value = inc.name
      incentivoForm.value = {
        employee: inc.employee,
        employee_name: inc.employee_name,
        employee_search: inc.employee_name,
        custom_provincia: inc.custom_provincia || '',
        salary_component: inc.salary_component,
        payroll_date: inc.payroll_date,
        incentive_amount: inc.incentive_amount,
        custom_by_hours: inc.custom_by_hours,
        custom_incentive_hours: inc.custom_incentive_hours || '',
        custom_justificación: inc.custom_justificación || ''
      }
      empleadosSugeridos.value = []
      showIncentivoModal.value = true
    }
    
    const buscarEmpleados = async () => {
      const search = incentivoForm.value.employee_search
      if (!search || search.length < 2) {
        empleadosSugeridos.value = []
        return
      }
      
      try {
        const result = await call('frappe.client.get_list', {
          doctype: 'Employee',
          filters: [['employee_name', 'like', `%${search}%`]],
          fields: ['name', 'employee_name', 'department'],
          limit_page_length: 10
        })
        empleadosSugeridos.value = result || []
      } catch (error) {
        console.error('Error buscando empleados:', error)
      }
    }
    
    const seleccionarEmpleadoIncentivo = (emp) => {
      incentivoForm.value.employee = emp.name
      incentivoForm.value.employee_name = emp.employee_name
      incentivoForm.value.employee_search = emp.employee_name
      empleadosSugeridos.value = []
    }
    
    const guardarIncentivo = async () => {
      if (!incentivoForm.value.employee || !incentivoForm.value.salary_component) {
        showToast('Completa los campos requeridos', 'warning')
        return
      }
      
      guardandoIncentivo.value = true
      try {
        if (incentivoEditando.value) {
          await call('frappe.client.set_value', {
            doctype: 'Employee Incentive',
            name: incentivoEditando.value,
            fieldname: {
              salary_component: incentivoForm.value.salary_component,
              payroll_date: incentivoForm.value.payroll_date,
              incentive_amount: incentivoForm.value.incentive_amount,
              custom_provincia: incentivoForm.value.custom_provincia,
              custom_by_hours: incentivoForm.value.custom_by_hours ? 1 : 0,
              custom_incentive_hours: incentivoForm.value.custom_incentive_hours,
              custom_justificación: incentivoForm.value.custom_justificación
            }
          })
          showToast('Incentivo actualizado', 'success')
        } else {
          await call('frappe.client.insert', {
            doc: {
              doctype: 'Employee Incentive',
              employee: incentivoForm.value.employee,
              salary_component: incentivoForm.value.salary_component,
              payroll_date: incentivoForm.value.payroll_date,
              incentive_amount: incentivoForm.value.incentive_amount,
              custom_provincia: incentivoForm.value.custom_provincia,
              custom_by_hours: incentivoForm.value.custom_by_hours ? 1 : 0,
              custom_incentive_hours: incentivoForm.value.custom_incentive_hours,
              custom_justificación: incentivoForm.value.custom_justificación
            }
          })
          showToast('Incentivo creado', 'success')
        }
        
        showIncentivoModal.value = false
        await cargarIncentivos()
        
      } catch (error) {
        console.error('Error guardando incentivo:', error)
        showToast('Error al guardar el incentivo', 'error')
      } finally {
        guardandoIncentivo.value = false
      }
    }
    
    const abrirIncentivo = (name) => {
      window.open(`/app/employee-incentive/${name}`, '_blank')
    }
    
    const getIncentivoEstadoBadge = (docstatus, workflow_state) => {
      if (workflow_state === 'Approved' || docstatus === 1) return 'green'
      if (workflow_state === 'Rejected') return 'red'
      return 'gray'
    }
    
    const getIncentivoEstadoLabel = (docstatus, workflow_state) => {
      if (workflow_state) return workflow_state
      if (docstatus === 0) return 'Borrador'
      if (docstatus === 1) return 'Enviado'
      if (docstatus === 2) return 'Cancelado'
      return 'Desconocido'
    }
    
    const formatDuration = (duration) => {
      if (!duration) return '-'
      return duration
    }
    
    const limpiarFiltrosIncentivos = () => {
      filtrosIncentivos.value = {
        estado: '',
        employee: '',
        desde: getFechaHaceMeses(2),
        hasta: getHoy()
      }
      cargarIncentivos()
    }
    
    // ============================================
    // MÉTODOS GASTOS
    // ============================================
    
    const cargarGastos = async () => {
      loadingGastos.value = true
      try {
        // Construir filtros como array para soportar operadores
        const filters_array = []
        
        // Filtro por estado
        if (filtrosGastos.value.estado) {
          filters_array.push(['status', '=', filtrosGastos.value.estado])
        }
        
        // Filtro por empleado (búsqueda parcial)
        if (filtrosGastos.value.employee && filtrosGastos.value.employee.trim()) {
          filters_array.push(['employee_name', 'like', `%${filtrosGastos.value.employee.trim()}%`])
        }
        
        // Filtro por fecha desde
        if (filtrosGastos.value.desde) {
          filters_array.push(['posting_date', '>=', filtrosGastos.value.desde])
        }
        
        // Filtro por fecha hasta
        if (filtrosGastos.value.hasta) {
          filters_array.push(['posting_date', '<=', filtrosGastos.value.hasta])
        }
        
        const result = await call('frappe.client.get_list', {
          doctype: 'Expense Claim',
          filters: filters_array,
          fields: [
            'name', 'employee', 'employee_name', 'department', 'company',
            'posting_date', 'total_claimed_amount', 'total_sanctioned_amount',
            'approval_status', 'status', 'docstatus', 'remark'
          ],
          order_by: 'posting_date desc',
          limit_page_length: 100
        })
        
        gastos.value = result || []
        
        // Calcular resumen
        let totalReclamado = 0
        let totalAprobado = 0
        let pendientes = 0
        for (const gasto of gastos.value) {
          totalReclamado += gasto.total_claimed_amount || 0
          totalAprobado += gasto.total_sanctioned_amount || 0
          if (gasto.status === 'Draft' || gasto.approval_status === 'Draft') {
            pendientes++
          }
        }
        resumenGastos.value = {
          total_reclamado: totalReclamado,
          total_aprobado: totalAprobado,
          pendientes: pendientes
        }
        
      } catch (error) {
        console.error('Error cargando gastos:', error)
        showToast('Error al cargar gastos', 'error')
      } finally {
        loadingGastos.value = false
      }
    }
    
    const cargarExpenseTypes = async () => {
      try {
        const result = await call('frappe.client.get_list', {
          doctype: 'Expense Claim Type',
          fields: ['name'],
          limit_page_length: 0
        })
        expenseTypes.value = result || []
      } catch (error) {
        console.error('Error cargando tipos de gasto:', error)
      }
    }
    
    const limpiarFiltrosGastos = () => {
      filtrosGastos.value = {
        estado: '',
        employee: '',
        desde: getFechaHaceMeses(2),
        hasta: getHoy()
      }
      cargarGastos()
    }
    
    const nuevoGasto = async () => {
      await cargarExpenseTypes()
      gastoEditando.value = null
      gastoForm.value = {
        employee: '',
        employee_name: '',
        employee_search: '',
        posting_date: new Date().toISOString().split('T')[0],
        expenses: [{ expense_type: '', description: '', amount: 0 }],
        remark: ''
      }
      empleadosSugeridosGasto.value = []
      showGastoModal.value = true
    }
    
    const editarGasto = async (gasto) => {
      await cargarExpenseTypes()
      gastoEditando.value = gasto.name
      
      // Cargar detalle completo
      const doc = await call('frappe.client.get', {
        doctype: 'Expense Claim',
        name: gasto.name
      })
      
      gastoForm.value = {
        employee: doc.employee,
        employee_name: doc.employee_name,
        employee_search: doc.employee_name,
        posting_date: doc.posting_date,
        expenses: (doc.expenses || []).map(e => ({
          expense_type: e.expense_type,
          description: e.description,
          amount: e.amount
        })),
        remark: doc.remark || ''
      }
      
      if (gastoForm.value.expenses.length === 0) {
        gastoForm.value.expenses = [{ expense_type: '', description: '', amount: 0 }]
      }
      
      empleadosSugeridosGasto.value = []
      showGastoModal.value = true
    }
    
    const verDetalleGasto = async (gasto) => {
      try {
        const doc = await call('frappe.client.get', {
          doctype: 'Expense Claim',
          name: gasto.name
        })
        gastoDetalle.value = doc
        showDetalleGastoModal.value = true
      } catch (error) {
        console.error('Error cargando detalle:', error)
        showToast('Error al cargar detalle', 'error')
      }
    }
    
    const buscarEmpleadosGasto = async () => {
      const search = gastoForm.value.employee_search
      if (!search || search.length < 2) {
        empleadosSugeridosGasto.value = []
        return
      }
      
      try {
        const result = await call('frappe.client.get_list', {
          doctype: 'Employee',
          filters: [['employee_name', 'like', `%${search}%`]],
          fields: ['name', 'employee_name', 'department'],
          limit_page_length: 10
        })
        empleadosSugeridosGasto.value = result || []
      } catch (error) {
        console.error('Error buscando empleados:', error)
      }
    }
    
    const seleccionarEmpleadoGasto = (emp) => {
      gastoForm.value.employee = emp.name
      gastoForm.value.employee_name = emp.employee_name
      gastoForm.value.employee_search = emp.employee_name
      empleadosSugeridosGasto.value = []
    }
    
    const agregarLineaGasto = () => {
      gastoForm.value.expenses.push({ expense_type: '', description: '', amount: 0 })
    }
    
    const eliminarLineaGasto = (idx) => {
      gastoForm.value.expenses.splice(idx, 1)
      if (gastoForm.value.expenses.length === 0) {
        gastoForm.value.expenses = [{ expense_type: '', description: '', amount: 0 }]
      }
    }
    
    const calcularTotalGasto = () => {
      return gastoForm.value.expenses.reduce((sum, e) => sum + (parseFloat(e.amount) || 0), 0)
    }
    
    const guardarGasto = async () => {
      if (!gastoForm.value.employee) {
        showToast('Selecciona un empleado', 'warning')
        return
      }
      
      const lineasValidas = gastoForm.value.expenses.filter(e => e.expense_type && e.amount > 0)
      if (lineasValidas.length === 0) {
        showToast('Añade al menos una línea de gasto', 'warning')
        return
      }
      
      guardandoGasto.value = true
      try {
        if (gastoEditando.value) {
          // Actualizar existente
          await call('frappe.client.set_value', {
            doctype: 'Expense Claim',
            name: gastoEditando.value,
            fieldname: {
              posting_date: gastoForm.value.posting_date,
              remark: gastoForm.value.remark
            }
          })
          showToast('Gasto actualizado', 'success')
        } else {
          // Crear nuevo
          await call('frappe.client.insert', {
            doc: {
              doctype: 'Expense Claim',
              employee: gastoForm.value.employee,
              posting_date: gastoForm.value.posting_date,
              expenses: lineasValidas.map(e => ({
                expense_type: e.expense_type,
                description: e.description,
                amount: parseFloat(e.amount) || 0
              })),
              remark: gastoForm.value.remark
            }
          })
          showToast('Gasto creado', 'success')
        }
        
        showGastoModal.value = false
        await cargarGastos()
        
      } catch (error) {
        console.error('Error guardando gasto:', error)
        showToast('Error al guardar el gasto', 'error')
      } finally {
        guardandoGasto.value = false
      }
    }
    
    const abrirGasto = (name) => {
      window.open(`/app/expense-claim/${name}`, '_blank')
    }
    
    const getApprovalBadge = (status) => {
      if (status === 'Approved') return 'green'
      if (status === 'Rejected') return 'red'
      return 'gray'
    }
    
    const getGastoEstadoBadge = (status) => {
      if (status === 'Paid') return 'green'
      if (status === 'Submitted' || status === 'Unpaid') return 'blue'
      if (status === 'Rejected' || status === 'Cancelled') return 'red'
      return 'gray'
    }
    
    const formatDate = (date) => {
      if (!date) return '-'
      return new Date(date).toLocaleDateString('es-ES')
    }
    
    // Lifecycle
    onMounted(() => {
      cargarDatos()
    })
    
    return {
      // Estado principal
      mainTab,
      loading,
      generandoExcel,
      generandoMasivo,
      guardandoEdicion,
      activeTab,
      filters,
      previsiones,
      liquidaciones,
      liquidacionesBorrador,
      borradoresSeleccionados,
      liquidacionesValidadas,
      resumen,
      seleccionadas,
      seleccionadasLiquidaciones,
      allPrevisionesSelected,
      allLiquidacionesSelected,
      showDetalleModal,
      showEnvioAsesoriaModal,
      liquidacionesParaEnvio,
      seleccionadasParaAsesoria,
      enviandoAsesoria,
      todasSeleccionadasAsesoria,
      detalleActual,
      showHorasExtrasModal,
      horasExtrasData,
      showPagoModal,
      fechaPago,
      showResultadoMasivoModal,
      resultadoMasivo,
      showExplicacionModal,
      explicacionActual,
      showAyudaModal,
      ayudaActual,
      showEdicionModal,
      edicionData,
      vacacionesInfo,
      toast,
      toastIcon,
      
      // Métodos Nóminas
      cargarDatos,
      limpiarFiltros,
      generarPrevisiones,
      liquidarSeleccionadas,
      generarTodasLiquidaciones,
      validarSeleccionadas,
      abrirEdicionLiquidacion,
      guardarEdicionLiquidacion,
      editarCampoLiquidacion,
      calcularBrutoPreview,
      calcularBaseSS,
      abrirEnvioAsesoria,
      toggleSelectAllAsesoria,
      calcularTotalAsesoria,
      calcularTotalHorasAsesoria,
      enviarAAsesoria,
      marcarComoPagado,
      confirmarPago,
      generarReporteExcel,
      verDetalle,
      agregarHorasExtras,
      guardarHorasExtras,
      toggleSelectAll,
      toggleSelectAllLiquidaciones,
      abrirLiquidacion,
      formatCurrency,
      formatNumber,
      getEstadoBadgeTheme,
      getWorkflowBadgeTheme,
      mostrarAyuda,
      mostrarExplicacion,
      getSourceDocUrl,
      
      // Estado Incentivos
      loadingIncentivos,
      guardandoIncentivo,
      incentivos,
      filtrosIncentivos,
      resumenIncentivos,
      showIncentivoModal,
      incentivoEditando,
      incentivoForm,
      salaryComponents,
      empleadosSugeridos,
      
      // Métodos Incentivos
      cargarIncentivos,
      limpiarFiltrosIncentivos,
      nuevoIncentivo,
      editarIncentivo,
      buscarEmpleados,
      seleccionarEmpleadoIncentivo,
      guardarIncentivo,
      abrirIncentivo,
      getIncentivoEstadoBadge,
      getIncentivoEstadoLabel,
      formatDuration,
      
      // Estado Gastos
      loadingGastos,
      guardandoGasto,
      gastos,
      filtrosGastos,
      resumenGastos,
      showGastoModal,
      showDetalleGastoModal,
      gastoEditando,
      gastoDetalle,
      gastoForm,
      expenseTypes,
      empleadosSugeridosGasto,
      
      // Métodos Gastos
      cargarGastos,
      limpiarFiltrosGastos,
      nuevoGasto,
      editarGasto,
      verDetalleGasto,
      buscarEmpleadosGasto,
      seleccionarEmpleadoGasto,
      agregarLineaGasto,
      eliminarLineaGasto,
      calcularTotalGasto,
      guardarGasto,
      abrirGasto,
      getApprovalBadge,
      getGastoEstadoBadge,
      formatDate
    }
  }
}
</script>

<style scoped>
.form-select {
  @apply block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
