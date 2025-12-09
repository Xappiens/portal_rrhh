// SPA Routes Handler
// This file handles client-side routing for the SPA

// Check if we're in a browser environment
if (typeof window !== 'undefined') {

  // Initialize SPA routing
  function initSPARouting() {
    // Get current path and determine which page to show
    const currentPath = window.location.pathname;
    const config = window.PORTAL_RRHH_CONFIG || {};

    // Map paths to page names
    const pathToPage = {
      '/portal-rrhh': 'dashboard',
      '/portal-rrhh/': 'dashboard',
      '/portal-rrhh/dashboard': 'dashboard',
      '/portal-rrhh/empleados': 'empleados',
      '/portal-rrhh/vacantes': 'vacantes',
      '/portal-rrhh/solicitudes': 'solicitudes',
      '/portal-rrhh/evaluaciones': 'evaluaciones',
      '/portal-rrhh/reportes': 'reportes',
      '/portal-rrhh/reportes': 'reportes',
      '/portal-rrhh/timesheets': 'timesheets',
      '/portal-rrhh/ai-dashboard': 'ai-dashboard',
      '/portal-rrhh/cv-analysis': 'cv-analysis'
    };

    // Get current page from path or config
    const currentPage = pathToPage[currentPath] || config.currentPage || 'dashboard';

    // Store current page for Vue app
    window.currentPage = currentPage;

    // If we're not on the main portal page, redirect to it with the correct page
    if (currentPath !== '/portal-rrhh' && currentPath !== '/portal-rrhh/') {
      // Update URL without reloading
      if (history.replaceState) {
        history.replaceState(null, null, '/portal-rrhh');
      }
    }
  }

  // Handle browser back/forward buttons
  window.addEventListener('popstate', function (event) {
    initSPARouting();
    // Let Vue Router handle the navigation
    if (window.router) {
      window.router.push(window.location.pathname);
    }
  });

  // Handle page refresh
  window.addEventListener('beforeunload', function (event) {
    // Save current route to sessionStorage
    if (window.router) {
      sessionStorage.setItem('lastRoute', window.router.currentRoute.value.path);
    }
  });

  // Initialize routing on page load
  window.addEventListener('load', function (event) {
    initSPARouting();

    // Restore route from sessionStorage if available
    const lastRoute = sessionStorage.getItem('lastRoute');
    if (lastRoute && window.router) {
      window.router.push(lastRoute);
    }
  });

  // Initialize immediately if DOM is already loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSPARouting);
  } else {
    initSPARouting();
  }
}
