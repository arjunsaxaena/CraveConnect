import { userAPI } from './api';

const BASE_URL = '/orders';

const cartService = {
  // Create a new order
  createOrder: async (orderData) => {
    try {
      const response = await userAPI.post(`${BASE_URL}`, orderData);
      return response.data;
    } catch (error) {
      console.error('Error creating order:', error);
      throw error.response?.data?.message || 'Failed to create order. Please try again.';
    }
  },  // Get user's order history
  getOrderHistory: async () => {
    try {
      const response = await userAPI.get(`${BASE_URL}/history`);
      return response.data;
    } catch (error) {
      console.error('Error fetching order history:', error);
      throw error.response?.data?.message || 'Failed to fetch order history. Please try again.';
    }
  },
  // Get order details by ID
  getOrderById: async (orderId) => {
    try {
      const response = await userAPI.get(`${BASE_URL}/${orderId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching order ${orderId}:`, error);
      throw error.response?.data?.message || 'Failed to fetch order details. Please try again.';
    }
  },

  // Update order status (for restaurant owners or admin)
  updateOrderStatus: async (orderId, status) => {
    try {
      const response = await userAPI.put(`${BASE_URL}/${orderId}/status`, { status });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Process payment for order
  processPayment: async (orderId, paymentDetails) => {
    try {
      const response = await userAPI.post(`${BASE_URL}/${orderId}/payment`, paymentDetails);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Cancel an order
  cancelOrder: async (orderId, reason) => {
    try {
      const response = await userAPI.put(`${BASE_URL}/${orderId}/cancel`, { reason });
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default cartService;
