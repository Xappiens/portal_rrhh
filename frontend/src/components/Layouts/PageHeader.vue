<template>
  <div class="bg-white border-b border-gray-200 px-6 py-4">
    <div class="flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <div v-if="!hideTitle">
          <h1 class="text-2xl font-semibold text-gray-900">{{ title }}</h1>
          <p class="text-sm text-gray-600">{{ subtitle }}</p>
        </div>
        <div v-if="breadcrumbs && breadcrumbs.length > 0" class="flex items-center space-x-2 text-sm text-gray-500">
          <span v-for="(crumb, index) in breadcrumbs" :key="index" class="flex items-center">
            <span v-if="index > 0" class="mx-2">/</span>
            <span :class="index === breadcrumbs.length - 1 ? 'text-gray-900 font-medium' : 'text-gray-500 hover:text-gray-700 cursor-pointer'">
              {{ crumb.label }}
            </span>
          </span>
        </div>
      </div>
      <div class="flex items-center space-x-3">
        <slot name="actions">
          <Button
            v-if="showExport"
            variant="outline"
            size="sm"
          >
            <template #prefix>
              <FeatherIcon name="download" class="h-4" />
            </template>
            Exportar
          </Button>
          <Button
            v-if="showNewButton"
            variant="solid"
            size="sm"
            @click="handleButtonClick"
          >
            <template #prefix>
              <FeatherIcon :name="newButtonIcon || 'plus'" class="h-4" />
            </template>
            {{ newButtonText }}
          </Button>
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  hideTitle: {
    type: Boolean,
    default: false
  },
  breadcrumbs: {
    type: Array,
    default: () => []
  },
  showExport: {
    type: Boolean,
    default: false
  },
  showNewButton: {
    type: Boolean,
    default: false
  },
  newButtonText: {
    type: String,
    default: 'Nuevo'
  },
  newButtonIcon: {
    type: String,
    default: 'plus'
  }
})

const handleButtonClick = () => {
  // Handle different button actions based on the button text
  if (props.newButtonText === 'Registro de Jornada') {
    // Redirect to HRMS attendance
    window.location.href = '/hrms'
  } else {
    // For other buttons, emit an event or handle differently
    console.log('Button clicked:', props.newButtonText)
  }
}
</script>
