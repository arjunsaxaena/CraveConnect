import React, { useContext } from 'react';
import { CartContext } from '../../context/CartContext';
import Button from './Button';
import { TrashIcon } from '@heroicons/react/24/outline';
import { Link } from 'react-router-dom';
import { formatCurrency } from '../../utils/formatters';

const CartItem = ({ item, onUpdateQuantity, onRemove }) => {
  return (
    <div className="flex items-center justify-between py-4 border-b">
      <div className="flex items-center gap-4">
        <img 
          src={item.image || 'https://via.placeholder.com/80'} 
          alt={item.name} 
          className="w-20 h-20 object-cover rounded"
        />
        <div>
          <h4 className="font-medium text-gray-900">{item.name}</h4>
          <p className="text-sm text-gray-500">{item.restaurantName}</p>
          <p className="mt-1 text-primary-500 font-semibold">
            {formatCurrency(item.price)}
          </p>
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        <div className="flex items-center">
          <button
            onClick={() => onUpdateQuantity(item.id, item.quantity - 1)}
            className="w-8 h-8 flex items-center justify-center bg-gray-100 rounded-l hover:bg-gray-200"
          >
            -
          </button>
          <span className="w-10 text-center">{item.quantity}</span>
          <button
            onClick={() => onUpdateQuantity(item.id, item.quantity + 1)}
            className="w-8 h-8 flex items-center justify-center bg-gray-100 rounded-r hover:bg-gray-200"
          >
            +
          </button>
        </div>
        <button
          onClick={() => onRemove(item.id)}
          className="text-red-500 p-1 hover:bg-red-50 rounded"
        >
          <TrashIcon className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

const Cart = ({ isOpen, onClose }) => {
  // Try to use cart context with fallbacks for when context is not available
  const cartContext = React.useContext(CartContext);
  // Provide fallback values when context is not available
  const items = cartContext?.items || [];
  const totalItems = cartContext?.totalItems || 0;
  const totalAmount = cartContext?.totalAmount || 0;
  const removeFromCart = cartContext?.removeFromCart || (() => {});
  const updateQuantity = cartContext?.updateQuantity || (() => {});
  const clearCart = cartContext?.clearCart || (() => {});
  
  // Prevent body scrolling when cart is open
  React.useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    
    // Cleanup function to restore scrolling
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex justify-end">
      <div className="w-full max-w-md bg-white h-full shadow-xl flex flex-col animate-slide-in-right">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-xl font-semibold">Your Cart</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            &times;
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {items.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <svg 
                className="w-16 h-16 text-gray-300 mb-4" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth="2" 
                  d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" 
                />
              </svg>
              <p className="text-gray-500 mb-2">Your cart is empty</p>
              <Button size="sm" onClick={onClose}>
                Browse Restaurants
              </Button>
            </div>
          ) : (
            <>
              {items.map((item) => (
                <CartItem
                  key={item.id}
                  item={item}
                  onUpdateQuantity={updateQuantity}
                  onRemove={removeFromCart}
                />
              ))}
            </>
          )}
        </div>

        {items.length > 0 && (
          <div className="p-4 border-t">
            <div className="flex justify-between mb-2">
              <span className="text-gray-600">Subtotal ({totalItems} items)</span>
              <span className="font-semibold">{formatCurrency(totalAmount)}</span>
            </div>
            <div className="flex justify-between mb-4">
              <span className="text-gray-600">Delivery Fee</span>
              <span className="font-semibold">{formatCurrency(5.99)}</span>
            </div>
            <div className="flex justify-between mb-6 text-lg font-bold">
              <span>Total</span>
              <span>{formatCurrency(totalAmount + 5.99)}</span>
            </div>
            
            <div className="grid grid-cols-2 gap-3">
              <Button 
                variant="outline" 
                onClick={clearCart}
                className="border-red-500 text-red-500 hover:bg-red-50"
              >
                Clear Cart
              </Button>
              <Link 
                to="/checkout" 
                onClick={onClose}
              >
                <Button className="w-full">
                  Checkout
                </Button>
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Cart;
