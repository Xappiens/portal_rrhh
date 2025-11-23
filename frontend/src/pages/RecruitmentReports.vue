<template>
  <div class="flex-1 p-6 bg-gray-50 overflow-y-auto min-h-0">
    <!-- Header -->
    <div class="mb-8">
      <h2 class="text-2xl font-semibold text-gray-900 mb-2">📊 Informes de Reclutamiento IA</h2>
      <p class="text-sm text-gray-600">Generar informes completos de reclutamiento basados en análisis de CV</p>
    </div>

    <!-- Input Form Section -->
    <div v-if="!effectiveJobOpening" class="mb-6">
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-2">📝 Seleccionar Vacante</h3>
        <p class="text-sm text-gray-600 mb-6">Selecciona una vacante para generar un informe de reclutamiento.</p>
        
        <div class="mb-6">
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
                  :placeholder="formJobOpening ? 'Type Job Opening ID or name...' : 'Type Job Opening ID or name manually...'"
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
                title="Browse openings list"
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
                <div class="text-xs text-gray-500 px-2 py-1 mb-1 font-semibold">Select from list ({{ filteredOpenings.length }} results):</div>
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
                No openings found matching "{{ openingSearchText }}"
              </div>
              <div v-else class="p-4 text-sm text-gray-500 text-center">
                Start typing to search, or scroll to browse all openings
              </div>
            </div>
            <p v-if="loadingJobOpenings" class="text-xs text-gray-500 mt-1">Loading openings...</p>
            <p v-if="formJobOpening && !loadingJobOpenings" class="text-xs text-green-600 mt-1">
              ✓ Selected: {{ getOpeningDisplayName(formJobOpening) }}
            </p>
          </div>
        </div>

        <button 
          @click="generateReport" 
          :disabled="!canGenerate || isGenerating" 
          class="w-full px-6 py-3 bg-blue-500 text-white rounded-lg font-semibold hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          <span v-if="isGenerating">🔄 Generando...</span>
          <span v-else>🚀 Generar Informe</span>
        </button>
      </div>

      <!-- All Existing Reports - Show when no job opening selected -->
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">📋 Todos los Informes de Reclutamiento</h3>
        <div v-if="loadingReports" class="text-sm text-gray-500 italic py-8 text-center">Cargando informes...</div>
        <div v-else-if="allReports.length > 0" class="space-y-2 max-h-96 overflow-y-auto">
          <div 
            v-for="rpt in allReports" 
            :key="rpt.name"
            @click="loadReportAndSetJobOpening(rpt.name, rpt.job_opening)"
            :class="[
              'p-4 rounded-lg border cursor-pointer transition-all',
              report && report.name === rpt.name 
                ? 'bg-blue-50 border-blue-300 shadow-sm' 
                : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
            ]"
          >
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <span class="font-medium text-gray-900">{{ rpt.report_title || rpt.name }}</span>
                  <span :class="[
                    'px-2 py-1 rounded text-xs font-medium',
                    rpt.status === 'Completed' ? 'bg-green-100 text-green-800' :
                    rpt.status === 'Generating' ? 'bg-yellow-100 text-yellow-800' :
                    rpt.status === 'Failed' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  ]">
                    {{ rpt.status }}
                  </span>
                </div>
                <div class="text-xs text-gray-500 space-y-1">
                  <div v-if="rpt.job_opening">
                    <span class="font-medium">Vacante:</span> {{ rpt.job_opening }}
                  </div>
                  <div v-if="rpt.report_generated_date">
                    <span>Generado: {{ formatDate(rpt.report_generated_date) }}</span>
                  </div>
                  <div v-if="rpt.candidates_analyzed !== undefined">
                    <span>{{ rpt.candidates_analyzed }} candidatos analizados</span>
                  </div>
                  <div class="font-mono text-xs text-gray-400">
                    ID: {{ rpt.name }}
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <button 
                  v-if="report && report.name === rpt.name"
                  class="text-blue-600 hover:text-blue-800 text-sm font-medium px-3 py-1 bg-blue-100 rounded"
                >
                  ✓ Viendo
                </button>
                <button 
                  v-else
                  class="text-gray-600 hover:text-gray-800 text-sm font-medium px-3 py-1 bg-gray-100 rounded hover:bg-gray-200"
                >
                  Ver →
                </button>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-sm text-gray-500 italic py-8 text-center">
          No se encontraron informes. Selecciona una vacante y genera un informe para comenzar.
        </div>
      </div>
    </div>

    <!-- Report Controls -->
    <div v-else class="mb-6">
      <div class="bg-white rounded-lg shadow p-6 mb-4">
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
        </div>
        <div v-else class="text-sm text-gray-500 italic">Cargando datos de la vacante...</div>
      </div>
      <div class="flex gap-3 flex-wrap">
        <button @click="generateReport" :disabled="isGenerating" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed">
          <span v-if="isGenerating">🔄 Generando...</span>
          <span v-else>📊 Generar Informe</span>
        </button>
        <button @click="clearInputs" class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700">Cambiar Vacante</button>
        <button v-if="report" @click="reloadReport" class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700">🔄 Recargar</button>
        <button v-if="report && isStatusGenerating(report.status)" @click="triggerProcessing" class="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700">⚡ Iniciar Procesamiento</button>
        <button v-if="report && isStatusCompleted(report.status)" @click="exportToPDF" :disabled="exportingPDF" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed">
          <span v-if="exportingPDF">⏳ Exportando...</span>
          <span v-else>📄 Exportar PDF</span>
        </button>
        <button v-if="report && isStatusCompleted(report.status)" @click="exportToExcel" :disabled="exportingExcel" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed">
          <span v-if="exportingExcel">⏳ Exportando...</span>
          <span v-else>📊 Exportar Excel</span>
        </button>
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

    <!-- Loading State -->
    <div v-if="isGenerating && !report" class="bg-white rounded-lg shadow p-8 text-center mb-6">
      <div class="relative inline-block mb-6">
        <div class="w-16 h-16 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin"></div>
      </div>
      <h3 class="text-xl font-semibold text-gray-900 mb-2">🤖 Generando Informe...</h3>
      <p class="text-sm text-gray-600 mb-6">Esto puede tardar unos momentos</p>
      <div class="mb-4">
        <p class="text-sm text-gray-600 mb-2">Verificando estado... ({{ pollingAttempts }}/60 intentos, ~{{ Math.round(pollingAttempts * 2) }}s transcurridos)</p>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div class="bg-blue-500 h-2 rounded-full transition-all" :style="{width: Math.min((pollingAttempts / 60) * 100, 100) + '%'}"></div>
        </div>
      </div>
      <button v-if="pollingAttempts > 5" @click="cancelGeneration" class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600">Cancelar Generación</button>
    </div>

    <!-- Report Results -->
    <div v-if="report" class="space-y-6">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex justify-between items-center mb-4 pb-4 border-b border-gray-200">
          <h3 v-if="isStatusCompleted(report.status)" class="text-xl font-semibold text-gray-900">✅ Informe Completo</h3>
          <h3 v-else-if="isStatusGenerating(report.status)" class="text-xl font-semibold text-gray-900">⏳ Informe Generándose</h3>
          <h3 v-else-if="isStatusFailed(report.status)" class="text-xl font-semibold text-gray-900">❌ Informe Fallido</h3>
          <h3 v-else class="text-xl font-semibold text-gray-900">📊 Informe (Estado: {{ report.status }})</h3>
          <div class="flex items-center gap-3">
            <div v-if="report.report_generated_date" class="text-sm text-gray-500">
              Generado el {{ formatDate(report.report_generated_date) }}
            </div>
            <div v-if="isStatusCompleted(report.status)" class="flex gap-2">
              <button @click="exportToPDF" :disabled="exportingPDF" class="px-3 py-1.5 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed">
                <span v-if="exportingPDF">⏳</span>
                <span v-else>📄 PDF</span>
              </button>
              <button @click="exportToExcel" :disabled="exportingExcel" class="px-3 py-1.5 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed">
                <span v-if="exportingExcel">⏳</span>
                <span v-else>📊 Excel</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Report Summary - Always show basic info -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xl">📋</span>
              <h4 class="text-sm font-medium text-gray-700">ID del Informe</h4>
            </div>
            <div class="text-sm font-mono text-gray-900">{{ report.name }}</div>
          </div>

          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xl">👥</span>
              <h4 class="text-sm font-medium text-gray-700">Candidatos Analizados</h4>
            </div>
            <div class="text-3xl font-bold text-gray-900">{{ report.candidates_analyzed || 0 }}</div>
          </div>

          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xl">🏆</span>
              <h4 class="text-sm font-medium text-gray-700">Mejores Candidatos</h4>
            </div>
            <div class="text-3xl font-bold text-gray-900">{{ report.top_candidates ? report.top_candidates.length : 0 }}</div>
          </div>
        </div>

        <!-- Show info when generating -->
        <div v-if="isStatusGenerating(report.status)" class="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6">
          <h4 class="text-lg font-semibold text-yellow-900 mb-4 pb-3 border-b border-yellow-300">⏳ El informe se está generando</h4>
          <div class="text-yellow-800">
            <p class="mb-2">El informe se está procesando actualmente en segundo plano.</p>
            <p class="mb-2"><strong>ID del Informe:</strong> <span class="font-mono">{{ report.name }}</span></p>
            <p class="mb-2"><strong>Vacante:</strong> {{ report.job_opening }}</p>
            <p v-if="report.report_generated_date" class="mb-2"><strong>Iniciado:</strong> {{ formatDate(report.report_generated_date) }}</p>
            <div class="mt-4 p-3 bg-yellow-100 rounded border border-yellow-300">
              <p class="text-sm font-semibold mb-2">⚠️ Si el informe está atascado en estado "Generándose":</p>
              <ul class="text-sm list-disc list-inside space-y-1">
                <li>Asegúrate de que <code class="bg-yellow-200 px-1 rounded">bench start</code> esté ejecutándose (trabajadores en segundo plano)</li>
                <li>Verifica si la cola de trabajos en segundo plano se está procesando</li>
                <li>Haz clic en el botón "Recargar" para verificar manualmente el estado</li>
                <li>El informe podría estar esperando a que se completen los análisis de CV</li>
              </ul>
            </div>
            <p class="text-sm mt-4">Esta página se actualizará automáticamente cuando el informe esté listo. También puedes hacer clic en el botón "Recargar" para verificar el estado.</p>
          </div>
        </div>

        <!-- AI Analysis Summary - Show when completed OR when generating and has content -->
        <div v-if="isStatusCompleted(report.status) || (isStatusGenerating(report.status) && report.ai_analysis_summary && report.ai_analysis_summary !== '<p>Report is being generated. Please wait...</p>')" class="bg-gray-50 rounded-lg p-6 mb-6">
          <h4 class="text-lg font-semibold text-gray-900 mb-4 pb-3 border-b border-gray-200">📋 Resumen Ejecutivo</h4>
          <div v-if="report.ai_analysis_summary && report.ai_analysis_summary !== '<p>Report is being generated. Please wait...</p>'" class="text-gray-700 leading-relaxed prose max-w-none" v-html="report.ai_analysis_summary"></div>
          <div v-else-if="isStatusCompleted(report.status)" class="text-gray-500 italic">No hay resumen disponible</div>
          <div v-else class="text-gray-500 italic">El resumen aparecerá cuando el informe esté listo...</div>
        </div>

        <!-- Top Candidates -->
        <div v-if="isStatusCompleted(report.status) && report.top_candidates && report.top_candidates.length > 0" class="bg-gray-50 rounded-lg p-6 mb-6">
          <h4 class="text-lg font-semibold text-gray-900 mb-4 pb-3 border-b border-gray-200">🏆 Mejores Candidatos</h4>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-100">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Rango</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Candidato</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Puntuación</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Recomendación</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Fortalezas</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Preocupaciones</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Acciones</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="(candidate, index) in report.top_candidates" :key="candidate.name || candidate.candidate || index" class="hover:bg-gray-50">
                  <td class="px-4 py-3 text-sm font-medium text-gray-900">#{{ candidate.ai_ranking || index + 1 }}</td>
                  <td class="px-4 py-3 text-sm text-gray-900">{{ candidate.candidate_name || candidate.candidate || 'N/A' }}</td>
                  <td class="px-4 py-3 text-sm text-gray-900">
                    <div class="flex items-center">
                      <span class="font-semibold">{{ candidate.overall_score || 0 }}%</span>
                      <div class="ml-2 w-16 bg-gray-200 rounded-full h-2">
                        <div class="bg-blue-500 h-2 rounded-full" :style="{width: (candidate.overall_score || 0) + '%'}"></div>
                      </div>
                    </div>
                  </td>
                  <td class="px-4 py-3 text-sm">
                    <span :class="getRecommendationClass(candidate.recommendation)" class="px-2 py-1 rounded-full text-xs font-medium">
                      {{ candidate.recommendation || 'N/A' }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600 max-w-xs">{{ candidate.strengths || 'N/A' }}</td>
                  <td class="px-4 py-3 text-sm text-gray-600 max-w-xs">{{ candidate.concerns || 'N/A' }}</td>
                  <td class="px-4 py-3 text-sm">
                    <button v-if="candidate.cv_analysis_link" @click="viewCVAnalysis(candidate.cv_analysis_link)" class="text-blue-600 hover:text-blue-800 underline">Ver Análisis de CV</button>
                    <span v-else class="text-gray-400 text-xs">Sin enlace</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- Show message when no top candidates -->
        <div v-if="isStatusCompleted(report.status) && (!report.top_candidates || report.top_candidates.length === 0)" class="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6">
          <h4 class="text-lg font-semibold text-yellow-900 mb-2">🏆 Mejores Candidatos</h4>
          <p class="text-yellow-800">No se encontraron mejores candidatos. Esto generalmente significa que no hay análisis de CV completados para esta vacante.</p>
        </div>

        <!-- Hiring Recommendations - Show when completed -->
        <div v-if="isStatusCompleted(report.status)" class="bg-gray-50 rounded-lg p-6 mb-6">
          <h4 class="text-lg font-semibold text-gray-900 mb-4 pb-3 border-b border-gray-200">💡 Recomendaciones de Contratación</h4>
          <div v-if="report.hiring_recommendations && report.hiring_recommendations.trim().length > 0" class="text-gray-700 leading-relaxed prose max-w-none" v-html="report.hiring_recommendations"></div>
          <div v-else class="text-gray-500 italic">No hay recomendaciones disponibles</div>
        </div>

        <!-- Skills Gap Analysis - Show when completed -->
        <div v-if="isStatusCompleted(report.status)" class="bg-gray-50 rounded-lg p-6 mb-6">
          <h4 class="text-lg font-semibold text-gray-900 mb-4 pb-3 border-b border-gray-200">📊 Análisis de Brecha de Habilidades</h4>
          <div v-if="report.skills_gap_analysis && report.skills_gap_analysis.trim().length > 0" class="text-gray-700 leading-relaxed whitespace-pre-wrap font-mono text-sm bg-white p-4 rounded border">{{ report.skills_gap_analysis }}</div>
          <div v-else class="text-gray-500 italic">No hay análisis de brecha de habilidades disponible</div>
        </div>

        <!-- Market Insights - Show when completed -->
        <div v-if="isStatusCompleted(report.status)" class="bg-gray-50 rounded-lg p-6 mb-6">
          <h4 class="text-lg font-semibold text-gray-900 mb-4 pb-3 border-b border-gray-200">🌐 Perspectivas del Mercado</h4>
          <div v-if="report.market_insights && report.market_insights.trim().length > 0" class="text-gray-700 leading-relaxed whitespace-pre-wrap font-mono text-sm bg-white p-4 rounded border">{{ report.market_insights }}</div>
          <div v-else class="text-gray-500 italic">No hay perspectivas del mercado disponibles</div>
        </div>
        
        <!-- Debug Info Section - Show all report data -->
        <div v-if="isStatusCompleted(report.status)" class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
          <h4 class="text-lg font-semibold text-blue-900 mb-4 pb-3 border-b border-blue-300">🔍 Detalles del Informe</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <strong class="text-blue-900">ID del Informe:</strong>
              <span class="text-blue-700 font-mono ml-2">{{ report.name }}</span>
            </div>
            <div>
              <strong class="text-blue-900">Vacante:</strong>
              <span class="text-blue-700 ml-2">{{ report.job_opening }}</span>
            </div>
            <div>
              <strong class="text-blue-900">Estado:</strong>
              <span class="text-blue-700 ml-2">{{ report.status }}</span>
            </div>
            <div>
              <strong class="text-blue-900">Candidatos Analizados:</strong>
              <span class="text-blue-700 ml-2">{{ report.candidates_analyzed || 0 }}</span>
            </div>
            <div v-if="report.report_generated_date">
              <strong class="text-blue-900">Fecha de Generación:</strong>
              <span class="text-blue-700 ml-2">{{ formatDate(report.report_generated_date) }}</span>
            </div>
            <div v-if="report.top_candidates">
              <strong class="text-blue-900">Cantidad de Mejores Candidatos:</strong>
              <span class="text-blue-700 ml-2">{{ report.top_candidates.length || 0 }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { call } from 'frappe-ui'

export default {
  name: 'RecruitmentReports',
  props: {
    jobOpening: String
  },
  data() {
    return {
      report: null,
      isGenerating: false,
      error: null,
      formJobOpening: '',
      pollingAttempts: 0,
      pollingInterval: null,
      jobOpeningData: null,
      loadingJobOpening: false,
      jobOpeningsList: [],
      loadingJobOpenings: false,
      exportingPDF: false,
      exportingExcel: false,
      availableReports: [],
      loadingReports: false,
      allReports: [],
      openingSearchText: '',
      showOpeningDropdown: false,
      highlightedOpeningIndex: -1
    }
  },
  computed: {
    effectiveJobOpening() {
      return this.formJobOpening || 
             this.jobOpening || 
             this.$route.params.jobOpening || 
             this.$route.query.opening || 
             ''
    },
    canGenerate() {
      return this.formJobOpening
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
    }
  },
  mounted() {
    this.loadJobOpeningsList()
    this.loadAllReports()
    
    if (this.$route.query.reportId) {
      this.loadReportById(this.$route.query.reportId)
    } else if (this.effectiveJobOpening) {
      this.loadJobOpeningData()
      this.loadExistingReports()
    }
  },
  watch: {
    effectiveJobOpening(newVal) {
      if (newVal) {
        if (!this.jobOpeningData) {
          this.loadJobOpeningData()
        }
        // Load existing reports for this job opening
        this.loadExistingReports()
      }
    }
  },
  beforeUnmount() {
    if (this.pollingInterval) {
      clearTimeout(this.pollingInterval)
    }
  },
  methods: {
    clearInputs() {
      this.formJobOpening = ''
      this.openingSearchText = ''
      this.showOpeningDropdown = false
      this.report = null
      this.error = null
      this.isGenerating = false
      this.jobOpeningData = null
      this.availableReports = []
      // Reload all reports when clearing
      this.loadAllReports()
    },
    clearOpening() {
      this.formJobOpening = ''
      this.openingSearchText = ''
      this.showOpeningDropdown = false
      this.jobOpeningData = null
    },
    selectOpening(opening) {
      this.formJobOpening = opening.name
      this.openingSearchText = opening.job_title || opening.name
      this.showOpeningDropdown = false
      this.highlightedOpeningIndex = -1
      this.onJobOpeningChange()
    },
    onOpeningSearchInput() {
      // User is typing - allow manual entry
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
    toggleOpeningDropdown() {
      this.showOpeningDropdown = !this.showOpeningDropdown
      if (this.showOpeningDropdown) {
        this.highlightedOpeningIndex = -1
      }
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
    getOpeningDisplayName(openingId) {
      const opening = this.jobOpeningsList.find(o => o.name === openingId)
      if (opening) {
        return opening.job_title || opening.name
      }
      return openingId
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
        const dropdown = document.querySelector('#job-opening-input')?.parentElement?.querySelector('.absolute')
        if (dropdown) {
          const highlightedItem = dropdown.querySelectorAll('div[class*="cursor-pointer"]')[this.highlightedOpeningIndex]
          if (highlightedItem) {
            highlightedItem.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
          }
        }
      })
    },
    clearError() {
      this.error = null
    },
    cancelGeneration() {
      if (this.pollingInterval) {
        clearTimeout(this.pollingInterval)
        this.pollingInterval = null
      }
      this.isGenerating = false
      this.pollingAttempts = 0
      this.error = 'Generación del informe cancelada'
    },
    async generateReport() {
      if (!this.effectiveJobOpening) {
        this.error = 'Por favor selecciona una Vacante'
        return
      }

      console.log('🚀 Starting report generation for:', this.effectiveJobOpening)
      await this.loadJobOpeningData()

      this.isGenerating = true
      this.error = null
      this.pollingAttempts = 0
      
      // Clear any existing polling
      if (this.pollingInterval) {
        clearTimeout(this.pollingInterval)
        this.pollingInterval = null
      }
      
      try {
        console.log('📞 Calling generate_recruitment_report API...')
        const data = await call('ai_hr_recruitment.ai_hr_recruitment.api.recruitment_reports.generate_recruitment_report', {
          job_opening: this.effectiveJobOpening
        })
  
        console.log('📥 API Response:', data)
  
        if (!data) {
          throw new Error('No response from server')
        }

        // Get report_id from response - it might be in different places
        let reportId = data.report_id || data.name || data.report_name
        
        if (!reportId) {
          console.error('❌ No report_id in response. Full response:', JSON.stringify(data, null, 2))
          // Try to get the latest report for this job opening as fallback
          console.log('🔄 Trying to get latest report for job opening as fallback...')
          try {
            const reports = await call('ai_hr_recruitment.ai_hr_recruitment.api.recruitment_reports.get_reports_for_job_opening', {
              job_opening: this.effectiveJobOpening
            })
            if (reports && reports.length > 0) {
              reportId = reports[0].name
              console.log('✅ Found existing report:', reportId)
            }
          } catch (fallbackError) {
            console.error('❌ Fallback also failed:', fallbackError)
          }
          
          if (!reportId) {
            this.error = 'El servidor no devolvió un ID de informe. Respuesta: ' + JSON.stringify(data)
            this.isGenerating = false
            return
          }
        }

        console.log('📋 Report ID received:', reportId)
        console.log('📊 Response status:', data.status)
  
        // ALWAYS load the report, regardless of response status
        console.log('📥 Loading report:', reportId)
        await this.loadReport(reportId)
        
        // Refresh the reports list to include the new report
        await this.loadExistingReports()
        // Also refresh all reports list
        await this.loadAllReports()
        
        // After loading, check the actual report status
        if (this.report) {
          const reportStatus = (this.report.status || '').toLowerCase()
          console.log('📊 Loaded report status:', reportStatus)
          
          if (reportStatus === 'completed') {
            console.log('✅ Report is already completed!')
            this.isGenerating = false
            this.error = null
            if (this.pollingInterval) {
              clearTimeout(this.pollingInterval)
              this.pollingInterval = null
            }
          } else if (reportStatus === 'generating' || reportStatus === 'draft') {
            console.log('⏳ Report is generating, starting polling...')
            this.isGenerating = true
            // Clear any existing polling first
            if (this.pollingInterval) {
              clearTimeout(this.pollingInterval)
              this.pollingInterval = null
            }
            this.pollReportStatus(reportId)
          } else if (reportStatus === 'failed') {
            console.log('❌ Report failed')
            this.isGenerating = false
            this.error = this.report.ai_analysis_summary || 'La generación del informe falló'
          } else {
            console.log('⚠️ Unknown report status:', this.report.status)
            this.isGenerating = false
          }
        } else {
          console.error('❌ Failed to load report after generation')
          this.error = 'El informe fue creado pero no se pudo cargar. ID del Informe: ' + reportId
          this.isGenerating = false
        }
      } catch (error) {
        console.error('❌ Error generating report:', error)
        this.error = error.message || 'Error al generar el informe. Por favor verifica tu conexión e intenta nuevamente.'
        this.isGenerating = false
        // Clear polling on error
        if (this.pollingInterval) {
          clearTimeout(this.pollingInterval)
          this.pollingInterval = null
        }
      }
    },
  
    async pollReportStatus(reportId) {
      if (!reportId) {
        console.error('❌ Cannot poll: no reportId provided')
        this.isGenerating = false
        return
      }
      
      const maxAttempts = 60
      console.log('🔄 Starting polling for report:', reportId)
      
      // Ensure isGenerating is true when starting polling
      this.isGenerating = true
      
      // Clear any existing polling first
      if (this.pollingInterval) {
        console.log('🧹 Clearing existing polling interval')
        clearTimeout(this.pollingInterval)
        this.pollingInterval = null
      }
  
      const poll = async () => {
        try {
          // Increment attempts BEFORE the call so UI updates immediately
          this.pollingAttempts++
          console.log(`🔄 Polling attempt ${this.pollingAttempts}/${maxAttempts} for report ${reportId}`)
          
          // Check max attempts
          if (this.pollingAttempts > maxAttempts) {
            console.log('⏹️ Polling stopped - reached max attempts')
            if (this.report && (this.report.status === 'Generating' || this.report.status === 'generating')) {
              this.error = `El informe sigue procesándose después de ${maxAttempts * 2} segundos. Los trabajadores en segundo plano podrían no estar ejecutándose. Por favor verifica si 'bench start' está ejecutándose, o haz clic en "Recargar" para verificar el estado nuevamente.`
            }
            this.isGenerating = false
            if (this.pollingInterval) {
              clearTimeout(this.pollingInterval)
            }
            this.pollingInterval = null
            return
          }

          console.log(`📞 Calling get_recruitment_report for ${reportId}...`)
          const report = await call('ai_hr_recruitment.ai_hr_recruitment.api.recruitment_reports.get_recruitment_report', {
            report_id: reportId
          })
  
          console.log(`📥 Poll ${this.pollingAttempts}: Report status:`, report ? report.status : 'null')
  
          if (report) {
            // Always update the report so UI shows latest data
            this.report = report
            console.log('✅ Updated report in UI. Status:', report.status)
            
            // Normalize status for comparison
            const reportStatus = (report.status || '').toLowerCase()
            
            if (reportStatus === 'completed') {
              console.log('✅✅✅ Report completed!')
              this.isGenerating = false
              if (this.pollingInterval) {
                clearTimeout(this.pollingInterval)
              }
              this.pollingInterval = null
              this.error = null
              return
            } else if (reportStatus === 'failed') {
              console.log('❌ Report failed')
              this.error = report.ai_analysis_summary || 'La generación del informe falló'
              this.isGenerating = false
              if (this.pollingInterval) {
                clearTimeout(this.pollingInterval)
              }
              this.pollingInterval = null
              return
            } else if (reportStatus === 'generating' || reportStatus === 'draft') {
              console.log(`⏳ Still generating... (attempt ${this.pollingAttempts}/${maxAttempts})`)
              this.isGenerating = true
              // Continue polling
              if (this.pollingAttempts < maxAttempts) {
                console.log(`⏰ Scheduling next poll in 2 seconds...`)
                this.pollingInterval = setTimeout(() => {
                  console.log('⏰ Polling interval triggered')
                  poll()
                }, 2000)
                console.log('✅ Polling interval set:', this.pollingInterval)
              } else {
                this.error = `El informe sigue procesándose después de ${maxAttempts * 2} segundos. Los trabajadores en segundo plano podrían no estar ejecutándose.`
                this.isGenerating = false
                if (this.pollingInterval) {
                  clearTimeout(this.pollingInterval)
                }
                this.pollingInterval = null
              }
              return
            } else {
              console.log('⚠️ Unknown status:', report.status)
              // Continue polling for unknown status
              if (this.pollingAttempts < maxAttempts) {
                this.isGenerating = true
                this.pollingInterval = setTimeout(() => {
                  console.log('⏰ Polling interval triggered (unknown status)')
                  poll()
                }, 2000)
              } else {
                this.error = `Estado de informe desconocido: ${report.status}. Mostrando datos actuales de todos modos.`
                this.isGenerating = false
                if (this.pollingInterval) {
                  clearTimeout(this.pollingInterval)
                }
                this.pollingInterval = null
              }
              return
            }
          } else {
            console.log('⚠️ No report data returned')
            if (this.pollingAttempts < maxAttempts) {
              this.isGenerating = true
              this.pollingInterval = setTimeout(() => {
                console.log('⏰ Polling interval triggered (no data)')
                poll()
              }, 2000)
            } else {
              this.error = 'No se pudo recuperar los datos del informe después de múltiples intentos'
              this.isGenerating = false
              if (this.pollingInterval) {
                clearTimeout(this.pollingInterval)
              }
              this.pollingInterval = null
            }
          }
        } catch (error) {
          console.error('❌ Error polling:', error)
          console.error('❌ Error details:', error.message, error.stack)
          if (this.pollingAttempts < maxAttempts) {
            console.log(`🔄 Retrying after error (attempt ${this.pollingAttempts}/${maxAttempts})...`)
            this.isGenerating = true
            this.pollingInterval = setTimeout(() => {
              console.log('⏰ Polling interval triggered (error retry)')
              poll()
            }, 3000)
          } else {
            this.error = 'Error al verificar el estado del informe: ' + (error.message || 'Error desconocido')
            this.isGenerating = false
            if (this.pollingInterval) {
              clearTimeout(this.pollingInterval)
            }
            this.pollingInterval = null
          }
        }
      }
  
      // Start polling immediately (first attempt)
      console.log('🚀 Starting first poll immediately...')
      this.pollingAttempts = 0
      // Start immediately - don't wait
      poll()
    },
  
    async loadReport(reportId) {
      try {
        this.error = null
        console.log('Loading report:', reportId)
        const report = await call('ai_hr_recruitment.ai_hr_recruitment.api.recruitment_reports.get_recruitment_report', {
          report_id: reportId
        })
        
        console.log('Loaded report:', report)
        console.log('Report status:', report ? report.status : 'null')
        console.log('Report data:', JSON.stringify(report, null, 2))
        
        if (report) {
          // Always set the report so it's visible
          this.report = report
          if (report.job_opening) {
            this.formJobOpening = report.job_opening
            // Update search text to show selected value
            const opening = this.jobOpeningsList.find(o => o.name === report.job_opening)
            if (opening) {
              this.openingSearchText = opening.job_title || opening.name
            }
            this.loadJobOpeningData()
          }
          
          // Handle status appropriately - normalize for case-insensitive comparison
          const reportStatus = (report.status || '').toLowerCase()
          if (reportStatus === 'generating' || reportStatus === 'draft') {
            console.log('Report still generating, starting polling...')
            this.isGenerating = true
            // Clear any existing polling interval
            if (this.pollingInterval) {
              clearTimeout(this.pollingInterval)
              this.pollingInterval = null
            }
            this.pollReportStatus(reportId)
          } else if (reportStatus === 'completed') {
            console.log('✅ Report already completed, showing results')
            this.isGenerating = false
            this.error = null // Clear any errors
            // Clear any polling
            if (this.pollingInterval) {
              clearTimeout(this.pollingInterval)
              this.pollingInterval = null
            }
          } else if (reportStatus === 'failed') {
            console.log('❌ Report failed')
            this.isGenerating = false
            this.error = 'La generación del informe falló'
            // Clear any polling
            if (this.pollingInterval) {
              clearTimeout(this.pollingInterval)
              this.pollingInterval = null
            }
          } else {
            console.log('⚠️ Unknown report status:', report.status)
            this.isGenerating = false
            // Clear any polling
            if (this.pollingInterval) {
              clearTimeout(this.pollingInterval)
              this.pollingInterval = null
            }
          }
        } else {
          this.error = 'Informe no encontrado'
          this.isGenerating = false
        }
      } catch (error) {
        console.error('Error loading report:', error)
        this.error = 'Error al cargar el informe: ' + (error.message || 'Error desconocido')
        this.isGenerating = false
      }
    },

    async loadReportById(reportId = null) {
      if (!reportId) {
        this.error = 'Por favor proporciona un ID de Informe'
        return
      }

      this.isGenerating = true
      this.error = null
      await this.loadReport(reportId)
    },

    async reloadReport() {
      if (this.report && this.report.name) {
        console.log('Reloading report:', this.report.name)
        this.isGenerating = true
        this.error = null
        await this.loadReport(this.report.name)
        // If report is still generating, polling will continue in loadReport
      } else {
        console.log('No report to reload')
      }
    },

    async triggerProcessing() {
      if (!this.report || !this.report.name) {
        this.error = 'No hay informe disponible para iniciar el procesamiento'
        return
      }

      const reportStatus = (this.report.status || '').toLowerCase()
      if (reportStatus !== 'generating' && reportStatus !== 'draft') {
        this.error = 'El informe no está en estado Generándose'
        return
      }

      try {
        this.error = null
        const response = await call('ai_hr_recruitment.ai_hr_recruitment.api.recruitment_reports.trigger_report_processing', {
          report_id: this.report.name
        })
        
        console.log('Triggered processing:', response)
        this.isGenerating = true
        // Start polling to check status
        this.pollReportStatus(this.report.name)
      } catch (error) {
        console.error('Error triggering processing:', error)
        this.error = 'Error al iniciar el procesamiento: ' + (error.message || 'Error desconocido')
      }
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

    async loadJobOpeningData() {
      if (!this.effectiveJobOpening) return
      
      this.loadingJobOpening = true
      try {
        const jobOpening = await call('frappe.client.get', {
          doctype: 'Job Opening',
          name: this.effectiveJobOpening
        })
        this.jobOpeningData = jobOpening
        console.log('Loaded job opening data:', jobOpening)
      } catch (error) {
        console.error('Error loading job opening data:', error)
        this.jobOpeningData = null
      } finally {
        this.loadingJobOpening = false
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
        console.log('Loaded job openings list:', this.jobOpeningsList.length)
      } catch (error) {
        console.error('Error loading job openings list:', error)
        this.jobOpeningsList = []
      } finally {
        this.loadingJobOpenings = false
      }
    },

    async onJobOpeningChange() {
      if (this.formJobOpening) {
        // Update search text to show selected value
        const opening = this.jobOpeningsList.find(o => o.name === this.formJobOpening)
        if (opening) {
          this.openingSearchText = opening.job_title || opening.name
        }
        
        await this.loadJobOpeningData()
        await this.loadExistingReports()
      } else {
        this.openingSearchText = ''
        this.jobOpeningData = null
        this.availableReports = []
        this.report = null
      }
    },

    async loadExistingReports() {
      if (!this.effectiveJobOpening) {
        this.availableReports = []
        return
      }

      this.loadingReports = true
      try {
        const reports = await call('ai_hr_recruitment.ai_hr_recruitment.api.recruitment_reports.get_reports_for_job_opening', {
          job_opening: this.effectiveJobOpening
        })
        
        if (reports && reports.length > 0) {
          this.availableReports = reports
        } else {
          this.availableReports = []
        }
      } catch (error) {
        console.error('Error loading existing reports:', error)
        this.availableReports = []
        // Don't show error if it's just that no reports exist
        if (error.message && !error.message.includes('not found')) {
          console.warn('Could not load existing reports:', error.message)
        }
      } finally {
        this.loadingReports = false
      }
    },

    async loadAllReports() {
      this.loadingReports = true
      try {
        // Get all AI Recruitment Reports
        const reports = await call('frappe.client.get_list', {
          doctype: 'AI Recruitment Report',
          fields: ['name', 'report_title', 'status', 'report_generated_date', 'candidates_analyzed', 'job_opening'],
          limit_page_length: 100,
          order_by: 'report_generated_date desc'
        })
        
        if (reports && reports.length > 0) {
          this.allReports = reports
        } else {
          this.allReports = []
        }
      } catch (error) {
        console.error('Error loading all reports:', error)
        this.allReports = []
      } finally {
        this.loadingReports = false
      }
    },

    async loadReportAndSetJobOpening(reportId, jobOpening) {
      // Set the job opening first
      if (jobOpening) {
        this.formJobOpening = jobOpening
        // Update search text to show selected value
        const opening = this.jobOpeningsList.find(o => o.name === jobOpening)
        if (opening) {
          this.openingSearchText = opening.job_title || opening.name
        }
        await this.loadJobOpeningData()
      }
      // Load the report
      await this.loadReport(reportId)
      // Refresh all reports list
      await this.loadAllReports()
    },

    getRecommendationClass(recommendation) {
      const classes = {
        'Hire': 'bg-green-100 text-green-800',
        'Consider': 'bg-blue-100 text-blue-800',
        'Additional Interview': 'bg-yellow-100 text-yellow-800',
        'Reject': 'bg-red-100 text-red-800',
        'Contratar': 'bg-green-100 text-green-800',
        'Considerar': 'bg-blue-100 text-blue-800',
        'Entrevista Adicional': 'bg-yellow-100 text-yellow-800',
        'Rechazar': 'bg-red-100 text-red-800'
      }
      return classes[recommendation] || 'bg-gray-100 text-gray-800'
    },

    viewCVAnalysis(analysisId) {
      // Navigate to CV Analysis page
      this.$router.push({
        name: 'CVAnalysis',
        query: { analysisId: analysisId }
      })
    },

    async exportToPDF() {
      if (!this.report || !this.report.name) {
        this.error = 'No hay informe disponible para exportar'
        return
      }

      if (!this.isStatusCompleted(this.report.status)) {
        this.error = 'El informe debe estar completado antes de exportar'
        return
      }

      this.exportingPDF = true
      this.error = null

      try {
        // Build API URL with authentication
        const baseUrl = window.location.origin
        const apiUrl = `${baseUrl}/api/method/ai_hr_recruitment.ai_hr_recruitment.api.recruitment_reports.export_report_to_pdf?report_id=${encodeURIComponent(this.report.name)}`
        
        // Use fetch with credentials to include session cookie
        const response = await fetch(apiUrl, {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Accept': 'application/pdf'
          }
        })
        
        if (!response.ok) {
          throw new Error(`Export failed: ${response.statusText}`)
        }
        
        // Get blob from response
        const blob = await response.blob()
        
        // Create download link from blob
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '')
        link.download = `recruitment_report_${this.report.name}_${timestamp}.pdf`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
      } catch (error) {
        console.error('Error exporting PDF:', error)
        this.error = 'Error al exportar PDF: ' + (error.message || 'Error desconocido')
      } finally {
        this.exportingPDF = false
      }
    },

    async exportToExcel() {
      if (!this.report || !this.report.name) {
        this.error = 'No hay informe disponible para exportar'
        return
      }

      if (!this.isStatusCompleted(this.report.status)) {
        this.error = 'El informe debe estar completado antes de exportar'
        return
      }

      this.exportingExcel = true
      this.error = null

      try {
        // Build API URL with authentication
        const baseUrl = window.location.origin
        const apiUrl = `${baseUrl}/api/method/ai_hr_recruitment.ai_hr_recruitment.api.recruitment_reports.export_report_to_excel?report_id=${encodeURIComponent(this.report.name)}`
        
        // Use fetch with credentials to include session cookie
        const response = await fetch(apiUrl, {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Accept': 'text/csv,application/csv'
          }
        })
        
        if (!response.ok) {
          throw new Error(`Export failed: ${response.statusText}`)
        }
        
        // Get blob from response
        const blob = await response.blob()
        
        // Create download link from blob
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '')
        link.download = `recruitment_report_${this.report.name}_${timestamp}.csv`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
      } catch (error) {
        console.error('Error exporting Excel:', error)
        this.error = 'Error al exportar Excel: ' + (error.message || 'Error desconocido')
      } finally {
        this.exportingExcel = false
      }
    },
    isStatusCompleted(status) {
      return status && status.toLowerCase() === 'completed'
    },
    isStatusGenerating(status) {
      return status && status.toLowerCase() === 'generating'
    },
    isStatusFailed(status) {
      return status && status.toLowerCase() === 'failed'
    }
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
</style>

