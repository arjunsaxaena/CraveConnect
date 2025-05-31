import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import cartService from '../services/cartService';
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

const OrderHistoryPage = () => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    const fetchOrderHistory = async () => {
      try {
        const data = await cartService.getOrderHistory();
        setOrders(data);
      } catch (err) {
        setError('Failed to load order history. Please try again.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchOrderHistory();
  }, []);

  const filteredOrders = activeTab === 'all' 
    ? orders 
    : orders.filter(order => {
        if (activeTab === 'active') {
          return ['pending', 'confirmed', 'preparing', 'ready', 'in-delivery'].includes(order.status);
        } else if (activeTab === 'completed') {
          return order.status === 'delivered';
        } else if (activeTab === 'cancelled') {
          return order.status === 'cancelled';
        }
        return true;
      });

  if (loading) {
    return (
      <MainLayout>
        <div className="container mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold mb-8">Order History</h1>
          <div className="animate-pulse">
            {[...Array(3)].map((_, index) => (
              <div key={index} className="bg-white rounded-lg shadow-md p-6 mb-4">
                <div className="h-6 bg-gray-200 rounded w-1/4 mb-4"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              </div>
            ))}
          </div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Order History</h1>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 rounded-lg p-4 mb-6">
            <p>{error}</p>
          </div>
        )}

        <div className="mb-6 border-b">
          <nav className="-mb-px flex space-x-8">
            {['all', 'active', 'completed', 'cancelled'].map((tab) => (
              <button
                key={tab}
                className={`
                  py-4 px-1 border-b-2 font-medium text-sm
                  ${activeTab === tab 
                    ? 'border-primary-500 text-primary-600' 
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}
                `}
                onClick={() => setActiveTab(tab)}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </nav>
        </div>

        {filteredOrders.length === 0 ? (
          <div className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No orders found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {activeTab === 'all' 
                ? "You haven't placed any orders yet." 
                : `You don't have any ${activeTab} orders.`}
            </p>
            <div className="mt-6">
              <Link
                to="/restaurants"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
              >
                Browse Restaurants
              </Link>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredOrders.map((order) => {
              const statusInfo = ORDER_STATUSES[order.status] || ORDER_STATUSES['pending'];
              
              return (
                <Link 
                  to={`/orders/${order.id}`} 
                  key={order.id}
                  className="block bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow"
                >
                  <div className="p-6">
                    <div className="flex flex-wrap justify-between items-start mb-4">
                      <div>
                        <h2 className="text-lg font-semibold">Order #{order.id}</h2>
                        <p className="text-gray-500 text-sm">{formatDate(order.createdAt)}</p>
                      </div>
                      <span className={`${statusInfo.color} px-3 py-1 rounded-full text-sm font-medium`}>
                        {statusInfo.label}
                      </span>
                    </div>
                    
                    <div className="flex flex-wrap gap-4 mb-4">
                      <div className="flex-1 min-w-[200px]">
                        <p className="text-sm text-gray-500 mb-1">Restaurant</p>
                        <p className="font-medium">{order.restaurant?.name || 'Multiple restaurants'}</p>
                      </div>
                      <div className="flex-1 min-w-[200px]">
                        <p className="text-sm text-gray-500 mb-1">Items</p>
                        <p className="font-medium">{order.items.length} items</p>
                      </div>
                      <div className="flex-1 min-w-[200px]">
                        <p className="text-sm text-gray-500 mb-1">Total</p>
                        <p className="font-medium">{formatCurrency(order.totalAmount)}</p>
                      </div>
                    </div>
                    
                    <div className="flex flex-wrap gap-4">
                      <div className="flex-1">
                        {order.items.slice(0, 3).map((item, index) => (
                          <div key={index} className="flex items-center text-sm">
                            <span className="mr-2">{item.quantity}x</span>
                            <span className="truncate">{item.name}</span>
                          </div>
                        ))}
                        {order.items.length > 3 && (
                          <div className="text-sm text-gray-500 mt-1">
                            +{order.items.length - 3} more items
                          </div>
                        )}
                      </div>
                      <div className="flex items-center text-primary-600 font-medium text-sm">
                        View Order Details
                        <svg
                          className="w-5 h-5 ml-1"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="M9 5l7 7-7 7"
                          ></path>
                        </svg>
                      </div>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </div>
    </MainLayout>
  );
};

export default OrderHistoryPage;
