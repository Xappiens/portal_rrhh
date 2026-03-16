<template>
  <div class="h-full bg-gray-50 flex overflow-hidden">
    <!-- Left Panel: List -->
    <div class="flex-1 flex flex-col overflow-hidden" :class="selectedVacante ? 'border-r' : ''">
      <!-- Header -->
      <div class="px-6 py-4 bg-white border-b flex items-center justify-between flex-shrink-0">
        <div>
          <h2 class="text-lg font-semibold text-gray-900">Vacantes</h2>
          <p class="text-xs text-gray-500">{{ filteredVacantes.length }} ofertas de trabajo</p>
        </div>
        <Button variant="solid" size="sm" @click="openCreateModal">
          <template #prefix>
            <FeatherIcon name="plus" class="h-4" />
          </template>
          Nueva Vacante
        </Button>
      </div>

      <!-- Stats -->
      <div class="px-6 py-3 bg-white border-b flex-shrink-0">
        <div class="flex gap-3">
          <Card 
            class="flex-1 p-3 cursor-pointer"
            :class="statusFilter === 'Open' ? 'ring-2 ring-green-500' : ''"
            @click="toggleFilter('Open')"
          >
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-green-500"></div>
              <span class="text-xs text-gray-600">Abiertas</span>
              <span class="text-sm font-semibold text-gray-900 ml-auto">{{ stats.open }}</span>
            </div>
          </Card>
          <Card 
            class="flex-1 p-3 cursor-pointer"
            :class="statusFilter === 'Closed' ? 'ring-2 ring-gray-500' : ''"
            @click="toggleFilter('Closed')"
          >
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-gray-400"></div>
              <span class="text-xs text-gray-600">Cerradas</span>
              <span class="text-sm font-semibold text-gray-900 ml-auto">{{ stats.closed }}</span>
            </div>
          </Card>
          <Card class="flex-1 p-3">
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-blue-500"></div>
              <span class="text-xs text-gray-600">Candidatos</span>
              <span class="text-sm font-semibold text-gray-900 ml-auto">{{ stats.totalApplicants }}</span>
            </div>
          </Card>
          <Card class="flex-1 p-3">
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-orange-500"></div>
              <span class="text-xs text-gray-600">Con candidatos</span>
              <span class="text-sm font-semibold text-gray-900 ml-auto">{{ stats.withApplicants }}</span>
            </div>
          </Card>
        </div>
      </div>

      <!-- Filters -->
      <div class="px-6 py-3 bg-white border-b flex-shrink-0">
        <div class="flex items-center gap-2 flex-wrap">
          <div class="flex-1 min-w-[200px]">
            <Input v-model="searchQuery" type="text" placeholder="Buscar por título, empresa..." size="sm">
              <template #prefix>
                <FeatherIcon name="search" class="h-4 text-gray-400" />
              </template>
            </Input>
          </div>
          <select v-model="companyFilter" class="text-xs border border-gray-300 rounded px-2 py-1.5">
            <option value="">Empresa</option>
            <option v-for="c in companiesList" :key="c" :value="c">{{ c }}</option>
          </select>
          <select v-model="departmentFilter" class="text-xs border border-gray-300 rounded px-2 py-1.5">
            <option value="">Departamento</option>
            <option v-for="d in departments" :key="d" :value="d">{{ d }}</option>
          </select>
          <select v-model="designationFilter" class="text-xs border border-gray-300 rounded px-2 py-1.5">
            <option value="">Puesto/Perfil</option>
            <option v-for="d in designationsList" :key="d" :value="d">{{ d }}</option>
          </select>
          <select v-model="locationFilter" class="text-xs border border-gray-300 rounded px-2 py-1.5">
            <option value="">Ubicación</option>
            <option v-for="l in locationsList" :key="l" :value="l">{{ l }}</option>
          </select>
          <select v-model="employmentTypeFilter" class="text-xs border border-gray-300 rounded px-2 py-1.5">
            <option value="">Tipo Empleo</option>
            <option v-for="t in employmentTypesList" :key="t" :value="t">{{ t }}</option>
          </select>
          <select v-model="applicantsFilter" class="text-xs border border-gray-300 rounded px-2 py-1.5">
            <option value="">Candidatos</option>
            <option value="with">Con candidatos</option>
            <option value="without">Sin candidatos</option>
          </select>
          <Button v-if="hasFilters" variant="ghost" size="sm" @click="clearFilters">
            <FeatherIcon name="x" class="h-4" />
          </Button>
        </div>
      </div>

      <!-- List -->
      <div class="flex-1 overflow-y-auto">
        <div v-if="loading" class="p-8 text-center">
          <LoadingIndicator class="h-6 w-6 mx-auto text-gray-500" />
          <p class="text-sm text-gray-500 mt-2">Cargando...</p>
        </div>

        <div v-else-if="filteredVacantes.length === 0" class="p-8 text-center">
          <FeatherIcon name="inbox" class="h-8 w-8 text-gray-300 mx-auto mb-2" />
          <p class="text-sm text-gray-500">No hay vacantes</p>
        </div>

        <div v-else class="divide-y divide-gray-100">
          <div
            v-for="v in paginatedVacantes"
            :key="v.name"
            class="px-6 py-3 hover:bg-gray-50 cursor-pointer flex items-center gap-3"
            :class="{ 'bg-blue-50': selectedVacante?.name === v.name }"
            @click="selectVacante(v)"
          >
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="text-sm font-medium text-gray-900 truncate">{{ v.job_title }}</span>
                <Badge v-if="v.applicant_count" theme="blue" variant="subtle" size="sm">
                  {{ v.applicant_count }}
                </Badge>
              </div>
              <div class="text-xs text-gray-500 truncate">{{ v.company }} · {{ v.department || 'Sin depto.' }}</div>
            </div>
            <Badge 
              :theme="v.status === 'Open' ? 'green' : 'gray'" 
              variant="subtle" 
              size="sm"
              class="cursor-pointer"
              @click.stop="toggleVacanteStatus(v)"
            >
              {{ v.status === 'Open' ? 'Abierta' : 'Cerrada' }}
            </Badge>
            <FeatherIcon name="chevron-right" class="h-4 text-gray-400 flex-shrink-0" />
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="px-6 py-2 bg-white border-t flex items-center justify-center gap-2 flex-shrink-0">
        <Button variant="ghost" size="sm" :disabled="currentPage === 1" @click="currentPage--">
          <FeatherIcon name="chevron-left" class="h-4" />
        </Button>
        <span class="text-xs text-gray-500">{{ currentPage }} / {{ totalPages }}</span>
        <Button variant="ghost" size="sm" :disabled="currentPage >= totalPages" @click="currentPage++">
          <FeatherIcon name="chevron-right" class="h-4" />
        </Button>
      </div>
    </div>

    <!-- Right Panel: Detail -->
    <div v-if="selectedVacante" class="w-1/2 bg-white flex flex-col overflow-hidden">
      <!-- Detail Header -->
      <div class="px-6 py-4 border-b flex items-start justify-between flex-shrink-0">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-1">
            <Badge 
              :theme="selectedVacante.status === 'Open' ? 'green' : 'gray'" 
              variant="subtle" 
              size="sm"
              class="cursor-pointer"
              @click="toggleVacanteStatus(selectedVacante)"
            >
              {{ selectedVacante.status === 'Open' ? 'Abierta' : 'Cerrada' }}
            </Badge>
            <span class="text-xs text-gray-400 font-mono">{{ selectedVacante.name }}</span>
          </div>
          <h3 class="text-base font-semibold text-gray-900">{{ selectedVacante.job_title }}</h3>
          <p class="text-xs text-gray-500">{{ selectedVacante.designation }}</p>
        </div>
        <div class="flex items-center gap-1">
          <Button variant="ghost" size="sm" @click="editVacante(selectedVacante)">
            <FeatherIcon name="edit-2" class="h-4" />
          </Button>
          <Button variant="ghost" size="sm" @click="openInDesk(selectedVacante.name, 'Job Opening')">
            <FeatherIcon name="external-link" class="h-4" />
          </Button>
          <Button variant="ghost" size="sm" @click="selectedVacante = null">
            <FeatherIcon name="x" class="h-4" />
          </Button>
        </div>
      </div>

      <!-- Detail Info -->
      <div class="px-6 py-4 border-b flex-shrink-0">
        <div class="grid grid-cols-2 gap-3 text-sm">
          <div>
            <span class="text-xs text-gray-500">Empresa</span>
            <p class="text-gray-900">{{ selectedVacante.company || '-' }}</p>
          </div>
          <div>
            <span class="text-xs text-gray-500">Departamento</span>
            <p class="text-gray-900">{{ selectedVacante.department || '-' }}</p>
          </div>
          <div>
            <span class="text-xs text-gray-500">Ubicación</span>
            <p class="text-gray-900">{{ selectedVacante.location || '-' }}</p>
          </div>
          <div>
            <span class="text-xs text-gray-500">Plazas</span>
            <p class="text-gray-900">{{ selectedVacante.vacancies || 1 }}</p>
          </div>
          <div>
            <span class="text-xs text-gray-500">Publicada</span>
            <p class="text-gray-900">{{ formatDate(selectedVacante.posted_on) || '-' }}</p>
          </div>
          <div>
            <span class="text-xs text-gray-500">Cierre</span>
            <p :class="isExpired(selectedVacante.closes_on) ? 'text-red-600' : 'text-gray-900'">
              {{ formatDate(selectedVacante.closes_on) || '-' }}
            </p>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="px-6 py-3 border-b flex gap-2 flex-shrink-0">
        <Button variant="outline" size="sm" class="flex-1" @click="goToRecruitmentReports">
          <template #prefix><FeatherIcon name="bar-chart-2" class="h-4" /></template>
          Informes IA
        </Button>
        <Button variant="outline" size="sm" class="flex-1" @click="goToCVAnalysis">
          <template #prefix><FeatherIcon name="cpu" class="h-4" /></template>
          Análisis CV
        </Button>
      </div>

      <!-- Applicants Header -->
      <div class="px-6 py-2 border-b bg-gray-50 flex-shrink-0">
        <span class="text-xs font-medium text-gray-700">Candidatos ({{ applicants.length }})</span>
      </div>

      <!-- Applicants List -->
      <div class="flex-1 overflow-y-auto">
        <div v-if="loadingApplicants" class="p-6 text-center">
          <LoadingIndicator class="h-5 w-5 mx-auto text-gray-500" />
        </div>

        <div v-else-if="applicants.length === 0" class="p-6 text-center text-sm text-gray-500">
          No hay candidatos
        </div>

        <div v-else class="divide-y divide-gray-100">
          <div v-for="a in applicants" :key="a.name" class="px-6 py-3 hover:bg-gray-50">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-xs font-medium text-gray-600">
                  {{ getInitials(a.applicant_name) }}
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-900">{{ a.applicant_name }}</p>
                  <p class="text-xs text-gray-500">{{ a.email_id }}</p>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <Badge v-if="a.custom_ai_score" :theme="getScoreTheme(a.custom_ai_score)" variant="subtle" size="sm">
                  {{ a.custom_ai_score }}%
                </Badge>
                <Badge 
                  :theme="getApplicantStatusTheme(a.status)" 
                  variant="subtle" 
                  size="sm"
                  class="cursor-pointer"
                  @click="cycleApplicantStatus(a)"
                >
                  {{ getApplicantStatusLabel(a.status) }}
                </Badge>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Dialog -->
    <Dialog v-model="showCreateModal" :options="{ title: editingVacante ? 'Editar Vacante' : 'Nueva Vacante', size: '2xl' }">
      <template #body-content>
        <form @submit.prevent="saveVacante" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-xs font-medium text-gray-700 mb-1 block">Título *</label>
              <Input v-model="form.job_title" type="text" size="sm" required />
            </div>
            <div>
              <label class="text-xs font-medium text-gray-700 mb-1 block">Designación *</label>
              <select v-model="form.designation" class="w-full text-sm border border-gray-300 rounded px-3 py-1.5" required>
                <option value="">Seleccionar</option>
                <option v-for="d in designations" :key="d.name" :value="d.name">{{ d.name }}</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-xs font-medium text-gray-700 mb-1 block">Empresa *</label>
              <select v-model="form.company" class="w-full text-sm border border-gray-300 rounded px-3 py-1.5" required>
                <option value="">Seleccionar</option>
                <option v-for="c in companies" :key="c.name" :value="c.name">{{ c.name }}</option>
              </select>
            </div>
            <div>
              <label class="text-xs font-medium text-gray-700 mb-1 block">Departamento</label>
              <select v-model="form.department" class="w-full text-sm border border-gray-300 rounded px-3 py-1.5">
                <option value="">Seleccionar</option>
                <option v-for="d in departmentsList" :key="d.name" :value="d.name">{{ d.name }}</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-3 gap-4">
            <div>
              <label class="text-xs font-medium text-gray-700 mb-1 block">Ubicación</label>
              <select v-model="form.location" class="w-full text-sm border border-gray-300 rounded px-3 py-1.5">
                <option value="">Seleccionar</option>
                <option v-for="l in branches" :key="l.name" :value="l.name">{{ l.name }}</option>
              </select>
            </div>
            <div>
              <label class="text-xs font-medium text-gray-700 mb-1 block">Tipo Empleo</label>
              <select v-model="form.employment_type" class="w-full text-sm border border-gray-300 rounded px-3 py-1.5">
                <option value="">Seleccionar</option>
                <option v-for="t in employmentTypes" :key="t.name" :value="t.name">{{ t.name }}</option>
              </select>
            </div>
            <div>
              <label class="text-xs font-medium text-gray-700 mb-1 block">Plazas</label>
              <Input v-model.number="form.vacancies" type="number" size="sm" min="1" />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-xs font-medium text-gray-700 mb-1 block">Fecha Publicación</label>
              <Input v-model="form.posted_on" type="date" size="sm" />
            </div>
            <div>
              <label class="text-xs font-medium text-gray-700 mb-1 block">Fecha Cierre</label>
              <Input v-model="form.closes_on" type="date" size="sm" />
            </div>
          </div>

          <div class="grid grid-cols-4 gap-4">
            <div>
              <label class="text-xs font-medium text-gray-700 mb-1 block">Moneda</label>
              <select v-model="form.currency" class="w-full text-sm border border-gray-300 rounded px-3 py-1.5">
                <option value="EUR">EUR</option>
                <option value="USD">USD</option>
              </select>
            </div>
            <div>
              <label class="text-xs font-medium text-gray-700 mb-1 block">Salario Mín</label>
              <Input v-model.number="form.lower_range" type="number" size="sm" />
            </div>
            <div>
              <label class="text-xs font-medium text-gray-700 mb-1 block">Salario Máx</label>
              <Input v-model.number="form.upper_range" type="number" size="sm" />
            </div>
            <div>
              <label class="text-xs font-medium text-gray-700 mb-1 block">Por</label>
              <select v-model="form.salary_per" class="w-full text-sm border border-gray-300 rounded px-3 py-1.5">
                <option value="Month">Mes</option>
                <option value="Year">Año</option>
              </select>
            </div>
          </div>

          <div>
            <label class="text-xs font-medium text-gray-700 mb-1 block">Descripción</label>
            <textarea v-model="form.description" rows="4" class="w-full text-sm border border-gray-300 rounded px-3 py-2"></textarea>
          </div>

          <div class="flex justify-end gap-2 pt-4 border-t">
            <Button variant="outline" size="sm" type="button" @click="closeCreateModal">Cancelar</Button>
            <Button variant="solid" size="sm" type="submit" :loading="saving">{{ editingVacante ? 'Guardar' : 'Crear' }}</Button>
          </div>
        </form>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { FeatherIcon, Button, Card, Badge, Input, Dialog, LoadingIndicator, call, debounce } from 'frappe-ui'

const router = useRouter()

const loading = ref(true)
const saving = ref(false)
const vacantes = ref([])
const applicants = ref([])
const loadingApplicants = ref(false)

const searchQuery = ref('')
const statusFilter = ref('')
const departmentFilter = ref('')
const companyFilter = ref('')
const designationFilter = ref('')
const locationFilter = ref('')
const employmentTypeFilter = ref('')
const applicantsFilter = ref('')
const currentPage = ref(1)
const itemsPerPage = 20

const showCreateModal = ref(false)
const selectedVacante = ref(null)
const editingVacante = ref(null)

const form = ref(getEmptyForm())

const companies = ref([])
const departmentsList = ref([])
const designations = ref([])
const employmentTypes = ref([])
const branches = ref([])

const stats = computed(() => ({
  open: vacantes.value.filter(v => v.status === 'Open').length,
  closed: vacantes.value.filter(v => v.status === 'Closed').length,
  totalApplicants: vacantes.value.reduce((sum, v) => sum + (v.applicant_count || 0), 0),
  withApplicants: vacantes.value.filter(v => (v.applicant_count || 0) > 0).length
}))

const departments = computed(() => {
  return [...new Set(vacantes.value.map(v => v.department).filter(Boolean))].sort()
})

const companiesList = computed(() => {
  return [...new Set(vacantes.value.map(v => v.company).filter(Boolean))].sort()
})

const designationsList = computed(() => {
  return [...new Set(vacantes.value.map(v => v.designation).filter(Boolean))].sort()
})

const locationsList = computed(() => {
  return [...new Set(vacantes.value.map(v => v.location).filter(Boolean))].sort()
})

const employmentTypesList = computed(() => {
  return [...new Set(vacantes.value.map(v => v.employment_type).filter(Boolean))].sort()
})

const hasFilters = computed(() => 
  searchQuery.value || statusFilter.value || departmentFilter.value || 
  companyFilter.value || designationFilter.value || locationFilter.value || 
  employmentTypeFilter.value || applicantsFilter.value
)

const filteredVacantes = computed(() => {
  let result = [...vacantes.value]
  
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(v => 
      v.job_title?.toLowerCase().includes(q) ||
      v.company?.toLowerCase().includes(q) ||
      v.designation?.toLowerCase().includes(q)
    )
  }
  
  if (statusFilter.value) {
    result = result.filter(v => v.status === statusFilter.value)
  }
  
  if (departmentFilter.value) {
    result = result.filter(v => v.department === departmentFilter.value)
  }
  
  if (companyFilter.value) {
    result = result.filter(v => v.company === companyFilter.value)
  }
  
  if (designationFilter.value) {
    result = result.filter(v => v.designation === designationFilter.value)
  }
  
  if (locationFilter.value) {
    result = result.filter(v => v.location === locationFilter.value)
  }
  
  if (employmentTypeFilter.value) {
    result = result.filter(v => v.employment_type === employmentTypeFilter.value)
  }
  
  if (applicantsFilter.value === 'with') {
    result = result.filter(v => (v.applicant_count || 0) > 0)
  } else if (applicantsFilter.value === 'without') {
    result = result.filter(v => (v.applicant_count || 0) === 0)
  }
  
  return result
})

const totalPages = computed(() => Math.ceil(filteredVacantes.value.length / itemsPerPage))

const paginatedVacantes = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  return filteredVacantes.value.slice(start, start + itemsPerPage)
})

function getEmptyForm() {
  return {
    job_title: '', designation: '', company: '', department: '',
    employment_type: '', location: '', vacancies: 1,
    posted_on: new Date().toISOString().split('T')[0], closes_on: '',
    currency: 'EUR', lower_range: null, upper_range: null, salary_per: 'Month',
    description: '', publish: false, publish_salary_range: false
  }
}

async function loadVacantes() {
  loading.value = true
  try {
    const result = await call('frappe.client.get_list', {
      doctype: 'Job Opening',
      fields: ['name', 'job_title', 'designation', 'status', 'company', 'department', 
               'location', 'employment_type', 'vacancies', 'posted_on', 'closes_on', 
               'description', 'currency', 'lower_range', 'upper_range', 'salary_per'],
      limit_page_length: 0,
      order_by: 'modified desc'
    })
    
    const counts = await call('frappe.client.get_list', {
      doctype: 'Job Applicant',
      fields: ['job_title', 'count(name) as count'],
      group_by: 'job_title',
      limit_page_length: 0
    })
    
    const countMap = {}
    counts.forEach(item => { countMap[item.job_title] = item.count })
    
    vacantes.value = (result || []).map(v => ({
      ...v,
      applicant_count: countMap[v.name] || 0
    }))
  } catch (error) {
    console.error('Error:', error)
  } finally {
    loading.value = false
  }
}

async function loadApplicants(jobOpening) {
  loadingApplicants.value = true
  applicants.value = []
  try {
    const result = await call('frappe.client.get_list', {
      doctype: 'Job Applicant',
      fields: ['name', 'applicant_name', 'email_id', 'status', 'custom_ai_score'],
      filters: { job_title: jobOpening },
      order_by: 'custom_ai_score desc',
      limit_page_length: 100
    })
    applicants.value = result || []
  } catch (error) {
    console.error('Error:', error)
  } finally {
    loadingApplicants.value = false
  }
}

async function loadFormData() {
  try {
    const [c, d, des, e, b] = await Promise.all([
      call('frappe.client.get_list', { doctype: 'Company', fields: ['name'], limit_page_length: 100 }),
      call('frappe.client.get_list', { doctype: 'Department', fields: ['name'], limit_page_length: 100 }),
      call('frappe.client.get_list', { doctype: 'Designation', fields: ['name'], limit_page_length: 500 }),
      call('frappe.client.get_list', { doctype: 'Employment Type', fields: ['name'], limit_page_length: 50 }),
      call('frappe.client.get_list', { doctype: 'Branch', fields: ['name'], limit_page_length: 100 })
    ])
    companies.value = c || []
    departmentsList.value = d || []
    designations.value = des || []
    employmentTypes.value = e || []
    branches.value = b || []
  } catch (error) {
    console.error('Error:', error)
  }
}

function toggleFilter(status) {
  statusFilter.value = statusFilter.value === status ? '' : status
  currentPage.value = 1
}

function clearFilters() {
  searchQuery.value = ''
  statusFilter.value = ''
  departmentFilter.value = ''
  companyFilter.value = ''
  designationFilter.value = ''
  locationFilter.value = ''
  employmentTypeFilter.value = ''
  applicantsFilter.value = ''
  currentPage.value = 1
}

function selectVacante(v) {
  selectedVacante.value = v
  loadApplicants(v.name)
}

function openCreateModal() {
  editingVacante.value = null
  form.value = getEmptyForm()
  showCreateModal.value = true
}

function editVacante(v) {
  editingVacante.value = v
  form.value = { ...v }
  showCreateModal.value = true
}

function closeCreateModal() {
  showCreateModal.value = false
  editingVacante.value = null
}

async function saveVacante() {
  saving.value = true
  try {
    if (editingVacante.value) {
      await call('frappe.client.set_value', {
        doctype: 'Job Opening',
        name: editingVacante.value.name,
        fieldname: form.value
      })
    } else {
      await call('frappe.client.insert', {
        doc: { doctype: 'Job Opening', ...form.value, status: 'Open' }
      })
    }
    closeCreateModal()
    await loadVacantes()
  } catch (error) {
    console.error('Error:', error)
  } finally {
    saving.value = false
  }
}

async function toggleVacanteStatus(v) {
  const newStatus = v.status === 'Open' ? 'Closed' : 'Open'
  try {
    await call('frappe.client.set_value', {
      doctype: 'Job Opening',
      name: v.name,
      fieldname: { status: newStatus }
    })
    v.status = newStatus
  } catch (error) {
    console.error('Error:', error)
  }
}

const applicantStatuses = ['Open', 'Replied', 'Hold', 'Accepted', 'Rejected']

async function cycleApplicantStatus(a) {
  const currentIndex = applicantStatuses.indexOf(a.status)
  const nextIndex = (currentIndex + 1) % applicantStatuses.length
  const newStatus = applicantStatuses[nextIndex]
  
  try {
    await call('frappe.client.set_value', {
      doctype: 'Job Applicant',
      name: a.name,
      fieldname: { status: newStatus }
    })
    a.status = newStatus
  } catch (error) {
    console.error('Error:', error)
  }
}

function getApplicantStatusLabel(status) {
  const labels = { Open: 'Abierto', Replied: 'Respondido', Hold: 'Espera', Accepted: 'Aceptado', Rejected: 'Rechazado' }
  return labels[status] || status
}

function getApplicantStatusTheme(status) {
  const themes = { Open: 'blue', Replied: 'purple', Hold: 'orange', Accepted: 'green', Rejected: 'red' }
  return themes[status] || 'gray'
}

function getScoreTheme(score) {
  if (score >= 70) return 'green'
  if (score >= 50) return 'orange'
  return 'red'
}

function goToRecruitmentReports() {
  if (selectedVacante.value) {
    router.push({ name: 'RecruitmentReports', params: { jobOpening: selectedVacante.value.name } })
  }
}

function goToCVAnalysis() {
  if (selectedVacante.value) {
    router.push({ name: 'CVAnalysis', params: { jobOpening: selectedVacante.value.name } })
  }
}

function openInDesk(name, doctype) {
  window.open(`/app/${doctype.toLowerCase().replace(/ /g, '-')}/${name}`, '_blank')
}

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })
}

function isExpired(d) {
  return d && new Date(d) < new Date()
}

function getInitials(name) {
  if (!name) return '?'
  return name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
}

watch(searchQuery, debounce(() => { currentPage.value = 1 }, 300))

onMounted(async () => {
  await Promise.all([loadVacantes(), loadFormData()])
})
</script>
