import { menuAPI, createFormDataConfig } from './api';

/**
 * Menu Service - handles all API calls related to menu items
 */
const MenuService = {
  /**
   * Get all menu items
   * @returns {Promise} - API response
   */
  getAllMenuItems: async () => {
    try {
      const response = await menuAPI.get('/menu');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get menu item by ID
   * @param {string} id - Menu item ID
   * @returns {Promise} - API response
   */
  getMenuItemById: async (id) => {
    try {
      const response = await menuAPI.get(`/menu/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get menu items by restaurant ID
   * @param {string} restaurantId - Restaurant ID
   * @returns {Promise} - API response
   */
  getMenuItemsByRestaurantId: async (restaurantId) => {
    try {
      const response = await menuAPI.get(`/menu/restaurant/${restaurantId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Create a new menu item
   * @param {Object} menuItemData - Menu item data
   * @returns {Promise} - API response
   */
  createMenuItem: async (menuItemData) => {
    try {
      // Handle file uploads with FormData
      const formData = new FormData();
      
      // Append text fields
      Object.keys(menuItemData).forEach(key => {
        if (key !== 'item_image') {
          formData.append(key, menuItemData[key]);
        }
      });
      
      // Append file if it exists
      if (menuItemData.item_image) {
        formData.append('item_image', menuItemData.item_image);
      }
      
      const response = await menuAPI.post('/menu', formData, createFormDataConfig());
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Update an existing menu item
   * @param {string} id - Menu item ID
   * @param {Object} menuItemData - Updated menu item data
   * @returns {Promise} - API response
   */
  updateMenuItem: async (id, menuItemData) => {
    try {
      // Handle file uploads with FormData
      const formData = new FormData();
      
      // Append text fields
      Object.keys(menuItemData).forEach(key => {
        if (key !== 'item_image') {
          formData.append(key, menuItemData[key]);
        }
      });
      
      // Append file if it exists
      if (menuItemData.item_image) {
        formData.append('item_image', menuItemData.item_image);
      }
      
      const response = await menuAPI.patch(`/menu?id=${id}`, formData, createFormDataConfig());
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Delete a menu item
   * @param {string} id - Menu item ID
   * @returns {Promise} - API response
   */
  deleteMenuItem: async (id) => {
    try {
      const response = await menuAPI.delete(`/menu/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export default MenuService;
