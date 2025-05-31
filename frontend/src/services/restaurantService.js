import { restaurantAPI, createFormDataConfig } from './api';

/**
 * Restaurant Service - handles all API calls related to restaurants
 */
const RestaurantService = {
  /**
   * Get all restaurants
   * @returns {Promise} - API response
   */
  getAllRestaurants: async () => {
    try {
      const response = await restaurantAPI.get('/restaurants');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get restaurant by ID
   * @param {string} id - Restaurant ID
   * @returns {Promise} - API response
   */
  getRestaurantById: async (id) => {
    try {
      const response = await restaurantAPI.get(`/restaurants/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Create a new restaurant
   * @param {Object} restaurantData - Restaurant data
   * @returns {Promise} - API response
   */
  createRestaurant: async (restaurantData) => {
    try {
      // Handle file uploads with FormData
      const formData = new FormData();
      
      // Append text fields
      Object.keys(restaurantData).forEach(key => {
        if (key !== 'restaurant_image' && key !== 'menu_image') {
          formData.append(key, restaurantData[key]);
        }
      });
      
      // Append files if they exist
      if (restaurantData.restaurant_image) {
        formData.append('restaurant_image', restaurantData.restaurant_image);
      }
      
      if (restaurantData.menu_image) {
        formData.append('menu_image', restaurantData.menu_image);
      }
      
      const response = await restaurantAPI.post('/restaurants', formData, createFormDataConfig());
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Update an existing restaurant
   * @param {string} id - Restaurant ID
   * @param {Object} restaurantData - Updated restaurant data
   * @returns {Promise} - API response
   */
  updateRestaurant: async (id, restaurantData) => {
    try {
      // Handle file uploads with FormData
      const formData = new FormData();
      
      // Append text fields
      Object.keys(restaurantData).forEach(key => {
        if (key !== 'restaurant_image' && key !== 'menu_image') {
          formData.append(key, restaurantData[key]);
        }
      });
      
      // Append files if they exist
      if (restaurantData.restaurant_image) {
        formData.append('restaurant_image', restaurantData.restaurant_image);
      }
      
      if (restaurantData.menu_image) {
        formData.append('menu_image', restaurantData.menu_image);
      }
      
      const response = await restaurantAPI.patch(`/restaurants?id=${id}`, formData, createFormDataConfig());
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Delete a restaurant
   * @param {string} id - Restaurant ID
   * @returns {Promise} - API response
   */
  deleteRestaurant: async (id) => {
    try {
      const response = await restaurantAPI.delete(`/restaurants/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export default RestaurantService;
