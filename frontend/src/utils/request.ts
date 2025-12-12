import axios from 'axios';
import { message } from 'antd';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // TODO: Add token to headers if it exists
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    if (error.response) {
      // Server responded with a status code outside the 2xx range
      const errorMessage = error.response.data?.detail || 'An error occurred';
      message.error(errorMessage);
    } else if (error.request) {
      // Request was made but no response received
      message.error('No response from server');
    } else {
      // Something happened in setting up the request
      message.error('Request error');
    }
    return Promise.reject(error);
  }
);

export default api;
