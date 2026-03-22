import axios from 'axios';

const AGENT_API_URL = import.meta.env.VITE_AGENT_API_URL;

const axiosInstance = axios.create({
    baseURL: AGENT_API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add request interceptor
axiosInstance.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('authData');
        if (token) {
            const authData = JSON.parse(token);
            config.headers.Authorization = `Bearer ${authData.accessToken}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default axiosInstance; 