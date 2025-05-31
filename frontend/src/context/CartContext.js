import React, { createContext, useContext, useReducer, useEffect } from 'react';

// Export CartContext so it can be imported directly
export const CartContext = createContext();

const initialState = {
  items: [],
  totalAmount: 0,
  totalItems: 0,
};

// Cart reducer to handle various actions
const cartReducer = (state, action) => {
  switch (action.type) {
    case 'ADD_ITEM': {
      const existingItemIndex = state.items.findIndex(
        (item) => item.id === action.payload.id
      );

      let updatedItems = [...state.items];
      
      if (existingItemIndex !== -1) {
        // Item already exists in cart, update quantity
        const existingItem = state.items[existingItemIndex];
        const updatedItem = {
          ...existingItem,
          quantity: existingItem.quantity + action.payload.quantity,
        };
        updatedItems[existingItemIndex] = updatedItem;
      } else {
        // Add new item to cart
        updatedItems = [...state.items, { ...action.payload }];
      }

      // Calculate new totals
      const totalItems = updatedItems.reduce((sum, item) => sum + item.quantity, 0);
      const totalAmount = updatedItems.reduce(
        (sum, item) => sum + item.price * item.quantity, 
        0
      );

      // Save to localStorage
      localStorage.setItem('cart', JSON.stringify({
        items: updatedItems,
        totalItems,
        totalAmount
      }));

      return {
        items: updatedItems,
        totalItems,
        totalAmount,
      };
    }

    case 'REMOVE_ITEM': {
      const existingItemIndex = state.items.findIndex(
        (item) => item.id === action.payload
      );

      if (existingItemIndex === -1) return state;

      let updatedItems = [...state.items];
      const existingItem = state.items[existingItemIndex];

      if (existingItem.quantity === 1) {
        // Remove item entirely if quantity is 1
        updatedItems = state.items.filter(item => item.id !== action.payload);
      } else {
        // Decrease quantity by 1
        const updatedItem = {
          ...existingItem,
          quantity: existingItem.quantity - 1,
        };
        updatedItems[existingItemIndex] = updatedItem;
      }

      // Calculate new totals
      const totalItems = updatedItems.reduce((sum, item) => sum + item.quantity, 0);
      const totalAmount = updatedItems.reduce(
        (sum, item) => sum + item.price * item.quantity, 
        0
      );

      // Save to localStorage
      localStorage.setItem('cart', JSON.stringify({
        items: updatedItems,
        totalItems,
        totalAmount
      }));

      return {
        items: updatedItems,
        totalItems,
        totalAmount,
      };
    }

    case 'UPDATE_QUANTITY': {
      const { id, quantity } = action.payload;
      if (quantity <= 0) {
        return state;
      }

      const updatedItems = state.items.map(item => 
        item.id === id ? { ...item, quantity } : item
      );

      // Calculate new totals
      const totalItems = updatedItems.reduce((sum, item) => sum + item.quantity, 0);
      const totalAmount = updatedItems.reduce(
        (sum, item) => sum + item.price * item.quantity, 
        0
      );

      // Save to localStorage
      localStorage.setItem('cart', JSON.stringify({
        items: updatedItems,
        totalItems,
        totalAmount
      }));

      return {
        items: updatedItems,
        totalItems,
        totalAmount,
      };
    }

    case 'CLEAR_CART':
      localStorage.removeItem('cart');
      return initialState;

    case 'LOAD_CART':
      return action.payload;

    default:
      return state;
  }
};

export const CartProvider = ({ children }) => {
  const [cartState, dispatch] = useReducer(cartReducer, initialState);

  // Load cart from localStorage on initial mount
  useEffect(() => {
    const savedCart = localStorage.getItem('cart');
    if (savedCart) {
      dispatch({
        type: 'LOAD_CART',
        payload: JSON.parse(savedCart)
      });
    }
  }, []);

  // Cart actions
  const addToCart = (item) => {
    dispatch({
      type: 'ADD_ITEM',
      payload: item,
    });
  };

  const removeFromCart = (id) => {
    dispatch({
      type: 'REMOVE_ITEM',
      payload: id,
    });
  };

  const updateQuantity = (id, quantity) => {
    dispatch({
      type: 'UPDATE_QUANTITY',
      payload: { id, quantity },
    });
  };

  const clearCart = () => {
    dispatch({ type: 'CLEAR_CART' });
  };

  const value = {
    ...cartState,
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};

export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};
