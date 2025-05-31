import React, { useState } from 'react';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Formik, Form } from 'formik';
import * as Yup from 'yup';
import MainLayout from '../layouts/MainLayout';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import cartService from '../services/cartService';
import { formatCurrency } from '../utils/formatters';

const validationSchema = Yup.object().shape({
  address: Yup.string().required('Delivery address is required'),
  city: Yup.string().required('City is required'),
  zipCode: Yup.string().required('ZIP code is required'),
  phone: Yup.string().required('Phone number is required'),
});

const CheckoutPage = () => {
  const { user } = useAuth();
  const { items, totalItems, totalAmount, clearCart } = useCart();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState('card');

  if (items.length === 0) {
    return (
      <MainLayout>
        <div className="container mx-auto px-4 py-12 text-center">
          <h2 className="text-2xl font-semibold mb-6">Your cart is empty</h2>
          <p className="text-gray-600 mb-6">Add some delicious items to your cart before checking out.</p>
          <Button onClick={() => navigate('/restaurants')}>Browse Restaurants</Button>
        </div>
      </MainLayout>
    );
  }

  const handleSubmit = async (values) => {
    setIsLoading(true);
    
    try {
      // Prepare order data
      const orderData = {
        items: items.map(item => ({
          menuItemId: item.id,
          quantity: item.quantity,
          specialInstructions: item.specialInstructions || '',
        })),
        deliveryAddress: {
          address: values.address,
          city: values.city,
          zipCode: values.zipCode,
        },
        contactPhone: values.phone,
        paymentMethod: paymentMethod,
        totalAmount: totalAmount + 5.99, // Including delivery fee
      };
      
      // Call API to create order
      const response = await cartService.createOrder(orderData);
      
      // Success - clear cart and redirect
      clearCart();
      navigate(`/orders/${response.orderId}`, { 
        state: { success: true, message: 'Order placed successfully!' } 
      });
    } catch (error) {
      console.error('Error placing order:', error);
      // Handle errors - show error message
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Checkout</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-xl font-semibold mb-4">Delivery Information</h2>
              
              <Formik
                initialValues={{
                  address: user?.address || '',
                  city: user?.city || '',
                  zipCode: user?.zipCode || '',
                  phone: user?.phone || '',
                }}
                validationSchema={validationSchema}
                onSubmit={handleSubmit}
              >
                {({ isSubmitting }) => (
                  <Form className="space-y-4">
                    <Input
                      label="Delivery Address"
                      name="address"
                      placeholder="Enter your full address"
                    />
                    
                    <div className="grid grid-cols-2 gap-4">
                      <Input
                        label="City"
                        name="city"
                        placeholder="City"
                      />
                      <Input
                        label="ZIP Code"
                        name="zipCode"
                        placeholder="ZIP Code"
                      />
                    </div>
                    
                    <Input
                      label="Phone Number"
                      name="phone"
                      placeholder="Phone number for delivery updates"
                    />
                    
                    <div className="mt-6">
                      <h3 className="font-medium mb-3">Payment Method</h3>
                      <div className="space-y-2">
                        <label className="flex items-center p-3 border rounded cursor-pointer hover:bg-gray-50">
                          <input
                            type="radio"
                            name="paymentMethod"
                            value="card"
                            checked={paymentMethod === 'card'}
                            onChange={() => setPaymentMethod('card')}
                            className="mr-2"
                          />
                          <span>Credit/Debit Card</span>
                        </label>
                        
                        <label className="flex items-center p-3 border rounded cursor-pointer hover:bg-gray-50">
                          <input
                            type="radio"
                            name="paymentMethod"
                            value="cash"
                            checked={paymentMethod === 'cash'}
                            onChange={() => setPaymentMethod('cash')}
                            className="mr-2"
                          />
                          <span>Cash on Delivery</span>
                        </label>
                      </div>
                    </div>
                    
                    {paymentMethod === 'card' && (
                      <div className="border-t pt-4 mt-4">
                        <Input
                          label="Card Number"
                          name="cardNumber"
                          placeholder="1234 5678 9012 3456"
                        />
                        
                        <div className="grid grid-cols-2 gap-4 mt-4">
                          <Input
                            label="Expiry Date"
                            name="expiryDate"
                            placeholder="MM/YY"
                          />
                          <Input
                            label="CVV"
                            name="cvv"
                            placeholder="123"
                            type="password"
                          />
                        </div>
                      </div>
                    )}
                    
                    <div className="pt-4">
                      <Button 
                        type="submit" 
                        className="w-full"
                        disabled={isLoading || isSubmitting}
                      >
                        {isLoading ? 'Processing...' : 'Place Order'}
                      </Button>
                    </div>
                  </Form>
                )}
              </Formik>
            </div>
          </div>
          
          <div>
            <div className="bg-white rounded-lg shadow-md p-6 sticky top-24">
              <h2 className="text-xl font-semibold mb-4">Order Summary</h2>
              
              <div className="space-y-3 mb-6">
                {items.map((item) => (
                  <div key={item.id} className="flex justify-between items-center">
                    <div className="flex items-center">
                      <span className="bg-primary-100 text-primary-700 w-6 h-6 rounded-full flex items-center justify-center mr-2">
                        {item.quantity}
                      </span>
                      <span className="text-gray-800">{item.name}</span>
                    </div>
                    <span className="font-medium">{formatCurrency(item.price * item.quantity)}</span>
                  </div>
                ))}
              </div>
              
              <div className="border-t pt-4">
                <div className="flex justify-between mb-2">
                  <span className="text-gray-600">Subtotal ({totalItems} items)</span>
                  <span>{formatCurrency(totalAmount)}</span>
                </div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-600">Delivery Fee</span>
                  <span>{formatCurrency(5.99)}</span>
                </div>
                <div className="flex justify-between font-bold text-lg mt-4">
                  <span>Total</span>
                  <span>{formatCurrency(totalAmount + 5.99)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default CheckoutPage;
