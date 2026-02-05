<template>
  <Dialog
    v-model="show"
    :options="{
      title: 'Solicitar Modificación de Retención IRPF',
      size: '2xl',
      actions: [
        {
          label: 'Enviar Solicitud',
          variant: 'solid',
          loading: submitting,
          disabled: !canSubmit,
          onClick: submitRequest,
        },
      ],
    }"
  >
    <template #body-content>
      <div class="p-5 text-base text-gray-800 max-h-[70vh] overflow-y-auto">
        <div class="space-y-5">
          <!-- Aviso sobre campos obligatorios -->
          <div class="bg-red-50 border border-red-200 rounded-lg p-4">
            <div class="flex items-start gap-2">
              <FeatherIcon name="alert-triangle" class="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div class="text-sm text-red-800">
                <p class="font-semibold mb-1">Campos obligatorios:</p>
                <ul class="list-disc list-inside space-y-1 text-xs">
                  <li>Debe indicar el porcentaje de retención IRPF deseado</li>
                  <li>Debe seleccionar la fecha de efecto</li>
                  <li>Debe indicar el motivo de la solicitud</li>
                  <li>Debe confirmar la declaración voluntaria</li>
                </ul>
                <p class="mt-2 text-xs font-medium">No podrá enviar la solicitud sin completar todos los campos obligatorios.</p>
              </div>
            </div>
          </div>

          <!-- Retención IRPF Actual (solo lectura) -->
          <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
              Retención IRPF Actual
            </label>
            <div class="flex items-center gap-2">
              <FeatherIcon name="percent" class="h-4 w-4 text-gray-500" />
              <span class="font-mono text-sm text-gray-900">{{ currentIrpf }}%</span>
            </div>
          </div>

          <!-- Nueva Retención IRPF -->
          <div>
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
              Nueva Retención IRPF (%) *
            </label>
            <div class="flex items-center gap-2">
              <input
                type="number"
                v-model.number="form.requested_irpf"
                min="0"
                max="100"
                step="0.5"
                placeholder="Ej: 15"
                class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                :class="irpfError ? 'border-red-500' : ''"
                @input="validateIrpf"
              />
              <span class="text-gray-500">%</span>
            </div>
            <p v-if="irpfError" class="mt-1 text-sm text-red-600">
              {{ irpfError }}
            </p>
            <p v-else class="mt-1 text-xs text-gray-500">
              Introduzca el porcentaje de retención IRPF deseado (0-100%)
            </p>
          </div>

          <!-- Tipo de Solicitud -->
          <div>
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
              Tipo de Solicitud *
            </label>
            <select
              v-model="form.irpf_type"
              class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
            >
              <option value="Incremento voluntario">Incremento voluntario</option>
              <option value="Reducción a mínimo legal">Reducción a mínimo legal</option>
              <option value="Otro">Otro</option>
            </select>
          </div>

          <!-- Fecha de Efecto -->
          <div>
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
              Fecha de Efecto *
            </label>
            <input
              type="date"
              v-model="form.effective_date"
              :min="minDate"
              class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
              :class="dateError ? 'border-red-500' : ''"
            />
            <p v-if="dateError" class="mt-1 text-sm text-red-600">
              {{ dateError }}
            </p>
            <p v-else class="mt-1 text-xs text-gray-500">
              Fecha a partir de la cual se aplicará la nueva retención
            </p>
          </div>

          <!-- Motivo -->
          <div>
            <Input
              label="Motivo de la solicitud *"
              type="textarea"
              v-model="form.reason"
              rows="3"
              placeholder="Explique el motivo por el que solicita la modificación de su retención IRPF..."
              :class="reasonError ? 'border-red-500' : ''"
            />
            <p v-if="reasonError" class="mt-1 text-sm text-red-600">
              {{ reasonError }}
            </p>
          </div>

          <!-- Declaración Voluntaria -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <label class="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                v-model="form.voluntary_declaration"
                class="mt-1 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <div>
                <span class="text-sm font-medium text-blue-900">
                  {{ declarationTitle }}
                </span>
                <p class="text-xs text-blue-700 mt-1">
                  {{ declarationText }}
                </p>
              </div>
            </label>
            <p v-if="declarationError" class="mt-2 text-sm text-red-600">
              {{ declarationError }}
            </p>
          </div>

          <!-- Información adicional -->
          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div class="flex items-start gap-2">
              <FeatherIcon name="info" class="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div class="text-sm text-yellow-800">
                <p class="font-semibold mb-1">Proceso de aprobación:</p>
                <ul class="list-disc list-inside space-y-1 text-xs">
                  <li>Su solicitud será revisada por su responsable directo y el departamento de RRHH</li>
                  <li>Recibirá una notificación cuando sea procesada</li>
                  <li>Si es aprobada, su retención IRPF se actualizará automáticamente</li>
                  <li>El cambio se aplicará a partir de la fecha de efecto indicada</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Error message -->
          <div v-if="error">
            <ErrorMessage :message="error" />
          </div>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { Dialog, Input, FeatherIcon, ErrorMessage, createResource } from 'frappe-ui'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  currentIrpf: {
    type: Number,
    default: 0,
  },
  employeeId: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['update:modelValue', 'success'])

const show = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

// Fecha mínima = hoy
const minDate = computed(() => {
  const today = new Date()
  return today.toISOString().split('T')[0]
})

const form = ref({
  requested_irpf: null,
  irpf_type: 'Incremento voluntario',
  effective_date: '',
  reason: '',
  voluntary_declaration: false,
})

const submitting = ref(false)
const error = ref(null)
const irpfError = ref('')
const dateError = ref('')
const reasonError = ref('')
const declarationError = ref('')

// Computed para determinar si se puede enviar el formulario
const canSubmit = computed(() => {
  const hasValidIrpf = form.value.requested_irpf !== null && 
                       form.value.requested_irpf >= 0 && 
                       form.value.requested_irpf <= 100 &&
                       !irpfError.value
  const hasDate = !!form.value.effective_date
  const hasReason = !!form.value.reason?.trim()
  const hasDeclaration = form.value.voluntary_declaration === true
  return hasValidIrpf && hasDate && hasReason && hasDeclaration && !submitting.value
})

// Computed para el título de la declaración según el tipo de solicitud
const declarationTitle = computed(() => {
  switch (form.value.irpf_type) {
    case 'Incremento voluntario':
      return 'Declaro que solicito voluntariamente un tipo de retención IRPF SUPERIOR al calculado reglamentariamente *'
    case 'Reducción a mínimo legal':
      return 'Declaro que solicito voluntariamente la aplicación del tipo de retención MÍNIMO legal *'
    default:
      return 'Declaro que solicito voluntariamente la modificación de mi tipo de retención IRPF *'
  }
})

// Computed para el texto de la declaración según el tipo de solicitud
const declarationText = computed(() => {
  switch (form.value.irpf_type) {
    case 'Incremento voluntario':
      return 'En virtud del art. 88.5 del Reglamento del IRPF (Real Decreto 439/2007), solicito que se me aplique el porcentaje de retención indicado, entendiéndose éste superior al resultante de lo previsto en dicho Reglamento. Este nuevo tipo de retención se aplicará, como mínimo, hasta el final del año y, en tanto no renuncie por escrito al mismo o no solicite un tipo de retención superior, durante los ejercicios sucesivos.'
    case 'Reducción a mínimo legal':
      return 'Solicito que se me aplique el tipo de retención mínimo legal establecido en el Reglamento del IRPF (Real Decreto 439/2007) según mis circunstancias personales y familiares. Este tipo de retención se calculará conforme a los datos comunicados en el modelo 145.'
    default:
      return 'Solicito voluntariamente la modificación de mi porcentaje de retención IRPF al indicado en esta solicitud. Entiendo que este cambio se aplicará según las disposiciones del Reglamento del IRPF (Real Decreto 439/2007).'
  }
})

// Resource para crear la solicitud
const createRequest = createResource({
  url: 'portal_rrhh.api.irpf.create_irpf_retention_request',
  method: 'POST',
  onSuccess() {
    emit('success')
    show.value = false
    resetForm()
    if (window.frappe && window.frappe.show_alert) {
      window.frappe.show_alert({
        message: 'Solicitud enviada correctamente. Puedes ver su estado en tu perfil.',
        indicator: 'green',
      })
    }
  },
  onError(e) {
    if (e.messages) {
      error.value = e.messages.join('\n')
    } else {
      error.value = e.message || 'Error al crear la solicitud'
    }
  },
})

// Validar IRPF
function validateIrpf() {
  if (form.value.requested_irpf === null || form.value.requested_irpf === '') {
    irpfError.value = ''
    return
  }

  const value = parseFloat(form.value.requested_irpf)
  
  if (isNaN(value)) {
    irpfError.value = 'Debe introducir un número válido'
    return
  }
  
  if (value < 0) {
    irpfError.value = 'El porcentaje no puede ser negativo'
    return
  }
  
  if (value > 100) {
    irpfError.value = 'El porcentaje no puede superar el 100%'
    return
  }

  irpfError.value = ''
}

// Enviar solicitud
async function submitRequest() {
  if (submitting.value) return
  submitting.value = true
  error.value = null
  irpfError.value = ''
  dateError.value = ''
  reasonError.value = ''
  declarationError.value = ''

  // Validaciones
  if (form.value.requested_irpf === null || form.value.requested_irpf === '') {
    irpfError.value = 'El porcentaje de retención IRPF es obligatorio'
    submitting.value = false
    return
  }

  const irpfValue = parseFloat(form.value.requested_irpf)
  if (isNaN(irpfValue) || irpfValue < 0 || irpfValue > 100) {
    irpfError.value = 'El porcentaje debe estar entre 0 y 100'
    submitting.value = false
    return
  }

  if (!form.value.effective_date) {
    dateError.value = 'La fecha de efecto es obligatoria'
    submitting.value = false
    return
  }

  if (!form.value.reason?.trim()) {
    reasonError.value = 'El motivo de la solicitud es obligatorio'
    submitting.value = false
    return
  }

  if (!form.value.voluntary_declaration) {
    declarationError.value = 'Debe confirmar la declaración voluntaria'
    submitting.value = false
    return
  }

  try {
    const payload = {
      data: {
        employee: props.employeeId,
        requested_irpf: irpfValue,
        irpf_type: form.value.irpf_type,
        effective_date: form.value.effective_date,
        reason: form.value.reason,
        voluntary_declaration: form.value.voluntary_declaration ? 1 : 0,
      }
    }

    console.log('Enviando solicitud de retención IRPF:', payload)
    const result = await createRequest.submit(payload)
    console.log('Respuesta del servidor:', result)
  } catch (e) {
    console.error('Error al crear solicitud:', e)
    if (e.messages && Array.isArray(e.messages)) {
      error.value = e.messages.join('\n')
    } else if (e.messages) {
      error.value = e.messages
    } else if (e.exc) {
      error.value = e.exc
    } else {
      error.value = e.message || 'Error al crear la solicitud'
    }
  } finally {
    submitting.value = false
  }
}

// Resetear formulario
function resetForm() {
  form.value = {
    requested_irpf: null,
    irpf_type: 'Incremento voluntario',
    effective_date: '',
    reason: '',
    voluntary_declaration: false,
  }
  error.value = null
  irpfError.value = ''
  dateError.value = ''
  reasonError.value = ''
  declarationError.value = ''
}

// Resetear cuando se cierra el diálogo
watch(show, (newVal) => {
  if (!newVal) {
    resetForm()
  }
})
</script>
