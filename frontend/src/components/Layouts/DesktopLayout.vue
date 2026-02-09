<template>
  <div class="flex h-screen w-screen">
    <div class="h-full border-r bg-gray-50">
      <AppSidebar />
    </div>
    <div class="flex-1 flex flex-col h-full overflow-hidden">
      <PageHeader
        :title="currentPageTitle"
        :subtitle="currentPageSubtitle"
        :breadcrumbs="[]"
        :show-export="false"
        :show-new-button="!!currentPageActionButton"
        :new-button-text="currentPageActionButton"
        :new-button-icon="currentPageActionIcon"
      />
      <div class="flex-1 overflow-hidden">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
import AppSidebar from '@/components/Layouts/AppSidebar.vue'
import PageHeader from '@/components/Layouts/PageHeader.vue'
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const pageConfigs = {
  'Home': {
    title: 'Portal RRHH',
    subtitle: '',
    actionButton: '',
    actionIcon: ''
  },
  'Dashboard': {
    title: 'Panel Principal',
    subtitle: '',
    actionButton: 'Registro de Jornada',
    actionButton: 'Registro de Jornada',
    actionIcon: 'clock'
  },
  'Fichaje': {
    title: 'Fichaje',
    subtitle: '',
    actionButton: '',
    actionIcon: ''
  },
  'Contratacion': {
    title: 'Contratación',
    subtitle: '',
    actionButton: '',
    actionIcon: ''
  },
  'Empleados': {
    title: 'Empleados',
    subtitle: '',
    actionButton: '',
    actionIcon: ''
  },
  'Vacantes': {
    title: 'Vacantes',
    subtitle: '',
    actionButton: 'Nueva Vacante',
    actionIcon: 'plus'
  },
  'Solicitudes': {
    title: 'Solicitudes',
    subtitle: '',
    actionButton: 'Nueva Solicitud',
    actionIcon: 'plus'
  },
  'Evaluaciones': {
    title: 'Evaluaciones',
    subtitle: '',
    actionButton: 'Nueva Evaluación',
    actionIcon: 'plus'
  },
  'Reportes': {
    title: 'Reportes',
    subtitle: '',
    actionButton: 'Generar Reporte',
    actionIcon: 'file-text'
  },
  'AIDashboard': {
    title: 'Panel de Reclutamiento con IA',
    subtitle: '',
    actionButton: 'Ver Panel',
    actionIcon: 'computer'
  },
  'CVAnalysis': {
    title: 'Análisis de CV con IA',
    subtitle: '',
    actionButton: 'Analizar CV',
    actionIcon: 'file-text-icon'
  },
  'RecruitmentReports': {
    title: 'Reportes de Reclutamiento',
    subtitle: '',
    actionButton: 'Generar Reporte',
    actionIcon: 'file-text'
  },
  'Departamentos': {
    title: 'Mi Equipo',
    subtitle: '',
    actionButton: '',
    actionIcon: ''
  },
  'Configuracion': {
    title: 'Configuración',
    subtitle: '',
    actionButton: 'Guardar Cambios',
    actionIcon: 'save'
  },
  'Nominas': {
    title: 'Gestión de Nóminas',
    subtitle: 'Sistema de liquidación de nóminas para docentes',
    actionButton: '',
    actionIcon: ''
  }
}

const currentPageConfig = computed(() => {
  return pageConfigs[route.name] || pageConfigs['Home']
})

const currentPageName = computed(() => route.name)
const currentPageTitle = computed(() => currentPageConfig.value.title)
const currentPageSubtitle = computed(() => currentPageConfig.value.subtitle)
const currentPageActionButton = computed(() => currentPageConfig.value.actionButton)
const currentPageActionIcon = computed(() => currentPageConfig.value.actionIcon)
</script>
