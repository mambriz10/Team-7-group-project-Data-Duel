/**
 * DataDuel Configuration
 * Environment-aware API URL configuration
 */

// Configuration for different environments
const config = {
  development: {
    apiUrl: 'http://127.0.0.1:5000',
    environment: 'development'
  },
  production: {
    // Render backend URL (update with your actual Render URL after deployment)
    apiUrl: 'https://dataduel-backend.onrender.com',
    environment: 'production'
  }
};

// Auto-detect environment based on hostname
const isDevelopment = 
  window.location.hostname === 'localhost' || 
  window.location.hostname === '127.0.0.1' ||
  window.location.hostname === '';

const ENV = isDevelopment ? 'development' : 'production';

// Export configuration
export const API_URL = config[ENV].apiUrl;
export const ENVIRONMENT = ENV;
export const IS_DEVELOPMENT = isDevelopment;
export const IS_PRODUCTION = !isDevelopment;

// Log configuration on load (helpful for debugging)
console.log(`%c[DataDuel Config]`, 'color: #10b981; font-weight: bold');
console.log(`  Environment: ${ENVIRONMENT}`);
console.log(`  API URL: ${API_URL}`);
console.log(`  Hostname: ${window.location.hostname}`);

