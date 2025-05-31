import { userAPI } from './api';

/**
 * Auth Service - handles all API calls related to authentication
 */
const AuthService = {
  /**
   * Register a new user
   * @param {Object} userData - User registration data
   * @returns {Promise} - API response
   */
  register: async (userData) => {
    try {
      const response = await userAPI.post('/users/register', userData);
      if (response.data.token) {
        localStorage.setItem('auth_token', response.data.token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Login a user
   * @param {Object} credentials - User login credentials
   * @returns {Promise} - API response
   */
  login: async (credentials) => {
    try {
      const response = await userAPI.post('/users/login', credentials);
      if (response.data.token) {
        localStorage.setItem('auth_token', response.data.token);
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Logout the current user
   */
  logout: () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    // Redirect to home page or login page
    window.location.href = '/';
  },

  /**
   * Get the current authenticated user
   * @returns {Object|null} - User object or null if not authenticated
   */
  getCurrentUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  /**
   * Check if user is authenticated
   * @returns {boolean} - True if authenticated, false otherwise
   */
  isAuthenticated: () => {
    return !!localStorage.getItem('auth_token');
  },

  /**
   * Send phone verification code
   * @param {string} phone - Phone number
   * @returns {Promise} - API response
   */
  sendVerificationCode: async (phone) => {
    try {
      const response = await userAPI.post('/users/send-verification', { phone });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Verify phone number with code
   * @param {string} phone - Phone number
   * @param {string} code - Verification code
   * @returns {Promise} - API response
   */
  verifyPhone: async (phone, code) => {
    try {
      const response = await userAPI.post('/users/verify-phone', { 
        phone, 
        verification_code: code 
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export default AuthService;
