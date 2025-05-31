import { restaurantAPI, menuAPI } from './api';

const searchService = {
  // Search by general query (across restaurants and menu items)
  search: async (query, filters = {}) => {
    try {
      // Request from both services
      const [restaurantResponse, menuResponse] = await Promise.all([
        restaurantAPI.get('/restaurants/search', { 
          params: { q: query, ...filters } 
        }).catch(err => {
          console.error('Restaurant search error:', err);
          return { data: [] }; // Return empty array on error
        }),
        menuAPI.get('/menu/search', { 
          params: { q: query, ...filters } 
        }).catch(err => {
          console.error('Menu search error:', err);
          return { data: [] }; // Return empty array on error
        })
      ]);
      
      // Combine results
      return {
        restaurants: restaurantResponse.data || [],
        menuItems: menuResponse.data || []
      };
    } catch (error) {
      console.error('Search error:', error);
      throw new Error('Failed to perform search. Please try again later.');
    }
  },

  // Search restaurants
  searchRestaurants: async (query, filters = {}) => {
    try {
      const response = await restaurantAPI.get('/restaurants/search', { 
        params: {
          q: query,
          ...filters
        } 
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Search menu items
  searchMenuItems: async (query, filters = {}) => {
    try {
      const response = await menuAPI.get('/menu/search', { 
        params: { 
          q: query,
          ...filters
        } 
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get search suggestions as user types
  getSearchSuggestions: async (query) => {
    try {
      // Get suggestions from restaurant service
      const response = await restaurantAPI.get('/search/suggestions', { 
        params: { q: query } 
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default searchService;
