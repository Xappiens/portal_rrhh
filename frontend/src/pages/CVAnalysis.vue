<template>
  <div class="flex-1 p-6 bg-gray-50 overflow-y-auto h-full">
    <!-- Header -->
    <div class="mb-8">
      <h2 class="text-2xl font-semibold text-gray-900 mb-2">📄 Análisis de CV con IA</h2>
      <p class="text-sm text-gray-600">Analiza CVs de candidatos usando IA para evaluar la adecuación y coincidencia de habilidades</p>
    </div>

    <!-- Input Form Section -->
    <div v-if="!effectiveJobApplicant || !effectiveJobOpening" class="mb-6">
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-2">📝 Ingresar Detalles del Análisis</h3>
        <p class="text-sm text-gray-600 mb-6">Selecciona un Solicitante de Empleo y una Vacante de los menús desplegables a continuación. La Vacante se completará automáticamente cuando selecciones un Solicitante de Empleo.</p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div class="relative">
            <label for="job-applicant-input" class="block text-sm font-medium text-gray-700 mb-2">
              <span>👤</span> Solicitante de Empleo
            </label>
            <div class="flex gap-2">
              <div class="relative flex-1">
                <input
                  id="job-applicant-input"
                  type="text"
                  v-model="applicantSearchText"
                  @input="onApplicantSearchInput"
                  @focus="onApplicantFocus"
                  @blur="handleApplicantBlur"
                  @keydown.enter.prevent="handleApplicantEnter"
                  @keydown.escape="showApplicantDropdown = false"
                  @keydown.down.prevent="navigateApplicantDropdown(1)"
                  @keydown.up.prevent="navigateApplicantDropdown(-1)"
                  :placeholder="formJobApplicant ? 'Escribe el ID o nombre del Solicitante...' : 'Escribe el ID o nombre del Solicitante manualmente...'"
                  :disabled="loadingJobApplicants"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                />
                <div v-if="formJobApplicant" class="absolute right-2 top-1/2 transform -translate-y-1/2">
                  <button
                    @click="clearApplicant"
                    class="text-gray-400 hover:text-gray-600"
                    type="button"
                  >
                    ✕
                  </button>
                </div>
              </div>
              <button
                type="button"
                @click="toggleApplicantDropdown"
                :disabled="loadingJobApplicants"
                class="px-4 py-2 border border-gray-300 rounded-lg bg-white hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                title="Explorar lista de solicitantes"
              >
                <span class="text-lg">▼</span>
              </button>
            </div>
            <!-- Dropdown with filtered results - appears below the input -->
            <div
              v-if="showApplicantDropdown"
              class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto"
            >
              <div v-if="filteredApplicants.length > 0" class="p-2">
                <div class="text-xs text-gray-500 px-2 py-1 mb-1 font-semibold">Seleccionar de la lista ({{ filteredApplicants.length }} resultados):</div>
              <div
                v-for="(applicant, index) in filteredApplicants"
                :key="applicant.name"
                @mousedown.prevent="selectApplicant(applicant)"
                :class="[
                  'px-4 py-2 cursor-pointer border-b border-gray-100 last:border-b-0',
                  index === highlightedApplicantIndex ? 'bg-blue-100' : 'hover:bg-blue-50'
                ]"
              >
                <div class="font-medium text-gray-900">{{ applicant.applicant_name || applicant.name }}</div>
                <div class="text-sm text-gray-500">{{ applicant.email_id || '' }}</div>
                <div class="text-xs text-gray-400 font-mono">{{ applicant.name }}</div>
              </div>
              </div>
              <div v-else-if="applicantSearchText" class="p-4 text-sm text-gray-500 text-center">
                No se encontraron solicitantes que coincidan con "{{ applicantSearchText }}"
              </div>
              <div v-else class="p-4 text-sm text-gray-500 text-center">
                Comienza a escribir para buscar, o desplázate para explorar todos los solicitantes
              </div>
            </div>
            <p v-if="loadingJobApplicants" class="text-xs text-gray-500 mt-1">Cargando solicitantes...</p>
            <p v-if="formJobApplicant && !loadingJobApplicants" class="text-xs text-green-600 mt-1">
              ✓ Seleccionado: {{ getApplicantDisplayName(formJobApplicant) }}
            </p>
          </div>

          <div class="relative">
            <label for="job-opening-input" class="block text-sm font-medium text-gray-700 mb-2">
              <span>💼</span> Vacante
            </label>
            <div class="flex gap-2">
              <div class="relative flex-1">
                <input
                  id="job-opening-input"
                  type="text"
                  v-model="openingSearchText"
                  @input="onOpeningSearchInput"
                  @focus="onOpeningFocus"
                  @blur="handleOpeningBlur"
                  @keydown.enter.prevent="handleOpeningEnter"
                  @keydown.escape="showOpeningDropdown = false"
                  @keydown.down.prevent="navigateOpeningDropdown(1)"
                  @keydown.up.prevent="navigateOpeningDropdown(-1)"
                  :placeholder="formJobOpening ? 'Escribe el ID o nombre de la Vacante...' : 'Escribe el ID o nombre de la Vacante manualmente...'"
                  :disabled="loadingJobOpenings"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                />
                <div v-if="formJobOpening" class="absolute right-2 top-1/2 transform -translate-y-1/2">
                  <button
                    @click="clearOpening"
                    class="text-gray-400 hover:text-gray-600"
                    type="button"
                  >
                    ✕
                  </button>
                </div>
              </div>
              <button
                type="button"
                @click="toggleOpeningDropdown"
                :disabled="loadingJobOpenings"
                class="px-4 py-2 border border-gray-300 rounded-lg bg-white hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                title="Explorar lista de vacantes"
              >
                <span class="text-lg">▼</span>
              </button>
            </div>
            <!-- Dropdown with filtered results - appears below the input -->
            <div
              v-if="showOpeningDropdown"
              class="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto"
            >
              <div v-if="filteredOpenings.length > 0" class="p-2">
                <div class="text-xs text-gray-500 px-2 py-1 mb-1 font-semibold">Seleccionar de la lista ({{ filteredOpenings.length }} resultados):</div>
              <div
                v-for="(opening, index) in filteredOpenings"
                :key="opening.name"
                @mousedown.prevent="selectOpening(opening)"
                :class="[
                  'px-4 py-2 cursor-pointer border-b border-gray-100 last:border-b-0',
                  index === highlightedOpeningIndex ? 'bg-blue-100' : 'hover:bg-blue-50'
                ]"
              >
                <div class="font-medium text-gray-900">{{ opening.job_title || opening.name }}</div>
                <div class="text-sm text-gray-500">{{ opening.designation || '' }}</div>
                <div class="text-xs text-gray-400 font-mono">{{ opening.name }}</div>
              </div>
              </div>
              <div v-else-if="openingSearchText" class="p-4 text-sm text-gray-500 text-center">
                No se encontraron vacantes que coincidan con "{{ openingSearchText }}"
              </div>
              <div v-else class="p-4 text-sm text-gray-500 text-center">
                Comienza a escribir para buscar, o desplázate para explorar todas las vacantes
              </div>
            </div>
            <p v-if="loadingJobOpenings" class="text-xs text-gray-500 mt-1">Cargando vacantes...</p>
            <p v-if="formJobOpening && !loadingJobOpenings" class="text-xs text-green-600 mt-1">
              ✓ Seleccionado: {{ getOpeningDisplayName(formJobOpening) }}
            </p>
          </div>
        </div>

        <button 
          @click="startAnalysis" 
          :disabled="!canAnalyze || isAnalyzing" 
          class="w-full px-6 py-3 bg-blue-500 text-white rounded-lg font-semibold hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          <span v-if="isAnalyzing">🔄 Analizando...</span>
          <span v-else>🚀 Iniciar Análisis con IA</span>
        </button>
      </div>
    </div>

    <!-- Analysis Controls -->
    <div v-else class="mb-6">
      <div class="bg-white rounded-lg shadow p-6 mb-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="border-r border-gray-200 pr-6">
            <div class="flex items-center gap-3 mb-4 pb-3 border-b border-gray-200">
              <span class="text-2xl">👤</span>
              <h4 class="text-lg font-semibold text-gray-900">Solicitante de Empleo</h4>
              <span class="text-xs text-gray-500 font-mono ml-auto">{{ effectiveJobApplicant }}</span>
            </div>
            <div v-if="applicantData" class="space-y-2">
              <p class="text-sm"><span class="font-medium text-gray-700">Nombre:</span> <span class="text-gray-900">{{ applicantData.applicant_name || 'N/A' }}</span></p>
              <p class="text-sm"><span class="font-medium text-gray-700">Correo:</span> <span class="text-gray-900">{{ applicantData.email_id || 'N/A' }}</span></p>
              <p v-if="applicantData.phone_number" class="text-sm"><span class="font-medium text-gray-700">Teléfono:</span> <span class="text-gray-900">{{ applicantData.phone_number }}</span></p>
              <p v-if="applicantData.designation" class="text-sm"><span class="font-medium text-gray-700">Designación:</span> <span class="text-gray-900">{{ applicantData.designation }}</span></p>
              <p v-if="applicantData.status" class="text-sm"><span class="font-medium text-gray-700">Estado:</span> <span class="text-gray-900">{{ applicantData.status }}</span></p>
            </div>
            <div v-else class="text-sm text-gray-500 italic">Cargando datos del solicitante...</div>
          </div>

          <div>
            <div class="flex items-center gap-3 mb-4 pb-3 border-b border-gray-200">
              <span class="text-2xl">💼</span>
              <h4 class="text-lg font-semibold text-gray-900">Vacante</h4>
              <span class="text-xs text-gray-500 font-mono ml-auto">{{ effectiveJobOpening }}</span>
            </div>
            <div v-if="jobOpeningData" class="space-y-2">
              <p class="text-sm"><span class="font-medium text-gray-700">Título:</span> <span class="text-gray-900">{{ jobOpeningData.job_title || 'N/A' }}</span></p>
              <p v-if="jobOpeningData.designation" class="text-sm"><span class="font-medium text-gray-700">Designación:</span> <span class="text-gray-900">{{ jobOpeningData.designation }}</span></p>
              <p v-if="jobOpeningData.company" class="text-sm"><span class="font-medium text-gray-700">Empresa:</span> <span class="text-gray-900">{{ jobOpeningData.company }}</span></p>
              <p v-if="jobOpeningData.department" class="text-sm"><span class="font-medium text-gray-700">Departamento:</span> <span class="text-gray-900">{{ jobOpeningData.department }}</span></p>
              <p v-if="jobOpeningData.location" class="text-sm"><span class="font-medium text-gray-700">Ubicación:</span> <span class="text-gray-900">{{ jobOpeningData.location }}</span></p>
              <p v-if="jobOpeningData.employment_type" class="text-sm"><span class="font-medium text-gray-700">Tipo:</span> <span class="text-gray-900">{{ jobOpeningData.employment_type }}</span></p>
              <p v-if="jobOpeningData.status" class="text-sm"><span class="font-medium text-gray-700">Estado:</span> <span class="text-gray-900">{{ jobOpeningData.status }}</span></p>
            </div>
            <div v-else class="text-sm text-gray-500 italic">Cargando datos de la vacante...</div>
          </div>
        </div>
      </div>
      <div class="flex gap-3 flex-wrap">
        <button @click="analyzeCV" :disabled="isAnalyzing" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed">
          <span v-if="isAnalyzing">🔄 Analizando...</span>
          <span v-else>🔍 Analizar CV</span>
        </button>
        <button @click="clearInputs" class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700">Cambiar IDs</button>
        <button v-if="analysis" @click="reloadAnalysis" class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700">🔄 Recargar</button>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span class="text-xl">⚠️</span>
        <div>
          <strong class="text-red-800">Error:</strong> 
          <span class="text-red-700">{{ error }}</span>
        </div>
      </div>
      <button @click="clearError" class="text-red-600 hover:text-red-800">✕</button>
    </div>

    <!-- Recent CV Analysis Section -->
    <div v-if="!isAnalyzing && !analysis && !effectiveJobApplicant && !effectiveJobOpening" class="bg-white rounded-lg shadow p-6 mb-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-4 pb-3 border-b border-gray-200">📊 Análisis de CV Recientes</h3>
      <div v-if="recentAnalyses.length > 0" class="max-h-96 overflow-y-auto pr-2 space-y-3">
        <div
          v-for="recent in recentAnalyses"
          :key="recent.name"
          @click="loadAnalysis(recent.name)"
          class="p-4 border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 cursor-pointer transition-colors">
          <div class="flex justify-between items-start mb-2">
            <div class="flex-1">
              <div class="font-medium text-gray-900 mb-1">
                {{ recent.candidate_name || recent.job_applicant || 'Candidato Desconocido' }}
              </div>
              <div class="text-sm text-gray-600 mb-2">
                {{ recent.job_title || recent.job_opening || 'Trabajo Desconocido' }}
              </div>
            </div>
            <span :class="[
              'px-2 py-1 rounded-full text-xs font-medium',
              recent.status === 'Completed' ? 'bg-green-100 text-green-800' :
              recent.status === 'Analyzing' ? 'bg-yellow-100 text-yellow-800' :
              recent.status === 'Failed' ? 'bg-red-100 text-red-800' :
              'bg-gray-100 text-gray-800'
            ]">
              {{ recent.status }}
            </span>
          </div>
          <div v-if="recent.status === 'Completed'" class="flex gap-4 text-sm">
            <div class="text-gray-600">
              <span class="font-medium">Habilidades:</span> {{ recent.skills_match_percentage || 0 }}%
            </div>
            <div class="text-gray-600">
              <span class="font-medium">Experiencia:</span> {{ recent.experience_relevance || 0 }}/5
            </div>
            <div class="text-gray-600">
              <span class="font-medium">Confianza:</span> {{ recent.ai_confidence_score || 0 }}%
            </div>
          </div>
          <div v-if="recent.analysis_timestamp" class="text-xs text-gray-500 mt-2">
            {{ formatDate(recent.analysis_timestamp) }}
          </div>
        </div>
      </div>
      <div v-else class="text-center py-8 text-gray-500">
        <div class="text-4xl mb-3">📭</div>
        <p>No se encontraron análisis de CV recientes.</p>
        <p class="text-sm mt-2">Comienza a analizar CVs para verlos aquí.</p>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isAnalyzing && !analysis" class="bg-white rounded-lg shadow p-8 text-center mb-6">
      <div class="relative inline-block mb-6">
        <div class="w-16 h-16 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin"></div>
      </div>
      <h3 class="text-xl font-semibold text-gray-900 mb-2">🤖 La IA está Analizando el CV...</h3>
      <p class="text-sm text-gray-600 mb-6">Este es un análisis real usando OpenAI GPT-4</p>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 text-left">
        <div class="p-3 rounded-lg" :class="pollingAttempts > 0 ? 'bg-blue-50 text-blue-700' : 'bg-gray-50 text-gray-500'">
          <span class="mr-2">✓</span> Solicitud en cola
        </div>
        <div class="p-3 rounded-lg" :class="pollingAttempts > 2 ? 'bg-blue-50 text-blue-700' : 'bg-gray-50 text-gray-500'">
          <span class="mr-2">⏳</span> Procesando CV
        </div>
        <div class="p-3 rounded-lg" :class="pollingAttempts > 5 ? 'bg-blue-50 text-blue-700' : 'bg-gray-50 text-gray-500'">
          <span class="mr-2">⏳</span> Llamando a OpenAI
        </div>
        <div class="p-3 rounded-lg" :class="pollingAttempts > 8 ? 'bg-blue-50 text-blue-700' : 'bg-gray-50 text-gray-500'">
          <span class="mr-2">⏳</span> Analizando resultados
        </div>
      </div>
      <div class="mb-4">
        <p class="text-sm text-gray-600 mb-2">Verificando estado... ({{ pollingAttempts }}/30 intentos, ~{{ Math.round(pollingAttempts * 2) }}s transcurridos)</p>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div class="bg-blue-500 h-2 rounded-full transition-all" :style="{width: Math.min((pollingAttempts / 30) * 100, 100) + '%'}"></div>
        </div>
      </div>
      <button v-if="pollingAttempts > 5" @click="cancelAnalysis" class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600">Cancelar Análisis</button>
    </div>

    <!-- Analysis Results -->
    <div v-if="analysis" class="space-y-6">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex justify-between items-center mb-4 pb-4 border-b border-gray-200">
          <h3 v-if="analysis.status === 'Completed'" class="text-xl font-semibold text-gray-900">✅ Análisis Completado</h3>
          <h3 v-else-if="analysis.status === 'Analyzing'" class="text-xl font-semibold text-gray-900">⏳ Análisis en Progreso</h3>
          <h3 v-else-if="analysis.status === 'Failed'" class="text-xl font-semibold text-gray-900">❌ Análisis Fallido</h3>
          <h3 v-else class="text-xl font-semibold text-gray-900">📊 Análisis (Estado: {{ analysis.status }})</h3>
          <div v-if="analysis.analysis_timestamp" class="text-sm text-gray-500">
            Analizado el {{ formatDate(analysis.analysis_timestamp) }}
          </div>
        </div>

        <!-- Debug Info -->
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-6 text-sm text-blue-900">
          <p class="font-semibold mb-2">🔍 Información de Depuración:</p>
          <p><strong>Estado:</strong> {{ analysis.status }}</p>
          <p><strong>ID del Análisis:</strong> {{ analysis.name }}</p>
          <p><strong>Tiene texto:</strong> {{ analysis.cv_analysis_text ? 'Sí (' + analysis.cv_analysis_text.length + ' caracteres)' : 'No' }}</p>
          <p><strong>Habilidades:</strong> {{ analysis.skills_match_percentage || 'N/A' }}%</p>
          <p><strong>Experiencia:</strong> {{ analysis.experience_relevance || 'N/A' }}</p>
          <p><strong>Educación:</strong> {{ analysis.education_match || 'N/A' }}</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xl">🎯</span>
              <h4 class="text-sm font-medium text-gray-700">Coincidencia de Habilidades</h4>
            </div>
            <div class="text-3xl font-bold text-gray-900 mb-2">{{ analysis.skills_match_percentage || 0 }}%</div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="bg-blue-500 h-2 rounded-full" :style="{width: (analysis.skills_match_percentage || 0) + '%'}"></div>
            </div>
          </div>

          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xl">💼</span>
              <h4 class="text-sm font-medium text-gray-700">Experiencia</h4>
            </div>
            <div class="text-2xl mb-2">
              <span v-for="i in 5" :key="i" :class="i <= getExperienceRating() ? 'text-yellow-500' : 'text-gray-300'">★</span>
            </div>
            <div class="text-sm font-semibold text-gray-700">{{ getExperienceRating() }}/5</div>
          </div>

          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xl">🎓</span>
              <h4 class="text-sm font-medium text-gray-700">Educación</h4>
            </div>
            <div class="text-2xl mb-2">
              <span v-for="i in 5" :key="i" :class="i <= getEducationRating() ? 'text-yellow-500' : 'text-gray-300'">★</span>
            </div>
            <div class="text-sm font-semibold text-gray-700">{{ getEducationRating() }}/5</div>
          </div>

          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xl">📊</span>
              <h4 class="text-sm font-medium text-gray-700">Confianza de la IA</h4>
            </div>
            <div class="text-3xl font-bold text-gray-900 mb-2">{{ analysis.ai_confidence_score || 0 }}%</div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div class="bg-green-500 h-2 rounded-full" :style="{width: (analysis.ai_confidence_score || 0) + '%'}"></div>
            </div>
          </div>
        </div>

        <div class="bg-gray-50 rounded-lg p-6 mb-6">
          <h4 class="text-lg font-semibold text-gray-900 mb-4 pb-3 border-b border-gray-200">📋 Análisis Detallado de la IA</h4>
          <div v-if="analysis.cv_analysis_text && analysis.cv_analysis_text.trim().length > 0" class="text-gray-700 leading-relaxed whitespace-pre-wrap" v-html="analysis.cv_analysis_text"></div>
          <div v-else class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-yellow-800">
            <p class="font-semibold mb-2">⚠️ El análisis se completó pero no se generó texto detallado.</p>
            <p class="text-sm mb-2">Esto podría suceder si:</p>
            <ul class="text-sm list-disc list-inside mb-3">
              <li>La respuesta de la IA estaba incompleta</li>
              <li>Hubo un error al analizar la respuesta de la IA</li>
              <li>Los datos del análisis aún se están procesando</li>
            </ul>
            <button @click="reloadAnalysis" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">🔄 Recargar Análisis</button>
          </div>
        </div>

        <div class="bg-gray-50 rounded-lg p-6">
          <h4 class="text-lg font-semibold text-gray-900 mb-4 pb-3 border-b border-gray-200">💡 Recomendaciones de la IA</h4>
          <div class="text-gray-700 leading-relaxed">
            <p v-if="analysis.ai_recommendations && analysis.ai_recommendations.trim().length > 0">
              {{ analysis.ai_recommendations }}
            </p>
            <p v-else class="text-gray-500 italic">
              ⚠️ No se generaron recomendaciones para este análisis.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { call } from 'frappe-ui'

export default {
  name: 'CVAnalysis',
  props: {
    jobApplicant: String,
    jobOpening: String
  },
  data() {
    return {
      analysis: null,
      isAnalyzing: false,
      error: null,
      formJobApplicant: '',
      formJobOpening: '',
      applicantSearchText: '',
      openingSearchText: '',
      showApplicantDropdown: false,
      showOpeningDropdown: false,
      highlightedApplicantIndex: -1,
      highlightedOpeningIndex: -1,
      pollingAttempts: 0,
      pollingInterval: null,
      applicantData: null,
      jobOpeningData: null,
      loadingApplicant: false,
      loadingJobOpening: false,
      jobApplicantsList: [],
      jobOpeningsList: [],
      loadingJobApplicants: false,
      loadingJobOpenings: false,
      recentAnalyses: []
    }
  },
  computed: {
    effectiveJobApplicant() {
      return this.formJobApplicant || 
             this.jobApplicant || 
             this.$route.params.jobApplicant || 
             this.$route.query.applicant || 
             ''
    },
    effectiveJobOpening() {
      return this.formJobOpening || 
             this.jobOpening || 
             this.$route.params.jobOpening || 
             this.$route.query.opening || 
             ''
    },
    canAnalyze() {
      return this.formJobApplicant && this.formJobOpening
    },
    filteredApplicants() {
      if (!this.applicantSearchText) {
        // Show all when no search text (user can browse)
        return this.jobApplicantsList
      }
      const searchLower = this.applicantSearchText.toLowerCase()
      return this.jobApplicantsList.filter(applicant => {
        const name = (applicant.applicant_name || '').toLowerCase()
        const email = (applicant.email_id || '').toLowerCase()
        const id = (applicant.name || '').toLowerCase()
        return name.includes(searchLower) || email.includes(searchLower) || id.includes(searchLower)
      })
    },
    filteredOpenings() {
      if (!this.openingSearchText) {
        // Show all when no search text (user can browse)
        return this.jobOpeningsList
      }
      const searchLower = this.openingSearchText.toLowerCase()
      return this.jobOpeningsList.filter(opening => {
        const title = (opening.job_title || '').toLowerCase()
        const designation = (opening.designation || '').toLowerCase()
        const id = (opening.name || '').toLowerCase()
        return title.includes(searchLower) || designation.includes(searchLower) || id.includes(searchLower)
      })
    },
    hasValidData() {
      if (this.analysis && this.analysis.status === 'Completed') {
        return true
      }
      return this.analysis && (
        this.analysis.skills_match_percentage ||
        this.analysis.experience_relevance ||
        this.analysis.education_match ||
        (this.analysis.cv_analysis_text && this.analysis.cv_analysis_text.trim().length > 0)
      )
    }
  },
  mounted() {
    // Load job applicants and job openings lists
    this.loadJobApplicantsList()
    this.loadJobOpeningsList()
    this.loadRecentAnalyses()
    
    if (this.$route.query.analysisId) {
      this.loadAnalysisById(this.$route.query.analysisId)
    } else if (this.effectiveJobApplicant && this.effectiveJobOpening) {
      this.loadApplicantAndJobData()
    }
  },
  watch: {
    effectiveJobApplicant(newVal) {
      if (newVal && !this.applicantData) {
        this.loadApplicantData()
      }
    },
    effectiveJobOpening(newVal) {
      if (newVal && !this.jobOpeningData) {
        this.loadJobOpeningData()
      }
    }
  },
  beforeUnmount() {
    if (this.pollingInterval) {
      clearTimeout(this.pollingInterval)
    }
  },
  methods: {
    startAnalysis() {
      if (this.canAnalyze) {
        this.analyzeCV()
      }
    },
    clearInputs() {
      this.formJobApplicant = ''
      this.formJobOpening = ''
      this.applicantSearchText = ''
      this.openingSearchText = ''
      this.showApplicantDropdown = false
      this.showOpeningDropdown = false
      this.analysis = null
      this.error = null
      this.isAnalyzing = false
      this.applicantData = null
      this.jobOpeningData = null
    },
    clearApplicant() {
      this.formJobApplicant = ''
      this.applicantSearchText = ''
      this.showApplicantDropdown = false
      this.applicantData = null
    },
    clearOpening() {
      this.formJobOpening = ''
      this.openingSearchText = ''
      this.showOpeningDropdown = false
      this.jobOpeningData = null
    },
    selectApplicant(applicant) {
      this.formJobApplicant = applicant.name
      this.applicantSearchText = applicant.applicant_name || applicant.name
      this.showApplicantDropdown = false
      this.highlightedApplicantIndex = -1
      this.onJobApplicantChange()
    },
    selectOpening(opening) {
      this.formJobOpening = opening.name
      this.openingSearchText = opening.job_title || opening.name
      this.showOpeningDropdown = false
      this.highlightedOpeningIndex = -1
      this.onJobOpeningChange()
    },
    onApplicantSearchInput() {
      // User is typing - allow manual entry
      // If they type something that looks like an ID, accept it
      const trimmed = this.applicantSearchText.trim()
      if (trimmed) {
        // Check if it's an exact match first
        const exactMatch = this.jobApplicantsList.find(a => {
          const searchLower = trimmed.toLowerCase()
          const nameMatch = a.name && a.name.toLowerCase() === searchLower
          const applicantNameMatch = a.applicant_name && a.applicant_name.toLowerCase() === searchLower
          const emailMatch = a.email_id && a.email_id.toLowerCase() === searchLower
          return nameMatch || applicantNameMatch || emailMatch
        })
        
        if (exactMatch) {
          // Found exact match - set it
          this.formJobApplicant = exactMatch.name
          this.applicantSearchText = exactMatch.applicant_name || exactMatch.name
        } else {
          // Allow manual entry - user can type any ID or name
          // Set it as the form value (will be validated on submit)
          this.formJobApplicant = trimmed
        }
      } else {
        // Empty - clear selection
        this.formJobApplicant = ''
      }
      
      // Show dropdown if it's open, but don't force it
      if (this.showApplicantDropdown) {
        this.highlightedApplicantIndex = -1
      }
    },
    onApplicantFocus() {
      // Show dropdown when focused, but user can still type freely
      if (this.jobApplicantsList.length > 0) {
        this.showApplicantDropdown = true
      }
    },
    onOpeningSearchInput() {
      // User is typing - allow manual entry
      // If they type something that looks like an ID, accept it
      const trimmed = this.openingSearchText.trim()
      if (trimmed) {
        // Check if it's an exact match first
        const exactMatch = this.jobOpeningsList.find(o => {
          const searchLower = trimmed.toLowerCase()
          const nameMatch = o.name && o.name.toLowerCase() === searchLower
          const titleMatch = o.job_title && o.job_title.toLowerCase() === searchLower
          const designationMatch = o.designation && o.designation.toLowerCase() === searchLower
          return nameMatch || titleMatch || designationMatch
        })
        
        if (exactMatch) {
          // Found exact match - set it
          this.formJobOpening = exactMatch.name
          this.openingSearchText = exactMatch.job_title || exactMatch.name
        } else {
          // Allow manual entry - user can type any ID or name
          // Set it as the form value (will be validated on submit)
          this.formJobOpening = trimmed
        }
      } else {
        // Empty - clear selection
        this.formJobOpening = ''
      }
      
      // Show dropdown if it's open, but don't force it
      if (this.showOpeningDropdown) {
        this.highlightedOpeningIndex = -1
      }
    },
    onOpeningFocus() {
      // Show dropdown when focused, but user can still type freely
      if (this.jobOpeningsList.length > 0) {
        this.showOpeningDropdown = true
      }
    },
    toggleApplicantDropdown() {
      this.showApplicantDropdown = !this.showApplicantDropdown
      if (this.showApplicantDropdown) {
        this.highlightedApplicantIndex = -1
      }
    },
    toggleOpeningDropdown() {
      this.showOpeningDropdown = !this.showOpeningDropdown
      if (this.showOpeningDropdown) {
        this.highlightedOpeningIndex = -1
      }
    },
    handleApplicantBlur() {
      // Delay hiding dropdown to allow click events
      setTimeout(() => {
        this.showApplicantDropdown = false
        // If formJobApplicant is set, update search text to show selected value
        if (this.formJobApplicant) {
          const applicant = this.jobApplicantsList.find(a => a.name === this.formJobApplicant)
          if (applicant) {
            this.applicantSearchText = applicant.applicant_name || applicant.name
          }
        }
      }, 200)
    },
    handleOpeningBlur() {
      // Delay hiding dropdown to allow click events
      setTimeout(() => {
        this.showOpeningDropdown = false
        // If formJobOpening is set, update search text to show selected value
        if (this.formJobOpening) {
          const opening = this.jobOpeningsList.find(o => o.name === this.formJobOpening)
          if (opening) {
            this.openingSearchText = opening.job_title || opening.name
          }
        }
      }, 200)
    },
    getApplicantDisplayName(applicantId) {
      const applicant = this.jobApplicantsList.find(a => a.name === applicantId)
      if (applicant) {
        return applicant.applicant_name || applicant.name
      }
      return applicantId
    },
    getOpeningDisplayName(openingId) {
      const opening = this.jobOpeningsList.find(o => o.name === openingId)
      if (opening) {
        return opening.job_title || opening.name
      }
      return openingId
    },
    handleApplicantEnter() {
      if (this.highlightedApplicantIndex >= 0 && this.filteredApplicants[this.highlightedApplicantIndex]) {
        this.selectApplicant(this.filteredApplicants[this.highlightedApplicantIndex])
      } else if (this.filteredApplicants.length > 0) {
        // Select first result if nothing is highlighted
        this.selectApplicant(this.filteredApplicants[0])
      } else if (this.applicantSearchText.trim()) {
        // If user typed something and pressed enter, try to use it as ID
        this.formJobApplicant = this.applicantSearchText.trim()
        this.showApplicantDropdown = false
        this.onJobApplicantChange()
      }
    },
    handleOpeningEnter() {
      if (this.highlightedOpeningIndex >= 0 && this.filteredOpenings[this.highlightedOpeningIndex]) {
        this.selectOpening(this.filteredOpenings[this.highlightedOpeningIndex])
      } else if (this.filteredOpenings.length > 0) {
        // Select first result if nothing is highlighted
        this.selectOpening(this.filteredOpenings[0])
      } else if (this.openingSearchText.trim()) {
        // If user typed something and pressed enter, try to use it as ID
        this.formJobOpening = this.openingSearchText.trim()
        this.showOpeningDropdown = false
        this.onJobOpeningChange()
      }
    },
    navigateApplicantDropdown(direction) {
      if (!this.showApplicantDropdown || this.filteredApplicants.length === 0) return
      
      this.highlightedApplicantIndex += direction
      
      if (this.highlightedApplicantIndex < 0) {
        this.highlightedApplicantIndex = this.filteredApplicants.length - 1
      } else if (this.highlightedApplicantIndex >= this.filteredApplicants.length) {
        this.highlightedApplicantIndex = 0
      }
      
      // Scroll highlighted item into view
      this.$nextTick(() => {
        const dropdown = document.querySelector('#job-applicant-search')?.parentElement?.querySelector('.absolute')
        if (dropdown) {
          const highlightedItem = dropdown.children[this.highlightedApplicantIndex]
          if (highlightedItem) {
            highlightedItem.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
          }
        }
      })
    },
    navigateOpeningDropdown(direction) {
      if (!this.showOpeningDropdown || this.filteredOpenings.length === 0) return
      
      this.highlightedOpeningIndex += direction
      
      if (this.highlightedOpeningIndex < 0) {
        this.highlightedOpeningIndex = this.filteredOpenings.length - 1
      } else if (this.highlightedOpeningIndex >= this.filteredOpenings.length) {
        this.highlightedOpeningIndex = 0
      }
      
      // Scroll highlighted item into view
      this.$nextTick(() => {
        const dropdown = document.querySelector('#job-opening-search')?.parentElement?.querySelector('.absolute')
        if (dropdown) {
          const highlightedItem = dropdown.children[this.highlightedOpeningIndex]
          if (highlightedItem) {
            highlightedItem.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
          }
        }
      })
    },
    clearError() {
      this.error = null
    },
    cancelAnalysis() {
      if (this.pollingInterval) {
        clearTimeout(this.pollingInterval)
        this.pollingInterval = null
      }
      this.isAnalyzing = false
      this.pollingAttempts = 0
      this.error = 'Análisis cancelado'
    },
    async analyzeCV() {
      if (!this.effectiveJobApplicant || !this.effectiveJobOpening) {
        this.error = 'Por favor proporciona tanto el ID del Solicitante de Empleo como el ID de la Vacante'
        return
      }

      await this.loadApplicantAndJobData()

      this.isAnalyzing = true
      this.error = null
      this.pollingAttempts = 0
      
      try {
        const data = await call('ai_hr_recruitment.ai_hr_recruitment.api.cv_analysis.analyze_cv_with_ai', {
          job_applicant: this.effectiveJobApplicant,
          job_opening: this.effectiveJobOpening
        })
  
        if (data && data.status) {
          if (data.status === 'processing') {
            this.pollAnalysisStatus(data.analysis_id)
          } else if (data.status === 'exists') {
            await this.loadAnalysis(data.analysis_id)
            this.isAnalyzing = false
          } else if (data.status === 'error') {
            this.error = data.message || 'El análisis falló al iniciar'
            this.isAnalyzing = false
          }
        } else {
          this.error = 'Respuesta inesperada del servidor'
          this.isAnalyzing = false
        }
      } catch (error) {
        this.error = error.message || 'Error al iniciar el análisis de CV. Por favor verifica tu conexión e intenta nuevamente.'
        this.isAnalyzing = false
      }
    },
  
    async pollAnalysisStatus(analysisId) {
      const maxAttempts = 30
      this.pollingAttempts = 0
  
      const poll = async () => {
        if (!this.isAnalyzing) {
          return
        }

        try {
          const analysis = await call('ai_hr_recruitment.ai_hr_recruitment.api.cv_analysis.get_cv_analysis', {
            analysis_id: analysisId
          })
  
          this.pollingAttempts++
  
          if (analysis && analysis.status) {
            if (analysis.status === 'Completed') {
              this.analysis = analysis
              
              if (analysis.job_applicant) {
                this.formJobApplicant = analysis.job_applicant
                const applicant = this.jobApplicantsList.find(a => a.name === analysis.job_applicant)
                if (applicant) {
                  this.applicantSearchText = applicant.applicant_name || applicant.name
                }
                this.loadApplicantData()
              }
              if (analysis.job_opening) {
                this.formJobOpening = analysis.job_opening
                const opening = this.jobOpeningsList.find(o => o.name === analysis.job_opening)
                if (opening) {
                  this.openingSearchText = opening.job_title || opening.name
                }
                this.loadJobOpeningData()
              }
              
              this.isAnalyzing = false
              this.pollingInterval = null
              this.pollingAttempts = 0
              return
            } else if (analysis.status === 'Failed') {
              this.error = this.getErrorMessage(analysis)
              this.isAnalyzing = false
              this.pollingInterval = null
              return
            } else if (analysis.status === 'Analyzing' || analysis.status === 'Pending') {
              if (this.pollingAttempts < maxAttempts) {
                this.pollingInterval = setTimeout(poll, 2000)
              } else {
                this.error = `El análisis sigue procesándose después de ${maxAttempts * 2} segundos. Los trabajadores en segundo plano podrían no estar ejecutándose. Por favor verifica si 'bench start' está en ejecución.`
                this.isAnalyzing = false
                this.pollingInterval = null
                this.analysis = analysis
              }
              return
            } else {
              if (this.pollingAttempts < maxAttempts) {
                this.pollingInterval = setTimeout(poll, 2000)
              } else {
                this.error = `Estado de análisis desconocido: ${analysis.status}. Mostrando datos actuales de todos modos.`
                this.analysis = analysis
                this.isAnalyzing = false
                this.pollingInterval = null
              }
              return
            }
          } else {
            if (this.pollingAttempts < maxAttempts) {
              this.pollingInterval = setTimeout(poll, 2000)
            } else {
              this.error = 'No se pudo recuperar el estado del análisis después de múltiples intentos'
              this.isAnalyzing = false
              this.pollingInterval = null
            }
            return
          }
        } catch (error) {
          if (this.pollingAttempts < maxAttempts && this.isAnalyzing) {
            this.pollingInterval = setTimeout(poll, 3000)
          } else {
            this.error = 'Error al verificar el estado del análisis: ' + (error.message || 'Error desconocido')
            this.isAnalyzing = false
            this.pollingInterval = null
          }
        }
      }
  
      poll()
    },
  
    async loadAnalysis(analysisId) {
      try {
        this.error = null
        const analysis = await call('ai_hr_recruitment.ai_hr_recruitment.api.cv_analysis.get_cv_analysis', {
          analysis_id: analysisId
        })
        
        if (analysis) {
          this.analysis = analysis
          if (analysis.job_applicant) {
            this.formJobApplicant = analysis.job_applicant
            const applicant = this.jobApplicantsList.find(a => a.name === analysis.job_applicant)
            if (applicant) {
              this.applicantSearchText = applicant.applicant_name || applicant.name
            }
            this.loadApplicantData()
          }
          if (analysis.job_opening) {
            this.formJobOpening = analysis.job_opening
            const opening = this.jobOpeningsList.find(o => o.name === analysis.job_opening)
            if (opening) {
              this.openingSearchText = opening.job_title || opening.name
            }
            this.loadJobOpeningData()
          }
          
          if (analysis.status === 'Analyzing' || analysis.status === 'Pending') {
            this.isAnalyzing = true
            this.pollAnalysisStatus(analysisId)
          } else if (analysis.status === 'Completed') {
            this.isAnalyzing = false
          } else {
            this.isAnalyzing = false
            if (analysis.status === 'Failed') {
              this.error = this.getErrorMessage(analysis)
            }
          }
        } else {
          this.error = 'Análisis no encontrado'
        }
      } catch (error) {
        this.error = 'Error al cargar el análisis: ' + (error.message || 'Error desconocido')
      }
    },

    async loadAnalysisById(analysisId = null) {
      if (!analysisId) {
        this.error = 'Por favor proporciona un ID de Análisis'
        return
      }

      this.isAnalyzing = true
      this.error = null
      await this.loadAnalysis(analysisId)
    },

    async reloadAnalysis() {
      if (this.analysis && this.analysis.name) {
        this.isAnalyzing = true
        await this.loadAnalysis(this.analysis.name)
        // Don't set isAnalyzing = false here - loadAnalysis already manages it:
        // - Sets it to false if status is Completed/Failed
        // - Sets it to true and starts polling if status is Pending/Analyzing
      }
    },

    getErrorMessage(analysis) {
      if (analysis.cv_analysis_text) {
        if (analysis.cv_analysis_text.includes('disabled')) {
          return 'El Análisis de CV está deshabilitado en la Configuración de IA de RRHH'
        }
        if (analysis.cv_analysis_text.includes('API key')) {
          return 'La clave API de OpenAI no está configurada en la Configuración de IA de RRHH'
        }
        if (analysis.cv_analysis_text.includes('rate limit')) {
          return 'Se excedió el límite de velocidad de la API de OpenAI. Por favor espera e intenta nuevamente'
        }
      }
      return 'El análisis falló. Por favor intenta nuevamente o revisa los registros de errores'
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      try {
        const date = new Date(dateString)
        return date.toLocaleString('es-ES', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch {
        return dateString
      }
    },

    async loadApplicantData() {
      if (!this.effectiveJobApplicant) return
      
      this.loadingApplicant = true
      try {
        const applicant = await call('frappe.client.get', {
          doctype: 'Job Applicant',
          name: this.effectiveJobApplicant
        })
        this.applicantData = applicant
      } catch (error) {
        this.applicantData = null
      } finally {
        this.loadingApplicant = false
      }
    },

    async loadJobOpeningData() {
      if (!this.effectiveJobOpening) return
      
      this.loadingJobOpening = true
      try {
        const jobOpening = await call('frappe.client.get', {
          doctype: 'Job Opening',
          name: this.effectiveJobOpening
        })
        this.jobOpeningData = jobOpening
      } catch (error) {
        this.jobOpeningData = null
      } finally {
        this.loadingJobOpening = false
      }
    },

    async loadApplicantAndJobData() {
      if (this.effectiveJobApplicant) {
        await this.loadApplicantData()
      }
      if (this.effectiveJobOpening) {
        await this.loadJobOpeningData()
      }
    },

    async loadJobApplicantsList() {
      this.loadingJobApplicants = true
      try {
        const applicants = await call('frappe.client.get_list', {
          doctype: 'Job Applicant',
          fields: ['name', 'applicant_name', 'email_id', 'job_title', 'status'],
          limit_page_length: 1000,
          order_by: 'modified desc'
        })
        this.jobApplicantsList = applicants || []
      } catch (error) {
        this.jobApplicantsList = []
      } finally {
        this.loadingJobApplicants = false
      }
    },

    async loadJobOpeningsList() {
      this.loadingJobOpenings = true
      try {
        const openings = await call('frappe.client.get_list', {
          doctype: 'Job Opening',
          fields: ['name', 'job_title', 'designation', 'status', 'company'],
          limit_page_length: 1000,
          order_by: 'modified desc'
        })
        this.jobOpeningsList = openings || []
      } catch (error) {
        this.jobOpeningsList = []
      } finally {
        this.loadingJobOpenings = false
      }
    },

    async onJobApplicantChange() {
      if (this.formJobApplicant) {
        // Update search text to show selected value
        const applicant = this.jobApplicantsList.find(a => a.name === this.formJobApplicant)
        if (applicant) {
          this.applicantSearchText = applicant.applicant_name || applicant.name
        }
        
        // Load applicant data to get job_title (which links to job opening)
        await this.loadApplicantData()
        
        // Auto-fill job opening if applicant has one
        if (this.applicantData && this.applicantData.job_title) {
          this.formJobOpening = this.applicantData.job_title
          // Update opening search text
          const opening = this.jobOpeningsList.find(o => o.name === this.formJobOpening)
          if (opening) {
            this.openingSearchText = opening.job_title || opening.name
          }
          // Also load the job opening data
          if (this.formJobOpening) {
            await this.loadJobOpeningData()
          }
        }
      } else {
        // Clear job opening if applicant is cleared
        this.formJobOpening = ''
        this.openingSearchText = ''
        this.applicantData = null
      }
    },

    async onJobOpeningChange() {
      if (this.formJobOpening) {
        // Update search text to show selected value
        const opening = this.jobOpeningsList.find(o => o.name === this.formJobOpening)
        if (opening) {
          this.openingSearchText = opening.job_title || opening.name
        }
        
        // Load job opening data
        await this.loadJobOpeningData()
        
        // Optionally, validate if selected applicant matches this opening
        if (this.formJobApplicant && this.applicantData) {
          if (this.applicantData.job_title !== this.formJobOpening) {
            console.warn('Advertencia: El Solicitante de Empleo seleccionado no está asociado con la Vacante seleccionada')
          }
        }
      } else {
        this.openingSearchText = ''
        this.jobOpeningData = null
      }
    },

    async loadRecentAnalyses() {
      try {
        const analyses = await call('frappe.client.get_list', {
          doctype: 'AI CV Analysis',
          fields: [
            'name',
            'job_applicant',
            'job_opening',
            'status',
            'skills_match_percentage',
            'experience_relevance',
            'education_match',
            'ai_confidence_score',
            'analysis_timestamp'
          ],
          limit_page_length: 10,
          order_by: 'analysis_timestamp desc'
        })

        // Enrich with applicant and opening names
        if (analyses && analyses.length > 0) {
          const applicantIds = [...new Set(analyses.map(a => a.job_applicant).filter(Boolean))]
          const openingIds = [...new Set(analyses.map(a => a.job_opening).filter(Boolean))]

          let applicantMap = {}
          let openingMap = {}

          if (applicantIds.length > 0) {
            const applicants = await call('frappe.client.get_list', {
              doctype: 'Job Applicant',
              fields: ['name', 'applicant_name'],
              filters: [['name', 'in', applicantIds]]
            })
            applicantMap = Object.fromEntries(applicants.map(a => [a.name, a.applicant_name]))
          }

          if (openingIds.length > 0) {
            const openings = await call('frappe.client.get_list', {
              doctype: 'Job Opening',
              fields: ['name', 'job_title'],
              filters: [['name', 'in', openingIds]]
            })
            openingMap = Object.fromEntries(openings.map(o => [o.name, o.job_title]))
          }

          this.recentAnalyses = analyses.map(analysis => ({
            ...analysis,
            candidate_name: applicantMap[analysis.job_applicant] || analysis.job_applicant,
            job_title: openingMap[analysis.job_opening] || analysis.job_opening
          }))
        } else {
          this.recentAnalyses = []
        }
      } catch (error) {
        this.recentAnalyses = []
      }
    },
    getExperienceRating() {
      if (!this.analysis || this.analysis.experience_relevance === undefined || this.analysis.experience_relevance === null) {
        return 0
      }
      // Parse the value to ensure it's a number
      const value = parseFloat(this.analysis.experience_relevance)
      // Handle both fractions (0.0-1.0) and integers (1-5)
      // API should return integers (1-5), but handle fractions just in case
      if (value <= 1.0 && value >= 0) {
        // It's a fraction, convert to integer (1-5)
        // 0.2 = 1 star, 0.4 = 2 stars, 0.6 = 3 stars, 0.8 = 4 stars, 1.0 = 5 stars
        return Math.max(1, Math.min(5, Math.round(value * 5)))
      } else if (value > 1.0 && value <= 5.0) {
        // It's already an integer (1-5), just ensure it's in range
        return Math.max(1, Math.min(5, Math.round(value)))
      } else {
        // Invalid value, return 0
        return 0
      }
    },
    getEducationRating() {
      if (!this.analysis || this.analysis.education_match === undefined || this.analysis.education_match === null) {
        return 0
      }
      // Parse the value to ensure it's a number
      const value = parseFloat(this.analysis.education_match)
      // Handle both fractions (0.0-1.0) and integers (1-5)
      // API should return integers (1-5), but handle fractions just in case
      if (value <= 1.0 && value >= 0) {
        // It's a fraction, convert to integer (1-5)
        // 0.2 = 1 star, 0.4 = 2 stars, 0.6 = 3 stars, 0.8 = 4 stars, 1.0 = 5 stars
        return Math.max(1, Math.min(5, Math.round(value * 5)))
      } else if (value > 1.0 && value <= 5.0) {
        // It's already an integer (1-5), just ensure it's in range
        return Math.max(1, Math.min(5, Math.round(value)))
      } else {
        // Invalid value, return 0
        return 0
      }
    },
  }
}
</script>

<style scoped>
/* Using Tailwind CSS - minimal custom styles only for animations */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Ensure smooth scrolling */
.overflow-y-auto {
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}
</style>
