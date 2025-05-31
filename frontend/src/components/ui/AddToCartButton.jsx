import React, { useState } from 'react';
import { useCart } from '../../context/CartContext';
import Button from './Button';
import { PlusIcon, MinusIcon } from '@heroicons/react/24/outline';
import { formatCurrency } from '../../utils/formatters';

const AddToCartButton = ({ menuItem }) => {
  const [quantity, setQuantity] = useState(1);
  const [specialInstructions, setSpecialInstructions] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { addToCart } = useCart();
  const handleAddToCart = () => {
    // Validate item has required properties
    if (!menuItem || !menuItem.id || !menuItem.name || menuItem.price === undefined) {
      console.error("Invalid menu item data:", menuItem);
      return;
    }

    const item = {
      id: menuItem.id,
      name: menuItem.name,
      price: menuItem.price || 0,
      image: menuItem.image || null,
      restaurantId: menuItem.restaurantId,
      restaurantName: menuItem.restaurantName || 'Restaurant',
      quantity: quantity,
      specialInstructions: specialInstructions.trim(),
    };

    addToCart(item);
    setIsModalOpen(false);
    
    // Reset state for next addition
    setQuantity(1);
    setSpecialInstructions('');
  };

  const incrementQuantity = () => {
    setQuantity(prev => prev + 1);
  };

  const decrementQuantity = () => {
    if (quantity > 1) {
      setQuantity(prev => prev - 1);
    }
  };

  return (
    <>
      <Button 
        onClick={() => setIsModalOpen(true)} 
        size="sm"
        className="w-full"
      >
        Add to Cart
      </Button>

      {/* Add to Cart Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg shadow-xl w-full max-w-md">
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-xl font-semibold">{menuItem.name}</h2>
              <button 
                onClick={() => setIsModalOpen(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                &times;
              </button>
            </div>
            
            {menuItem.image && (
              <img
                src={menuItem.image}
                alt={menuItem.name}
                className="w-full h-48 object-cover rounded-md mb-4"
              />
            )}

            <div className="mb-4">
              <p className="text-gray-700">{menuItem.description}</p>
              <p className="text-primary-600 font-semibold mt-2">
                {formatCurrency(menuItem.price)}
              </p>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Quantity
              </label>
              <div className="flex items-center">
                <button
                  onClick={decrementQuantity}
                  className="w-10 h-10 flex items-center justify-center bg-gray-100 rounded-l hover:bg-gray-200"
                >
                  <MinusIcon className="w-4 h-4" />
                </button>
                <span className="w-14 h-10 flex items-center justify-center border-t border-b">
                  {quantity}
                </span>
                <button
                  onClick={incrementQuantity}
                  className="w-10 h-10 flex items-center justify-center bg-gray-100 rounded-r hover:bg-gray-200"
                >
                  <PlusIcon className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Special Instructions (Optional)
              </label>
              <textarea
                value={specialInstructions}
                onChange={(e) => setSpecialInstructions(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                rows="3"
                placeholder="E.g., no onions, extra spicy, etc."
              ></textarea>
            </div>

            <div className="flex justify-between items-center">
              <div className="font-medium">
                Total: {formatCurrency(menuItem.price * quantity)}
              </div>
              <Button onClick={handleAddToCart}>
                Add to Cart
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default AddToCartButton;
