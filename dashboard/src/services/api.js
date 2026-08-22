import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
});

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => Promise.reject(error.response?.data || error.message || 'An error occurred'),
);

export default apiClient;
