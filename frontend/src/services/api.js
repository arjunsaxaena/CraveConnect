import axios from 'axios';

// Create base URLs for different services
const restaurantServiceBaseURL = 'http://localhost:8001/api';
const menuServiceBaseURL = 'http://localhost:8002/api';
const userServiceBaseURL = 'http://localhost:8003/api';
const fileServiceBaseURL = 'http://localhost:8004/api';

// Create axios instances for different services
const restaurantAPI = axios.create({
  baseURL: restaurantServiceBaseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const menuAPI = axios.create({
  baseURL: menuServiceBaseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const userAPI = axios.create({
  baseURL: userServiceBaseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const fileAPI = axios.create({
  baseURL: fileServiceBaseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
const addAuthToken = (api) => {
  api.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );
};

// Add response interceptor for error handling
const addErrorHandler = (api) => {
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      // Handle 401 Unauthorized errors
      if (error.response && error.response.status === 401) {
        localStorage.removeItem('auth_token');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );
};

// Add interceptors to all API instances
[restaurantAPI, menuAPI, userAPI, fileAPI].forEach((api) => {
  addAuthToken(api);
  addErrorHandler(api);
});

// For handling multipart form data
const createFormDataConfig = () => ({
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

export {
  restaurantAPI,
  menuAPI,
  userAPI,
  fileAPI,
  createFormDataConfig,
};
