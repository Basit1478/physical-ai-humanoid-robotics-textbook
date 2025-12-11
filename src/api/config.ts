// API Configuration
const API_BASE_URL = typeof window !== 'undefined'
  ? window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8001'
    : process.env.NEXT_PUBLIC_API_URL || 'https://your-backend-url.railway.app'
  : 'http://localhost:8001';

export { API_BASE_URL };