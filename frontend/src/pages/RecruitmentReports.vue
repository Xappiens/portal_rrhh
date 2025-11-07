<template>
  <div class="flex-1 p-6 bg-gray-50 overflow-y-auto">
    <!-- Header -->
    <div class="mb-8">
      <h2 class="text-2xl font-semibold text-gray-900 mb-2">📊 AI Recruitment Reports</h2>
      <p class="text-sm text-gray-600">Generate comprehensive recruitment reports based on CV analysis</p>
    </div>

    <!-- Input Form Section -->
    <div v-if="!effectiveJobOpening" class="mb-6">
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-2">📝 Select Job Opening</h3>
        <p class="text-sm text-gray-600 mb-6">Select a Job Opening to generate a recruitment report.</p>
        
        <div class="mb-6">
          <label for="job-opening" class="block text-sm font-medium text-gray-700 mb-2">
            <span>💼</span> Job Opening
          </label>
          <select
            id="job-opening"
            v-model="formJobOpening"
            @change="onJobOpeningChange"
            :disabled="loadingJobOpenings"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
          >
            <option value="">Select Job Opening...</option>
            <option v-for="opening in jobOpeningsList" :key="opening.name" :value="opening.name">
              {{ opening.job_title || opening.name }} {{ opening.designation ? `(${opening.designation})` : '' }}
            </option>
          </select>
          <p v-if="loadingJobOpenings" class="text-xs text-gray-500 mt-1">Loading openings...</p>
        </div>

        <button 
          @click="generateReport" 
          :disabled="!canGenerate || isGenerating" 
          class="w-full px-6 py-3 bg-blue-500 text-white rounded-lg font-semibold hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          <span v-if="isGenerating">🔄 Generating...</span>
          <span v-else>🚀 Generate Report</span>
        </button>
      </div>
    </div>

    <!-- Report Controls -->
    <div v-else class="mb-6">
      <div class="bg-white rounded-lg shadow p-6 mb-4">
        <div class="flex items-center gap-3 mb-4 pb-3 border-b border-gray-200">
          <span class="text-2xl">💼</span>
          <h4 class="text-lg font-semibold text-gray-900">Job Opening</h4>
          <span class="text-xs text-gray-500 font-mono ml-auto">{{ effectiveJobOpening }}</span>
        </div>
        <div v-if="jobOpeningData" class="space-y-2">
          <p class="text-sm"><span class="font-medium text-gray-700">Title:</span> <span class="text-gray-900">{{ jobOpeningData.job_title || 'N/A' }}</span></p>
          <p v-if="jobOpeningData.designation" class="text-sm"><span class="font-medium text-gray-700">Designation:</span> <span class="text-gray-900">{{ jobOpeningData.designation }}</span></p>
          <p v-if="jobOpeningData.company" class="text-sm"><span class="font-medium text-gray-700">Company:</span> <span class="text-gray-900">{{ jobOpeningData.company }}</span></p>
          <p v-if="jobOpeningData.department" class="text-sm"><span class="font-medium text-gray-700">Department:</span> <span class="text-gray-900">{{ jobOpeningData.department }}</span></p>
        </div>
        <div v-else class="text-sm text-gray-500 italic">Loading job opening data...</div>
      </div>
      <div class="flex gap-3 flex-wrap">
        <button @click="generateReport" :disabled="isGenerating" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed">
          <span v-if="isGenerating">🔄 Generating...</span>
          <span v-else>📊 Generate Report</span>
        </button>
        <button @click="clearInputs" class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700">Change Job Opening</button>
        <button v-if="report" @click="reloadReport" class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700">🔄 Reload</button>
        <button v-if="report && report.status === 'Generating'" @click="triggerProcessing" class="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700">⚡ Trigger Processing</button>
        <button v-if="report && report.status === 'Completed'" @click="exportToPDF" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">📄 Export PDF</button>
        <button v-if="report && report.status === 'Completed'" @click="exportToExcel" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">📊 Export Excel</button>
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
      <h3 class="text-xl font-semibold text-gray-900 mb-2">🤖 Generating Report...</h3>
      <p class="text-sm text-gray-600 mb-6">This may take a few moments</p>
      <div class="mb-4">
        <p class="text-sm text-gray-600 mb-2">Checking status... ({{ pollingAttempts }}/60 attempts, ~{{ Math.round(pollingAttempts * 2) }}s elapsed)</p>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div class="bg-blue-500 h-2 rounded-full transition-all" :style="{width: Math.min((pollingAttempts / 60) * 100, 100) + '%'}"></div>
        </div>
      </div>
      <button v-if="pollingAttempts > 5" @click="cancelGeneration" class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600">Cancel Generation</button>
    </div>

    <!-- Report Results -->
    <div v-if="report" class="space-y-6">
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex justify-between items-center mb-4 pb-4 border-b border-gray-200">
          <h3 v-if="report.status === 'Completed'" class="text-xl font-semibold text-gray-900">✅ Report Complete</h3>
          <h3 v-else-if="report.status === 'Generating'" class="text-xl font-semibold text-gray-900">⏳ Report Generating</h3>
          <h3 v-else-if="report.status === 'Failed'" class="text-xl font-semibold text-gray-900">❌ Report Failed</h3>
          <h3 v-else class="text-xl font-semibold text-gray-900">📊 Report (Status: {{ report.status }})</h3>
          <div v-if="report.report_generated_date" class="text-sm text-gray-500">
            Generated on {{ formatDate(report.report_generated_date) }}
          </div>
        </div>

        <!-- Report Summary - Always show basic info -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xl">📋</span>
              <h4 class="text-sm font-medium text-gray-700">Report ID</h4>
            </div>
            <div class="text-sm font-mono text-gray-900">{{ report.name }}</div>
          </div>

          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xl">👥</span>
              <h4 class="text-sm font-medium text-gray-700">Candidates Analyzed</h4>
            </div>
            <div class="text-3xl font-bold text-gray-900">{{ report.candidates_analyzed || 0 }}</div>
          </div>

          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xl">🏆</span>
              <h4 class="text-sm font-medium text-gray-700">Top Candidates</h4>
            </div>
            <div class="text-3xl font-bold text-gray-900">{{ report.top_candidates ? report.top_candidates.length : 0 }}</div>
          </div>
        </div>

        <!-- Show info when generating -->
        <div v-if="report.status === 'Generating'" class="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6">
          <h4 class="text-lg font-semibold text-yellow-900 mb-4 pb-3 border-b border-yellow-300">⏳ Report is being generated</h4>
          <div class="text-yellow-800">
            <p class="mb-2">The report is currently being processed in the background.</p>
            <p class="mb-2"><strong>Report ID:</strong> <span class="font-mono">{{ report.name }}</span></p>
            <p class="mb-2"><strong>Job Opening:</strong> {{ report.job_opening }}</p>
            <p v-if="report.report_generated_date" class="mb-2"><strong>Started:</strong> {{ formatDate(report.report_generated_date) }}</p>
            <div class="mt-4 p-3 bg-yellow-100 rounded border border-yellow-300">
              <p class="text-sm font-semibold mb-2">⚠️ If the report is stuck in "Generating" status:</p>
              <ul class="text-sm list-disc list-inside space-y-1">
                <li>Make sure <code class="bg-yellow-200 px-1 rounded">bench start</code> is running (background workers)</li>
                <li>Check if the background job queue is processing</li>
                <li>Click the "Reload" button to manually check the status</li>
                <li>The report might be waiting for CV analyses to complete</li>
              </ul>
            </div>
            <p class="text-sm mt-4">This page will automatically update when the report is ready. You can also click the "Reload" button to check the status.</p>
          </div>
        </div>

        <!-- AI Analysis Summary - Show when completed OR when generating and has content -->
        <div v-if="report.status === 'Completed' || (report.status === 'Generating' && report.ai_analysis_summary && report.ai_analysis_summary !== '<p>Report is being generated. Please wait...</p>')" class="bg-gray-50 rounded-lg p-6 mb-6">
          <h4 class="text-lg font-semibold text-gray-900 mb-4 pb-3 border-b border-gray-200">📋 Executive Summary</h4>
          <div v-if="report.ai_analysis_summary && report.ai_analysis_summary !== '<p>Report is being generated. Please wait...</p>'" class="text-gray-700 leading-relaxed prose max-w-none" v-html="report.ai_analysis_summary"></div>
          <div v-else-if="report.status === 'Completed'" class="text-gray-500 italic">No summary available</div>
          <div v-else class="text-gray-500 italic">Summary will appear when report is ready...</div>
        </div>

        <!-- Top Candidates -->
        <div v-if="report.status === 'Completed' && report.top_candidates && report.top_candidates.length > 0" class="bg-gray-50 rounded-lg p-6 mb-6">
          <h4 class="text-lg font-semibold text-gray-900 mb-4 pb-3 border-b border-gray-200">🏆 Top Candidates</h4>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-100">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Rank</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Candidate</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Score</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Recommendation</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Strengths</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Concerns</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Actions</th>
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
                    <button v-if="candidate.cv_analysis_link" @click="viewCVAnalysis(candidate.cv_analysis_link)" class="text-blue-600 hover:text-blue-800 underline">View CV Analysis</button>
                    <span v-else class="text-gray-400 text-xs">No link</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        <!-- Show message when no top candidates -->
        <div v-if="report.status === 'Completed' && (!report.top_candidates || report.top_candidates.length === 0)" class="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6">
          <h4 class="text-lg font-semibold text-yellow-900 mb-2">🏆 Top Candidates</h4>
          <p class="text-yellow-800">No top candidates found. This usually means there are no completed CV analyses for this job opening.</p>
        </div>

        <!-- Hiring Recommendations - Show when completed -->
        <div v-if="report.status === 'Completed'" class="bg-gray-50 rounded-lg p-6 mb-6">
          <h4 class="text-lg font-semibold text-gray-900 mb-4 pb-3 border-b border-gray-200">💡 Hiring Recommendations</h4>
          <div v-if="report.hiring_recommendations && report.hiring_recommendations.trim().length > 0" class="text-gray-700 leading-relaxed prose max-w-none" v-html="report.hiring_recommendations"></div>
          <div v-else class="text-gray-500 italic">No recommendations available</div>
        </div>

        <!-- Skills Gap Analysis - Show when completed -->
        <div v-if="report.status === 'Completed'" class="bg-gray-50 rounded-lg p-6 mb-6">
          <h4 class="text-lg font-semibold text-gray-900 mb-4 pb-3 border-b border-gray-200">📊 Skills Gap Analysis</h4>
          <div v-if="report.skills_gap_analysis && report.skills_gap_analysis.trim().length > 0" class="text-gray-700 leading-relaxed whitespace-pre-wrap font-mono text-sm bg-white p-4 rounded border">{{ report.skills_gap_analysis }}</div>
          <div v-else class="text-gray-500 italic">No skills gap analysis available</div>
        </div>

        <!-- Market Insights - Show when completed -->
        <div v-if="report.status === 'Completed'" class="bg-gray-50 rounded-lg p-6 mb-6">
          <h4 class="text-lg font-semibold text-gray-900 mb-4 pb-3 border-b border-gray-200">🌐 Market Insights</h4>
          <div v-if="report.market_insights && report.market_insights.trim().length > 0" class="text-gray-700 leading-relaxed whitespace-pre-wrap font-mono text-sm bg-white p-4 rounded border">{{ report.market_insights }}</div>
          <div v-else class="text-gray-500 italic">No market insights available</div>
        </div>
        
        <!-- Debug Info Section - Show all report data -->
        <div v-if="report.status === 'Completed'" class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
          <h4 class="text-lg font-semibold text-blue-900 mb-4 pb-3 border-b border-blue-300">🔍 Report Details</h4>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <strong class="text-blue-900">Report ID:</strong>
              <span class="text-blue-700 font-mono ml-2">{{ report.name }}</span>
            </div>
            <div>
              <strong class="text-blue-900">Job Opening:</strong>
              <span class="text-blue-700 ml-2">{{ report.job_opening }}</span>
            </div>
            <div>
              <strong class="text-blue-900">Status:</strong>
              <span class="text-blue-700 ml-2">{{ report.status }}</span>
            </div>
            <div>
              <strong class="text-blue-900">Candidates Analyzed:</strong>
              <span class="text-blue-700 ml-2">{{ report.candidates_analyzed || 0 }}</span>
            </div>
            <div v-if="report.report_generated_date">
              <strong class="text-blue-900">Generated Date:</strong>
              <span class="text-blue-700 ml-2">{{ formatDate(report.report_generated_date) }}</span>
            </div>
            <div v-if="report.top_candidates">
              <strong class="text-blue-900">Top Candidates Count:</strong>
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
      loadingJobOpenings: false
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
    }
  },
  mounted() {
    this.loadJobOpeningsList()
    
    if (this.$route.query.reportId) {
      this.loadReportById(this.$route.query.reportId)
    } else if (this.effectiveJobOpening) {
      this.loadJobOpeningData()
    }
  },
  watch: {
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
    clearInputs() {
      this.formJobOpening = ''
      this.report = null
      this.error = null
      this.isGenerating = false
      this.jobOpeningData = null
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
      this.error = 'Report generation cancelled'
    },
    async generateReport() {
      if (!this.effectiveJobOpening) {
        this.error = 'Please select a Job Opening'
        return
      }

      await this.loadJobOpeningData()

      this.isGenerating = true
      this.error = null
      this.pollingAttempts = 0
      
      try {
        const data = await call('ai_hr_recruitment.ai_hr_recruitment.api.recruitment_reports.generate_recruitment_report', {
          job_opening: this.effectiveJobOpening
        })
  
        if (data && data.status) {
          if (data.status === 'processing' || data.status === 'exists') {
            // Load the report first so it displays
            await this.loadReport(data.report_id)
            // If report is still generating, start/continue polling
            if (this.report && this.report.status === 'Generating') {
              this.isGenerating = true
              this.pollReportStatus(data.report_id)
            }
          } else if (data.status === 'error') {
            this.error = data.message || 'Report generation failed'
            this.isGenerating = false
          }
        } else {
          this.error = 'Unexpected response from server'
          this.isGenerating = false
        }
      } catch (error) {
        console.error('Error generating report:', error)
        this.error = error.message || 'Failed to generate report. Please check your connection and try again.'
        this.isGenerating = false
      }
    },
  
    async pollReportStatus(reportId) {
      const maxAttempts = 60 // Increased attempts
      this.pollingAttempts = 0
      console.log('Starting polling for report:', reportId)
      
      // Ensure isGenerating is true when starting polling
      this.isGenerating = true
  
      const poll = async () => {
        try {
          // Check max attempts first
          if (this.pollingAttempts >= maxAttempts) {
            console.log('Polling stopped - reached max attempts')
            // But still show the report if we have it
            if (this.report && this.report.status === 'Generating') {
              this.error = `Report still processing after ${maxAttempts * 2} seconds. The background workers might not be running. Please check if 'bench start' is running, or click "Reload" to check the status again.`
            }
            this.isGenerating = false
            this.pollingInterval = null
            return
          }

          console.log(`Polling attempt ${this.pollingAttempts + 1}/${maxAttempts} for report ${reportId}`)
          const report = await call('ai_hr_recruitment.ai_hr_recruitment.api.recruitment_reports.get_recruitment_report', {
            report_id: reportId
          })
  
          this.pollingAttempts++
          console.log('Report status:', report ? report.status : 'null')
          console.log('Full report data:', report)
  
          if (report) {
            // Always update the report so UI shows latest data
            this.report = report
            console.log('Updated report in UI. Status:', report.status)
            console.log('Report has top_candidates:', report.top_candidates ? report.top_candidates.length : 0)
            
            // Handle based on actual report status, not isGenerating flag
            if (report.status === 'Completed') {
              console.log('✅ Report completed!', report)
              console.log('Report summary length:', report.ai_analysis_summary ? report.ai_analysis_summary.length : 0)
              console.log('Top candidates count:', report.top_candidates ? report.top_candidates.length : 0)
              this.isGenerating = false
              this.pollingInterval = null
              this.pollingAttempts = 0
              this.error = null // Clear any errors
              return
            } else if (report.status === 'Failed') {
              console.log('❌ Report failed')
              this.error = report.ai_analysis_summary || 'Report generation failed'
              this.isGenerating = false
              this.pollingInterval = null
              return
            } else if (report.status === 'Generating' || report.status === 'Draft') {
              console.log(`⏳ Still generating... (attempt ${this.pollingAttempts}/${maxAttempts})`)
              // Keep isGenerating true while generating
              this.isGenerating = true
              // Continue polling - don't check isGenerating flag
              if (this.pollingAttempts < maxAttempts) {
                this.pollingInterval = setTimeout(poll, 2000)
              } else {
                this.error = `Report still processing after ${maxAttempts * 2} seconds. The background workers might not be running. Please check if 'bench start' is running, or click "Reload" to check the status again.`
                this.isGenerating = false
                this.pollingInterval = null
              }
              return
            } else {
              console.log('⚠️ Unknown status:', report.status)
              // Continue polling if we don't know the status
              if (this.pollingAttempts < maxAttempts) {
                this.isGenerating = true
                this.pollingInterval = setTimeout(poll, 2000)
              } else {
                this.error = `Unknown report status: ${report.status}. Showing current data anyway.`
                this.isGenerating = false
                this.pollingInterval = null
              }
              return
            }
          } else {
            console.log('⚠️ No report data returned')
            if (this.pollingAttempts < maxAttempts) {
              this.isGenerating = true
              this.pollingInterval = setTimeout(poll, 2000)
            } else {
              this.error = 'Could not retrieve report data after multiple attempts'
              this.isGenerating = false
              this.pollingInterval = null
            }
          }
        } catch (error) {
          console.error('❌ Error polling:', error)
          this.pollingAttempts++
          if (this.pollingAttempts < maxAttempts) {
            console.log(`Retrying after error (attempt ${this.pollingAttempts}/${maxAttempts})...`)
            this.isGenerating = true
            this.pollingInterval = setTimeout(poll, 3000)
          } else {
            this.error = 'Error checking report status: ' + (error.message || 'Unknown error')
            this.isGenerating = false
            this.pollingInterval = null
          }
        }
      }
  
      // Start polling immediately
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
            this.loadJobOpeningData()
          }
          
          // Handle status appropriately
          if (report.status === 'Generating') {
            console.log('Report still generating, starting polling...')
            this.isGenerating = true
            // Clear any existing polling interval
            if (this.pollingInterval) {
              clearTimeout(this.pollingInterval)
              this.pollingInterval = null
            }
            this.pollReportStatus(reportId)
          } else if (report.status === 'Completed') {
            console.log('✅ Report already completed, showing results')
            this.isGenerating = false
            this.error = null // Clear any errors
          } else if (report.status === 'Failed') {
            console.log('❌ Report failed')
            this.isGenerating = false
            this.error = 'Report generation failed'
          } else {
            console.log('⚠️ Unknown report status:', report.status)
            this.isGenerating = false
          }
        } else {
          this.error = 'Report not found'
          this.isGenerating = false
        }
      } catch (error) {
        console.error('Error loading report:', error)
        this.error = 'Failed to load report: ' + (error.message || 'Unknown error')
        this.isGenerating = false
      }
    },

    async loadReportById(reportId = null) {
      if (!reportId) {
        this.error = 'Please provide a Report ID'
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
        this.error = 'No report available to trigger processing'
        return
      }

      if (this.report.status !== 'Generating') {
        this.error = 'Report is not in Generating status'
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
        this.error = 'Failed to trigger processing: ' + (error.message || 'Unknown error')
      }
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      try {
        const date = new Date(dateString)
        return date.toLocaleString('en-US', {
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
        await this.loadJobOpeningData()
      } else {
        this.jobOpeningData = null
      }
    },

    getRecommendationClass(recommendation) {
      const classes = {
        'Hire': 'bg-green-100 text-green-800',
        'Consider': 'bg-blue-100 text-blue-800',
        'Additional Interview': 'bg-yellow-100 text-yellow-800',
        'Reject': 'bg-red-100 text-red-800'
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
        this.error = 'No report available to export'
        return
      }

      if (this.report.status !== 'Completed') {
        this.error = 'Report must be completed before exporting'
        return
      }

      try {
        // Create download link
        const url = `/api/method/ai_hr_recruitment.ai_hr_recruitment.api.recruitment_reports.export_report_to_pdf?report_id=${this.report.name}`
        
        // Create a temporary link and trigger download
        const link = document.createElement('a')
        link.href = url
        link.download = `recruitment_report_${this.report.name}.pdf`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      } catch (error) {
        console.error('Error exporting PDF:', error)
        this.error = 'Failed to export PDF: ' + (error.message || 'Unknown error')
      }
    },

    async exportToExcel() {
      if (!this.report || !this.report.name) {
        this.error = 'No report available to export'
        return
      }

      if (this.report.status !== 'Completed') {
        this.error = 'Report must be completed before exporting'
        return
      }

      try {
        // Create download link
        const url = `/api/method/ai_hr_recruitment.ai_hr_recruitment.api.recruitment_reports.export_report_to_excel?report_id=${this.report.name}`
        
        // Create a temporary link and trigger download
        const link = document.createElement('a')
        link.href = url
        link.download = `recruitment_report_${this.report.name}.csv`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      } catch (error) {
        console.error('Error exporting Excel:', error)
        this.error = 'Failed to export Excel: ' + (error.message || 'Unknown error')
      }
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

