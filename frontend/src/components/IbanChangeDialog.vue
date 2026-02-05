<template>
  <Dialog
    v-model="show"
    :options="{
      title: 'Solicitar Cambio de IBAN',
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
                  <li>Debe introducir un IBAN válido</li>
                  <li>Debe adjuntar el justificante bancario (certificado de titularidad)</li>
                  <li>Debe indicar el motivo del cambio</li>
                </ul>
                <p class="mt-2 text-xs font-medium">No podrá enviar la solicitud sin completar todos los campos obligatorios.</p>
              </div>
            </div>
          </div>

          <!-- IBAN Actual (solo lectura) -->
          <div v-if="currentIban" class="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
              IBAN Actual
            </label>
            <div class="flex items-center gap-2">
              <FeatherIcon name="credit-card" class="h-4 w-4 text-gray-500" />
              <span class="font-mono text-sm text-gray-900">{{ formatIban(currentIban) }}</span>
            </div>
          </div>

          <!-- Nuevo IBAN -->
          <div>
            <Input
              label="Nuevo IBAN *"
              v-model="form.new_iban"
              placeholder="ES00 0000 0000 0 0 0000000000"
              :class="ibanError ? 'border-red-500' : ''"
              @update:modelValue="validateIBAN"
            />
            <p v-if="ibanError" class="mt-1 text-sm text-red-600">
              {{ ibanError }}
            </p>
            <p v-else class="mt-1 text-xs text-gray-500">
              Formato: ES00 0000 0000 0 0 0000000000
            </p>
          </div>

          <!-- Entidad Bancaria (calculada automáticamente) -->
          <div v-if="form.bank_entity" class="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
              Entidad Bancaria Detectada
            </label>
            <div class="flex items-center gap-2">
              <FeatherIcon name="building" class="h-4 w-4 text-blue-500" />
              <span class="font-medium text-sm text-blue-900">{{ form.bank_entity }}</span>
            </div>
          </div>

          <!-- Certificado Bancario -->
          <div>
            <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
              Certificado Bancario *
            </label>
            <p class="text-xs text-gray-500 mb-3">
              Suba el certificado bancario (PDF, PNG, JPG - Máx. 5MB)
            </p>
            <input
              type="file"
              ref="fileInput"
              @change="handleFileChange"
              accept=".pdf,.png,.jpg,.jpeg"
              class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 transition-colors cursor-pointer"
            />
            <p v-if="certificateError" class="mt-1 text-sm text-red-600">
              {{ certificateError }}
            </p>
            <div v-if="selectedFile" class="mt-3 flex items-center gap-2 bg-gray-50 p-2 rounded">
              <FeatherIcon name="file" class="h-4 w-4 text-gray-500" />
              <span class="text-sm text-gray-700">{{ selectedFile.name }}</span>
              <span class="text-xs text-gray-500">({{ formatFileSize(selectedFile.size) }})</span>
              <button
                @click="removeFile"
                class="ml-auto text-red-600 hover:text-red-700"
              >
                <FeatherIcon name="x" class="h-4 w-4" />
              </button>
            </div>
          </div>

          <!-- Razón del cambio -->
          <div>
            <Input
              label="Motivo del cambio *"
              type="textarea"
              v-model="form.reason"
              rows="3"
              placeholder="Explique el motivo del cambio de IBAN..."
              :class="reasonError ? 'border-red-500' : ''"
            />
            <p v-if="reasonError" class="mt-1 text-sm text-red-600">
              {{ reasonError }}
            </p>
          </div>

          <!-- Información adicional -->
          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div class="flex items-start gap-2">
              <FeatherIcon name="info" class="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div class="text-sm text-yellow-800">
                <p class="font-semibold mb-1">Proceso de aprobación:</p>
                <ul class="list-disc list-inside space-y-1 text-xs">
                  <li>Su solicitud será revisada por el departamento de RRHH</li>
                  <li>Recibirá una notificación cuando sea procesada</li>
                  <li>Si es aprobada, su IBAN se actualizará automáticamente</li>
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
  currentIban: {
    type: String,
    default: '',
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

const form = ref({
  new_iban: '',
  bank_entity: '',
  reason: '',
  certificate_attachment: null,
})

const selectedFile = ref(null)
const fileInput = ref(null)
const submitting = ref(false)
const error = ref(null)
const ibanError = ref('')
const certificateError = ref('')
const reasonError = ref('')

// Computed para determinar si se puede enviar el formulario
const canSubmit = computed(() => {
  const cleanIban = form.value.new_iban.replace(/\s/g, '').toUpperCase()
  const hasValidIban = cleanIban && validateIBANFormat(cleanIban) && !ibanError.value
  const hasFile = !!selectedFile.value
  const hasReason = !!form.value.reason?.trim()
  return hasValidIban && hasFile && hasReason && !submitting.value
})

// Resource para crear la solicitud
const createRequest = createResource({
  url: 'portal_rrhh.api.iban.create_iban_change_request',
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

// Formatear IBAN para mostrar
function formatIban(iban) {
  if (!iban) return ''
  const clean = iban.replace(/\s/g, '')
  return clean.match(/.{1,4}/g)?.join(' ') || clean
}

// Validar formato IBAN español
function validateIBANFormat(iban) {
  if (!iban) return false

  // Limpiar espacios y convertir a mayúsculas
  const cleanIban = iban.replace(/\s/g, '').toUpperCase()

  // Validar formato español (ES + 2 dígitos + 4 dígitos entidad + 4 dígitos sucursal + 2 dígitos control + 10 dígitos cuenta)
  // Formato específico: ES + 2 + 4 + 4 + 1 + 1 + 10 = ES + 22 dígitos
  const ibanRegex = /^ES\d{2}\d{4}\d{4}\d{1}\d{1}\d{10}$/
  if (!ibanRegex.test(cleanIban)) {
    return false
  }

  // Validar dígito de control usando el mismo algoritmo que el backend
  // Mover los primeros 4 caracteres al final
  const rearranged = cleanIban.slice(4) + cleanIban.slice(0, 4)
  
  // Convertir letras a números (A=10, B=11, etc.) y concatenar como string
  let numeric = ''
  for (const char of rearranged) {
    if (char >= 'A' && char <= 'Z') {
      numeric += String(char.charCodeAt(0) - 'A'.charCodeAt(0) + 10)
    } else {
      numeric += char
    }
  }

  // Verificar que el módulo 97 sea 1 (usando BigInt para manejar números grandes)
  try {
    const remainder = BigInt(numeric) % BigInt(97)
    return remainder === BigInt(1)
  } catch (e) {
    // Si hay error con BigInt, usar cálculo iterativo como fallback
    let remainder = 0
    for (let i = 0; i < numeric.length; i++) {
      remainder = (remainder * 10 + parseInt(numeric[i])) % 97
    }
    return remainder === 1
  }
}

// Validar IBAN en tiempo real
function validateIBAN(value) {
  if (!value) {
    ibanError.value = ''
    form.value.bank_entity = ''
    return
  }

  // Limpiar y formatear
  const clean = value.replace(/\s/g, '').toUpperCase()
  form.value.new_iban = formatIban(clean)

  // Validar formato
  if (!validateIBANFormat(clean)) {
    ibanError.value = 'El formato del IBAN no es válido'
    form.value.bank_entity = ''
    return
  }

  ibanError.value = ''
  
  // Calcular entidad bancaria
  const entityCode = clean.substring(4, 8)
  const bankEntities = {
    '0049': 'Banco Santander',
    '0128': 'Bankinter',
    '0182': 'BBVA',
    '2038': 'Bankia',
    '2100': 'CaixaBank',
    '0081': 'Banco Sabadell',
    '0030': 'Banco Español de Crédito',
    '0073': 'Openbank',
    '3058': 'Cajamar',
    '2085': 'Ibercaja',
  }
  form.value.bank_entity = bankEntities[entityCode] || `Entidad desconocida (${entityCode})`
}

// Manejar cambio de archivo
function handleFileChange(event) {
  const file = event.target.files[0]
  if (!file) return

  certificateError.value = ''

  // Validar tipo
  const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
  if (!allowedTypes.includes(file.type)) {
    certificateError.value = 'Solo se permiten archivos PDF, JPG, JPEG o PNG'
    return
  }

  // Validar tamaño (5MB)
  if (file.size > 5 * 1024 * 1024) {
    certificateError.value = 'El archivo no puede superar los 5MB'
    return
  }

  selectedFile.value = file
}

// Eliminar archivo
function removeFile() {
  selectedFile.value = null
  certificateError.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// Formatear tamaño de archivo
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Subir archivo y obtener URL
async function uploadFile() {
  if (!selectedFile.value) return null

  const formData = new FormData()
  formData.append('file', selectedFile.value)
  formData.append('doctype', 'IBAN Change Request')
  formData.append('docname', 'new-document')
  formData.append('fieldname', 'certificate_attachment')

  try {
    const res = await fetch('/api/method/upload_file', {
      method: 'POST',
      headers: {
        'X-Frappe-CSRF-Token': window.csrf_token || (window.frappe && window.frappe.csrf_token),
      },
      body: formData,
    })

    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(errorData.message || 'Error al subir el archivo')
    }

    const data = await res.json()
    return data.message?.file_url || null
  } catch (e) {
    console.error('Error uploading file:', e)
    throw e
  }
}

// Enviar solicitud
async function submitRequest() {
  if (submitting.value) return
  submitting.value = true
  error.value = null
  ibanError.value = ''
  certificateError.value = ''
  reasonError.value = ''

  // Validaciones
  if (!form.value.new_iban) {
    ibanError.value = 'El nuevo IBAN es obligatorio'
    submitting.value = false
    return
  }

  const cleanIban = form.value.new_iban.replace(/\s/g, '').toUpperCase()
  if (!validateIBANFormat(cleanIban)) {
    ibanError.value = 'El formato del IBAN no es válido'
    submitting.value = false
    return
  }

  if (!selectedFile.value) {
    certificateError.value = 'El certificado bancario es obligatorio'
    submitting.value = false
    return
  }

  if (!form.value.reason?.trim()) {
    reasonError.value = 'El motivo del cambio es obligatorio'
    submitting.value = false
    return
  }

  try {
    // Subir archivo primero
    const fileUrl = await uploadFile()
    if (!fileUrl) {
      throw new Error('No se pudo subir el certificado')
    }

    // Crear solicitud - pasar como objeto 'data' para compatibilidad
    const payload = {
      data: {
        employee: props.employeeId,
        new_iban: cleanIban,
        reason: form.value.reason || '',
        certificate_attachment: fileUrl,
      }
    }

    console.log('Enviando solicitud de cambio de IBAN:', payload)
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
    new_iban: '',
    bank_entity: '',
    reason: '',
    certificate_attachment: null,
  }
  selectedFile.value = null
  error.value = null
  ibanError.value = ''
  certificateError.value = ''
  reasonError.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// Resetear cuando se cierra el diálogo
watch(show, (newVal) => {
  if (!newVal) {
    resetForm()
  }
})
</script>
