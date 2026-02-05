<template>
  <Dialog
    v-model="show"
    :options="{
      title: 'Nueva Solicitud de Vacaciones',
      size: '4xl',
      actions: [
        {
          label: 'Enviar Solicitud',
          variant: 'solid',
          loading: submitting,
          onClick: submitRequest,
        },
      ],
    }"
  >
    <template #body-content>
      <!-- Loading State -->
      <div v-if="leaveContext.loading" class="p-8 text-center text-gray-500">
          Cargando información...
      </div>

      <div v-else class="p-5 text-base text-gray-800">
        
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8">
            
            <!-- LEFT COLUMN: Inputs & Context (Span 5) -->
            <div class="lg:col-span-5 flex flex-col gap-5">
                
                <!-- Context Info Box (Compact Vertical) -->
                <div class="flex flex-col gap-3 bg-gray-50 p-3 rounded-lg border border-gray-100 text-sm">
                     <!-- Approver -->
                     <div class="flex flex-col">
                         <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Aprobador</span>
                         <div class="flex items-center gap-2 mt-0.5">
                             <FeatherIcon name="user-check" class="h-4 w-4 text-blue-500" />
                             <span class="font-medium text-gray-900 truncate">
                                 {{ leaveContext.data?.approver?.name || 'No asignado' }}
                             </span>
                         </div>
                     </div>

                     <!-- Holiday List Display -->
                     <div v-if="leaveContext.data?.holiday_list_name" class="flex flex-col">
                         <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Calendario</span>
                         <div class="flex items-center gap-2 mt-0.5">
                             <FeatherIcon name="calendar" class="h-3.5 w-3.5 text-orange-500" />
                             <span class="font-medium text-gray-900 truncate">
                                 {{ leaveContext.data.holiday_list_name }}
                             </span>
                         </div>
                     </div>
                     
                     <div class="h-px bg-gray-200 w-full"></div>

                     <!-- Allocations Summary -->
                     <div class="flex flex-col">
                          <span class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Tus Saldos</span>
                          <div class="mt-1 flex flex-col gap-1 max-h-32 overflow-y-auto custom-scrollbar">
                              <div v-if="!leaveContext.data?.allocations?.length" class="text-gray-400 italic text-xs">
                                  Sin asignaciones activas.
                              </div>
                              <div v-for="alloc in leaveContext.data?.allocations" :key="alloc.name" class="flex justify-between items-center bg-white px-2 py-1.5 rounded border border-gray-100 shadow-sm text-xs">
                                  <span class="truncate pr-2" :title="alloc.contract_start_date">{{ formatDate(alloc.contract_start_date) }}</span>
                                  <span class="font-mono font-bold text-gray-700 bg-gray-100 px-1.5 py-0.5 rounded">{{ parseFloat(alloc.days_remaining).toFixed(1) }}d</span>
                              </div>
                          </div>
                     </div>
                </div>

                <!-- Leave Type -->
                <div class="flex flex-col gap-2">
                  <label class="font-medium text-gray-700 block text-sm">Tipo de Permiso</label>
                  <Autocomplete
                    :modelValue="form.leave_type"
                    :options="leaveTypeOptions"
                    placeholder="Selecciona un tipo..."
                    @update:modelValue="val => form.leave_type = val.value"
                  />
                </div>

                <!-- Request Type Toggle (if allowed) -->
                <div v-if="canRequestHours" class="flex flex-col gap-2">
                   <label class="font-medium text-gray-700 block text-sm">Modo</label>
                    <div class="flex flex-col gap-2">
                       <label class="flex items-center gap-2 cursor-pointer text-sm text-gray-700 select-none hover:text-gray-900">
                         <input type="radio" v-model="form.request_type" value="Por Días" name="req_type" class="text-gray-900 focus:ring-gray-900" />
                         Por Días (Jornada)
                       </label>
                        <label class="flex items-center gap-2 cursor-pointer text-sm text-gray-700 select-none hover:text-gray-900">
                         <input type="radio" v-model="form.request_type" value="Por Horas" name="req_type" class="text-gray-900 focus:ring-gray-900" />
                         Por Horas (Parcial)
                       </label>
                    </div>
                </div>

                <!-- Description -->
                <div>
                  <Input
                    label="Motivo"
                    type="textarea"
                    v-model="form.description"
                    rows="3"
                    placeholder="Comentarios..."
                  />
                </div>
                
                 <!-- Attachment -->
                <div>
                   <label class="font-medium text-gray-700 block text-sm mb-2">Comprobante (Opcional)</label>
                   <input 
                      type="file" 
                      ref="fileInput"
                      @change="handleFileChange"
                      class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 transition-colors cursor-pointer"
                   />
                </div>

            </div>

            <!-- RIGHT COLUMN: Calendar / Date Selection (Span 7) -->
            <div class="lg:col-span-7 flex flex-col gap-4">
                
                <!-- Visual Calendar for Days -->
                <div v-if="form.request_type === 'Por Días'" class="flex flex-col gap-3 h-full">
                    <div class="flex justify-between items-end">
                        <label class="font-medium text-gray-700 block text-sm">Selección de Fechas</label>
                        <!-- Legend inline -->
                        <div class="flex gap-3 text-[10px] text-gray-500">
                             <div class="flex items-center gap-1">
                                 <div class="w-2.5 h-2.5 bg-blue-600 rounded-[2px]"></div>
                                 <span>Selección</span>
                             </div>
                              <div class="flex items-center gap-1">
                                 <div class="w-2.5 h-2.5 bg-red-50 border border-red-100 rounded-[2px]"></div>
                                 <span class="text-red-600">Festivo</span>
                             </div>
                        </div>
                    </div>

                     <div class="border rounded-xl p-2 bg-white shadow-sm flex-1 min-h-[320px]">
                         <MonthCalendar
                            :selectable="true"
                            :selection="{ from: dates.from, to: dates.to }"
                            :holidays="leaveContext.data?.holidays || []"
                            :hide-controls="false"
                            @update:selection="handleDateSelection"
                        />
                     </div>

                    <!-- Calculation Feedback -->
                    <div v-if="dates.from" class="rounded-md border p-3 text-sm transition-all shadow-sm"
                        :class="dateFeedback.isError ? 'bg-red-50 border-red-100 text-red-700' : 'bg-blue-50 border-blue-100 text-blue-800'"
                    >
                        <div class="flex items-center gap-3">
                             <FeatherIcon :name="dateFeedback.isError ? 'alert-circle' : 'info'" class="h-5 w-5 flex-shrink-0" />
                             <div class="flex flex-col">
                                 <div class="font-semibold text-base leading-tight">
                                     <span v-if="!dates.to">Selecciona fecha fin...</span>
                                     <span v-else>{{ dateFeedback.days }} días efectivos</span>
                                 </div>
                                 <div v-if="dateFeedback.holidays.length" class="text-xs opacity-90 mt-0.5">
                                     Excluye: {{ dateFeedback.holidays.join(', ') }}
                                 </div>
                             </div>
                        </div>
                    </div>
                </div>

                <!-- Date + Hours Input (Hours Mode) -->
                <div v-else class="flex flex-col gap-4 p-4 bg-gray-50 rounded-xl border border-dashed border-gray-200 h-full justify-center">
                     <div class="flex flex-col gap-2">
                        <label class="font-medium text-gray-700 block text-sm">Fecha</label>
                        <DatePicker
                            v-model="dates.single"
                            placeholder="Selecciona fecha"
                            class="w-full"
                        />
                    </div>
                     <div class="flex flex-col gap-2">
                        <Input
                            label="Cantidad de Horas"
                            type="number"
                            v-model="form.hours"
                            placeholder="Ej: 4.5"
                            step="0.5"
                        />
                    </div>
                </div>

            </div>

        </div>
        
         <div v-if="error" class="mt-4">
             <ErrorMessage :message="error" />
         </div>

      </div>
    </template>
  </Dialog>

</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { createResource, DatePicker, Input, ErrorMessage, Autocomplete, FeatherIcon } from 'frappe-ui'
import MonthCalendar from '@/components/SpanishLeave/MonthCalendar.vue'
import dayjs from 'dayjs'
// Helpers needed for calculation
import isBetween from 'dayjs/plugin/isBetween'
dayjs.extend(isBetween)

const props = defineProps({
  modelValue: Boolean,
  leaveTypes: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:modelValue', 'success'])

// Resources
const leaveContext = createResource({
    url: 'portal_rrhh.api.spanish_leave.get_leave_form_context',
    cache: true 
})

const createRequest = createResource({
  url: 'portal_rrhh.api.spanish_leave.create_leave_application',
  makeParams(values) {
    return {
      data: values,
    }
  },
})

const show = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

// Fetch context when dialog opens
watch(show, (val) => {
    if (val) {
        leaveContext.fetch()
        resetForm()
    }
})

const form = ref({
  leave_type: '',
  request_type: 'Por Días',
  description: '',
  hours: 0,
  description: '',
  hours: 0,
})
const fileInput = ref(null)
const selectedFile = ref(null)

const dates = ref({
    from: '',
    to: '',
    single: ''
})

const error = ref(null)

// --- Helpers ---
function formatDate(d) {
    return dayjs(d).format('DD/MM/YYYY')
}

function handleDateSelection(val) {
    dates.value.from = val.from
    dates.value.to = val.to
}

// --- Calculation Logic in Frontend ---
const dateFeedback = computed(() => {
    if (!dates.value.from || !dates.value.to) return { days: 0, holidays: [], isError: false }
    
    const start = dayjs(dates.value.from)
    const end = dayjs(dates.value.to)
    
    if (end.isBefore(start)) {
        return { days: 0, holidays: [], isError: true, message: 'Fecha fin anterior a inicio' }
    }
    
    let days = 0
    const containedHolidays = []
    
    const holidays = leaveContext.data?.holidays || []
    
    let curr = start.clone()
    while (curr.isBefore(end) || curr.isSame(end, 'day')) {
        const dStr = curr.format('YYYY-MM-DD')
        const isWeekend = curr.day() === 0 || curr.day() === 6 // 0=Sun, 6=Sat
        const isHoliday = holidays.includes(dStr)
        
        if (!isWeekend && !isHoliday) {
            days++
        }
        
        if (isHoliday && !isWeekend) {
            containedHolidays.push(curr.format('DD MMM'))
        }
        
        curr = curr.add(1, 'day')
    }
    
    return {
        days,
        holidays: containedHolidays,
        isError: false
    }
})


// Computed options for Autocomplete
const leaveTypeOptions = computed(() => {
    return props.leaveTypes.map(lt => ({
        label: lt.leave_type_name,
        value: lt.name
    }))
})

// Computed for showing layout
const selectedTypeConfig = computed(() => {
    return props.leaveTypes.find(t => t.name === form.value.leave_type)
})

const canRequestHours = computed(() => {
    return selectedTypeConfig.value?.allow_hours_request
})

// Reset logic when type changes
watch(() => form.value.leave_type, () => {
    if (!canRequestHours.value) {
        form.value.request_type = 'Por Días'
    }
})

const submitting = ref(false)

function resetForm() {
    form.value.leave_type = ''
    form.value.request_type = 'Por Días'
    form.value.description = ''
    form.value.hours = 0
    dates.value = { from: '', to: '', single: ''}
    error.value = null
    form.value.hours = 0
    dates.value = { from: '', to: '', single: ''}
    error.value = null
    submitting.value = false
    selectedFile.value = null
    if (fileInput.value) fileInput.value.value = ''
}

function handleFileChange(event) {
    const file = event.target.files[0]
    if (file) {
        selectedFile.value = file
    } else {
        selectedFile.value = null
    }
}

async function uploadFile(docname) {
    if (!selectedFile.value) return

    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('doctype', 'Spanish Leave Application')
    formData.append('docname', docname)
    // formData.append('is_private', 1) // Optional

    try {
        const res = await fetch('/api/method/upload_file', {
            method: 'POST',
            headers: {
                'X-Frappe-CSRF-Token': window.csrf_token || (window.frappe && window.frappe.csrf_token)
            },
            body: formData
        })
        
        if (!res.ok) {
            console.error("Upload failed", res)
            // Non-blocking error, user can attach later
        }
    } catch (e) {
        console.error("Error uploading file", e)
    }
}

async function submitRequest() {
  if (submitting.value) return
  submitting.value = true
  error.value = null
  
  // Helper to exit early
  const stop = () => {
      submitting.value = false
  }
  
  if (!form.value.leave_type) {
      error.value = "Debes seleccionar un tipo de permiso."
      stop()
      return
  }

  const payload = {
      ...form.value,
  }

  if (form.value.request_type === 'Por Días') {
      if (!dates.value.from || !dates.value.to) {
          error.value = "Selecciona un rango de fechas completo."
          stop()
          return
      }
      if (dates.value.from > dates.value.to) {
          error.value = "La fecha de inicio no puede ser posterior a la fecha final."
          stop()
          return
      }
      if (dateFeedback.value.days <= 0) {
           error.value = "El rango seleccionado no contiene días laborables efectivos."
           stop()
           return
      }

      payload.from_date = dates.value.from
      payload.to_date = dates.value.to
  } else {
       if (!dates.value.single) {
          error.value = "Selecciona una fecha."
          stop()
          return
      }
      if (!form.value.hours || form.value.hours <= 0) {
           error.value = "Ingresa una cantidad de horas válida."
           stop()
           return
      }
      payload.request_date = dates.value.single
  }

  try {
    const res = await createRequest.submit(payload)
    if (selectedFile.value && res) {
        // Upload file if selected
        await uploadFile(res)
    }
    emit('success')
    show.value = false
  } catch (e) {
    if (e.messages) {
        error.value = e.messages.join('\n')
    } else {
        error.value = e.message || 'Error al crear la solicitud'
    }
  } finally {
      submitting.value = false
  }
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 3px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}
</style>
```
