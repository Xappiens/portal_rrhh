<template>
  <div class="flex-1 p-6 bg-gray-50">
    <div class="mb-8 pb-6 border-b border-gray-200">
      <div class="flex justify-between items-start">
        <div>
          <h2 class="text-2xl font-semibold text-gray-900 mb-2">🤖 AI Recruitment Dashboard</h2>
          <p class="text-sm text-gray-600">Track CV analyses and recruitment insights</p>
        </div>
        <div class="flex items-center gap-3">
          <span v-if="refreshInterval" class="text-xs text-gray-500">Auto-refreshing every 30s</span>
          <button @click="loadDashboardData" :disabled="loading" class="px-4 py-2 bg-blue-500 text-white rounded-lg font-semibold hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed">
            <span v-if="loading">🔄 Loading...</span>
            <span v-else>🔄 Refresh</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <strong class="text-red-800">⚠️ Error:</strong> 
        <span class="text-red-700">{{ error }}</span>
      </div>
      <button @click="loadDashboardData" class="px-3 py-1 bg-red-600 text-white rounded text-sm font-semibold hover:bg-red-700">Retry</button>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !stats.cvsAnalyzed" class="text-center py-16">
      <div class="inline-block w-12 h-12 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin mb-4"></div>
      <p class="text-gray-600">Loading dashboard data...</p>
    </div>

    <!-- Dashboard Content -->
    <div v-else>
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center shadow-md">
                <span class="text-2xl">📊</span>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">CVs Analyzed</p>
              <p class="text-3xl font-bold text-gray-900">{{ stats.cvsAnalyzed || 0 }}</p>
              <p class="text-xs text-gray-500 mt-1">Total completed analyses</p>
            </div>
          </div>
        </div>

        <div 
          class="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow cursor-pointer"
          @click="toggleReportsView"
          :class="showReports ? 'ring-2 ring-green-500' : ''"
        >
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center shadow-md">
                <span class="text-2xl">📄</span>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">Reports Generated</p>
              <p class="text-3xl font-bold text-gray-900">{{ stats.reportsGenerated || 0 }}</p>
              <p class="text-xs text-gray-500 mt-1">Recruitment reports created</p>
              <p v-if="showReports" class="text-xs text-green-600 mt-1 font-semibold">← Click to view reports</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-12 h-12 bg-yellow-500 rounded-lg flex items-center justify-center shadow-md">
                <span class="text-2xl">✅</span>
              </div>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">Success Rate</p>
              <p class="text-3xl font-bold text-gray-900">{{ stats.successRate || 0 }}%</p>
              <p class="text-xs text-gray-500 mt-1">Analysis completion rate</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Analyses/Reports Section -->
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex justify-between items-center mb-6 pb-4 border-b border-gray-200">
          <div class="flex items-center gap-3">
            <h3 class="text-lg font-semibold text-gray-900">
              <span v-if="!showReports">📋 Recent CV Analysis</span>
              <span v-else>📄 Recent Reports</span>
            </h3>
            <button 
              v-if="showReports"
              @click="showReports = false"
              class="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-semibold"
            >
              ← Back to Analyses
            </button>
          </div>
          <span v-if="(showReports ? recentReports : recentAnalyses).length > 0" class="px-3 py-1 bg-blue-500 text-white rounded-full text-xs font-semibold">
            {{ (showReports ? recentReports : recentAnalyses).length }} {{ showReports ? 'report' : 'analysis' }}{{ (showReports ? recentReports : recentAnalyses).length === 1 ? '' : 's' }}
          </span>
        </div>

        <!-- Reports View -->
        <template v-if="showReports">
          <!-- Empty State for Reports -->
          <div v-if="recentReports.length === 0" class="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
            <div class="text-5xl mb-4">📭</div>
            <h4 class="text-lg font-semibold text-gray-900 mb-2">No reports yet</h4>
            <p class="text-sm text-gray-600 mb-6">Start generating recruitment reports to see them here.</p>
            <button @click="goToReports" class="px-4 py-2 bg-green-500 text-white rounded-lg font-semibold hover:bg-green-600">
              Go to Reports →
            </button>
          </div>

          <!-- Reports List -->
          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div 
              v-for="(report, index) in recentReports" 
              :key="`report-${report.name}-${lastRefreshTime ? lastRefreshTime.getTime() : index}`" 
              class="bg-gray-50 rounded-lg p-5 border-2 border-gray-200 hover:border-green-400 cursor-pointer transition-all hover:shadow-lg"
              @click="viewReport(report)"
            >
              <div class="flex items-center gap-4 mb-4">
                <div class="w-14 h-14 rounded-lg bg-green-500 flex items-center justify-center text-white text-2xl font-bold flex-shrink-0 shadow-md">
                  📄
                </div>
                <div class="flex-1 min-w-0">
                  <h4 class="text-base font-semibold text-gray-900 truncate mb-1">{{ report.job_title || 'Unknown Position' }}</h4>
                  <p v-if="report.report_timestamp" class="text-xs text-gray-500 mt-1">
                    {{ formatDate(report.report_timestamp) }}
                  </p>
                </div>
              </div>
              <div class="flex justify-between items-center pt-4 border-t border-gray-200">
                <div class="flex flex-col items-center px-4 py-2 rounded-lg font-semibold shadow-sm bg-green-500 text-white">
                  <span class="text-xs opacity-90 mb-1">Candidates</span>
                  <span class="text-xl">{{ report.total_candidates || 0 }}</span>
                </div>
                <span class="text-sm text-green-600 font-semibold hover:text-green-800">View Report →</span>
              </div>
            </div>
          </div>
        </template>

        <!-- Analyses View -->
        <template v-else>
          <!-- Empty State for Analyses -->
          <div v-if="recentAnalyses.length === 0" class="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
            <div class="text-5xl mb-4">📭</div>
            <h4 class="text-lg font-semibold text-gray-900 mb-2">No analysis yet</h4>
            <p class="text-sm text-gray-600 mb-6">Start analyzing CVs to see results here.</p>
            <button @click="goToAnalysis" class="px-4 py-2 bg-blue-500 text-white rounded-lg font-semibold hover:bg-blue-600">
              Go to CV Analysis →
            </button>
          </div>

          <!-- Analyses List -->
          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div 
              v-for="(analysis, index) in recentAnalyses" 
              :key="`analysis-${analysis.name}-${lastRefreshTime ? lastRefreshTime.getTime() : index}`" 
              class="bg-gray-50 rounded-lg p-5 border-2 border-gray-200 hover:border-blue-400 cursor-pointer transition-all hover:shadow-lg"
              @click="viewAnalysis(analysis)"
            >
              <div class="flex items-center gap-4 mb-4">
                <div class="w-14 h-14 rounded-lg bg-blue-500 flex items-center justify-center text-white text-2xl font-bold flex-shrink-0 shadow-md">
                  {{ (analysis.candidate_name || 'U')[0].toUpperCase() }}
                </div>
                <div class="flex-1 min-w-0">
                  <h4 class="text-base font-semibold text-gray-900 truncate mb-1">{{ analysis.candidate_name || 'Unknown Candidate' }}</h4>
                  <p class="text-sm text-gray-600 truncate">{{ analysis.job_title || 'Unknown Position' }}</p>
                  <p v-if="analysis.analysis_timestamp" class="text-xs text-gray-500 mt-1">
                    {{ formatDate(analysis.analysis_timestamp) }}
                  </p>
                </div>
              </div>
              <div class="flex justify-between items-center pt-4 border-t border-gray-200">
                <div class="flex flex-col items-center px-4 py-2 rounded-lg font-semibold shadow-sm" :class="getScoreClass(analysis.overall_score) === 'high' ? 'bg-green-500 text-white' : getScoreClass(analysis.overall_score) === 'medium' ? 'bg-yellow-500 text-white' : 'bg-red-500 text-white'">
                  <span class="text-xs opacity-90 mb-1">Score</span>
                  <span class="text-xl">{{ analysis.overall_score || 0 }}%</span>
                </div>
                <span class="text-sm text-blue-600 font-semibold hover:text-blue-800">View Details →</span>
              </div>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import { call } from 'frappe-ui'

export default {
  name: 'AIDashboard',
  data() {
    return {
      stats: {
        cvsAnalyzed: 0,
        reportsGenerated: 0,
        successRate: 0
      },
      recentAnalyses: [],
      recentReports: [],
      showReports: false,
      loading: false,
      error: null,
      refreshInterval: null,
      lastRefreshTime: null
    }
  },
  mounted() {
    this.loadDashboardData()
    // Set up auto-refresh every 30 seconds
    this.startAutoRefresh()
  },
  beforeUnmount() {
    this.stopAutoRefresh()
  },
  activated() {
    // Refresh when component becomes active (kept-alive or route activation)
    this.loadDashboardData()
    this.startAutoRefresh()
  },
  deactivated() {
    // Stop auto-refresh when component is deactivated
    this.stopAutoRefresh()
  },
  watch: {
    // Refresh when navigating to this route (from any route)
    '$route'(to, from) {
      if (to.name === 'AIDashboard') {
        // Refresh immediately when route changes to AIDashboard
        this.loadDashboardData()
      }
    }
  },
  methods: {
    async loadDashboardData(silent = false) {
      // Don't show loading spinner for silent refreshes (auto-refresh)
      if (!silent) {
        this.loading = true
      }
      this.error = null
      try {
        const data = await call('ai_hr_recruitment.ai_hr_recruitment.www.ai_dashboard.get_dashboard_data', {
          limit: 10
        })
        
        if (data) {
          // Always update stats, even if some fields are missing
          if (data.stats) {
            this.stats = {
              cvsAnalyzed: data.stats.cvsAnalyzed ?? 0,
              reportsGenerated: data.stats.reportsGenerated ?? 0,
              successRate: data.stats.successRate ?? 0
            }
          }
          
          // Always update recent analyses array - create completely new array to force reactivity
          const newRecentAnalyses = Array.isArray(data.recent_analyses) ? JSON.parse(JSON.stringify(data.recent_analyses)) : []
          
          // Update the array directly - Vue should detect the change
          this.recentAnalyses = newRecentAnalyses
          this.lastRefreshTime = new Date()
          
          // Load reports if showing reports view
          if (this.showReports) {
            await this.loadReports()
          }
          
          // Force Vue to re-render after a microtask to ensure DOM updates
          this.$nextTick(() => {
            // Force update one more time to ensure rendering
            if (this.$forceUpdate) {
              this.$forceUpdate()
            }
          })
        } else {
          this.error = 'No data returned from server'
        }
      } catch (error) {
        this.error = error.message || error.exc || 'Failed to load dashboard data. Please check your connection.'
      } finally {
        this.loading = false
      }
    },
    async loadReports() {
      try {
        const reports = await call('ai_hr_recruitment.ai_hr_recruitment.www.ai_dashboard.get_recent_reports', {
          limit: 10
        })
        this.recentReports = Array.isArray(reports) ? JSON.parse(JSON.stringify(reports)) : []
      } catch (error) {
        this.recentReports = []
      }
    },
    async toggleReportsView() {
      this.showReports = !this.showReports
      if (this.showReports) {
        // Always reload reports when switching to reports view
        await this.loadReports()
      }
    },
    viewReport(report) {
      if (report.name) {
        this.$router.push({
          name: 'RecruitmentReports',
          query: {
            reportId: report.name
          }
        })
      }
    },
    goToReports() {
      this.$router.push({ name: 'RecruitmentReports' })
    },
    getScoreClass(score) {
      if (score >= 80) return 'high'
      if (score >= 60) return 'medium'
      return 'low'
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
    viewAnalysis(analysis) {
      if (analysis.name) {
        this.$router.push({
          name: 'CVAnalysis',
          params: {
            jobApplicant: analysis.job_applicant || '',
            jobOpening: analysis.job_opening || ''
          },
          query: {
            analysisId: analysis.name
          }
        })
      }
    },
    goToAnalysis() {
      this.$router.push({ name: 'CVAnalysis' })
    },
    startAutoRefresh() {
      // Clear any existing interval
      this.stopAutoRefresh()
      
      // Refresh every 30 seconds (silent refresh - no loading spinner)
      this.refreshInterval = setInterval(() => {
        this.loadDashboardData(true) // silent refresh
      }, 30000) // 30 seconds
    },
    stopAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval)
        this.refreshInterval = null
      }
    }
  }
}
</script>

<style scoped>
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
