<template>
  <div class="flex flex-col h-full overflow-hidden">
    <div class="flex-1 overflow-y-auto">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div class="md:flex md:items-center md:justify-between mb-6">
      <div class="flex-1 min-w-0">
        <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
          Onboarding
        </h2>
        <p class="mt-1 text-sm text-gray-500">
          Documentos pendientes de lectura y firma.
        </p>
      </div>
      <div class="mt-4 flex md:mt-0 md:ml-4">
        <Button variant="outline" @click="fetchDocs">
          <template #prefix>
            <FeatherIcon name="refresh-cw" class="w-4 h-4" />
          </template>
          Actualizar
        </Button>
      </div>
    </div>

    <div v-if="error" class="mb-6">
        <ErrorMessage :message="error" />
    </div>

    <div v-if="loading" class="flex justify-center py-10">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
    </div>

    <div v-else-if="docs.length === 0" class="text-center py-10 text-gray-500">
      <FeatherIcon name="check-circle" class="w-12 h-12 mx-auto mb-4 text-green-500" />
      <p class="text-lg">No se encontró historial de onboarding.</p>
    </div>

    <div v-else class="space-y-6">
      <div v-for="(group, processName) in groupedDocs" :key="processName" class="border rounded-lg bg-white overflow-hidden shadow-sm">
        
        <!-- Header -->
        <div 
          @click="toggleGroup(processName)"
          class="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50 transition-colors select-none"
        >
          <div class="flex items-center space-x-3">
             <div class="p-2 rounded-full" :class="group.isOpen ? 'bg-blue-50 text-blue-600' : 'bg-gray-100 text-gray-500'">
                <FeatherIcon :name="group.isOpen ? 'chevron-down' : 'chevron-right'" class="w-5 h-5 transition-transform duration-200" />
             </div>
             <div>
                <h3 class="text-lg font-medium text-gray-900">
                  {{ group.title }}
                </h3>
                <div class="flex items-center text-sm text-gray-500 space-x-2 mt-1">
                   <span>{{ formatDate(group.creation) }}</span>
                   <span>&bull;</span>
                   <Badge :theme="getProcessBadgeTheme(group.status)">
                      {{ getProcessStatusLabel(group.status) }}
                   </Badge>
                   <span class="text-xs text-gray-400">({{ group.docs.length }} docs)</span>
                </div>
             </div>
          </div>
        </div>

        <!-- Body (Grid of Cards) -->
        <div v-if="group.isOpen" class="p-6 border-t border-gray-100 bg-gray-50/50">
            <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              <Card
                v-for="doc in group.docs"
                :key="doc.row_name"
                class="flex flex-col h-full hover:shadow-lg transition-shadow duration-200 bg-white"
              >
                <div class="p-6 flex-1 flex flex-col">
                  <div class="flex items-start justify-between">
                     <div class="flex-1">
                         <h3 class="text-lg font-medium text-gray-900 mb-2 truncate" :title="doc.title">
                          {{ doc.title }}
                        </h3>
                        <div class="flex items-center space-x-2">
                            <Badge :theme="doc.is_completed ? 'green' : 'orange'">
                                {{ doc.is_completed ? 'Firmado' : 'Pendiente' }}
                            </Badge>
                        </div>
                     </div>
                     <FeatherIcon :name="doc.is_completed ? 'check-circle' : 'file-text'" 
                        :class="doc.is_completed ? 'text-green-500' : 'text-gray-400'" class="w-6 h-6 flex-shrink-0" />
                  </div>
                  
                  <p class="mt-4 text-sm text-gray-500 line-clamp-3">
                    {{ doc.description || 'Sin descripción' }}
                  </p>
                  
                  <div class="mt-6 pt-4 border-t border-gray-100 flex items-center justify-between">
                     <span class="text-xs text-gray-400">
                        {{ doc.type }}
                     </span>
                     <Button 
                        v-if="!doc.is_completed" 
                        variant="solid" 
                        @click="openDoc(doc)"
                     >
                       Revisar y Firmar
                     </Button>
                     <span v-else class="text-xs text-green-600 font-medium">
                         Completado el {{ formatDate(doc.completion_date) }}
                     </span>
                     <Button
                        v-if="doc.file_url"
                        variant="outline"
                        @click="downloadFile(doc.file_url)"
                        class="ml-2 px-2"
                        title="Descargar Archivo Adjunto"
                     >
                        <FeatherIcon name="download" class="w-4 h-4" />
                     </Button>
                  </div>
                </div>
              </Card>
            </div>
        </div>

      </div>
    </div>

    <!-- Document Viewer Modal -->
    <Dialog v-model="showModal" :options="{ size: '4xl' }">
      <template #body-title>
        <h3 class="text-lg font-bold">{{ selectedDoc?.title }}</h3>
      </template>
      <template #body-content>
        <div class="min-h-[400px] max-h-[60vh] overflow-y-auto border rounded bg-gray-50 p-4">
            <!-- File Link (Always visible if exists) -->
            <div v-if="selectedDoc?.file_url" class="mb-6 p-4 bg-blue-50 border border-blue-100 rounded-lg flex items-center justify-between">
                 <div class="flex items-center">
                    <FeatherIcon name="paperclip" class="w-5 h-5 text-blue-500 mr-2"/>
                    <span class="text-sm text-blue-700 font-medium">Documento Adjunto Disponible</span>
                 </div>
                 <a :href="selectedDoc.file_url" target="_blank" class="flex items-center text-white bg-blue-600 hover:bg-blue-700 px-3 py-1.5 rounded text-sm transition-colors">
                    <FeatherIcon name="download" class="w-4 h-4 mr-2"/>
                    Descargar
                 </a>
            </div>

            <!-- HTML Content -->
            <div v-if="selectedDoc?.html_content" v-html="selectedDoc.html_content" class="prose max-w-none"></div>
            
            <!-- Fallback if only file and no HTML, maybe show preview iframe? -->
            <div v-else-if="selectedDoc?.file_url && !selectedDoc?.html_content" class="flex flex-col items-center justify-center h-full mt-4">
                 <iframe v-if="isPdf(selectedDoc.file_url)" :src="selectedDoc.file_url" class="w-full h-[500px]" frameborder="0"></iframe>
                 <div v-else class="text-center text-gray-500">
                    <p>Vista previa no disponible.</p>
                    <p>Por favor descargue el archivo para visualizarlo.</p>
                 </div>
            </div>
            
            <div v-if="!selectedDoc?.html_content && !selectedDoc?.file_url" class="text-gray-500 italic text-center py-10">
                No hay contenido visualizable. Por favor contacte a RRHH.
            </div>
        </div>
        
        <div v-if="error" class="mt-4">
            <ErrorMessage :message="error" />
        </div>

        <div class="mt-4 p-4 bg-yellow-50 rounded border border-yellow-100">
            <label class="flex items-start space-x-3 cursor-pointer">
                <input type="checkbox" v-model="hasRead" class="mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 transition duration-150 ease-in-out">
                <span class="text-sm text-gray-700">
                    Declaro que he leído, comprendido y acepto el contenido del documento <strong>{{ selectedDoc?.title }}</strong>. 
                    Entiendo que al hacer clic en "Firmar Documento", se registrará mi aceptación con fecha y hora.
                </span>
            </label>
        </div>
      </template>
      <template #actions>
        <div class="flex justify-end space-x-2">
            <Button variant="subtle" @click="showModal = false">Cancelar</Button>
            <Button 
                variant="solid" 
                theme="blue" 
                :loading="signing" 
                :disabled="!hasRead"
                @click="signDoc"
            >
                Firmar Documento
            </Button>
        </div>
      </template>
    </Dialog>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { createResource, ErrorMessage } from 'frappe-ui'

// Resources
const pendingDocs = createResource({
    url: 'portal_rrhh.api.onboarding.get_my_onboarding_docs',
    auto: true
})

const signDocResource = createResource({
    url: 'portal_rrhh.api.signing.sign_document'
})

// UI State
const showModal = ref(false)
const selectedDoc = ref(null)
const hasRead = ref(false)
const openGroups = ref({}) // track open/closed state of accordions

// Helpers for grouping
const groupedDocs = computed(() => {
    if (!pendingDocs.data) return {}
    
    const groups = {}
    // The API returns sorted by newest first, so we process in order
    pendingDocs.data.forEach(doc => {
        if (!groups[doc.process_name]) {
            groups[doc.process_name] = {
                id: doc.process_name,
                title: doc.process_title || doc.process_name,
                status: doc.process_status,
                creation: doc.process_creation,
                docs: [],
                isOpen: false // reactive state will override this
            }
        }
        groups[doc.process_name].docs.push(doc)
    })

    // Apply reactive open state
    // Default: Open the first one (newest), close others
    const keys = Object.keys(groups)
    keys.forEach((key, index) => {
        if (openGroups.value[key] === undefined) {
             // Initialize state: First one open, others closed
             openGroups.value[key] = (index === 0)
        }
        groups[key].isOpen = openGroups.value[key]
    })
    
    return groups
})

const toggleGroup = (processName) => {
    openGroups.value[processName] = !openGroups.value[processName]
}

const getProcessBadgeTheme = (status) => {
    if (status === 'Completed') return 'green'
    if (status === 'Pending') return 'orange'
    if (status === 'In Progress') return 'blue'
    if (status === 'Cancelled') return 'red'
    return 'gray'
}

const getProcessStatusLabel = (status) => {
    if (status === 'Completed') return 'Completado'
    if (status === 'Pending') return 'Pendiente'
    if (status === 'In Progress') return 'En Progreso'
    if (status === 'Cancelled') return 'Cancelado'
    return status
}


// Computed wrappers
const docs = computed(() => pendingDocs.data || [])
const loading = computed(() => pendingDocs.loading)
const error = computed(() => {
    // Collect errors from both resources
    if (pendingDocs.error) return pendingDocs.error.message || pendingDocs.error
    if (signDocResource.error) return signDocResource.error.message || signDocResource.error
    return null
})
const signing = computed(() => signDocResource.loading)

const fetchDocs = () => {
    pendingDocs.fetch()
}

const openDoc = (doc) => {
    selectedDoc.value = doc
    hasRead.value = false
    showModal.value = true
    // Clear previous errors if any, though createResource handles its own state
    signDocResource.reset() 
}

const signDoc = async () => {
    if(!selectedDoc.value || !hasRead.value) return
    
    try {
        await signDocResource.submit({
            process_name: selectedDoc.value.process_name,
            row_name: selectedDoc.value.row_name
        })
        
        alert('Documento firmado correctamente')
        showModal.value = false
        pendingDocs.reload()
    } catch (e) {
        console.error(e)
        // Error is handled by computed `error` property
    }
}

const formatDate = (dateStr) => {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleDateString()
}

const isPdf = (url) => {
    return url?.toLowerCase().endsWith('.pdf')
}

const downloadFile = (url) => {
    window.open(url, '_blank')
}
</script>
