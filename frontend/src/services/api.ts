import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Dev-only startup log
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
    console.log(`[G-RAG] API Base URL: ${API_BASE_URL}`);
}

const api = axios.create({
    baseURL: `${API_BASE_URL}/api/v1`,
    timeout: 30000,
});

// Add a request interceptor to include the JWT token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('minirag_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Health check function
export const checkBackendHealth = async (): Promise<boolean> => {
    try {
        await axios.get(`${API_BASE_URL}/health`, { timeout: 5000 });
        return true;
    } catch {
        return false;
    }
};

export const getApiBaseUrl = () => API_BASE_URL;

export default api;
