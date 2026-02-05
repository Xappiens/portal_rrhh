<template>
  <div class="flex h-full flex-col overflow-hidden">
    
    <!-- Teleport Stats to Navbar Title Area -->
    <Teleport to="#page-header-title-area">
        <div v-if="dashboard.data" class="flex items-center gap-6 text-sm text-gray-600 border-l pl-4 hidden sm:flex ml-4">
                
                <!-- User Stats: Days Enjoyed with Detailed Tooltip -->
                 <Tooltip>
                    <template #body>
                        <div class="p-3 space-y-2 text-xs bg-white text-gray-900 rounded-lg shadow-xl border border-gray-200 min-w-[200px]">
                            <div class="font-semibold text-gray-900 border-b pb-1 mb-1">Desglose de Vacaciones</div>
                             <div class="flex justify-between gap-4">
                                <span>Asignados:</span>
                                <span class="font-medium font-mono">{{ dashboard.data.total_days_allocated }}</span>
                            </div>
                            <div class="flex justify-between gap-4 text-green-600">
                                <span>Disfrutados:</span>
                                <span class="font-medium font-mono">{{ dashboard.data.total_days_consumed }}</span>
                            </div>
                             <div class="flex justify-between gap-4 text-orange-600">
                                <span>Pendientes Aprob.:</span>
                                <span class="font-medium font-mono">{{ dashboard.data.total_days_pending }}</span>
                            </div>
                            <div class="border-t pt-2 mt-1 flex justify-between gap-4 font-bold text-gray-900">
                                <span>Disponibles:</span>
                                <span class="font-mono">{{ dashboard.data.total_days_remaining }}</span>
                            </div>
                            <div v-if="dashboard.data.total_hours_allocated > 0" class="pt-2 border-t mt-1">
                                <div class="font-semibold text-xs text-gray-500 mb-1">Horas de Libre Disposición</div>
                                <div class="flex justify-between gap-4">
                                    <span>Disp: {{ dashboard.data.total_hours_remaining?.toFixed(2) }}h</span>
                                    <span class="text-xs text-gray-400">/ {{ dashboard.data.total_hours_allocated?.toFixed(2) }}h</span>
                                </div>
                            </div>
                        </div>
                    </template>
                    <div class="flex flex-col cursor-help group">
                         <span class="text-xs text-gray-500 uppercase tracking-wider font-semibold group-hover:text-gray-800 transition-colors">Días Disfrutados</span>
                         <div class="flex items-baseline gap-1">
                             <span class="text-xl font-bold text-gray-900 leading-none">{{ dashboard.data.total_days_consumed }}</span>
                             <span class="text-xs text-gray-400 font-medium">/ {{ dashboard.data.total_days_allocated }}</span>
                         </div>
                    </div>
                 </Tooltip>

                <!-- Manager Stats -->
                <div v-if="dashboard.data.is_approver" class="flex items-center gap-4 border-l pl-4 border-gray-200">
                    <!-- Team Members -->
                    <Tooltip text="Empleados bajo supervisión">
                        <div class="flex flex-col items-start">
                             <span class="text-xs text-gray-500 uppercase tracking-wider font-semibold">Equipo</span>
                             <div class="flex items-center gap-1.5 text-gray-900">
                                 <FeatherIcon name="users" class="h-4 w-4 text-gray-400" />
                                 <span class="font-bold leading-none">{{ dashboard.data.team_members_count }}</span>
                             </div>
                        </div>
                    </Tooltip>

                    <!-- Pending Requests -->
                     <Tooltip text="Solicitudes pendientes de aprobar">
                        <div class="flex flex-col items-start cursor-pointer" @click="activeTab = 'team'">
                             <span class="text-xs text-gray-500 uppercase tracking-wider font-semibold">Pendientes</span>
                             <div class="flex items-center gap-1.5">
                                 <FeatherIcon name="inbox" class="h-4 w-4" :class="dashboard.data.pending_team_requests > 0 ? 'text-orange-500' : 'text-gray-400'" />
                                 <span class="font-bold leading-none" :class="dashboard.data.pending_team_requests > 0 ? 'text-orange-600' : 'text-gray-900'">
                                     {{ dashboard.data.pending_team_requests }}
                                 </span>
                             </div>
                        </div>
                    </Tooltip>
                </div>
        </div>
    </Teleport>

    <!-- Teleport Main Action to Navbar Action Area -->
    <Teleport to="#page-header-actions">
        <div class="flex items-center gap-2">
            <!-- Legend Popover -->
             <Popover>
                <template #target="{ toggle }">
                    <Button variant="ghost" icon="info" @click="toggle">
                    </Button>
                </template>
                <template #body>
                    <div class="p-3 w-48 bg-white rounded-lg shadow-xl border border-gray-100">
                        <div class="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Tipos de Permiso</div>
                        <div class="flex flex-col gap-2">
                            <div v-for="type in leaveTypesWithColors" :key="type.name" class="flex items-center gap-2">
                                <div class="w-3 h-3 rounded-full flex-shrink-0 bg-gray-200" :class="getColorCircleClass(type.color)"></div>
                                <span class="text-sm text-gray-700">{{ type.label }}</span>
                            </div>
                        </div>
                    </div>
                </template>
             </Popover>

            <Button variant="solid" @click="showDialog = true">
                <template #prefix>
                    <FeatherIcon name="plus" class="h-4 w-4" />
                </template>
                Nueva Solicitud
            </Button>
        </div>
    </Teleport>

    <!-- Content -->
    <div class="flex-1 overflow-hidden flex flex-col">
      <!-- Tabs Header -->
      <div class="flex border-b bg-gray-50 px-5 justify-between items-center h-12 flex-shrink-0">
        <div class="flex h-full gap-4">
            <div class="flex h-full">
                 <button
                  class="border-b-2 px-4 h-full text-sm font-medium transition-colors flex items-center"
                  :class="activeTab === 'my_leaves' ? 'border-gray-900 text-gray-900' : 'border-transparent text-gray-500 hover:text-gray-700'"
                  @click="activeTab = 'my_leaves'"
                >
                  Mis Vacaciones
                </button>
                <button
                  v-if="dashboard.data?.is_approver"
                  class="border-b-2 px-4 h-full text-sm font-medium transition-colors flex items-center"
                  :class="activeTab === 'team' ? 'border-gray-900 text-gray-900' : 'border-transparent text-gray-500 hover:text-gray-700'"
                  @click="activeTab = 'team'"
                >
                  Gestionar Equipo
                </button>
            </div>

            <!-- Team Mode Selector (Only in Team Tab) -->
            <div v-if="activeTab === 'team'" class="flex items-center h-full gap-2">
                <!-- Status Mode -->
                <div class="bg-white p-1 rounded-lg border shadow-sm inline-flex h-8 items-center">
                     <button 
                        class="px-3 py-1 text-xs font-medium rounded-md transition-all h-full flex items-center"
                        :class="teamViewMode === 'Pending' ? 'bg-gray-100 text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
                        @click="teamViewMode = 'Pending'"
                     >
                         Pendientes
                     </button>
                      <button 
                        class="px-3 py-1 text-xs font-medium rounded-md transition-all h-full flex items-center"
                        :class="teamViewMode === 'History' ? 'bg-gray-100 text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
                        @click="teamViewMode = 'History'"
                     >
                         Historial
                     </button>
                 </div>

                 <!-- View Type -->
                 <div class="bg-white p-1 rounded-lg border shadow-sm inline-flex h-8 items-center">
                     <button 
                        class="px-3 py-1 text-xs font-medium rounded-md transition-all h-full flex items-center gap-1"
                        :class="teamDisplayType === 'list' ? 'bg-gray-100 text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
                        @click="teamDisplayType = 'list'"
                     >
                         <FeatherIcon name="list" class="h-3 w-3" />
                         Lista
                     </button>
                      <button 
                        class="px-3 py-1 text-xs font-medium rounded-md transition-all h-full flex items-center gap-1"
                        :class="teamDisplayType === 'calendar' ? 'bg-gray-100 text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
                        @click="teamDisplayType = 'calendar'"
                     >
                         <FeatherIcon name="calendar" class="h-3 w-3" />
                         Calif.
                     </button>
                     <button 
                        class="px-3 py-1 text-xs font-medium rounded-md transition-all h-full flex items-center gap-1"
                        :class="teamDisplayType === 'gantt' ? 'bg-gray-100 text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'"
                        @click="teamDisplayType = 'gantt'"
                     >
                         <FeatherIcon name="bar-chart-2" class="h-3 w-3 rotate-90" />
                         Gantt
                     </button>
                 </div>
            </div>
        </div>

        <!-- View Scale Toggles (Only for My Leaves) -->
        <div v-if="activeTab === 'my_leaves'" class="flex items-center gap-2">
             <div class="bg-gray-200 rounded p-1 flex">
                 <button 
                  class="px-3 py-1 text-xs font-medium rounded transition-colors"
                  :class="viewMode === 'month' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
                  @click="viewMode = 'month'"
                 >
                     Mes
                 </button>
                  <button 
                  class="px-3 py-1 text-xs font-medium rounded transition-colors"
                  :class="viewMode === 'year' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'"
                  @click="viewMode = 'year'"
                 >
                     Año
                 </button>
             </div>
        </div>
            
            <!-- Filters (Only in Team Tab) right aligned -->
            <div v-if="activeTab === 'team'" class="flex items-center gap-2">
                 <!-- Employee Filter -->
                 <div class="w-40 sm:w-48">
                     <Autocomplete
                        :modelValue="teamFilterEmployee"
                        :options="employeeOptions"
                        placeholder="Empleados..."
                        @update:modelValue="val => teamFilterEmployee = val?.value || ''"
                     />
                 </div>
                 
                 <!-- Center Filter -->
                 <div class="w-32 sm:w-40">
                      <Autocomplete
                        :modelValue="teamFilterRoom"
                        :options="roomOptions"
                        placeholder="Centro..."
                        @update:modelValue="val => teamFilterRoom = val?.value || ''"
                     />
                 </div>

                 <!-- Leave Type Filter -->
                 <div class="w-32 sm:w-40">
                      <Autocomplete
                        :modelValue="teamFilterLeaveType"
                        :options="leaveTypeOptions"
                        placeholder="Tipo..."
                        @update:modelValue="val => teamFilterLeaveType = val?.value || ''"
                     />
                 </div>

                 <!-- Only My Team Filter (Solo para usuarios con rol "Validar HC") -->
                 <div v-if="dashboard.data?.has_validar_hc_role" class="flex items-center">
                     <label class="flex items-center gap-2 px-3 py-1.5 bg-white rounded-lg border shadow-sm cursor-pointer hover:bg-gray-50 transition-colors">
                         <input 
                            type="checkbox" 
                            v-model="teamFilterOnlyMyTeam"
                            class="w-4 h-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
                         />
                         <span class="text-xs font-medium text-gray-700 whitespace-nowrap">Solo mi equipo</span>
                     </label>
                 </div>
            </div>

      </div>

      <!-- Tab Content -->
      <div class="h-full overflow-y-auto bg-gray-50 p-4">
        
        <!-- Tab: Mis Vacaciones -->
        <div v-if="activeTab === 'my_leaves'" class="flex flex-col lg:flex-row gap-6 h-full">
          <!-- Calendar -->
          <div class="flex-1 h-full overflow-hidden flex flex-col">
             <!-- Month View -->
            <div v-if="viewMode === 'month'" class="rounded-xl border bg-white p-4 shadow-sm h-full overflow-y-auto">
                <MonthCalendar 
                   :events="calendarEvents"
                   :holidays="leaveContext.data?.holidays || []"
                />
            </div>

            <!-- Year View Grid -->
            <div v-else class="flex flex-col gap-2 h-full overflow-hidden">
                <!-- Year Header controls -->
                <div class="flex justify-between items-center bg-white px-4 py-2 rounded-lg border shadow-sm flex-shrink-0">
                    <div class="flex items-center gap-2">
                        <h2 class="text-base font-bold">{{ yearViewDate.format('YYYY') }}</h2>
                        <span v-if="leaveContext.data?.holiday_list_name" class="text-xs font-normal text-gray-500 bg-gray-100 px-2 py-0.5 rounded border">
                            {{ leaveContext.data.holiday_list_name }}
                        </span>
                    </div>
                    <div class="flex gap-1">
                        <Button icon="chevron-left" @click="prevYear" />
                        <Button icon="chevron-right" @click="nextYear" />
                    </div>
                </div>
                
                <!-- Compact Grid -->
                 <div class="flex-1 overflow-y-auto">
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2">
                        <div 
                            v-for="monthDate in yearMonths" 
                            :key="monthDate.toISOString()"
                            class="rounded-lg border bg-white p-2 shadow-sm"
                        >
                            <MonthCalendar 
                            :events="calendarEvents"
                            :model-date="monthDate"
                            :hide-controls="true"
                            :compact="true"
                            :holidays="leaveContext.data?.holidays || []"
                            class="text-xs"
                            />
                        </div>
                    </div>
                </div>
            </div>
          </div>

          <!-- List (Visible in Month View mostly, generally accessible) -->
          <div v-if="viewMode === 'month'" class="w-full lg:w-80 flex-shrink-0 overflow-y-auto pb-10">
             <div class="flex flex-col gap-3">
                 <h3 class="ml-1 text-lg font-medium">Últimas Solicitudes</h3>
                 <Card v-if="!myLeaves.data?.length" class="p-4 text-gray-500 text-center">
                     No tienes solicitudes recientes.
                 </Card>
                 <Card
                    v-for="leave in myLeaves.data"
                    :key="leave.name"
                    class="p-3 transition hover:shadow-md bg-white border border-gray-100"
                 >
                    <div class="flex justify-between items-center gap-2">
                        <div class="min-w-0">
                            <div class="font-medium text-gray-900 text-sm truncate" :title="leave.leave_type">{{ leave.leave_type }}</div>
                            <div class="text-xs text-gray-500 mt-0.5 truncate">
                                <span v-if="leave.request_type === 'Por Días'">
                                    {{ formatDate(leave.from_date) }} - {{ formatDate(leave.to_date) }}
                                </span>
                                <span v-else>
                                    {{ formatDate(leave.request_date) }} ({{ leave.total_hours }}h)
                                </span>
                            </div>
                        </div>
                        <div class="flex items-center gap-2 flex-shrink-0">
                           <!-- Botón para añadir más adjuntos -->
                           <Button 
                               variant="subtle" 
                               size="sm"
                               icon="plus"
                               @click="triggerAttachment(leave.name)"
                               title="Añadir comprobante"
                               class="text-gray-600 hover:text-gray-900"
                           />
                           
                           <!-- Botón para ver adjuntos existentes (abre Dialog) -->
                           <Button 
                               v-if="leave.attachments?.length > 0"
                               variant="subtle" 
                               size="sm" 
                               icon="file-text"
                               class="text-blue-600 bg-blue-50 hover:bg-blue-100 border-blue-100"
                               @click="openAttachmentsDialog(leave)"
                               :title="`Ver ${leave.attachments.length} comprobante(s)`"
                           >
                               <template #suffix>
                                   <span class="text-xs font-medium">{{ leave.attachments.length }}</span>
                               </template>
                           </Button>
                           
                           <Badge :variant="getStatusVariant(leave.status)" class="text-[10px] px-1.5 py-0.5">
                               {{ leave.status }}
                           </Badge>
                        </div>
                    </div>

                 </Card>
             </div>
          </div>
        </div>

        <!-- Tab: Team Management -->
        <div v-else-if="activeTab === 'team'" class="space-y-6">
             
             <!-- Filters removed and moved to navbar -->

             <!-- Team Calendar View -->
             <div v-if="teamDisplayType === 'calendar'" class="rounded-xl border bg-white p-4 shadow-sm h-[600px] overflow-hidden flex flex-col">
                 <MonthCalendar 
                    :events="teamCalendarEvents"
                    :selectable="false"
                 />
             </div>

             <!-- Team Gantt View -->
             <div v-else-if="teamDisplayType === 'gantt'">
                 <GanttChart 
                    :leaves="teamLeavesCalendarRes.data || []"
                    :employees="teamMembersResource.data || []"
                    :leave-types="dashboard.data?.leave_types_config || []"
                    :can-approve="dashboard.data?.is_approver"
                    @process="handleGanttProcess"
                 />
             </div>

             <!-- Team Requests List View -->
             <div v-else class="rounded-xl border bg-white shadow-sm overflow-hidden">

                 <div class="border-b bg-gray-50 px-6 py-4 flex justify-between items-center">
                    <h3 class="text-lg font-medium text-gray-900">
                        {{ teamViewMode === 'Pending' ? 'Solicitudes Pendientes' : 'Historial de Equipo' }}
                    </h3>
                    <span v-if="teamRequests.data" class="text-xs text-gray-500 font-medium bg-white px-2 py-1 rounded border">
                        {{ teamRequests.data.length }} registros
                    </span>
                 </div>
                 <div v-if="teamRequests.loading" class="p-6 text-center text-gray-500">Cargando...</div>
                 <div v-else-if="!teamRequests.data?.length" class="p-6 text-center text-gray-500 text-sm">
                     No hay solicitudes en esta vista.
                 </div>
                 <table v-else class="min-w-full divide-y divide-gray-200">
                     <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Empleado</th>
                            <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Tipo</th>
                             <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Fechas</th>
                             <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500" v-if="teamViewMode === 'History'">Estado</th>
                             <th class="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">Acciones</th>
                        </tr>
                     </thead>
                     <tbody class="divide-y divide-gray-200 bg-white">
                         <tr v-for="req in teamRequests.data" :key="req.name">
                             <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                 {{ req.employee_name }}
                             </td>
                             <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                 {{ req.leave_type }}
                             </td>
                              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                <span v-if="req.request_type === 'Por Días'">
                                    {{ formatDate(req.from_date) }} - {{ formatDate(req.to_date) }}
                                    <span class="ml-1 text-xs text-gray-400">({{ req.total_days }} días)</span>
                                </span>
                                <span v-else>
                                    {{ formatDate(req.request_date) }} ({{ req.total_hours }}h)
                                </span>
                             </td>
                              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500" v-if="teamViewMode === 'History'">
                                  <Badge :variant="getStatusVariant(req.status)">{{ req.status }}</Badge>
                              </td>
                             <td class="px-6 py-4 whitespace-nowrap text-right text-sm">
                                  <div class="flex justify-end gap-2" v-if="req.status === 'Abierta'">
                                      <Button variant="subtle" color="red" @click="process(req.name, 'reject')" :loading="processingId === req.name">
                                          Rechazar
                                      </Button>
                                      <Button variant="solid" color="green" @click="process(req.name, 'approve')" :loading="processingId === req.name">
                                          Aprobar
                                      </Button>
                                  </div>
                                  <div class="flex justify-end gap-2" v-else-if="req.status === 'Aprobada' && isFutureDate(req.to_date || req.request_date)">
                                       <Button variant="subtle" color="gray" @click="process(req.name, 'cancel')" :loading="processingId === req.name">
                                          Cancelar
                                      </Button>
                                  </div>
                                  <!-- Múltiples adjuntos en tabla de equipo -->
                                  <div class="flex justify-end gap-2 mt-1" v-if="req.attachments?.length > 0">
                                      <Button
                                          variant="ghost" 
                                          icon="paperclip" 
                                          @click="openAttachmentsDialog(req)"
                                          :title="`Ver ${req.attachments.length} comprobante(s)`"
                                          class="text-blue-600 hover:bg-blue-50"
                                      >
                                          <template #suffix>
                                              <span class="text-xs font-medium">{{ req.attachments.length }}</span>
                                          </template>
                                      </Button>
                                  </div>
                             </td>
                         </tr>
                     </tbody>
                 </table>
             </div>
        </div>

      </div>
    </div>

    <!-- Request Dialog -->
    <!-- Request Dialog -->
    <RequestDialog
        v-model="showDialog"
        :leave-types="dashboard.data?.leave_types_config || []"
        @success="refreshAll"
    />

    <!-- Hidden File Input for List Attachments -->
    <input 
        type="file" 
        ref="listFileInput"
        class="hidden"
        @change="handleListAttachment"
    />

    <!-- Attachments Dialog -->
    <Dialog 
        v-model="showAttachmentsDialog"
        :options="{
            title: 'Comprobantes Adjuntos',
            size: 'md'
        }"
    >
        <template #body-content>
            <div v-if="selectedLeaveForAttachments" class="space-y-3">
                <div class="text-sm text-gray-600 mb-4">
                    <span class="font-medium">{{ selectedLeaveForAttachments.leave_type }}</span>
                    <span v-if="selectedLeaveForAttachments.request_type === 'Por Días'" class="ml-2 text-gray-500">
                        ({{ formatDate(selectedLeaveForAttachments.from_date) }} - {{ formatDate(selectedLeaveForAttachments.to_date) }})
                    </span>
                    <span v-else class="ml-2 text-gray-500">
                        ({{ formatDate(selectedLeaveForAttachments.request_date) }})
                    </span>
                </div>
                
                <div v-if="selectedLeaveForAttachments.attachments?.length > 0" class="divide-y divide-gray-100">
                    <div 
                        v-for="att in selectedLeaveForAttachments.attachments" 
                        :key="att.name" 
                        class="flex items-center justify-between gap-3 py-3 group"
                    >
                        <div class="flex items-center gap-3 min-w-0 flex-1">
                            <FeatherIcon name="file" class="h-5 w-5 text-gray-400 flex-shrink-0" />
                            <a 
                                :href="att.file_url" 
                                target="_blank"
                                class="text-sm text-blue-600 hover:text-blue-800 truncate"
                                :title="att.file_name"
                            >
                                {{ att.file_name || 'Archivo' }}
                            </a>
                        </div>
                        <Button 
                            variant="ghost" 
                            size="sm"
                            icon="trash-2"
                            class="text-red-500 hover:text-red-700 hover:bg-red-50 flex-shrink-0"
                            @click="deleteAttachmentFromDialog(att.name)"
                            title="Eliminar"
                        />
                    </div>
                </div>
                <div v-else class="text-center text-gray-500 py-4">
                    No hay comprobantes adjuntos
                </div>
                
                <!-- Botón para añadir más -->
                <div class="pt-3 border-t">
                    <Button 
                        variant="subtle" 
                        icon="plus"
                        @click="triggerAttachmentFromDialog"
                        class="w-full"
                    >
                        Añadir comprobante
                    </Button>
                </div>
            </div>
        </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { createResource, Popover, Tooltip, FeatherIcon, Autocomplete, Dialog } from 'frappe-ui'
import dayjs from 'dayjs'
import RequestDialog from '@/components/SpanishLeave/RequestDialog.vue'
import MonthCalendar from '@/components/SpanishLeave/MonthCalendar.vue'
import GanttChart from '@/components/SpanishLeave/GanttChart.vue'

const activeTab = ref('my_leaves')
const viewMode = ref('month') // 'month' | 'year'
const showDialog = ref(false)
const processingId = ref(null)

const listFileInput = ref(null)
const attachingToId = ref(null)

// Attachments Dialog State
const showAttachmentsDialog = ref(false)
const selectedLeaveForAttachments = ref(null)

function openAttachmentsDialog(leave) {
    selectedLeaveForAttachments.value = leave
    showAttachmentsDialog.value = true
}

// Team Management State
const teamViewMode = ref('Pending') // 'Pending' | 'History'
const teamDisplayType = ref('list') // 'list' | 'calendar'
const teamFilterEmployee = ref('')
const teamFilterRoom = ref('')
const teamFilterLeaveType = ref('')
const teamFilterOnlyMyTeam = ref(true) // Solo para usuarios con rol "Validar HC" - activado por defecto

const yearViewDate = ref(dayjs())

// Context for Filters (Rooms, etc)
const leaveContext = createResource({
    url: 'portal_rrhh.api.spanish_leave.get_leave_form_context',
    auto: true
})

// Resources
const dashboard = createResource({
    url: 'portal_rrhh.api.spanish_leave.get_dashboard_data',
    auto: true
})

const myLeaves = createResource({
    url: 'portal_rrhh.api.spanish_leave.get_my_leaves',
    auto: true
})


const teamRequests = createResource({
    url: 'portal_rrhh.api.spanish_leave.get_team_requests',
    auto: true,
    makeParams() {
        return {
            status: teamViewMode.value,
            employee: teamFilterEmployee.value,
            leave_type: teamFilterLeaveType.value,
            location: teamFilterRoom.value,
            only_my_team: teamFilterOnlyMyTeam.value || undefined
        }
    }
})

const teamLeavesCalendarRes = createResource({
    url: 'portal_rrhh.api.spanish_leave.get_team_leaves',
    auto: true,
    makeParams() {
        // We'll just fetch a wide range or current month +/- ?
        // For now, let's fetch roughly current year/window or based on calendar view date?
        // MonthCalendar handles internal date, but we need data.
        // Let's simplified fetch: current year or so.
        // Or better: rely on month change if we had that event.
        // For simplicity: fetch everything from 6 months ago to 6 months ahead?
        // Let's just fetch all 'approved' for now or a large window.
        return {
             month_start: dayjs().subtract(6, 'month').format('YYYY-MM-DD'),
             month_end: dayjs().add(6, 'month').format('YYYY-MM-DD'),
             employee: teamFilterEmployee.value,
             leave_type: teamFilterLeaveType.value,
             location: teamFilterRoom.value
        }
    }
})

// Employees List for Autocomplete
const teamMembersResource = createResource({
    url: 'portal_rrhh.api.spanish_leave.get_my_team_members',
    auto: true
})

// Processing Logic
const processResource = createResource({
    url: 'portal_rrhh.api.spanish_leave.process_request',
})

// Delete Attachment Resource
const deleteAttachmentResource = createResource({
    url: 'portal_rrhh.api.spanish_leave.delete_attachment',
})

async function process(name, action) {
    processingId.value = name
    try {
        await processResource.submit({ name, action })
        teamRequests.reload()
        teamLeavesCalendarRes.reload()
        dashboard.reload()
    } catch(e) {
        console.error(e)
    } finally {
        processingId.value = null
    }
}

// Handler para procesar desde Gantt
async function handleGanttProcess({ name, action }) {
    await process(name, action)
}

function refreshAll() {
    dashboard.reload()
    myLeaves.reload()
    teamRequests.reload()
}

function openAttachment(url) {
    if (!url) return
    window.open(url, '_blank')
}

function triggerAttachment(id) {
    attachingToId.value = id
    listFileInput.value?.click()
}

async function handleListAttachment(event) {
    const file = event.target.files[0]
    if (!file || !attachingToId.value) return
    
    // Reset input
    event.target.value = ''
    
    const docname = attachingToId.value
    attachingToId.value = null
    
    // Upload logic
    const formData = new FormData()
    formData.append('file', file)
    formData.append('doctype', 'Spanish Leave Application')
    formData.append('docname', docname)
    
    try {
        const res = await fetch('/api/method/upload_file', {
            method: 'POST',
            headers: {
                'X-Frappe-CSRF-Token': window.csrf_token || (window.frappe && window.frappe.csrf_token)
            },
            body: formData
        })
        
        if (res.ok) {
            if (window.frappe && window.frappe.show_alert) {
                window.frappe.show_alert({
                    message: 'Comprobante adjuntado correctamente',
                    indicator: 'green'
                })
            }
            // Recargar datos y cerrar dialog si estaba abierto
            await myLeaves.reload()
            teamRequests.reload()
            
            // Si el dialog está abierto, actualizar el leave seleccionado
            if (showAttachmentsDialog.value && selectedLeaveForAttachments.value?.name === docname) {
                const updatedLeave = myLeaves.data?.find(l => l.name === docname)
                if (updatedLeave) {
                    selectedLeaveForAttachments.value = updatedLeave
                }
            }
        } else {
             if (window.frappe && window.frappe.show_alert) {
                 window.frappe.show_alert({
                    message: 'Error al subir el archivo',
                    indicator: 'red'
                })
             }
        }
    } catch (e) {
        console.error(e)
         if (window.frappe && window.frappe.show_alert) {
             window.frappe.show_alert({
                message: 'Error de conexión',
                indicator: 'red'
            })
         }
    }
}

async function deleteAttachment(docname, fileName) {
    if (!confirm('¿Estás seguro de que deseas eliminar este comprobante?')) return
    
    try {
        await deleteAttachmentResource.submit({
            file_name: fileName,
            docname: docname
        })
        
        if (window.frappe && window.frappe.show_alert) {
            window.frappe.show_alert({
                message: 'Comprobante eliminado correctamente',
                indicator: 'green'
            })
        }
        myLeaves.reload()
        teamRequests.reload()
    } catch (e) {
        console.error(e)
        if (window.frappe && window.frappe.show_alert) {
            window.frappe.show_alert({
                message: 'Error al eliminar el archivo',
                indicator: 'red'
            })
        }
    }
}

async function deleteAttachmentFromDialog(fileName) {
    if (!selectedLeaveForAttachments.value) return
    if (!confirm('¿Estás seguro de que deseas eliminar este comprobante?')) return
    
    const docname = selectedLeaveForAttachments.value.name
    
    try {
        await deleteAttachmentResource.submit({
            file_name: fileName,
            docname: docname
        })
        
        // Actualizar la lista local de attachments
        selectedLeaveForAttachments.value.attachments = selectedLeaveForAttachments.value.attachments.filter(
            att => att.name !== fileName
        )
        
        // Si no quedan attachments, cerrar el dialog
        if (selectedLeaveForAttachments.value.attachments.length === 0) {
            showAttachmentsDialog.value = false
        }
        
        if (window.frappe && window.frappe.show_alert) {
            window.frappe.show_alert({
                message: 'Comprobante eliminado correctamente',
                indicator: 'green'
            })
        }
        myLeaves.reload()
        teamRequests.reload()
    } catch (e) {
        console.error(e)
        if (window.frappe && window.frappe.show_alert) {
            window.frappe.show_alert({
                message: 'Error al eliminar el archivo',
                indicator: 'red'
            })
        }
    }
}

function triggerAttachmentFromDialog() {
    if (!selectedLeaveForAttachments.value) return
    attachingToId.value = selectedLeaveForAttachments.value.name
    listFileInput.value?.click()
}

// Helpers
function formatDate(date) {
    if (!date) return '-'
    return dayjs(date).format('DD MMM YYYY')
}

function getStatusVariant(status) {
    if (status === 'Aprobada') return 'green'
    if (status === 'Rechazada') return 'red'
    if (status === 'Abierta') return 'orange'
    return 'gray'
}

function prevYear() {
    yearViewDate.value = yearViewDate.value.subtract(1, 'year')
}
function nextYear() {
    yearViewDate.value = yearViewDate.value.add(1, 'year')
}

// Year Grid Generation
const yearMonths = computed(() => {
    const start = yearViewDate.value.startOf('year')
    const months = []
    for(let i=0; i<12; i++) {
        months.push(start.add(i, 'month'))
    }
    return months
})

// Refetch team requests when filters change
watch([teamViewMode, teamFilterEmployee, teamFilterRoom, teamFilterLeaveType, teamFilterOnlyMyTeam], () => {
    teamRequests.fetch()
    teamLeavesCalendarRes.fetch()
})

const employeeOptions = computed(() => {
    if (!teamMembersResource.data) return []
    return teamMembersResource.data.map(e => ({
        label: e.employee_name,
        value: e.name
    }))
})

const roomOptions = computed(() => {
    // Base list of all rooms
    const allRooms = leaveContext.data?.rooms || []
    
    // If we have team members, only show rooms they belong to
    if (teamMembersResource.data?.length) {
        const teamRooms = new Set(teamMembersResource.data.map(e => e.custom_centro).filter(Boolean))
        
        // Filter allRooms to only those in teamRooms
        const filtered = allRooms.filter(r => teamRooms.has(r.name))
        
        // If we found matches, return them. 
        // If for some reason we have IDs in teamRooms that aren't in allRooms (unlikely), 
        // we might miss them, but generally safe to rely on allRooms for metadata.
        if (filtered.length > 0) {
            return filtered.map(r => ({
                label: r.room_name,
                value: r.name
            }))
        }
    }

    // Fallback: show all rooms if no team data or no matches
    return allRooms.map(r => ({
        label: r.room_name,
        value: r.name
    }))
})

const leaveTypeOptions = computed(() => {
    if (!dashboard.data?.leave_types_config) return []
    return dashboard.data.leave_types_config.map(l => ({
        label: l.leave_type_name,
        value: l.name
    }))
})

function isFutureDate(dateStr) {
    if (!dateStr) return false
    return dayjs(dateStr).isAfter(dayjs(), 'day')
}

// Color Management for Leave Types
const PALETTE = ['blue', 'purple', 'teal', 'orange', 'pink', 'indigo', 'yellow', 'red', 'green']
const leaveTypesWithColors = computed(() => {
    if (!dashboard.data?.leave_types_config) return []
    
    return dashboard.data.leave_types_config.map((opt, idx) => ({
        name: opt.name,
        label: opt.leave_type_name,
        color: PALETTE[idx % PALETTE.length] // Cycle through palette
    }))
})

// Quick lookup map for color by leave type name
const colorMap = computed(() => {
    const map = {
        'Rechazada': 'gray' // Always gray
    }
    leaveTypesWithColors.value.forEach(t => {
        map[t.name] = t.color
    })
    return map
})

function getColorCircleClass(color) {
    const map = {
        green: 'bg-green-500',
        orange: 'bg-orange-500',
        red: 'bg-red-500',
        blue: 'bg-blue-500',
        purple: 'bg-purple-500',
        pink: 'bg-pink-500',
        teal: 'bg-teal-500',
        indigo: 'bg-indigo-500',
        yellow: 'bg-yellow-500',
        gray: 'bg-gray-500',
    }
    return map[color] || map['gray']
}

// Calendar Logic
const calendarEvents = computed(() => {
    if (!myLeaves.data) return []
    
    return myLeaves.data.map(leave => {
        let color = colorMap.value[leave.leave_type] || 'gray'
        if (leave.status === 'Rechazada') color = 'gray' 

        return {
            id: leave.name,
            title: leave.leave_type, // Short title
            tooltip: `${leave.leave_type} (${leave.status})${leave.description ? ': ' + leave.description : ''}`,
            color: color,
            from_date: leave.request_type === 'Por Días' ? leave.from_date : null,
            to_date: leave.request_type === 'Por Días' ? leave.to_date : null,
            date: leave.request_type === 'Por Horas' ? leave.request_date : null
        }
    })
})

const teamCalendarEvents = computed(() => {
    if(!teamLeavesCalendarRes.data) return []
    
    return teamLeavesCalendarRes.data.map(leave => {
        let color = colorMap.value[leave.leave_type] || 'gray'
        if (leave.status === 'Rechazada') color = 'gray' 

        return {
            id: leave.name,
            title: `${leave.employee_name} - ${leave.leave_type}`, 
            tooltip: `${leave.employee_name}: ${leave.leave_type} (${leave.status})`,
            color: color,
            status: leave.status, // Para distinguir solicitudes pendientes
            from_date: leave.request_type === 'Por Días' ? leave.from_date : null,
            to_date: leave.request_type === 'Por Días' ? leave.to_date : null,
            date: leave.request_type === 'Por Horas' ? leave.request_date : null
        }
    })
})

</script>
