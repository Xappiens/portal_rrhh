<template>
  <div
    class="relative flex h-full flex-col justify-between transition-all duration-300 ease-in-out"
    :class="isSidebarCollapsed ? 'w-12' : 'w-[220px]'"
  >
    <div>
      <UserDropdown
        class="p-2"
        :isCollapsed="isSidebarCollapsed"
        :appName="appConfig?.app_name"
        :appLogo="appConfig?.app_logo"
      />
    </div>
    <div class="flex-1 overflow-y-auto">
      <div class="mb-3 flex flex-col">
        <SidebarLink
          id="notifications-btn"
          :label="__('Notificaciones')"
          :isCollapsed="isSidebarCollapsed"
          @click="() => toggleNotificationPanel()"
          class="relative mx-2 my-0.5"
        >
          <template #icon>
            <NotificationsIcon />
          </template>
          <template #right>
            <Badge
              v-if="
                !isSidebarCollapsed &&
                notificationsStore().unreadNotificationsCount
              "
              :label="notificationsStore().unreadNotificationsCount"
              variant="subtle"
            />
            <div
              v-else-if="notificationsStore().unreadNotificationsCount"
              class="absolute -left-1.5 top-1 z-20 h-[5px] w-[5px] translate-x-6 translate-y-1 rounded-full bg-gray-800 ring-1 ring-white"
            />
          </template>
        </SidebarLink>
      </div>
      <div v-for="view in allViews" :key="view.label">
        <div
          v-if="!view.hideLabel && isSidebarCollapsed && view.views?.length"
          class="mx-2 my-2 h-1 border-b"
        />
        <Section
          :label="view.name"
          :hideLabel="view.hideLabel"
          :isOpened="view.opened"
        >
          <template #header="{ opened, hide, toggle }">
            <div
              v-if="!hide"
              class="flex cursor-pointer gap-1.5 px-1 text-base font-medium text-gray-600 transition-all duration-300 ease-in-out"
              :class="
                isSidebarCollapsed
                  ? 'ml-0 h-0 overflow-hidden opacity-0'
                  : 'ml-2 mt-4 h-7 w-auto opacity-100'
              "
              @click="toggle()"
            >
              <FeatherIcon
                name="chevron-right"
                class="h-4 text-gray-900 transition-all duration-300 ease-in-out"
                :class="{ 'rotate-90': opened }"
              />
              <span>{{ __(view.name) }}</span>
            </div>
          </template>
          <nav class="flex flex-col">
            <SidebarLink
              v-for="link in view.views"
              :icon="link.icon"
              :label="__(link.label)"
              :to="link.to"
              :isCollapsed="isSidebarCollapsed"
              class="mx-2 my-0.5"
            />
          </nav>
        </Section>
      </div>
    </div>
        <div class="m-2 flex flex-col gap-1">
          <SidebarLink
            :label="isSidebarCollapsed ? __('Expandir') : __('Contraer')"
            :isCollapsed="isSidebarCollapsed"
            @click="isSidebarCollapsed = !isSidebarCollapsed"
            class=""
          >
        <template #icon>
          <span class="grid h-4.5 w-4.5 flex-shrink-0 place-items-center">
            <FeatherIcon
              name="chevron-left"
              class="h-4.5 w-4.5 text-gray-700 duration-300 ease-in-out"
              :class="{ '[transform:rotateY(180deg)]': isSidebarCollapsed }"
            />
          </span>
        </template>
      </SidebarLink>
    </div>
  </div>
</template>

<script setup>
import Section from '@/components/Section.vue'
import UserDropdown from '@/components/UserDropdown.vue'
import SidebarLink from '@/components/SidebarLink.vue'
import NotificationsIcon from '@/components/Icons/NotificationsIcon.vue'
import ProfileIcon from '@/components/Icons/ProfileIcon.vue'
import DashboardIcon from '@/components/Icons/DashboardIcon.vue'
import EmpleadosIcon from '@/components/Icons/EmpleadosIcon.vue'
import VacantesIcon from '@/components/Icons/VacantesIcon.vue'
import SolicitudesIcon from '@/components/Icons/SolicitudesIcon.vue'
import EvaluacionesIcon from '@/components/Icons/EvaluacionesIcon.vue'
import ReportesIcon from '@/components/Icons/ReportesIcon.vue'
import DepartamentosIcon from '@/components/Icons/DepartamentosIcon.vue'
import ConfiguracionIcon from '@/components/Icons/ConfiguracionIcon.vue'
import AIDashboardIcon from '@/components/Icons/AIDashboardIcon.vue'
import CVAnalysisIcon from '@/components/Icons/CVAnalysisIcon.vue'
import RecruitmentReportIcon from '@/components/Icons/RecruitmentReportIcon.vue'
import TimesheetsIcon from '@/components/Icons/TimesheetsIcon.vue'
import { FeatherIcon, Badge, createResource } from 'frappe-ui'
import { useStorage } from '@vueuse/core'
import { computed } from 'vue'

const isSidebarCollapsed = useStorage('isSidebarCollapsed', false)

// Mapa de iconos por nombre de ruta (route name del router)
const iconMap = {
  Profile: ProfileIcon,
  Contratacion: VacantesIcon,
  Empleados: EmpleadosIcon,
  Timesheets: TimesheetsIcon,
  Vacantes: VacantesIcon,
  Solicitudes: SolicitudesIcon,
  Evaluaciones: EvaluacionesIcon,
  Reportes: ReportesIcon,
  AIDashboard: AIDashboardIcon,
  CVAnalysis: CVAnalysisIcon,
  RecruitmentReports: RecruitmentReportIcon,
  AttendanceReport: ReportesIcon,
  Departamentos: DepartamentosIcon,
  Configuracion: ConfiguracionIcon,
}

const sidebarItems = createResource({
  url: 'portal_rrhh.api.sidebar.get_sidebar_items',
  auto: true,
})

const appConfig = computed(() => sidebarItems.data?.app_config || {})

const allViews = computed(() => {
  const data = sidebarItems.data || {}
  // Handle case where data might be the array (old format cache?) or new object
  const items = Array.isArray(data) ? data : (data.items || [])

  const sections = {}
  const order = [] // To preserve section order of appearance

  for (const item of items) {
    const sectionName = item.section || 'General'
    
    if (!sections[sectionName]) {
      sections[sectionName] = []
      order.push(sectionName)
    }

    let icon = item.icon
    // Fallback to iconMap if no icon provided and path matches known routes
    if (!icon && iconMap[item.path]) {
      icon = iconMap[item.path]
    }
    // If still no icon, use default
    if (!icon) icon = 'circle'

    sections[sectionName].push({
      label: item.title,
      icon: icon,
      to: item.path,
    })
  }

  return order.map(name => ({
    name,
    hideLabel: name === 'General', // Hide label for generic section
    opened: true,
    views: sections[name]
  }))
})

function toggleNotificationPanel() {
  // Implementar lógica de notificaciones

}

function notificationsStore() {
  return {
    unreadNotificationsCount: 0
  }
}

function __(text) {
  return text
}
</script>
