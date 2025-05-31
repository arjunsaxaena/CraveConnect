import React, { useEffect, useState } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import cartService from '../services/cartService';
import Button from '../components/ui/Button';
import { formatCurrency, formatDate } from '../utils/formatters';

const ORDER_STATUSES = {
  'pending': { color: 'bg-yellow-100 text-yellow-800', label: 'Pending' },
  'confirmed': { color: 'bg-blue-100 text-blue-800', label: 'Confirmed' },
  'preparing': { color: 'bg-indigo-100 text-indigo-800', label: 'Preparing' },
  'ready': { color: 'bg-purple-100 text-purple-800', label: 'Ready for Pickup' },
  'in-delivery': { color: 'bg-pink-100 text-pink-800', label: 'In Delivery' },
  'delivered': { color: 'bg-green-100 text-green-800', label: 'Delivered' },
  'cancelled': { color: 'bg-red-100 text-red-800', label: 'Cancelled' },
};

const OrderTrackingPage = () => {
  const { orderId } = useParams();
  const location = useLocation();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchOrderDetails = async () => {
      try {
        const data = await cartService.getOrderById(orderId);
        setOrder(data);
      } catch (err) {
        setError('Failed to load order details. Please try again.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchOrderDetails();

    // Poll for order status updates every 30 seconds
    const intervalId = setInterval(fetchOrderDetails, 30000);
    
    return () => clearInterval(intervalId);
  }, [orderId]);

  const handleCancelOrder = async () => {
    if (!window.confirm('Are you sure you want to cancel this order?')) return;
    
    try {
      await cartService.cancelOrder(orderId, 'Customer requested cancellation');
      // Refresh order data
      const updatedOrder = await cartService.getOrderById(orderId);
      setOrder(updatedOrder);
    } catch (err) {
      setError('Failed to cancel order. Please try again or contact support.');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="container mx-auto px-4 py-12 text-center">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mx-auto mb-6"></div>
            <div className="h-64 bg-gray-200 rounded max-w-lg mx-auto"></div>
          </div>
        </div>
      </MainLayout>
    );
  }

  if (error || !order) {
    return (
      <MainLayout>
        <div className="container mx-auto px-4 py-12 text-center">
          <h2 className="text-2xl font-semibold mb-4">Oops! Something went wrong</h2>
          <p className="text-gray-600 mb-6">{error || 'Order not found'}</p>
          <Button onClick={() => window.location.reload()}>Try Again</Button>
        </div>
      </MainLayout>
    );
  }

  const statusInfo = ORDER_STATUSES[order.status] || ORDER_STATUSES['pending'];

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        {location.state?.success && (
          <div className="bg-green-50 border border-green-200 text-green-800 rounded-lg p-4 mb-6">
            <p className="font-medium">{location.state.message}</p>
          </div>
        )}

        <div className="flex flex-wrap items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">Order #{orderId}</h1>
          <span className={`${statusInfo.color} px-3 py-1 rounded-full text-sm font-medium`}>
            {statusInfo.label}
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            {/* Order Timeline */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-xl font-semibold mb-4">Order Status</h2>
              
              <div className="relative">
                <div className="absolute left-4 top-0 h-full w-0.5 bg-gray-200"></div>
                
                {['confirmed', 'preparing', 'in-delivery', 'delivered'].map((status, index) => {
                  const isCompleted = ['delivered', 'in-delivery', 'preparing', 'confirmed']
                    .indexOf(order.status) >= index;
                  const isCurrent = order.status === status;
                    
                  return (
                    <div key={status} className="relative flex items-start mb-6 pl-10">
                      <div className={`absolute left-2 -translate-x-1/2 w-6 h-6 rounded-full ${
                        isCompleted ? 'bg-primary-500' : 'bg-gray-200'
                      } flex items-center justify-center z-10`}>
                        {isCompleted && (
                          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 0 1 0 1.414l-8 8a1 1 0 0 1-1.414 0l-4-4a1 1 0 0 1 1.414-1.414L8 12.586l7.293-7.293a1 1 0 0 1 1.414 0z" clipRule="evenodd" />
                          </svg>
                        )}
                      </div>
                      <div>
                        <h3 className={`font-medium ${isCurrent ? 'text-primary-600' : ''}`}>
                          {ORDER_STATUSES[status].label}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {isCurrent ? 'Current status' : isCompleted ? 'Completed' : 'Pending'}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>

              {(order.status === 'pending' || order.status === 'confirmed') && (
                <div className="mt-4 pt-4 border-t">
                  <Button 
                    variant="outline" 
                    className="border-red-500 text-red-500 hover:bg-red-50"
                    onClick={handleCancelOrder}
                  >
                    Cancel Order
                  </Button>
                </div>
              )}
            </div>

            {/* Order Items */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Order Items</h2>
              <div className="space-y-4">
                {order.items.map((item) => (
                  <div key={item.id} className="flex justify-between items-center">
                    <div className="flex items-center gap-4">
                      <div className="w-16 h-16 rounded-lg bg-gray-100 flex items-center justify-center">
                        {item.image ? (
                          <img 
                            src={item.image} 
                            alt={item.name}
                            className="w-full h-full object-cover rounded-lg" 
                          />
                        ) : (
                          <span className="text-2xl">🍽️</span>
                        )}
                      </div>
                      <div>
                        <p className="font-medium">{item.name}</p>
                        <p className="text-sm text-gray-500">Quantity: {item.quantity}</p>
                        {item.specialInstructions && (
                          <p className="text-xs text-gray-500 mt-1">
                            Note: {item.specialInstructions}
                          </p>
                        )}
                      </div>
                    </div>
                    <p className="font-medium">{formatCurrency(item.price * item.quantity)}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          <div>
            {/* Order Summary */}
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-24">
              <h2 className="text-xl font-semibold mb-4">Order Summary</h2>
              
              <div className="space-y-4 mb-6">
                <div className="flex justify-between">
                  <span className="text-gray-600">Order Date</span>
                  <span>{formatDate(order.createdAt)}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">Restaurant</span>
                  <span>{order.restaurant?.name || 'Multiple restaurants'}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">Delivery Address</span>
                  <span className="text-right">{order.deliveryAddress.address}, {order.deliveryAddress.city}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">Payment Method</span>
                  <span className="capitalize">{order.paymentMethod}</span>
                </div>
              </div>
              
              <div className="border-t pt-4">
                <div className="flex justify-between mb-2">
                  <span className="text-gray-600">Subtotal</span>
                  <span>{formatCurrency(order.totalAmount - 5.99)}</span>
                </div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-600">Delivery Fee</span>
                  <span>{formatCurrency(5.99)}</span>
                </div>
                <div className="flex justify-between font-bold text-lg mt-4">
                  <span>Total</span>
                  <span>{formatCurrency(order.totalAmount)}</span>
                </div>
              </div>

              {order.status === 'delivered' && (
                <div className="mt-6 pt-4 border-t">
                  <Button className="w-full">Reorder</Button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default OrderTrackingPage;
