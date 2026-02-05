<template>
  <div class="h-full bg-gray-50 flex flex-col overflow-hidden">

    <!-- Información sobre nuevo procedimiento -->
    <div class="mx-6 mt-4 mb-4">
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex items-start">
          <FeatherIcon name="info" class="h-5 w-5 text-blue-600 mr-3 mt-0.5 flex-shrink-0" />
          <div class="flex-1">
            <h4 class="text-sm font-semibold text-blue-900 mb-1">Nuevo Procedimiento de Creación</h4>
            <p class="text-sm text-blue-800">
              Este es el nuevo procedimiento para crear nuevas Hojas de Contratación (HC) y Anexos. 
              Por favor, utiliza esta página para crear todos los documentos relacionados con contratación, 
              asegurando que se vinculen correctamente al empleado correspondiente.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters Section -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 mx-6 mb-6 flex-shrink-0">
      <div class="px-4 py-3">
        <div class="flex items-center space-x-3">
          <!-- Búsqueda por Nombre -->
          <div class="flex-1">
            <Input
              v-model="searchFilters.employeeName"
              type="text"
              placeholder="Buscar por nombre..."
              variant="outline"
              size="sm"
            >
              <template #prefix>
                <FeatherIcon name="search" class="h-4 text-gray-400" />
              </template>
            </Input>
          </div>

          <!-- Búsqueda por DNI/NIE -->
          <div class="flex-1">
            <Input
              v-model="searchFilters.dninie"
              type="text"
              placeholder="Buscar por DNI/NIE..."
              variant="outline"
              size="sm"
            >
              <template #prefix>
                <FeatherIcon name="credit-card" class="h-4 text-gray-400" />
              </template>
            </Input>
          </div>

          <!-- Búsqueda por Provincia -->
          <div class="flex-1 relative">
            <div class="relative">
              <Input
                v-model="provinciaSearchText"
                type="text"
                placeholder="Buscar por provincia..."
                variant="outline"
                size="sm"
                @input="onProvinciaSearchInput"
                @focus="onProvinciaFocus"
                @blur="handleProvinciaBlur"
                @keydown.enter.prevent="handleProvinciaEnter"
                @keydown.escape="showProvinciaDropdown = false"
                @keydown.down.prevent="navigateProvinciaDropdown(1)"
                @keydown.up.prevent="navigateProvinciaDropdown(-1)"
              >
                <template #prefix>
                  <FeatherIcon name="map-pin" class="h-4 text-gray-400" />
                </template>
              </Input>
              <button
                v-if="searchFilters.provincia"
                @click="clearProvincia"
                class="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                type="button"
              >
                <FeatherIcon name="x" class="h-4" />
              </button>
            </div>
            <!-- Dropdown con opciones filtradas -->
            <div
              v-if="showProvinciaDropdown && filteredProvincias.length > 0"
              class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto"
            >
              <div class="p-2">
                <div class="text-xs text-gray-500 px-2 py-1 mb-1 font-semibold">
                  Seleccionar provincia ({{ filteredProvincias.length }} resultados):
                </div>
                <div
                  v-for="(provincia, index) in filteredProvincias"
                  :key="provincia"
                  @mousedown.prevent="selectProvincia(provincia)"
                  :class="[
                    'px-4 py-2 cursor-pointer border-b border-gray-100 last:border-b-0',
                    index === highlightedProvinciaIndex ? 'bg-blue-100' : 'hover:bg-blue-50'
                  ]"
                >
                  <div class="font-medium text-gray-900">{{ provincia }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Búsqueda por Empresa -->
          <div class="flex-1 relative">
            <div class="relative">
              <Input
                v-model="companySearchText"
                type="text"
                placeholder="Buscar por empresa..."
                variant="outline"
                size="sm"
                @input="onCompanySearchInput"
                @focus="onCompanyFocus"
                @blur="handleCompanyBlur"
                @keydown.enter.prevent="handleCompanyEnter"
                @keydown.escape="showCompanyDropdown = false"
                @keydown.down.prevent="navigateCompanyDropdown(1)"
                @keydown.up.prevent="navigateCompanyDropdown(-1)"
              >
                <template #prefix>
                  <FeatherIcon name="building" class="h-4 text-gray-400" />
                </template>
              </Input>
              <button
                v-if="searchFilters.company"
                @click="clearCompany"
                class="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                type="button"
              >
                <FeatherIcon name="x" class="h-4" />
              </button>
            </div>
            <!-- Dropdown con opciones filtradas -->
            <div
              v-if="showCompanyDropdown && filteredCompanies.length > 0"
              class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto"
            >
              <div class="p-2">
                <div class="text-xs text-gray-500 px-2 py-1 mb-1 font-semibold">
                  Seleccionar empresa ({{ filteredCompanies.length }} resultados):
                </div>
                <div
                  v-for="(company, index) in filteredCompanies"
                  :key="company"
                  @mousedown.prevent="selectCompany(company)"
                  :class="[
                    'px-4 py-2 cursor-pointer border-b border-gray-100 last:border-b-0',
                    index === highlightedCompanyIndex ? 'bg-blue-100' : 'hover:bg-blue-50'
                  ]"
                >
                  <div class="font-medium text-gray-900">{{ company }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Búsqueda por Responsable -->
          <div class="flex-1 relative">
            <div class="relative">
              <Input
                v-model="reportsToSearchText"
                type="text"
                placeholder="Buscar por responsable..."
                variant="outline"
                size="sm"
                @input="onReportsToSearchInput"
                @focus="onReportsToFocus"
                @blur="handleReportsToBlur"
                @keydown.enter.prevent="handleReportsToEnter"
                @keydown.escape="showReportsToDropdown = false"
                @keydown.down.prevent="navigateReportsToDropdown(1)"
                @keydown.up.prevent="navigateReportsToDropdown(-1)"
              >
                <template #prefix>
                  <FeatherIcon name="user" class="h-4 text-gray-400" />
                </template>
              </Input>
              <button
                v-if="searchFilters.reportsTo"
                @click="clearReportsTo"
                class="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                type="button"
              >
                <FeatherIcon name="x" class="h-4" />
              </button>
            </div>
            <!-- Dropdown con opciones filtradas -->
            <div
              v-if="showReportsToDropdown && filteredReportsTo.length > 0"
              class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto"
            >
              <div class="p-2">
                <div class="text-xs text-gray-500 px-2 py-1 mb-1 font-semibold">
                  Seleccionar responsable ({{ filteredReportsTo.length }} resultados):
                </div>
                <div
                  v-for="(reportsTo, index) in filteredReportsTo"
                  :key="reportsTo.value"
                  @mousedown.prevent="selectReportsTo(reportsTo)"
                  :class="[
                    'px-4 py-2 cursor-pointer border-b border-gray-100 last:border-b-0',
                    index === highlightedReportsToIndex ? 'bg-blue-100' : 'hover:bg-blue-50'
                  ]"
                >
                  <div class="font-medium text-gray-900">{{ reportsTo.label }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Botón Limpiar Filtros -->
          <div class="flex-shrink-0">
            <Button
              variant="outline"
              size="sm"
              @click="clearFilters"
              :disabled="!hasActiveFilters"
            >
              <FeatherIcon name="x" class="h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Employee Management Section -->
    <div class="flex gap-6 px-6 pb-6 flex-1 min-h-0 overflow-hidden">
      <!-- Left Column: Employee List -->
      <div
        class="bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col h-full overflow-hidden"
        :class="isEmployeeListCollapsed ? 'w-64' : 'w-1/3'"
      >
        <div class="px-4 py-3 border-b border-gray-200 flex-shrink-0">
          <div v-if="isEmployeeListCollapsed && selectedEmployee" class="flex items-center justify-between">
            <div class="flex-1 min-w-0">
              <h3 class="text-sm font-medium text-gray-900 truncate">{{ selectedEmployee.employee_name }}</h3>
              <p class="text-xs text-gray-500 truncate">{{ selectedEmployee.custom_dninie }}</p>
            </div>
            <button
              @click="expandEmployeeList"
              class="ml-2 p-1 text-gray-400"
              title="Mostrar todos los empleados"
            >
              <FeatherIcon name="maximize-2" class="h-4 w-4" />
            </button>
          </div>
          <div v-else class="flex items-center justify-between w-full">
            <h3 class="text-sm font-medium text-gray-900">Empleados</h3>
            <div class="flex items-center space-x-2">
              <span class="text-xs text-gray-500">
                {{ filteredEmployees.length }}{{ isLoadingMore ? '+' : '' }} de {{ totalEmployees }}
              </span>
              <FeatherIcon v-if="isLoadingMore" name="loader" class="h-3 w-3 animate-spin text-blue-500" />
            </div>
          </div>
        </div>
        <div class="overflow-y-auto flex-1">
          <div v-if="loadingEmployees" class="p-4 text-center text-gray-500">
            <FeatherIcon name="loader" class="h-6 w-6 animate-spin mx-auto mb-2" />
            Cargando empleados...
          </div>
          <div v-else-if="!filteredEmployees || filteredEmployees.length === 0" class="p-4 text-center text-gray-500">
            No hay empleados disponibles
          </div>
          <div v-else-if="isEmployeeListCollapsed && selectedEmployee" class="p-2">
            <!-- Mostrar solo el empleado seleccionado cuando está colapsada -->
            <div class="bg-blue-50 rounded-lg p-3 border border-blue-200">
              <div class="flex items-start justify-between">
                <div class="flex items-center space-x-3 flex-1 min-w-0">
                  <div class="flex-shrink-0 h-8 w-8">
                    <div class="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                      <span class="text-xs font-semibold text-blue-700">
                        {{ getInitials(selectedEmployee.employee_name) }}
                      </span>
                    </div>
                  </div>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 truncate">
                      {{ selectedEmployee.employee_name || 'Sin nombre' }}
                    </p>
                    <p class="text-xs text-gray-600 truncate">
                      {{ selectedEmployee.custom_dninie || selectedEmployee.name || 'Sin DNI' }}
                    </p>
                    <p class="text-xs text-gray-500 truncate">
                      {{ selectedEmployee.designation || 'Sin puesto' }}
                    </p>
                    <a
                      v-if="selectedEmployee.name"
                      @click="openFormInNewTab('Employee', selectedEmployee.name, $event)"
                      class="text-xs text-blue-600 hover:text-blue-800 hover:underline font-mono cursor-pointer inline-block mt-1"
                      title="Ver detalle del empleado"
                    >
                      ID: {{ selectedEmployee.name }}
                    </a>
                    <div v-if="selectedEmployee.companies && selectedEmployee.companies.length > 0" class="text-xs text-gray-600">
                      <div class="font-medium text-gray-700 mb-1">{{ selectedEmployee.status_text }}</div>
                      <div v-for="company in selectedEmployee.companies" :key="company" class="truncate">
                        {{ company }}
                      </div>
                    </div>
                    <div v-else class="text-xs text-gray-500">
                      {{ selectedEmployee.status_text }}
                    </div>
                  </div>
                </div>
                <div class="flex-shrink-0 ml-3">
                  <div
                    v-if="selectedEmployee.status === 'Alta'"
                    class="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium"
                  >
                    {{ selectedEmployee.status }}
                  </div>
                  <div
                    v-else-if="selectedEmployee.status === 'Baja'"
                    class="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-medium"
                  >
                    {{ selectedEmployee.status }}
                  </div>
                  <div
                    v-else
                    class="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-medium"
                  >
                    {{ selectedEmployee.status }}
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="divide-y divide-gray-200">
            <div
              v-for="employee in filteredEmployees"
              :key="employee.name"
              @click="selectEmployee(employee)"
              class="p-3 cursor-pointer"
              :class="{
                'bg-blue-50 border-r-2 border-blue-500': selectedEmployee?.name === employee.name,
                'opacity-50': isLoadingJobOffers && selectedEmployee?.name === employee.name
              }"
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
                      {{ employee.custom_dninie || employee.name || 'Sin DNI' }}
                    </p>
                    <p class="text-xs text-gray-500 truncate">
                      {{ employee.designation || 'Sin puesto' }}
                    </p>
                    <a
                      v-if="employee.name"
                      @click="openFormInNewTab('Employee', employee.name, $event)"
                      class="text-xs text-blue-600 hover:text-blue-800 hover:underline font-mono cursor-pointer inline-block mt-1"
                      title="Ver detalle del empleado"
                    >
                      ID: {{ employee.name }}
                    </a>
                    <div v-if="employee.companies && employee.companies.length > 0" class="text-xs text-gray-600">
                      <div class="font-medium text-gray-700 mb-1">{{ employee.status_text }}</div>
                      <div v-for="company in employee.companies" :key="company" class="truncate">
                        {{ company }}
                      </div>
                    </div>
                    <div v-else class="text-xs text-gray-500">
                      {{ employee.status_text }}
                    </div>
                  </div>
                </div>

           <!-- Estado en la parte superior derecha -->
                <div class="flex-shrink-0 ml-3">
             <div
               v-if="employee.status === 'Alta'"
               class="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium"
             >
               {{ employee.status }}
                    </div>
                    <div
               v-else-if="employee.status === 'Baja'"
               class="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-medium"
                    >
               {{ employee.status }}
                    </div>
             <div
               v-else
               class="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-medium"
             >
               {{ employee.status }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Hojas de Contratación -->
      <div class="flex-1 bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col h-full overflow-hidden">
        <div class="px-4 py-3 border-b border-gray-200 flex-shrink-0 flex items-center justify-between">
          <h3 class="text-sm font-medium text-gray-900">
            {{ selectedEmployee ? `Hojas de Contratación - ${selectedEmployee.employee_name}` : 'Selecciona un empleado' }}
          </h3>
          <div v-if="selectedEmployee" class="flex items-center space-x-2">
            <button
              @click="createNewJobOffer"
              class="flex items-center space-x-2 px-3 py-1.5 text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
              title="Crear nueva HC para este empleado"
            >
              <FeatherIcon name="plus" class="h-4 w-4" />
              <span>Nueva HC</span>
            </button>
            <button
              v-if="isEmployeeListCollapsed"
              @click="expandEmployeeList"
              class="flex items-center space-x-2 px-3 py-1.5 text-xs font-medium text-blue-600 bg-blue-50 rounded-md"
            >
              <FeatherIcon name="users" class="h-4 w-4" />
              <span>Mostrar empleados</span>
            </button>
          </div>
        </div>
        <div class="overflow-y-auto flex-1">
          <div v-if="!selectedEmployee" class="p-8 text-center text-gray-500">
            <FeatherIcon name="user" class="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>Selecciona un empleado para ver sus Hojas de Contratación</p>
          </div>
          <div v-else-if="isLoadingJobOffers" class="p-8 text-center text-gray-500">
            <FeatherIcon name="loader" class="h-8 w-8 animate-spin mx-auto mb-4" />
            <p class="text-sm">Cargando Hojas de Contratación...</p>
            <p class="text-xs text-gray-400 mt-2">Por favor espera...</p>
          </div>
          <div v-else-if="!filteredJobOffers || filteredJobOffers.length === 0" class="p-4 text-center text-gray-500">
            <FeatherIcon name="file-text" class="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>No hay Hojas de Contratación para este empleado</p>
            <p v-if="hasJobOfferFilters" class="text-xs text-gray-400 mt-2">Intenta ajustar los filtros de provincia o empresa</p>
          </div>
          <div v-else class="divide-y divide-gray-200">
            <div
              v-for="jobOffer in filteredJobOffers"
              :key="jobOffer.name"
              class="p-4 border-l-4 border-transparent"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center space-x-3 mb-3">
                    <div class="flex-1">
                      <div class="flex items-center space-x-2">
                        <h4 class="text-base font-semibold text-gray-900">{{ jobOffer.designation || 'Sin título' }}</h4>
                        <button
                          v-if="jobOffer.name"
                          @click="createNewModificacionRRHH(jobOffer.name, $event)"
                          class="flex items-center space-x-1 px-2 py-1 text-xs font-medium text-white bg-green-600 hover:bg-green-700 rounded-md transition-colors"
                          title="Crear nuevo anexo para esta hoja de contratación"
                        >
                          <FeatherIcon name="plus" class="h-3 w-3" />
                          <span>Nuevo Anexo</span>
                        </button>
                      </div>
                      <a
                        v-if="jobOffer.name"
                        @click="openFormInNewTab('Job Offer', jobOffer.name, $event)"
                        class="text-sm text-blue-600 hover:text-blue-800 hover:underline font-mono cursor-pointer inline-block"
                        title="Ver detalle de la hoja de contratación"
                      >
                        ID: {{ jobOffer.name }}
                      </a>
                      <p v-else class="text-sm text-gray-500 font-mono">ID: Sin ID</p>
                    </div>
                    <div
                      v-if="jobOffer.workflow_state === 'Alta'"
                      class="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium"
                    >
                      {{ jobOffer.workflow_state }}
                    </div>
                    <div
                      v-else-if="jobOffer.workflow_state === 'Baja'"
                      class="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-medium"
                    >
                      {{ jobOffer.workflow_state }}
                    </div>
                    <div
                      v-else-if="jobOffer.workflow_state === 'Pendiente'"
                      class="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-medium"
                    >
                      {{ jobOffer.workflow_state }}
                    </div>
                    <div
                      v-else-if="jobOffer.workflow_state === 'Cancelado'"
                      class="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-medium"
                    >
                      {{ jobOffer.workflow_state }}
                    </div>
                    <div
                      v-else
                      class="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-medium"
                    >
                      {{ jobOffer.workflow_state || 'Sin estado' }}
                    </div>
                  </div>

                  <!-- Información principal del Job Offer -->
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
                    <div class="space-y-2">
                      <div class="flex items-center space-x-2 text-sm">
                        <FeatherIcon name="calendar" class="h-4 w-4 text-gray-400" />
                        <span class="text-gray-600">Fecha de oferta:</span>
                        <span class="font-medium text-gray-900">
                          {{ jobOffer.offer_date ? formatDate(jobOffer.offer_date) : 'No especificada' }}
                        </span>
                      </div>

                      <div class="flex items-center space-x-2 text-sm">
                        <FeatherIcon name="building" class="h-4 w-4 text-gray-400" />
                        <span class="text-gray-600">Empresa:</span>
                        <span class="font-medium text-gray-900">{{ jobOffer.company || 'No especificada' }}</span>
                      </div>

                      <div v-if="jobOffer.custom_tipo_de_contrato" class="flex items-center space-x-2 text-sm">
                        <FeatherIcon name="file-text" class="h-4 w-4 text-gray-400" />
                        <span class="text-gray-600">Tipo de contrato:</span>
                        <span class="font-medium text-gray-900">{{ jobOffer.custom_tipo_de_contrato }}</span>
                      </div>
                    </div>

                    <div class="space-y-2">
                      <div v-if="jobOffer.custom_fecha_inicio" class="flex items-center space-x-2 text-sm">
                        <FeatherIcon name="play" class="h-4 w-4 text-gray-400" />
                        <span class="text-gray-600">Inicio:</span>
                        <span class="font-medium text-gray-900">{{ formatDate(jobOffer.custom_fecha_inicio) }}</span>
                      </div>

                      <div v-if="jobOffer.custom_fecha_fin" class="flex items-center space-x-2 text-sm">
                        <FeatherIcon name="stop" class="h-4 w-4 text-gray-400" />
                        <span class="text-gray-600">Fin:</span>
                        <span class="font-medium text-gray-900">{{ formatDate(jobOffer.custom_fecha_fin) }}</span>
                      </div>

                      <div v-if="jobOffer.custom_estado_de_tramitacion" class="flex items-center space-x-2 text-sm">
                        <FeatherIcon name="settings" class="h-4 w-4 text-gray-400" />
                        <span class="text-gray-600">Tramitación:</span>
                        <span class="font-medium text-gray-900">{{ jobOffer.custom_estado_de_tramitacion }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- Información adicional -->
                  <div class="flex flex-wrap gap-2 text-xs">
                    <div v-if="jobOffer.custom_firmado" class="flex items-center space-x-1 px-2 py-1 bg-green-100 text-green-800 rounded-full">
                      <FeatherIcon name="check" class="h-3 w-3" />
                      <span>Firmado</span>
                    </div>
                    <div v-if="jobOffer.custom_contrato" class="flex items-center space-x-1 px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
                      <FeatherIcon name="file" class="h-3 w-3" />
                      <span>Contrato</span>
                    </div>
                    <div v-if="jobOffer.custom_comun" class="flex items-center space-x-1 px-2 py-1 bg-purple-100 text-purple-800 rounded-full">
                      <FeatherIcon name="users" class="h-3 w-3" />
                      <span>Común</span>
                    </div>
                  </div>
                </div>

                <!-- Modificaciones RRHH -->
                <div v-if="getModificacionesForJobOffer(jobOffer.name).length > 0" class="mt-4 ml-4 border-l-2 border-blue-200 pl-4">
                  <div class="flex items-center justify-between mb-3">
                    <h6 class="text-sm font-medium text-gray-700 flex items-center">
                      <FeatherIcon name="edit-3" class="h-4 w-4 mr-2 text-blue-600" />
                      Modificaciones RRHH ({{ getModificacionesForJobOffer(jobOffer.name).length }})
                    </h6>
                    <button
                      @click="toggleJobOfferExpansion(jobOffer.name)"
                      class="text-sm text-blue-600 flex items-center font-medium"
                    >
                      <FeatherIcon
                        :name="expandedJobOffers.has(jobOffer.name) ? 'chevron-up' : 'chevron-down'"
                        class="h-4 w-4 mr-1"
                      />
                      {{ expandedJobOffers.has(jobOffer.name) ? 'Ocultar' : 'Mostrar' }}
                    </button>
                  </div>

                  <div v-if="expandedJobOffers.has(jobOffer.name)" class="space-y-3">
                    <div
                      v-for="(modificacion, index) in getModificacionesForJobOffer(jobOffer.name)"
                      :key="modificacion.name"
                      class="bg-blue-50 rounded-lg p-3 border border-blue-200 relative"
                    >
                      <!-- Indicador de lista -->
                      <div class="absolute -left-6 top-3 w-3 h-3 bg-blue-400 rounded-full border-2 border-white"></div>

                      <div class="flex items-start justify-between mb-2">
                        <div class="flex-1">
                          <h6 class="text-sm font-semibold text-gray-900">{{ modificacion.tipo_actualizacion || 'Modificación' }}</h6>
                          <a
                            v-if="modificacion.name"
                            @click="openFormInNewTab('Modificaciones RRHH', modificacion.name, $event)"
                            class="text-xs text-blue-600 hover:text-blue-800 hover:underline font-mono cursor-pointer inline-block"
                            title="Ver detalle de la modificación RRHH"
                          >
                            ID: {{ modificacion.name }}
                          </a>
                          <p v-else class="text-xs text-gray-500 font-mono">ID: Sin ID</p>
                        </div>
                        <div
                          v-if="modificacion.workflow_state === 'Alta'"
                          class="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium"
                        >
                          {{ modificacion.workflow_state }}
                        </div>
                        <div
                          v-else-if="modificacion.workflow_state === 'Baja'"
                          class="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-medium"
                        >
                          {{ modificacion.workflow_state }}
                        </div>
                        <div
                          v-else-if="modificacion.workflow_state === 'Pendiente'"
                          class="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-medium"
                        >
                          {{ modificacion.workflow_state }}
                        </div>
                        <div
                          v-else
                          class="px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs font-medium"
                        >
                          {{ modificacion.workflow_state || 'Sin estado' }}
                        </div>
                      </div>

                      <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                        <div v-if="modificacion.start_date" class="flex items-center space-x-2">
                          <FeatherIcon name="play" class="h-4 w-4 text-gray-400" />
                          <span class="text-gray-600">Inicio:</span>
                          <span class="font-medium text-gray-900">{{ formatDate(modificacion.start_date) }}</span>
                        </div>
                        <div v-if="modificacion.end_date" class="flex items-center space-x-2">
                          <FeatherIcon name="stop" class="h-4 w-4 text-gray-400" />
                          <span class="text-gray-600">Fin:</span>
                          <span class="font-medium text-gray-900">{{ formatDate(modificacion.end_date) }}</span>
                        </div>
                        <div v-if="modificacion.custom_tipo_de_contrato" class="flex items-center space-x-2">
                          <FeatherIcon name="file-text" class="h-4 w-4 text-gray-400" />
                          <span class="text-gray-600">Tipo:</span>
                          <span class="font-medium text-gray-900">{{ modificacion.custom_tipo_de_contrato }}</span>
                        </div>
                        <div v-if="modificacion.custom_provincia" class="flex items-center space-x-2">
                          <FeatherIcon name="map-pin" class="h-4 w-4 text-gray-400" />
                          <span class="text-gray-600">Provincia:</span>
                          <span class="font-medium text-gray-900">{{ modificacion.custom_provincia }}</span>
                        </div>
                      </div>

                      <div class="flex flex-wrap gap-2 mt-2">
                        <div v-if="modificacion.custom_firmado" class="flex items-center space-x-1 px-2 py-1 bg-green-100 text-green-800 rounded-full">
                          <FeatherIcon name="check" class="h-3 w-3" />
                          <span class="text-xs">Firmado</span>
                        </div>
                        <div v-if="modificacion.custom_comun" class="flex items-center space-x-1 px-2 py-1 bg-purple-100 text-purple-800 rounded-full">
                          <FeatherIcon name="users" class="h-3 w-3" />
                          <span class="text-xs">Común</span>
                        </div>
                      </div>
                    </div>
                  </div>
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
import { FeatherIcon, Button, Badge, Card, createResource, Input } from 'frappe-ui'
import { ref, computed, watch, onMounted } from 'vue'


// Employee management
const selectedEmployee = ref(null)

// Search filters
const searchFilters = ref({
  employeeName: '',
  dninie: '',
  provincia: '',
  company: '',
  reportsTo: ''
})

// Autocomplete states for provincia
const provinciaSearchText = ref('')
const provinciasList = ref([])
const showProvinciaDropdown = ref(false)
const highlightedProvinciaIndex = ref(-1)
const isLoadingProvincias = ref(false)

// Autocomplete states for company
const companySearchText = ref('')
const companiesList = ref([])
const showCompanyDropdown = ref(false)
const highlightedCompanyIndex = ref(-1)
const isLoadingCompanies = ref(false)

// Autocomplete states for reportsTo (responsable)
const reportsToSearchText = ref('')
const reportsToList = ref([])
const showReportsToDropdown = ref(false)
const highlightedReportsToIndex = ref(-1)
const isLoadingReportsTo = ref(false)

// Timeout para debounce de recarga
let reloadTimeout = null
let searchTimeout = null

// Empleados - lista completa y estado de carga
const allEmployees = ref([])
const totalEmployees = ref(0)
const isLoadingInitial = ref(false)
const isLoadingMore = ref(false)
const hasLoadedAll = ref(false)

// Empleados filtrados (para mostrar en UI)
const filteredEmployees = ref([])

// Estado de carga simplificado
const isLoadingJobOffers = ref(false)
const jobOffersData = ref([])
const currentEmployeeId = ref(null)

// Modificaciones RRHH
const modificacionesData = ref([])
const isLoadingModificaciones = ref(false)
const expandedJobOffers = ref(new Set())
const isEmployeeListCollapsed = ref(false)

// Constantes de paginación
const INITIAL_LOAD_LIMIT = 100
const BATCH_SIZE = 200

// Función para construir filtros del servidor
const buildServerFilters = () => {
  const filters = {}
  
  // Búsqueda por texto (nombre o DNI) - se envía al servidor
  const searchText = searchFilters.value.employeeName.trim() || searchFilters.value.dninie.trim()
  if (searchText) {
    filters.search_text = searchText
  }
  
  // Add provincia filter if provided
  if (searchFilters.value.provincia.trim()) {
    filters.provincia = searchFilters.value.provincia.trim()
  }
  
  // Add company filter if provided
  if (searchFilters.value.company.trim()) {
    filters.company = searchFilters.value.company.trim()
  }
  
  // Add reportsTo filter if provided
  if (searchFilters.value.reportsTo.trim()) {
    filters.reports_to = searchFilters.value.reportsTo.trim()
  }
  
  return filters
}

// Función para cargar empleados desde el servidor
const loadEmployees = async (limit = null, offset = 0, append = false) => {
  try {
    const { call } = await import('frappe-ui')
    const filters = buildServerFilters()
    
    const params = {
      filters: JSON.stringify(filters)
    }
    
    if (limit) {
      params.limit = limit
      params.offset = offset
    }
    
    const result = await call('portal_rrhh.api.employee.get_employees', params)
    
    if (result) {
      const data = result.data || result || []
      const total = result.total || data.length
      
      if (append) {
        // Añadir a la lista existente, evitando duplicados
        const existingIds = new Set(allEmployees.value.map(e => e.name))
        const newEmployees = data.filter(e => !existingIds.has(e.name))
        allEmployees.value = [...allEmployees.value, ...newEmployees]
      } else {
        allEmployees.value = data
      }
      
      totalEmployees.value = total
      updateFilteredEmployees()
      
      return { data, total }
    }
    
    return { data: [], total: 0 }
  } catch (error) {
    console.error('Error loading employees:', error)
    return { data: [], total: 0 }
  }
}

// Función para cargar empleados en segundo plano
const loadRemainingEmployees = async () => {
  if (hasLoadedAll.value || isLoadingMore.value) return
  
  const currentCount = allEmployees.value.length
  if (currentCount >= totalEmployees.value) {
    hasLoadedAll.value = true
    return
  }
  
  isLoadingMore.value = true
  
  try {
    let offset = currentCount
    
    while (offset < totalEmployees.value) {
      const { data } = await loadEmployees(BATCH_SIZE, offset, true)
      
      if (!data || data.length === 0) break
      
      offset += data.length
      
      // Pequeña pausa para no bloquear la UI
      await new Promise(resolve => setTimeout(resolve, 50))
    }
    
    hasLoadedAll.value = true
  } catch (error) {
    console.error('Error loading remaining employees:', error)
  } finally {
    isLoadingMore.value = false
  }
}

// Función para actualizar la lista filtrada
const updateFilteredEmployees = () => {
  filteredEmployees.value = allEmployees.value
}

// Función principal de carga inicial
const initialLoad = async () => {
  isLoadingInitial.value = true
  hasLoadedAll.value = false
  allEmployees.value = []
  
  try {
    // Cargar primeros 100
    await loadEmployees(INITIAL_LOAD_LIMIT, 0, false)
    
    // Cargar el resto en segundo plano
    setTimeout(() => {
      loadRemainingEmployees()
    }, 100)
  } finally {
    isLoadingInitial.value = false
  }
}

// Función para recargar con filtros (búsqueda en servidor)
const reloadWithFilters = async () => {
  isLoadingInitial.value = true
  hasLoadedAll.value = false
  allEmployees.value = []
  
  try {
    // Cuando hay filtros activos, cargar todo de una vez (el servidor filtra)
    const hasActiveSearchFilters = 
      searchFilters.value.employeeName.trim() ||
      searchFilters.value.dninie.trim() ||
      searchFilters.value.provincia.trim() ||
      searchFilters.value.company.trim() ||
      searchFilters.value.reportsTo.trim()
    
    if (hasActiveSearchFilters) {
      // Con filtros, cargar todo (el servidor ya filtra)
      await loadEmployees(null, 0, false)
      hasLoadedAll.value = true
    } else {
      // Sin filtros, usar carga paginada
      await loadEmployees(INITIAL_LOAD_LIMIT, 0, false)
      setTimeout(() => {
        loadRemainingEmployees()
      }, 100)
    }
  } finally {
    isLoadingInitial.value = false
  }
}

// Loading states
const loadingEmployees = computed(() => isLoadingInitial.value)

// Computed properties for filtered options
const filteredProvincias = computed(() => {
  if (!provinciaSearchText.value.trim()) {
    return provinciasList.value
  }
  const search = provinciaSearchText.value.toLowerCase()
  return provinciasList.value.filter(p => 
    p && p.toLowerCase().includes(search)
  )
})

const filteredCompanies = computed(() => {
  if (!companySearchText.value.trim()) {
    return companiesList.value
  }
  const search = companySearchText.value.toLowerCase()
  return companiesList.value.filter(c => 
    c && c.toLowerCase().includes(search)
  )
})

const filteredReportsTo = computed(() => {
  if (!reportsToSearchText.value.trim()) {
    return reportsToList.value
  }
  const search = reportsToSearchText.value.toLowerCase()
  return reportsToList.value.filter(r => 
    r && r.label && r.label.toLowerCase().includes(search)
  )
})

// Load provincias and companies
const loadProvincias = async () => {
  if (provinciasList.value.length > 0) return // Already loaded
  
  isLoadingProvincias.value = true
  try {
    const { call } = await import('frappe-ui')
    const data = await call('portal_rrhh.api.filters.get_unique_provinces')
    provinciasList.value = data || []
  } catch (error) {
    console.error('Error loading provincias:', error)
    provinciasList.value = []
  } finally {
    isLoadingProvincias.value = false
  }
}

const loadCompanies = async () => {
  if (companiesList.value.length > 0) return // Already loaded
  
  isLoadingCompanies.value = true
  try {
    const { call } = await import('frappe-ui')
    const data = await call('portal_rrhh.api.filters.get_unique_companies')
    companiesList.value = data || []
  } catch (error) {
    console.error('Error loading companies:', error)
    companiesList.value = []
  } finally {
    isLoadingCompanies.value = false
  }
}

const loadReportsTo = async () => {
  if (reportsToList.value.length > 0) return // Already loaded
  
  isLoadingReportsTo.value = true
  try {
    const { call } = await import('frappe-ui')
    const data = await call('portal_rrhh.api.filters.get_unique_reports_to')
    reportsToList.value = data || []
  } catch (error) {
    console.error('Error loading reports_to:', error)
    reportsToList.value = []
  } finally {
    isLoadingReportsTo.value = false
  }
}

// Provincia autocomplete handlers
const onProvinciaSearchInput = () => {
  const trimmed = provinciaSearchText.value.trim()
  searchFilters.value.provincia = trimmed
  showProvinciaDropdown.value = true
  highlightedProvinciaIndex.value = -1
  // Recargar empleados con debounce cuando se escribe manualmente
  if (reloadTimeout) {
    clearTimeout(reloadTimeout)
  }
  reloadTimeout = setTimeout(() => {
    if (employees.reload) {
      employees.reload()
    }
  }, 500)
}

const onProvinciaFocus = () => {
  if (provinciasList.value.length === 0) {
    loadProvincias()
  }
  if (filteredProvincias.value.length > 0) {
    showProvinciaDropdown.value = true
  }
}

const handleProvinciaBlur = () => {
  // Delay to allow click events
  setTimeout(() => {
    showProvinciaDropdown.value = false
    highlightedProvinciaIndex.value = -1
  }, 200)
}

const selectProvincia = async (provincia) => {
  provinciaSearchText.value = provincia
  searchFilters.value.provincia = provincia
  
  showProvinciaDropdown.value = false
  highlightedProvinciaIndex.value = -1
  
  // Esperar un momento para que Vue procese el cambio reactivo
  await new Promise(resolve => setTimeout(resolve, 100))
  
  // Forzar recarga del resource con nuevos parámetros
  if (employees) {
    if (typeof employees.reload === 'function') {
      employees.reload()
    } else if (typeof employees.fetch === 'function') {
      employees.fetch()
    }
  }
}

const clearProvincia = () => {
  provinciaSearchText.value = ''
  searchFilters.value.provincia = ''
  showProvinciaDropdown.value = false
  // Forzar recarga de empleados
  if (employees.reload) {
    employees.reload()
  }
}

const navigateProvinciaDropdown = (direction) => {
  if (!showProvinciaDropdown.value || filteredProvincias.value.length === 0) return
  
  highlightedProvinciaIndex.value += direction
  
  if (highlightedProvinciaIndex.value < 0) {
    highlightedProvinciaIndex.value = filteredProvincias.value.length - 1
  } else if (highlightedProvinciaIndex.value >= filteredProvincias.value.length) {
    highlightedProvinciaIndex.value = 0
  }
}

const handleProvinciaEnter = () => {
  if (highlightedProvinciaIndex.value >= 0 && highlightedProvinciaIndex.value < filteredProvincias.value.length) {
    selectProvincia(filteredProvincias.value[highlightedProvinciaIndex.value])
  } else if (filteredProvincias.value.length === 1) {
    selectProvincia(filteredProvincias.value[0])
  }
}

// Company autocomplete handlers
const onCompanySearchInput = () => {
  const trimmed = companySearchText.value.trim()
  searchFilters.value.company = trimmed
  showCompanyDropdown.value = true
  highlightedCompanyIndex.value = -1
  // Recargar empleados con debounce cuando se escribe manualmente
  if (reloadTimeout) {
    clearTimeout(reloadTimeout)
  }
  reloadTimeout = setTimeout(() => {
    if (employees.reload) {
      employees.reload()
    }
  }, 500)
}

const onCompanyFocus = () => {
  if (companiesList.value.length === 0) {
    loadCompanies()
  }
  if (filteredCompanies.value.length > 0) {
    showCompanyDropdown.value = true
  }
}

const handleCompanyBlur = () => {
  // Delay to allow click events
  setTimeout(() => {
    showCompanyDropdown.value = false
    highlightedCompanyIndex.value = -1
  }, 200)
}

const selectCompany = async (company) => {
  companySearchText.value = company
  searchFilters.value.company = company
  
  showCompanyDropdown.value = false
  highlightedCompanyIndex.value = -1
  
  // Esperar un momento para que Vue procese el cambio reactivo
  await new Promise(resolve => setTimeout(resolve, 100))
  
  // Forzar recarga del resource con nuevos parámetros
  if (employees) {
    if (typeof employees.reload === 'function') {
      employees.reload()
    } else if (typeof employees.fetch === 'function') {
      employees.fetch()
    }
  }
}

const clearCompany = () => {
  companySearchText.value = ''
  searchFilters.value.company = ''
  showCompanyDropdown.value = false
  // Forzar recarga de empleados
  if (employees.reload) {
    employees.reload()
  }
}

const navigateCompanyDropdown = (direction) => {
  if (!showCompanyDropdown.value || filteredCompanies.value.length === 0) return
  
  highlightedCompanyIndex.value += direction
  
  if (highlightedCompanyIndex.value < 0) {
    highlightedCompanyIndex.value = filteredCompanies.value.length - 1
  } else if (highlightedCompanyIndex.value >= filteredCompanies.value.length) {
    highlightedCompanyIndex.value = 0
  }
}

const handleCompanyEnter = () => {
  if (highlightedCompanyIndex.value >= 0 && highlightedCompanyIndex.value < filteredCompanies.value.length) {
    selectCompany(filteredCompanies.value[highlightedCompanyIndex.value])
  } else if (filteredCompanies.value.length === 1) {
    selectCompany(filteredCompanies.value[0])
  }
}

// ReportsTo (Responsable) autocomplete handlers
const onReportsToSearchInput = () => {
  const trimmed = reportsToSearchText.value.trim()
  // Find matching value from list
  const match = reportsToList.value.find(r => r.label.toLowerCase() === trimmed.toLowerCase())
  searchFilters.value.reportsTo = match ? match.value : ''
  showReportsToDropdown.value = true
  highlightedReportsToIndex.value = -1
  // Recargar empleados con debounce cuando se escribe manualmente
  if (reloadTimeout) {
    clearTimeout(reloadTimeout)
  }
  reloadTimeout = setTimeout(() => {
    if (employees.reload) {
      employees.reload()
    }
  }, 500)
}

const onReportsToFocus = () => {
  if (reportsToList.value.length === 0) {
    loadReportsTo()
  }
  if (filteredReportsTo.value.length > 0) {
    showReportsToDropdown.value = true
  }
}

const handleReportsToBlur = () => {
  // Delay to allow click events
  setTimeout(() => {
    showReportsToDropdown.value = false
    highlightedReportsToIndex.value = -1
  }, 200)
}

const selectReportsTo = async (reportsTo) => {
  reportsToSearchText.value = reportsTo.label
  searchFilters.value.reportsTo = reportsTo.value
  
  showReportsToDropdown.value = false
  highlightedReportsToIndex.value = -1
  
  // Esperar un momento para que Vue procese el cambio reactivo
  await new Promise(resolve => setTimeout(resolve, 100))
  
  // Forzar recarga del resource con nuevos parámetros
  if (employees) {
    if (typeof employees.reload === 'function') {
      employees.reload()
    } else if (typeof employees.fetch === 'function') {
      employees.fetch()
    }
  }
}

const clearReportsTo = () => {
  reportsToSearchText.value = ''
  searchFilters.value.reportsTo = ''
  showReportsToDropdown.value = false
  // Forzar recarga de empleados
  if (employees.reload) {
    employees.reload()
  }
}

const navigateReportsToDropdown = (direction) => {
  if (!showReportsToDropdown.value || filteredReportsTo.value.length === 0) return
  
  highlightedReportsToIndex.value += direction
  
  if (highlightedReportsToIndex.value < 0) {
    highlightedReportsToIndex.value = filteredReportsTo.value.length - 1
  } else if (highlightedReportsToIndex.value >= filteredReportsTo.value.length) {
    highlightedReportsToIndex.value = 0
  }
}

const handleReportsToEnter = () => {
  if (highlightedReportsToIndex.value >= 0 && highlightedReportsToIndex.value < filteredReportsTo.value.length) {
    selectReportsTo(filteredReportsTo.value[highlightedReportsToIndex.value])
  } else if (filteredReportsTo.value.length === 1) {
    selectReportsTo(filteredReportsTo.value[0])
  }
}

// Función para cargar job offers usando Frappe UI
const loadJobOffers = async (employeeName) => {
  try {
    // Usar Frappe UI para hacer la llamada
    const { call } = await import('frappe-ui')
    const data = await call('portal_rrhh.api.job_offer.get_job_offers_by_employee', {
      employee_name: employeeName
    })

    return data || []
  } catch (error) {
    return []
  }
}

// Función para cargar modificaciones RRHH para un solo job offer
const loadModificacionesForSingleJobOffer = async (jobOfferName) => {
  try {
    // Verificar si ya tenemos las modificaciones para este job offer
    const existingModificaciones = modificacionesData.value.filter(mod => mod.job_offer_name === jobOfferName)
    if (existingModificaciones.length > 0) {
      return
    }

    // Verificar si ya se está cargando para este job offer
    if (isLoadingModificaciones.value) {
      return
    }

    isLoadingModificaciones.value = true

    const { call } = await import('frappe-ui')
    const response = await call('portal_rrhh.api.modificaciones_rrhh.get_modificaciones_by_job_offer', {
      job_offer_name: jobOfferName
    })

    // Agregar las modificaciones con referencia al job offer
    const modificacionesWithJobOffer = (response || []).map(mod => ({
      ...mod,
      job_offer_name: jobOfferName
    }))

    modificacionesData.value.push(...modificacionesWithJobOffer)
  } catch (error) {
    console.error('Error cargando modificaciones:', error)
  } finally {
    isLoadingModificaciones.value = false
  }
}

// Función para obtener modificaciones de un job offer específico
const getModificacionesForJobOffer = (jobOfferName) => {
  const modificaciones = modificacionesData.value.filter(mod => mod.job_offer_name === jobOfferName)
  return modificaciones
}

// Función para alternar expansión de job offer
const toggleJobOfferExpansion = (jobOfferName) => {
  if (expandedJobOffers.value.has(jobOfferName)) {
    expandedJobOffers.value.delete(jobOfferName)
  } else {
    expandedJobOffers.value.add(jobOfferName)
  }
}

const expandEmployeeList = () => {
  isEmployeeListCollapsed.value = false
}

// Función para seleccionar empleado
const selectEmployee = async (employee) => {
  // Prevenir clics múltiples
  if (isLoadingJobOffers.value) {
    return
  }

  // Si es el mismo empleado y ya tenemos datos, no recargar
  if (currentEmployeeId.value === employee.name && jobOffersData.value.length > 0) {
    selectedEmployee.value = employee
    return
  }

  // Ejecutar selección inmediatamente
  await performEmployeeSelection(employee)
}

// Función separada para la lógica de selección
const performEmployeeSelection = async (employee) => {
  // Iniciar carga
  isLoadingJobOffers.value = true
  selectedEmployee.value = employee
  currentEmployeeId.value = employee.name
  jobOffersData.value = []

  // Colapsar la lista de empleados para dar más espacio
  isEmployeeListCollapsed.value = true

  try {
    // Cargar job offers
    const data = await loadJobOffers(employee.name)
    jobOffersData.value = data

    // Limpiar modificaciones anteriores
    modificacionesData.value = []
    expandedJobOffers.value.clear()

    // Cargar modificaciones para todas las job offers automáticamente
    for (const jobOffer of data) {
      await loadModificacionesForSingleJobOffer(jobOffer.name)
    }

  } catch (error) {
    jobOffersData.value = []
  } finally {
    isLoadingJobOffers.value = false
  }
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

// Función para generar URL de formulario de Frappe
const getFormUrl = (doctype, docname) => {
  if (!docname) return '#'
  // Convertir doctype a slug (reemplazar espacios con guiones y convertir a minúsculas)
  const doctypeSlug = doctype.toLowerCase().replace(/\s+/g, '-')
  return `/app/${doctypeSlug}/${encodeURIComponent(docname)}`
}

// Función para abrir formulario en nueva pestaña
const openFormInNewTab = (doctype, docname, event) => {
  if (event) {
    event.stopPropagation()
  }
  const url = getFormUrl(doctype, docname)
  window.open(url, '_blank')
}

// Función para crear una nueva Job Offer con datos del empleado prellenados
const createNewJobOffer = async () => {
  if (!selectedEmployee.value || !selectedEmployee.value.name) {
    return
  }

  try {
    // Construir la URL solo con custom_empleado
    // El client script de Job Offer automáticamente encontrará el job_applicant
    // cuando se establezca custom_empleado usando la función find_and_set_job_applicant
    const employeeName = encodeURIComponent(selectedEmployee.value.name)
    const url = `/app/job-offer/new-job-offer?custom_empleado=${employeeName}`
    
    // Abrir en nueva pestaña para que el proceso sea inequívoco desde el empleado correcto
    window.open(url, '_blank')
  } catch (error) {
    console.error('Error al crear nueva Job Offer:', error)
  }
}

// Función para crear una nueva Modificación RRHH vinculada a una Job Offer
const createNewModificacionRRHH = (jobOfferName, event) => {
  if (event) {
    event.stopPropagation()
  }

  if (!jobOfferName) {
    return
  }

  try {
    // Construir la URL con el parámetro job_offer
    // El client script de Modificaciones RRHH automáticamente encontrará el empleado
    // cuando se establezca job_offer usando la lógica del onload
    // Convertir doctype a slug (reemplazar espacios con guiones y convertir a minúsculas)
    const doctypeSlug = 'Modificaciones RRHH'.toLowerCase().replace(/\s+/g, '-')
    const jobOfferEncoded = encodeURIComponent(jobOfferName)
    const url = `/app/${doctypeSlug}/new-${doctypeSlug}?job_offer=${jobOfferEncoded}`
    
    // Abrir en nueva pestaña
    window.open(url, '_blank')
  } catch (error) {
    console.error('Error al crear nueva Modificación RRHH:', error)
  }
}

// Función para formatear fechas
const formatDate = (dateString) => {
  if (!dateString) return 'No especificada'
  const date = new Date(dateString)
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
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

// Función para obtener el tema del workflow state
const getWorkflowStateTheme = (workflowState) => {
  const workflowMap = {
    'Alta': 'green',
    'Baja': 'red',
    'Baja Solicitada': 'orange',
    'Baja Tramitada': 'red',
    'Validado': 'blue',
    'Modificado': 'purple',
    'Borrador': 'gray',
    'Anulado': 'red',
    'Cancelado': 'red'
  }
  return workflowMap[workflowState] || 'gray'
}

// Función para obtener el tema del estado del empleado
const getEmployeeStatusTheme = (status) => {
  const statusMap = {
    'Alta': 'success',
    'Baja': 'danger',
    'Sin Hojas': 'gray',
    'Sin DNI': 'gray'
  }
  return statusMap[status] || 'gray'
}


// Computed para verificar si hay filtros activos
const hasActiveFilters = computed(() => {
  return searchFilters.value.employeeName.trim() !== '' || 
         searchFilters.value.dninie.trim() !== '' ||
         searchFilters.value.provincia.trim() !== '' ||
         searchFilters.value.company.trim() !== '' ||
         searchFilters.value.reportsTo.trim() !== ''
})

// Computed para verificar si hay filtros activos solo para Job Offers
const hasJobOfferFilters = computed(() => {
  return searchFilters.value.provincia.trim() !== '' || 
         searchFilters.value.company.trim() !== ''
})

// Función para limpiar filtros
const clearFilters = () => {
  searchFilters.value.employeeName = ''
  searchFilters.value.dninie = ''
  clearProvincia()
  clearCompany()
  clearReportsTo()
}

// Load data on mount
onMounted(() => {
  loadProvincias()
  loadCompanies()
  loadReportsTo()
  // Carga inicial de empleados
  initialLoad()
})

// Computed property para Job Offers filtrados
const filteredJobOffers = computed(() => {
  if (!jobOffersData.value || jobOffersData.value.length === 0) {
    return []
  }

  const provinciaFilter = searchFilters.value.provincia.trim().toLowerCase()
  const companyFilter = searchFilters.value.company.trim().toLowerCase()

  // Si no hay filtros de Job Offer, devolver todos
  if (!provinciaFilter && !companyFilter) {
    return jobOffersData.value
  }

  return jobOffersData.value.filter(jobOffer => {
    // Filtro por provincia
    if (provinciaFilter) {
      const provincia = jobOffer.custom_provincia || ''
      if (!provincia.toLowerCase().includes(provinciaFilter)) {
        return false
      }
    }

    // Filtro por empresa
    if (companyFilter) {
      const company = jobOffer.company || ''
      if (!company.toLowerCase().includes(companyFilter)) {
        return false
      }
    }

    return true
  })
})

// Watcher para sincronizar los textos de búsqueda con los filtros
watch(() => searchFilters.value.provincia, (newValue) => {
  if (provinciaSearchText.value !== newValue) {
    provinciaSearchText.value = newValue || ''
  }
})

watch(() => searchFilters.value.company, (newValue) => {
  if (companySearchText.value !== newValue) {
    companySearchText.value = newValue || ''
  }
})

watch(() => searchFilters.value.reportsTo, (newValue) => {
  if (newValue) {
    // Find the label for the current value
    const match = reportsToList.value.find(r => r.value === newValue)
    if (match && reportsToSearchText.value !== match.label) {
      reportsToSearchText.value = match.label
    }
  } else {
    reportsToSearchText.value = ''
  }
})

// Watcher para recargar empleados cuando cambian los filtros (búsqueda en servidor)
watch([
  () => searchFilters.value.employeeName,
  () => searchFilters.value.dninie,
  () => searchFilters.value.provincia, 
  () => searchFilters.value.company, 
  () => searchFilters.value.reportsTo
], ([newName, newDni, newProvincia, newCompany, newReportsTo], [oldName, oldDni, oldProvincia, oldCompany, oldReportsTo]) => {
  // Solo recargar si realmente cambió algún valor
  if (newName !== oldName || newDni !== oldDni || newProvincia !== oldProvincia || newCompany !== oldCompany || newReportsTo !== oldReportsTo) {
    // Limpiar timeout anterior
    if (searchTimeout) {
      clearTimeout(searchTimeout)
    }
    
    // Recargar con debounce para búsquedas de texto
    const delay = (newName !== oldName || newDni !== oldDni) ? 400 : 150
    
    searchTimeout = setTimeout(() => {
      reloadWithFilters()
    }, delay)
  }
}, { immediate: false })

// Watcher simple para resetear datos cuando cambia el empleado
watch(() => selectedEmployee.value, (newEmployee, oldEmployee) => {
  if (newEmployee?.name !== oldEmployee?.name) {
    jobOffersData.value = []
    currentEmployeeId.value = null
  }
})


</script>
