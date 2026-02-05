<template>
  <div class="flex h-screen w-screen">
    <div class="h-full border-r bg-gray-50">
      <AppSidebar />
    </div>
    <div class="flex-1 flex flex-col h-full overflow-hidden">
      <PageHeader
        :title="currentPageTitle"
        :subtitle="''"
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
    actionButton: '',
    actionIcon: ''
  },
  'Dashboard': {
    title: 'Panel Principal',
    actionButton: 'Registro de Jornada',
    actionButton: 'Registro de Jornada',
    actionIcon: 'clock'
  },
  'Fichaje': {
    title: 'Fichaje',
    actionButton: '',
    actionIcon: ''
  },
  'Contratacion': {
    title: 'Contratación',
    actionButton: '',
    actionIcon: ''
  },
  'Empleados': {
    title: 'Empleados',
    actionButton: '',
    actionIcon: ''
  },
  'Vacantes': {
    title: 'Vacantes',
    actionButton: 'Nueva Vacante',
    actionIcon: 'plus'
  },
  'Solicitudes': {
    title: 'Solicitudes',
    actionButton: 'Nueva Solicitud',
    actionIcon: 'plus'
  },
  'Evaluaciones': {
    title: 'Evaluaciones',
    actionButton: 'Nueva Evaluación',
    actionIcon: 'plus'
  },
  'Reportes': {
    title: 'Reportes',
    actionButton: 'Generar Reporte',
    actionIcon: 'file-text'
  },
  'AIDashboard': {
    title: 'Panel de Reclutamiento con IA',
    actionButton: 'Ver Panel',
    actionIcon: 'computer'
  },
  'CVAnalysis': {
    title: 'Análisis de CV con IA',
    actionButton: 'Analizar CV',
    actionIcon: 'file-text-icon'
  },
  'RecruitmentReports': {
    title: 'Reportes de Reclutamiento',
    actionButton: 'Generar Reporte',
    actionIcon: 'file-text'
  },
  'Departamentos': {
    title: 'Mi Equipo',
    actionButton: '',
    actionIcon: ''
  },
  'Configuracion': {
    title: 'Configuración',
    actionButton: 'Guardar Cambios',
    actionIcon: 'save'
  }
}

const currentPageConfig = computed(() => {
  return pageConfigs[route.name] || pageConfigs['Home']
})

const currentPageName = computed(() => route.name)
const currentPageTitle = computed(() => currentPageConfig.value.title)
const currentPageActionButton = computed(() => currentPageConfig.value.actionButton)
const currentPageActionIcon = computed(() => currentPageConfig.value.actionIcon)
</script>
