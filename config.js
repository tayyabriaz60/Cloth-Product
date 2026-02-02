// API Configuration
// For local development, use localhost
// For production, this will be set to your Render URL
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : window.location.origin; // Use same origin if frontend is served from backend
