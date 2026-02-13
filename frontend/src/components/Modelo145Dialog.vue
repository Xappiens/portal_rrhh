<template>
  <Dialog
    v-model="show"
    :options="{
      title: 'Presentar Modelo 145',
      size: '3xl',
      actions: [
        {
          label: 'Enviar Modelo 145',
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
          <!-- Aviso legal -->
          <div class="bg-red-50 border border-red-200 rounded-lg p-4">
            <div class="flex items-start gap-2">
              <FeatherIcon name="alert-triangle" class="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div class="text-sm text-red-800">
                <p class="font-semibold mb-1">Aviso importante:</p>
                <p class="text-xs">
                  La inclusión de datos falsos, incompletos o inexactos en esta comunicación, así como la falta de 
                  comunicación de variaciones, constituye infracción tributaria sancionable con multa del 
                  <strong>35% al 150%</strong> de las cantidades que se hubieran dejado de retener.
                </p>
              </div>
            </div>
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
            />
            <p class="mt-1 text-xs text-gray-500">
              Fecha a partir de la cual se aplican los datos comunicados
            </p>
          </div>

          <!-- SECCIÓN 1: Situación Familiar -->
          <div class="border border-gray-200 rounded-lg p-4">
            <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <span class="bg-blue-100 text-blue-800 rounded-full w-6 h-6 flex items-center justify-center text-xs">1</span>
              Situación Familiar
            </h3>
            
            <div class="space-y-3">
              <label class="flex items-start gap-3 cursor-pointer p-2 rounded hover:bg-gray-50">
                <input
                  type="radio"
                  v-model="form.family_situation"
                  value="1. Monoparental (soltero/a, viudo/a, divorciado/a con hijos menores a cargo)"
                  class="mt-1"
                />
                <div>
                  <span class="text-sm font-medium">Situación 1</span>
                  <p class="text-xs text-gray-500">Soltero/a, viudo/a, divorciado/a o separado/a con hijos menores de 18 años a cargo (custodia exclusiva)</p>
                </div>
              </label>
              
              <label class="flex items-start gap-3 cursor-pointer p-2 rounded hover:bg-gray-50">
                <input
                  type="radio"
                  v-model="form.family_situation"
                  value="2. Casado/a con cónyuge sin rentas superiores a 1.500€/año"
                  class="mt-1"
                />
                <div>
                  <span class="text-sm font-medium">Situación 2</span>
                  <p class="text-xs text-gray-500">Casado/a y no separado/a legalmente cuyo cónyuge no obtiene rentas superiores a 1.500€/año</p>
                </div>
              </label>
              
              <label class="flex items-start gap-3 cursor-pointer p-2 rounded hover:bg-gray-50">
                <input
                  type="radio"
                  v-model="form.family_situation"
                  value="3. Otra situación"
                  class="mt-1"
                />
                <div>
                  <span class="text-sm font-medium">Situación 3</span>
                  <p class="text-xs text-gray-500">Cualquier otra situación (solteros sin hijos, casados con cónyuge con rentas superiores a 1.500€, etc.)</p>
                </div>
              </label>
              
              <!-- NIF Cónyuge (si situación 2) -->
              <div v-if="form.family_situation && form.family_situation.startsWith('2.')" class="ml-9 mt-2">
                <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                  NIF del Cónyuge *
                </label>
                <input
                  type="text"
                  v-model="form.spouse_nif"
                  placeholder="12345678A"
                  maxlength="9"
                  class="block w-48 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm uppercase"
                />
              </div>
            </div>
          </div>

          <!-- Discapacidad del perceptor -->
          <div class="border border-gray-200 rounded-lg p-4">
            <h3 class="text-sm font-semibold text-gray-700 mb-3">Discapacidad del Perceptor</h3>
            
            <select
              v-model="form.disability_grade"
              class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
            >
              <option value="">Sin discapacidad reconocida</option>
              <option value="Igual o superior al 33% e inferior al 65%">Igual o superior al 33% e inferior al 65%</option>
              <option value="Igual o superior al 65%">Igual o superior al 65%</option>
            </select>
            
            <label v-if="form.disability_grade" class="flex items-center gap-2 mt-3 cursor-pointer">
              <input type="checkbox" v-model="form.disability_needs_help" class="rounded" />
              <span class="text-sm">Tengo acreditada la necesidad de ayuda de terceras personas o movilidad reducida</span>
            </label>
          </div>

          <!-- Movilidad Geográfica -->
          <div class="border border-gray-200 rounded-lg p-4">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" v-model="form.geographic_mobility" class="rounded" />
              <span class="text-sm font-medium">Movilidad geográfica</span>
            </label>
            <p class="text-xs text-gray-500 mt-1 ml-6">
              Marque si estaba en desempleo inscrito en la oficina de empleo y el puesto actual ha exigido traslado de residencia
            </p>
            
            <div v-if="form.geographic_mobility" class="ml-6 mt-3">
              <label class="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                Fecha del Traslado
              </label>
              <input
                type="date"
                v-model="form.mobility_date"
                class="block w-48 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
              />
            </div>
          </div>

          <!-- SECCIÓN 2: Descendientes -->
          <div class="border border-gray-200 rounded-lg p-4">
            <h3 class="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <span class="bg-blue-100 text-blue-800 rounded-full w-6 h-6 flex items-center justify-center text-xs">2</span>
              Hijos y Otros Descendientes
            </h3>
            <p class="text-xs text-gray-500 mb-3">
              Menores de 25 años (o mayores si son discapacitados) que conviven con usted y no tienen rentas anuales superiores a 8.000€
            </p>
            
            <!-- Lista de descendientes -->
            <div v-for="(desc, index) in form.descendants" :key="index" class="bg-gray-50 p-3 rounded mb-2">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium">Descendiente {{ index + 1 }}</span>
                <button @click="removeDescendant(index)" class="text-red-600 hover:text-red-700">
                  <FeatherIcon name="x" class="h-4 w-4" />
                </button>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Año de Nacimiento *</label>
                  <input
                    type="number"
                    v-model.number="desc.year_of_birth"
                    :min="1900"
                    :max="currentYear"
                    placeholder="2010"
                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                  />
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Año Adopción/Acogimiento</label>
                  <input
                    type="number"
                    v-model.number="desc.year_of_adoption"
                    :min="1900"
                    :max="currentYear"
                    placeholder="Opcional"
                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                  />
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Discapacidad</label>
                  <select
                    v-model="desc.disability_grade"
                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                  >
                    <option value="">Sin discapacidad</option>
                    <option value="Igual o superior al 33% e inferior al 65%">33% - 65%</option>
                    <option value="Igual o superior al 65%">65% o más</option>
                  </select>
                </div>
                <div v-if="desc.disability_grade" class="flex items-end">
                  <label class="flex items-center gap-2 cursor-pointer pb-2">
                    <input type="checkbox" v-model="desc.disability_needs_help" class="rounded" />
                    <span class="text-xs">Necesita ayuda</span>
                  </label>
                </div>
              </div>
            </div>
            
            <button
              @click="addDescendant"
              class="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700 mt-2"
            >
              <FeatherIcon name="plus" class="h-4 w-4" />
              Añadir descendiente
            </button>
            
            <label v-if="form.descendants.length > 0" class="flex items-center gap-2 mt-3 cursor-pointer">
              <input type="checkbox" v-model="form.descendants_exclusive_custody" class="rounded" />
              <span class="text-sm">Los hijos/descendientes conviven únicamente conmigo (custodia exclusiva)</span>
            </label>
          </div>

          <!-- SECCIÓN 3: Ascendientes -->
          <div class="border border-gray-200 rounded-lg p-4">
            <h3 class="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <span class="bg-blue-100 text-blue-800 rounded-full w-6 h-6 flex items-center justify-center text-xs">3</span>
              Ascendientes
            </h3>
            <p class="text-xs text-gray-500 mb-3">
              Mayores de 65 años (o menores si son discapacitados) que conviven con usted al menos la mitad del año y no tienen rentas superiores a 8.000€
            </p>
            
            <!-- Lista de ascendientes -->
            <div v-for="(asc, index) in form.ascendants" :key="index" class="bg-gray-50 p-3 rounded mb-2">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium">Ascendiente {{ index + 1 }}</span>
                <button @click="removeAscendant(index)" class="text-red-600 hover:text-red-700">
                  <FeatherIcon name="x" class="h-4 w-4" />
                </button>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Año de Nacimiento *</label>
                  <input
                    type="number"
                    v-model.number="asc.year_of_birth"
                    :min="1900"
                    :max="currentYear"
                    placeholder="1950"
                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                  />
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Nº descendientes que conviven</label>
                  <input
                    type="number"
                    v-model.number="asc.cohabiting_descendants"
                    min="0"
                    placeholder="Incluido usted"
                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                  />
                </div>
                <div>
                  <label class="block text-xs text-gray-500 mb-1">Discapacidad</label>
                  <select
                    v-model="asc.disability_grade"
                    class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                  >
                    <option value="">Sin discapacidad</option>
                    <option value="Igual o superior al 33% e inferior al 65%">33% - 65%</option>
                    <option value="Igual o superior al 65%">65% o más</option>
                  </select>
                </div>
                <div v-if="asc.disability_grade" class="flex items-end">
                  <label class="flex items-center gap-2 cursor-pointer pb-2">
                    <input type="checkbox" v-model="asc.disability_needs_help" class="rounded" />
                    <span class="text-xs">Necesita ayuda</span>
                  </label>
                </div>
              </div>
            </div>
            
            <button
              @click="addAscendant"
              class="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700 mt-2"
            >
              <FeatherIcon name="plus" class="h-4 w-4" />
              Añadir ascendiente
            </button>
          </div>

          <!-- SECCIÓN 4: Pensiones -->
          <div class="border border-gray-200 rounded-lg p-4">
            <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <span class="bg-blue-100 text-blue-800 rounded-full w-6 h-6 flex items-center justify-center text-xs">4</span>
              Pensiones Compensatorias y Anualidades
            </h3>
            <p class="text-xs text-gray-500 mb-3">Importes anuales fijados por resolución judicial</p>
            
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs text-gray-500 mb-1">Pensión compensatoria al cónyuge (€/año)</label>
                <input
                  type="number"
                  v-model.number="form.alimony_spouse"
                  min="0"
                  step="0.01"
                  placeholder="0.00"
                  class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                />
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">Anualidades por alimentos a hijos (€/año)</label>
                <input
                  type="number"
                  v-model.number="form.alimony_children"
                  min="0"
                  step="0.01"
                  placeholder="0.00"
                  class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm"
                />
              </div>
            </div>
          </div>

          <!-- SECCIÓN 5: Vivienda -->
          <div class="border border-gray-200 rounded-lg p-4">
            <h3 class="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <span class="bg-blue-100 text-blue-800 rounded-full w-6 h-6 flex items-center justify-center text-xs">5</span>
              Vivienda Habitual
            </h3>
            
            <label class="flex items-start gap-2 cursor-pointer">
              <input type="checkbox" v-model="form.housing_deduction" class="rounded mt-1" />
              <div>
                <span class="text-sm">Efectúo pagos por préstamos de vivienda habitual con derecho a deducción</span>
                <p class="text-xs text-gray-500">Solo contribuyentes que adquirieron su vivienda antes del 1 de enero de 2013 y con retribuciones inferiores a 33.007,20€/año</p>
              </div>
            </label>
          </div>

          <!-- SECCIÓN 6: Rendimientos Irregulares -->
          <div class="border border-gray-200 rounded-lg p-4">
            <h3 class="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
              <span class="bg-blue-100 text-blue-800 rounded-full w-6 h-6 flex items-center justify-center text-xs">6</span>
              Rendimientos Irregulares
            </h3>
            
            <label class="flex items-start gap-2 cursor-pointer">
              <input type="checkbox" v-model="form.irregular_income_previous" class="rounded mt-1" />
              <div>
                <span class="text-sm">He percibido rendimientos con período de generación superior a 2 años en los 5 ejercicios anteriores</span>
                <p class="text-xs text-gray-500">Marque si le fue aplicada la reducción por irregularidad pero no la aplicó en su autoliquidación del IRPF</p>
              </div>
            </label>
          </div>

          <!-- Declaración Responsable -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <label class="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                v-model="form.declaration_accepted"
                class="mt-1 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <div>
                <span class="text-sm font-medium text-blue-900">
                  Manifiesto ser contribuyente del IRPF y declaro que son ciertos los datos indicados *
                </span>
                <p class="text-xs text-blue-700 mt-1">
                  Presento ante la empresa o entidad pagadora la presente comunicación de mi situación personal y familiar, 
                  o de su variación, a los efectos previstos en el artículo 88 del Reglamento del IRPF.
                </p>
              </div>
            </label>
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
import { Dialog, FeatherIcon, ErrorMessage, createResource } from 'frappe-ui'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
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

const currentYear = new Date().getFullYear()

// Calcular el próximo lunes
function getNextMonday() {
  const today = new Date()
  const dayOfWeek = today.getDay() // 0 = domingo, 1 = lunes, ..., 6 = sábado
  let daysUntilMonday
  
  if (dayOfWeek === 0) {
    // Si es domingo, el próximo lunes es mañana
    daysUntilMonday = 1
  } else if (dayOfWeek === 1) {
    // Si es lunes, el próximo lunes es en 7 días
    daysUntilMonday = 7
  } else {
    // Para martes a sábado, calcular días hasta el próximo lunes
    daysUntilMonday = 8 - dayOfWeek
  }
  
  const nextMonday = new Date(today)
  nextMonday.setDate(today.getDate() + daysUntilMonday)
  return nextMonday.toISOString().split('T')[0]
}

// Fecha mínima = hoy
const minDate = computed(() => {
  const today = new Date()
  return today.toISOString().split('T')[0]
})

const form = ref({
  effective_date: getNextMonday(),
  family_situation: '3. Otra situación',
  spouse_nif: '',
  disability_grade: '',
  disability_needs_help: false,
  geographic_mobility: false,
  mobility_date: '',
  descendants: [],
  descendants_exclusive_custody: false,
  ascendants: [],
  alimony_spouse: 0,
  alimony_children: 0,
  housing_deduction: false,
  irregular_income_previous: false,
  declaration_accepted: false,
})

const submitting = ref(false)
const error = ref(null)

// Computed para determinar si se puede enviar el formulario
const canSubmit = computed(() => {
  const hasDate = !!form.value.effective_date
  const hasDeclaration = form.value.declaration_accepted === true
  
  // Validar NIF cónyuge si situación 2
  let validSpouseNif = true
  if (form.value.family_situation && form.value.family_situation.startsWith('2.')) {
    validSpouseNif = form.value.spouse_nif && form.value.spouse_nif.length === 9
  }
  
  // Validar descendientes (todos deben tener año de nacimiento)
  const validDescendants = form.value.descendants.every(d => d.year_of_birth)
  
  // Validar ascendientes (todos deben tener año de nacimiento)
  const validAscendants = form.value.ascendants.every(a => a.year_of_birth)
  
  // Si situación monoparental, debe tener al menos un descendiente
  let validMonoparental = true
  if (form.value.family_situation && form.value.family_situation.startsWith('1.')) {
    validMonoparental = form.value.descendants.length > 0
  }
  
  return hasDate && hasDeclaration && validSpouseNif && validDescendants && validAscendants && validMonoparental && !submitting.value
})

// Resource para crear el modelo
const createRequest = createResource({
  url: 'portal_rrhh.api.modelo145.create_modelo_145',
  method: 'POST',
  onSuccess() {
    emit('success')
    show.value = false
    resetForm()
    if (window.frappe && window.frappe.show_alert) {
      window.frappe.show_alert({
        message: 'Modelo 145 enviado correctamente. Puedes ver su estado en tu perfil.',
        indicator: 'green',
      })
    }
  },
  onError(e) {
    if (e.messages) {
      error.value = e.messages.join('\n')
    } else {
      error.value = e.message || 'Error al enviar el Modelo 145'
    }
  },
})

// Añadir descendiente
function addDescendant() {
  form.value.descendants.push({
    year_of_birth: null,
    year_of_adoption: null,
    disability_grade: '',
    disability_needs_help: false,
  })
}

// Eliminar descendiente
function removeDescendant(index) {
  form.value.descendants.splice(index, 1)
}

// Añadir ascendiente
function addAscendant() {
  form.value.ascendants.push({
    year_of_birth: null,
    cohabiting_descendants: null,
    disability_grade: '',
    disability_needs_help: false,
  })
}

// Eliminar ascendiente
function removeAscendant(index) {
  form.value.ascendants.splice(index, 1)
}

// Enviar solicitud
async function submitRequest() {
  if (submitting.value) return
  submitting.value = true
  error.value = null

  try {
    const payload = {
      data: {
        employee: props.employeeId,
        effective_date: form.value.effective_date,
        family_situation: form.value.family_situation,
        spouse_nif: form.value.spouse_nif?.toUpperCase() || '',
        disability_grade: form.value.disability_grade,
        disability_needs_help: form.value.disability_needs_help ? 1 : 0,
        geographic_mobility: form.value.geographic_mobility ? 1 : 0,
        mobility_date: form.value.mobility_date || null,
        descendants: form.value.descendants,
        descendants_exclusive_custody: form.value.descendants_exclusive_custody ? 1 : 0,
        ascendants: form.value.ascendants,
        alimony_spouse: form.value.alimony_spouse || 0,
        alimony_children: form.value.alimony_children || 0,
        housing_deduction: form.value.housing_deduction ? 1 : 0,
        irregular_income_previous: form.value.irregular_income_previous ? 1 : 0,
        declaration_accepted: form.value.declaration_accepted ? 1 : 0,
      }
    }

    console.log('Enviando Modelo 145:', payload)
    await createRequest.submit(payload)
  } catch (e) {
    console.error('Error al crear Modelo 145:', e)
    if (e.messages && Array.isArray(e.messages)) {
      error.value = e.messages.join('\n')
    } else if (e.messages) {
      error.value = e.messages
    } else {
      error.value = e.message || 'Error al enviar el Modelo 145'
    }
  } finally {
    submitting.value = false
  }
}

// Resetear formulario
function resetForm() {
  form.value = {
    effective_date: getNextMonday(),
    family_situation: '3. Otra situación',
    spouse_nif: '',
    disability_grade: '',
    disability_needs_help: false,
    geographic_mobility: false,
    mobility_date: '',
    descendants: [],
    descendants_exclusive_custody: false,
    ascendants: [],
    alimony_spouse: 0,
    alimony_children: 0,
    housing_deduction: false,
    irregular_income_previous: false,
    declaration_accepted: false,
  }
  error.value = null
}

// Resetear cuando se cierra el diálogo
watch(show, (newVal) => {
  if (!newVal) {
    resetForm()
  }
})
</script>
