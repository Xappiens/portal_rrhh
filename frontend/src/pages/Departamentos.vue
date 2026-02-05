<template>
  <div class="flex-1 p-4 bg-gray-50 overflow-y-auto">
    <!-- Header con estadísticas rápidas -->
    <div class="mb-4">
      <!-- Tarjetas de estadísticas rápidas -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div class="bg-blue-600 text-white rounded-lg p-3">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-blue-100 text-xs">Mi Equipo</p>
              <p class="text-2xl font-bold">{{ quickStats.team_size }}</p>
            </div>
            <FeatherIcon name="users" class="h-5 w-5 text-blue-200" />
          </div>
        </div>

        <div 
          class="rounded-lg p-3 cursor-pointer hover:shadow-md transition-all"
          :class="quickStats.pending_approvals > 0 ? 'bg-amber-500 text-white' : 'bg-white border border-gray-200'"
          @click="activeTab = 'approvals'"
        >
          <div class="flex items-center justify-between">
            <div>
              <p :class="quickStats.pending_approvals > 0 ? 'text-amber-100' : 'text-gray-500'" class="text-xs">Pendientes</p>
              <p class="text-2xl font-bold" :class="quickStats.pending_approvals > 0 ? '' : 'text-gray-900'">{{ quickStats.pending_approvals }}</p>
            </div>
            <FeatherIcon name="clock" :class="quickStats.pending_approvals > 0 ? 'text-amber-200' : 'text-amber-500'" class="h-5 w-5" />
          </div>
        </div>

        <div class="bg-white border border-gray-200 rounded-lg p-3">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-500 text-xs">Presentes Hoy</p>
              <p class="text-2xl font-bold text-green-600">{{ quickStats.present_today }}</p>
            </div>
            <FeatherIcon name="check-circle" class="h-5 w-5 text-green-500" />
          </div>
        </div>

        <div class="bg-white border border-gray-200 rounded-lg p-3">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-500 text-xs">De Baja Hoy</p>
              <p class="text-2xl font-bold text-red-600">{{ quickStats.on_leave_today }}</p>
            </div>
            <FeatherIcon name="calendar-minus" class="h-5 w-5 text-red-500" />
          </div>
        </div>
      </div>
    </div>

    <!-- Mensaje cuando no hay empleados asignados -->
    <div v-if="!loading && !dashboardData" class="bg-white rounded-lg border border-gray-200 p-6 text-center">
      <FeatherIcon name="users" class="h-8 w-8 text-gray-400 mx-auto mb-2" />
      <h3 class="text-sm font-medium text-gray-900 mb-1">No tienes empleados asignados</h3>
      <p class="text-xs text-gray-600">Contacta con RRHH si crees que deberías tener acceso a la gestión de un equipo.</p>
    </div>

    <!-- Contenido principal -->
    <div v-else>
      <!-- Tabs de navegación -->
      <div class="bg-white rounded-lg border border-gray-200">
        <div class="border-b border-gray-200">
          <nav class="flex -mb-px text-sm">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                'flex items-center px-4 py-2 font-medium border-b-2 transition-colors',
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              <FeatherIcon :name="tab.icon" class="h-3.5 w-3.5 mr-1.5" />
              {{ tab.label }}
              <Badge 
                v-if="tab.badge && tab.badge > 0" 
                :label="String(tab.badge)" 
                variant="solid"
                theme="red"
                size="sm"
                class="ml-1.5"
              />
            </button>
          </nav>
        </div>

        <!-- Contenido de los tabs -->
        <div class="p-4">
          <!-- Tab: Resumen -->
          <div v-if="activeTab === 'overview'">
            <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-4 gap-4">
              <!-- Solicitudes pendientes -->
              <div class="bg-gray-50 rounded-lg p-3">
                <div class="flex items-center justify-between mb-2">
                  <h3 class="text-sm font-medium text-gray-900 flex items-center">
                    <FeatherIcon name="clock" class="h-4 w-4 text-amber-500 mr-1.5" />
                    Solicitudes Pendientes
                  </h3>
                  <Badge 
                    v-if="pendingApprovals.leave_requests?.length > 0"
                    :label="String(pendingApprovals.leave_requests.length)"
                    theme="orange"
                    variant="subtle"
                    size="sm"
                  />
                </div>
                <div v-if="pendingApprovals.leave_requests?.length > 0" class="space-y-2 max-h-48 overflow-y-auto">
                  <div 
                    v-for="request in pendingApprovals.leave_requests.slice(0, 4)" 
                    :key="request.name"
                    class="flex items-center justify-between p-2 bg-white rounded border border-gray-100 text-xs"
                  >
                    <div class="flex-1 min-w-0">
                      <div class="font-medium text-gray-900 truncate">{{ request.employee_name }}</div>
                      <div class="text-gray-500">{{ formatDate(request.from_date) }} · {{ request.total_days }}d</div>
                    </div>
                    <div class="flex space-x-1 ml-2">
                      <Button 
                        variant="solid" 
                        theme="green" 
                        size="sm"
                        @click="approveRequest(request.name, 'approve')"
                        :loading="processingRequest === request.name"
                      >
                        <FeatherIcon name="check" class="h-3 w-3" />
                      </Button>
                      <Button 
                        variant="subtle" 
                        theme="red" 
                        size="sm"
                        @click="approveRequest(request.name, 'reject')"
                        :loading="processingRequest === request.name"
                      >
                        <FeatherIcon name="x" class="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </div>
                <div v-else class="text-center py-4 text-gray-400 text-xs">
                  <FeatherIcon name="check-circle" class="h-6 w-6 mx-auto mb-1" />
                  Sin pendientes
                </div>
              </div>

              <!-- Próximas ausencias -->
              <div class="bg-gray-50 rounded-lg p-3">
                <div class="flex items-center justify-between mb-2">
                  <h3 class="text-sm font-medium text-gray-900 flex items-center">
                    <FeatherIcon name="calendar" class="h-4 w-4 text-blue-500 mr-1.5" />
                    Próximas Ausencias
                  </h3>
                </div>
                <div v-if="dashboardData?.leave_summary?.upcoming_leaves?.length > 0" class="space-y-2 max-h-48 overflow-y-auto">
                  <div 
                    v-for="leave in dashboardData.leave_summary.upcoming_leaves.slice(0, 4)" 
                    :key="leave.name"
                    class="flex items-center p-2 bg-white rounded border border-gray-100 text-xs"
                  >
                    <div class="w-7 h-7 rounded-full bg-blue-100 flex items-center justify-center mr-2 flex-shrink-0">
                      <span class="text-xs font-medium text-blue-600">{{ getInitials(leave.employee_name) }}</span>
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="font-medium text-gray-900 truncate">{{ leave.employee_name }}</div>
                      <div class="text-gray-500">{{ formatDate(leave.from_date) }}</div>
                    </div>
                    <Badge :label="`${leave.total_days}d`" variant="subtle" size="sm" />
                  </div>
                </div>
                <div v-else class="text-center py-4 text-gray-400 text-xs">
                  <FeatherIcon name="sun" class="h-6 w-6 mx-auto mb-1" />
                  Sin ausencias
                </div>
              </div>

              <!-- Asistencia de hoy -->
              <div class="bg-gray-50 rounded-lg p-3">
                <div class="flex items-center justify-between mb-2">
                  <h3 class="text-sm font-medium text-gray-900 flex items-center">
                    <FeatherIcon name="clock" class="h-4 w-4 text-green-500 mr-1.5" />
                    Asistencia Hoy
                  </h3>
                </div>
                <div v-if="dashboardData?.attendance_summary?.today" class="space-y-2">
                  <!-- Barra visual -->
                  <div class="h-2 bg-gray-200 rounded-full overflow-hidden flex">
                    <div class="h-full bg-green-500" :style="{ width: attendancePercentage('present') + '%' }"></div>
                    <div class="h-full bg-purple-500" :style="{ width: attendancePercentage('wfh') + '%' }"></div>
                    <div class="h-full bg-amber-500" :style="{ width: attendancePercentage('on_leave') + '%' }"></div>
                    <div class="h-full bg-red-500" :style="{ width: attendancePercentage('absent') + '%' }"></div>
                  </div>
                  
                  <!-- Stats -->
                  <div class="grid grid-cols-2 gap-1 text-xs">
                    <div class="flex items-center">
                      <div class="w-2 h-2 bg-green-500 rounded-full mr-1.5"></div>
                      <span class="text-gray-600">Presentes: <strong>{{ dashboardData.attendance_summary.today.present }}</strong></span>
                    </div>
                    <div class="flex items-center">
                      <div class="w-2 h-2 bg-purple-500 rounded-full mr-1.5"></div>
                      <span class="text-gray-600">Remoto: <strong>{{ dashboardData.attendance_summary.today.wfh }}</strong></span>
                    </div>
                    <div class="flex items-center">
                      <div class="w-2 h-2 bg-amber-500 rounded-full mr-1.5"></div>
                      <span class="text-gray-600">Baja: <strong>{{ dashboardData.attendance_summary.today.on_leave }}</strong></span>
                    </div>
                    <div class="flex items-center">
                      <div class="w-2 h-2 bg-red-500 rounded-full mr-1.5"></div>
                      <span class="text-gray-600">Ausentes: <strong>{{ dashboardData.attendance_summary.today.absent }}</strong></span>
                    </div>
                  </div>

                  <!-- Sin registro -->
                  <div v-if="dashboardData.attendance_summary.today.no_record > 0" class="text-xs text-gray-500 pt-1 border-t border-gray-200">
                    <strong>{{ dashboardData.attendance_summary.today.no_record }}</strong> sin registro
                  </div>
                </div>
              </div>

              <!-- Contratos -->
              <div class="bg-gray-50 rounded-lg p-3">
                <div class="flex items-center justify-between mb-2">
                  <h3 class="text-sm font-medium text-gray-900 flex items-center">
                    <FeatherIcon name="file-text" class="h-4 w-4 text-indigo-500 mr-1.5" />
                    Contratos
                  </h3>
                </div>
                <div v-if="dashboardData?.job_offer_summary" class="space-y-2">
                  <div class="grid grid-cols-2 gap-2">
                    <div class="p-2 bg-green-50 rounded text-center">
                      <p class="text-lg font-bold text-green-600">{{ dashboardData.job_offer_summary.active }}</p>
                      <p class="text-xs text-green-700">Activos</p>
                    </div>
                    <div class="p-2 bg-amber-50 rounded text-center">
                      <p class="text-lg font-bold text-amber-600">{{ dashboardData.job_offer_summary.expiring_soon?.length || 0 }}</p>
                      <p class="text-xs text-amber-700">Por vencer</p>
                    </div>
                  </div>
                  
                  <div v-if="dashboardData.job_offer_summary.expiring_soon?.length > 0" class="space-y-1 max-h-24 overflow-y-auto">
                    <div 
                      v-for="jo in dashboardData.job_offer_summary.expiring_soon.slice(0, 2)"
                      :key="jo.name"
                      class="flex items-center justify-between p-1.5 bg-amber-50 rounded text-xs"
                    >
                      <span class="font-medium text-gray-900 truncate">{{ jo.applicant_name }}</span>
                      <Badge :label="`${jo.days_until_expiry}d`" theme="orange" variant="subtle" size="sm" />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Timesheets resumen -->
            <div v-if="dashboardData?.timesheet_summary" class="mt-4 bg-gray-50 rounded-lg p-3">
              <div class="flex items-center justify-between mb-2">
                <h3 class="text-sm font-medium text-gray-900 flex items-center">
                  <FeatherIcon name="clock" class="h-4 w-4 text-indigo-500 mr-1.5" />
                  Timesheets del Mes
                </h3>
              </div>
              <div class="grid grid-cols-4 gap-3 text-center">
                <div>
                  <p class="text-lg font-bold text-gray-900">{{ dashboardData.timesheet_summary.total }}</p>
                  <p class="text-xs text-gray-500">Total</p>
                </div>
                <div>
                  <p class="text-lg font-bold text-amber-600">{{ dashboardData.timesheet_summary.draft }}</p>
                  <p class="text-xs text-gray-500">Borradores</p>
                </div>
                <div>
                  <p class="text-lg font-bold text-green-600">{{ dashboardData.timesheet_summary.submitted }}</p>
                  <p class="text-xs text-gray-500">Enviados</p>
                </div>
                <div>
                  <p class="text-lg font-bold text-blue-600">{{ dashboardData.timesheet_summary.total_hours }}h</p>
                  <p class="text-xs text-gray-500">Horas</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Tab: Aprobaciones -->
          <div v-if="activeTab === 'approvals'">
            <div v-if="pendingApprovals.leave_requests?.length > 0" class="space-y-2">
              <div 
                v-for="request in pendingApprovals.leave_requests" 
                :key="request.name"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div class="flex items-center space-x-3">
                  <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                    <span class="text-xs font-medium text-blue-600">{{ getInitials(request.employee_name) }}</span>
                  </div>
                  <div>
                    <div class="text-sm font-medium text-gray-900">{{ request.employee_name }}</div>
                    <div class="text-xs text-gray-500 flex items-center space-x-2">
                      <Badge :label="request.leave_type" theme="blue" variant="subtle" size="sm" />
                      <span>{{ formatDate(request.from_date) }} - {{ formatDate(request.to_date) }}</span>
                      <span>({{ request.total_days }} días)</span>
                    </div>
                    <p v-if="request.description" class="text-xs text-gray-500 mt-1">{{ request.description }}</p>
                  </div>
                </div>
                <div class="flex space-x-2">
                  <Button 
                    variant="solid" 
                    theme="green"
                    size="sm"
                    @click="approveRequest(request.name, 'approve')"
                    :loading="processingRequest === request.name"
                  >
                    <template #prefix>
                      <FeatherIcon name="check" class="h-3.5 w-3.5" />
                    </template>
                    Aprobar
                  </Button>
                  <Button 
                    variant="subtle" 
                    theme="red"
                    size="sm"
                    @click="approveRequest(request.name, 'reject')"
                    :loading="processingRequest === request.name"
                  >
                    <template #prefix>
                      <FeatherIcon name="x" class="h-3.5 w-3.5" />
                    </template>
                    Rechazar
                  </Button>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-8">
              <FeatherIcon name="check-circle" class="h-10 w-10 text-green-200 mx-auto mb-2" />
              <h3 class="text-sm font-medium text-gray-900">¡Todo al día!</h3>
              <p class="text-xs text-gray-500">No hay solicitudes pendientes.</p>
            </div>
          </div>

          <!-- Tab: Equipo -->
          <div v-if="activeTab === 'team'">
            <div class="mb-3">
              <Input
                v-model="teamSearchQuery"
                type="text"
                placeholder="Buscar empleado..."
                size="sm"
              >
                <template #prefix>
                  <FeatherIcon name="search" class="h-3.5 w-3.5 text-gray-400" />
                </template>
              </Input>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
              <div 
                v-for="member in filteredTeamMembers" 
                :key="member.name"
                class="bg-gray-50 rounded-lg p-3"
              >
                <div class="flex items-start space-x-2">
                  <div class="flex-shrink-0">
                    <img 
                      v-if="member.image" 
                      :src="member.image" 
                      :alt="member.employee_name"
                      class="w-8 h-8 rounded-full object-cover"
                    />
                    <div v-else class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                      <span class="text-xs font-medium text-blue-600">{{ getInitials(member.employee_name) }}</span>
                    </div>
                  </div>
                  <div class="flex-1 min-w-0">
                    <h4 class="text-sm font-medium text-gray-900 truncate">{{ member.employee_name }}</h4>
                    <p class="text-xs text-gray-500 truncate">{{ member.designation || 'Sin cargo' }}</p>
                    
                    <div class="flex flex-wrap gap-1 mt-1.5">
                      <Badge 
                        v-if="member.today_attendance"
                        :label="getAttendanceLabel(member.today_attendance.status)"
                        :theme="getAttendanceTheme(member.today_attendance.status)"
                        variant="subtle"
                        size="sm"
                      />
                      <Badge 
                        v-else
                        label="Sin fichar"
                        theme="gray"
                        variant="subtle"
                        size="sm"
                      />
                      <Badge 
                        v-if="member.pending_leaves > 0"
                        :label="`${member.pending_leaves} pend.`"
                        theme="orange"
                        variant="subtle"
                        size="sm"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="filteredTeamMembers.length === 0" class="text-center py-8 text-gray-400">
              <FeatherIcon name="users" class="h-8 w-8 mx-auto mb-2" />
              <p class="text-sm">No se encontraron empleados</p>
            </div>
          </div>

          <!-- Tab: Calendario -->
          <div v-if="activeTab === 'calendar'">
            <div class="mb-3 flex items-center justify-between">
              <div class="flex items-center space-x-2">
                <Button variant="ghost" size="sm" @click="changeMonth(-1)">
                  <FeatherIcon name="chevron-left" class="h-4 w-4" />
                </Button>
                <span class="text-sm font-medium text-gray-900 w-32 text-center">{{ currentMonthName }}</span>
                <Button variant="ghost" size="sm" @click="changeMonth(1)">
                  <FeatherIcon name="chevron-right" class="h-4 w-4" />
                </Button>
              </div>
              <div class="flex items-center space-x-3 text-xs">
                <div class="flex items-center"><div class="w-2 h-2 bg-blue-500 rounded-full mr-1"></div>Vacaciones</div>
                <div class="flex items-center"><div class="w-2 h-2 bg-green-500 rounded-full mr-1"></div>Permiso</div>
                <div class="flex items-center"><div class="w-2 h-2 bg-red-500 rounded-full mr-1"></div>Baja</div>
              </div>
            </div>

            <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div class="grid grid-cols-7 bg-gray-50 border-b border-gray-200">
                <div v-for="day in weekDays" :key="day" class="p-2 text-center text-xs font-medium text-gray-600">
                  {{ day }}
                </div>
              </div>
              
              <div class="grid grid-cols-7">
                <div 
                  v-for="(day, index) in calendarDays" 
                  :key="index"
                  class="min-h-16 p-1 border-b border-r border-gray-100 text-xs"
                  :class="{ 'bg-gray-50': !day.isCurrentMonth, 'bg-blue-50': day.isToday }"
                >
                  <div 
                    class="font-medium mb-0.5"
                    :class="{ 
                      'text-gray-400': !day.isCurrentMonth, 
                      'text-blue-600': day.isToday,
                      'text-gray-700': day.isCurrentMonth && !day.isToday
                    }"
                  >
                    {{ day.date }}
                  </div>
                  <div class="space-y-0.5">
                    <div 
                      v-for="event in getEventsForDay(day.fullDate).slice(0, 2)"
                      :key="event.id"
                      class="px-1 py-0.5 rounded text-white truncate text-[10px]"
                      :style="{ backgroundColor: event.color }"
                      :title="`${event.title} - ${event.subtitle}`"
                    >
                      {{ event.title }}
                    </div>
                    <div 
                      v-if="getEventsForDay(day.fullDate).length > 2"
                      class="text-[10px] text-gray-500"
                    >
                      +{{ getEventsForDay(day.fullDate).length - 2 }} más
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Tab: Timesheets -->
          <div v-if="activeTab === 'timesheets'">
            <div v-if="dashboardData?.timesheet_summary" class="space-y-3">
              <div class="grid grid-cols-4 gap-3">
                <div class="bg-gray-50 rounded-lg p-3 text-center">
                  <p class="text-xl font-bold text-gray-900">{{ dashboardData.timesheet_summary.total }}</p>
                  <p class="text-xs text-gray-500">Total</p>
                </div>
                <div class="bg-gray-50 rounded-lg p-3 text-center">
                  <p class="text-xl font-bold text-amber-600">{{ dashboardData.timesheet_summary.draft }}</p>
                  <p class="text-xs text-gray-500">Borradores</p>
                </div>
                <div class="bg-gray-50 rounded-lg p-3 text-center">
                  <p class="text-xl font-bold text-green-600">{{ dashboardData.timesheet_summary.submitted }}</p>
                  <p class="text-xs text-gray-500">Enviados</p>
                </div>
                <div class="bg-gray-50 rounded-lg p-3 text-center">
                  <p class="text-xl font-bold text-blue-600">{{ dashboardData.timesheet_summary.total_hours }}h</p>
                  <p class="text-xs text-gray-500">Horas</p>
                </div>
              </div>

              <div v-if="dashboardData.timesheet_summary.recent?.length > 0" class="space-y-2">
                <h4 class="text-sm font-medium text-gray-900">Recientes</h4>
                <div 
                  v-for="ts in dashboardData.timesheet_summary.recent"
                  :key="ts.name"
                  class="flex items-center justify-between p-2 bg-gray-50 rounded-lg text-sm"
                >
                  <div class="flex items-center space-x-2">
                    <div class="w-7 h-7 rounded-full bg-indigo-100 flex items-center justify-center">
                      <FeatherIcon name="clock" class="h-3.5 w-3.5 text-indigo-600" />
                    </div>
                    <div>
                      <p class="font-medium text-gray-900 text-xs">{{ ts.employee_name }}</p>
                      <p class="text-xs text-gray-500">{{ formatDate(ts.start_date) }}</p>
                    </div>
                  </div>
                  <div class="flex items-center space-x-2">
                    <span class="font-semibold text-gray-900">{{ ts.total_hours }}h</span>
                    <Badge 
                      :label="ts.docstatus === 1 ? 'Enviado' : 'Borrador'"
                      :theme="ts.docstatus === 1 ? 'green' : 'orange'"
                      variant="subtle"
                      size="sm"
                    />
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
import { ref, computed, onMounted, watch } from 'vue'
import { call, Button, Badge, Input, FeatherIcon } from 'frappe-ui'

// State
const loading = ref(true)
const dashboardData = ref(null)
const quickStats = ref({
  team_size: 0,
  pending_approvals: 0,
  on_leave_today: 0,
  present_today: 0
})
const pendingApprovals = ref({ leave_requests: [], attendance_requests: [] })
const teamMembers = ref([])
const calendarEvents = ref([])
const processingRequest = ref(null)
const teamSearchQuery = ref('')

// Tabs
const activeTab = ref('overview')
const tabs = computed(() => [
  { id: 'overview', label: 'Resumen', icon: 'grid', badge: null },
  { id: 'approvals', label: 'Aprobaciones', icon: 'check-square', badge: pendingApprovals.value.leave_requests?.length || 0 },
  { id: 'team', label: 'Equipo', icon: 'users', badge: null },
  { id: 'calendar', label: 'Calendario', icon: 'calendar', badge: null },
  { id: 'timesheets', label: 'Timesheets', icon: 'clock', badge: null }
])

// Calendar state
const currentMonth = ref(new Date().getMonth())
const currentYear = ref(new Date().getFullYear())
const weekDays = ['L', 'M', 'X', 'J', 'V', 'S', 'D']

const currentMonthName = computed(() => {
  const date = new Date(currentYear.value, currentMonth.value)
  return date.toLocaleString('es-ES', { month: 'short', year: 'numeric' })
})

const calendarDays = computed(() => {
  const days = []
  const firstDay = new Date(currentYear.value, currentMonth.value, 1)
  const lastDay = new Date(currentYear.value, currentMonth.value + 1, 0)
  const today = new Date()
  
  let startDay = firstDay.getDay() - 1
  if (startDay < 0) startDay = 6
  
  const prevMonthLastDay = new Date(currentYear.value, currentMonth.value, 0).getDate()
  for (let i = startDay - 1; i >= 0; i--) {
    const date = prevMonthLastDay - i
    const fullDate = new Date(currentYear.value, currentMonth.value - 1, date)
    days.push({ date, fullDate: fullDate.toISOString().split('T')[0], isCurrentMonth: false, isToday: false })
  }
  
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const fullDate = new Date(currentYear.value, currentMonth.value, i)
    days.push({ date: i, fullDate: fullDate.toISOString().split('T')[0], isCurrentMonth: true, isToday: fullDate.toDateString() === today.toDateString() })
  }
  
  const remainingDays = 42 - days.length
  for (let i = 1; i <= remainingDays; i++) {
    const fullDate = new Date(currentYear.value, currentMonth.value + 1, i)
    days.push({ date: i, fullDate: fullDate.toISOString().split('T')[0], isCurrentMonth: false, isToday: false })
  }
  
  return days
})

const filteredTeamMembers = computed(() => {
  if (!teamSearchQuery.value) return teamMembers.value
  const query = teamSearchQuery.value.toLowerCase()
  return teamMembers.value.filter(m => 
    m.employee_name?.toLowerCase().includes(query) ||
    m.department?.toLowerCase().includes(query) ||
    m.designation?.toLowerCase().includes(query)
  )
})

// Methods
const refreshDashboard = async () => {
  loading.value = true
  await Promise.all([
    loadDashboard(),
    loadQuickStats(),
    loadPendingApprovals(),
    loadTeamMembers(),
    loadCalendarEvents()
  ])
  loading.value = false
}

const loadDashboard = async () => {
  try {
    const result = await call('portal_rrhh.api.department.get_department_dashboard')
    if (result.success) {
      dashboardData.value = result.data
    }
  } catch (error) {
    console.error('Error loading dashboard:', error)
  }
}

const loadQuickStats = async () => {
  try {
    const result = await call('portal_rrhh.api.department.get_department_stats')
    quickStats.value = result
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

const loadPendingApprovals = async () => {
  try {
    const result = await call('portal_rrhh.api.department.get_pending_approvals')
    pendingApprovals.value = result
  } catch (error) {
    console.error('Error loading approvals:', error)
  }
}

const loadTeamMembers = async () => {
  try {
    const result = await call('portal_rrhh.api.department.get_team_members')
    teamMembers.value = result
  } catch (error) {
    console.error('Error loading team:', error)
  }
}

const loadCalendarEvents = async () => {
  try {
    const result = await call('portal_rrhh.api.department.get_leave_calendar', {
      month: currentMonth.value + 1,
      year: currentYear.value
    })
    calendarEvents.value = result
  } catch (error) {
    console.error('Error loading calendar:', error)
  }
}

const approveRequest = async (name, action) => {
  processingRequest.value = name
  try {
    await call('portal_rrhh.api.department.approve_leave_request', { name, action })
    await Promise.all([loadPendingApprovals(), loadQuickStats(), loadDashboard()])
  } catch (error) {
    console.error('Error processing request:', error)
  } finally {
    processingRequest.value = null
  }
}

const changeMonth = (delta) => {
  currentMonth.value += delta
  if (currentMonth.value > 11) {
    currentMonth.value = 0
    currentYear.value++
  } else if (currentMonth.value < 0) {
    currentMonth.value = 11
    currentYear.value--
  }
  loadCalendarEvents()
}

const getEventsForDay = (dateStr) => {
  return calendarEvents.value.filter(event => dateStr >= event.start && dateStr <= event.end)
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('es-ES', { day: '2-digit', month: 'short' })
}

const getInitials = (name) => {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
}

const attendancePercentage = (type) => {
  const total = quickStats.value.team_size || 1
  const today = dashboardData.value?.attendance_summary?.today || {}
  return ((today[type] || 0) / total) * 100
}

const getAttendanceLabel = (status) => {
  const labels = { 'Present': 'Presente', 'Absent': 'Ausente', 'On Leave': 'Baja', 'Work From Home': 'Remoto', 'Half Day': 'Medio día' }
  return labels[status] || status
}

const getAttendanceTheme = (status) => {
  const themes = { 'Present': 'green', 'Absent': 'red', 'On Leave': 'orange', 'Work From Home': 'purple', 'Half Day': 'blue' }
  return themes[status] || 'gray'
}

watch([currentMonth, currentYear], () => loadCalendarEvents())

onMounted(() => refreshDashboard())
</script>
