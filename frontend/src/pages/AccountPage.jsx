import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import Card from '../components/ui/Card';
import Input from '../components/ui/Input';
import Button from '../components/ui/Button';
import { formatPhoneNumber } from '../utils/formatters';

const AccountPage = () => {
  const { user, loading: authLoading } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [updateSuccess, setUpdateSuccess] = useState(false);
  const [updateError, setUpdateError] = useState(null);

  // Profile update form
  const profileForm = useFormik({
    initialValues: {
      name: user?.name || '',
      phone: user?.phone || '',
      email: user?.email || '',
    },
    enableReinitialize: true,
    validationSchema: Yup.object({
      name: Yup.string().required('Name is required'),
      phone: Yup.string().required('Phone number is required'),
      email: Yup.string().email('Invalid email address'),
    }),
    onSubmit: async (values) => {
      try {
        setUpdateError(null);
        setUpdateSuccess(false);
        
        // In a real app, this would call a service to update the profile
        console.log('Updating profile:', values);
        
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setUpdateSuccess(true);
      } catch (error) {
        console.error('Failed to update profile:', error);
        setUpdateError(error.message || 'Failed to update profile. Please try again.');
      }
    },
  });

  // Handle tab change
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setUpdateSuccess(false);
    setUpdateError(null);
  };

  if (authLoading) {
    return (
      <div className="flex justify-center py-10">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="pb-12">
      <div className="bg-gradient-to-r from-primary-600 to-primary-800 text-white py-12">
        <div className="container-custom">
          <h1 className="text-3xl md:text-4xl font-bold">My Account</h1>
          <p className="mt-2 text-lg opacity-90">Manage your profile and preferences</p>
        </div>
      </div>

      <div className="container-custom mt-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <Card className="sticky top-8">
              <div className="flex flex-col">
                <div className="flex items-center pb-6 mb-6 border-b border-gray-200">
                  <div className="w-16 h-16 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-xl font-semibold">
                    {user?.name?.charAt(0).toUpperCase() || 'U'}
                  </div>
                  <div className="ml-4">
                    <h2 className="text-xl font-semibold">{user?.name || 'User'}</h2>
                    <p className="text-gray-500">{formatPhoneNumber(user?.phone) || 'No phone number'}</p>
                  </div>
                </div>

                <nav className="flex flex-col space-y-1">
                  <button
                    className={`px-4 py-3 rounded-md text-left ${
                      activeTab === 'profile'
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                    onClick={() => handleTabChange('profile')}
                  >
                    <div className="flex items-center">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      Profile Information
                    </div>
                  </button>
                  
                  <button
                    className={`px-4 py-3 rounded-md text-left ${
                      activeTab === 'orders'
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                    onClick={() => handleTabChange('orders')}
                  >
                    <div className="flex items-center">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                      </svg>
                      Order History
                    </div>
                  </button>
                  
                  <button
                    className={`px-4 py-3 rounded-md text-left ${
                      activeTab === 'favorites'
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                    onClick={() => handleTabChange('favorites')}
                  >
                    <div className="flex items-center">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                      </svg>
                      Favorite Restaurants
                    </div>
                  </button>
                  
                  <button
                    className={`px-4 py-3 rounded-md text-left ${
                      activeTab === 'settings'
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                    onClick={() => handleTabChange('settings')}
                  >
                    <div className="flex items-center">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      Account Settings
                    </div>
                  </button>
                </nav>
              </div>
            </Card>
          </div>

          {/* Content */}
          <div className="lg:col-span-2">
            {activeTab === 'profile' && (
              <Card>
                <h2 className="text-2xl font-semibold mb-6">Profile Information</h2>
                
                {updateSuccess && (
                  <div className="mb-6 p-3 bg-green-100 text-green-700 rounded-md">
                    Profile updated successfully!
                  </div>
                )}
                
                {updateError && (
                  <div className="mb-6 p-3 bg-red-100 text-red-700 rounded-md">
                    {updateError}
                  </div>
                )}
                
                <form onSubmit={profileForm.handleSubmit}>
                  <Input
                    label="Full Name"
                    id="name"
                    name="name"
                    value={profileForm.values.name}
                    onChange={profileForm.handleChange}
                    onBlur={profileForm.handleBlur}
                    error={profileForm.touched.name && profileForm.errors.name}
                    touched={profileForm.touched.name}
                    required
                  />
                  
                  <Input
                    label="Phone Number"
                    id="phone"
                    name="phone"
                    value={profileForm.values.phone}
                    onChange={profileForm.handleChange}
                    onBlur={profileForm.handleBlur}
                    error={profileForm.touched.phone && profileForm.errors.phone}
                    touched={profileForm.touched.phone}
                    required
                  />
                  
                  <Input
                    label="Email Address"
                    id="email"
                    name="email"
                    type="email"
                    value={profileForm.values.email}
                    onChange={profileForm.handleChange}
                    onBlur={profileForm.handleBlur}
                    error={profileForm.touched.email && profileForm.errors.email}
                    touched={profileForm.touched.email}
                  />
                  
                  <div className="mt-6">
                    <Button 
                      type="submit" 
                      isLoading={profileForm.isSubmitting}
                      disabled={!profileForm.dirty || !profileForm.isValid}
                    >
                      Update Profile
                    </Button>
                  </div>
                </form>
              </Card>
            )}
            
            {activeTab === 'orders' && (
              <Card>
                <h2 className="text-2xl font-semibold mb-6">Order History</h2>
                
                <div className="text-center py-8 text-gray-500">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                  </svg>
                  <p className="text-lg font-medium mb-2">No orders yet</p>
                  <p>Your order history will appear here after you place orders.</p>
                  <div className="mt-6">
                    <Button as="a" href="/restaurants">Browse Restaurants</Button>
                  </div>
                </div>
              </Card>
            )}
            
            {activeTab === 'favorites' && (
              <Card>
                <h2 className="text-2xl font-semibold mb-6">Favorite Restaurants</h2>
                
                <div className="text-center py-8 text-gray-500">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto text-gray-300 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                  <p className="text-lg font-medium mb-2">No favorites yet</p>
                  <p>Save your favorite restaurants to access them quickly here.</p>
                  <div className="mt-6">
                    <Button as="a" href="/restaurants">Find Restaurants</Button>
                  </div>
                </div>
              </Card>
            )}
            
            {activeTab === 'settings' && (
              <Card>
                <h2 className="text-2xl font-semibold mb-6">Account Settings</h2>
                
                <div className="space-y-6">
                  <div className="flex items-center justify-between pb-4 border-b border-gray-200">
                    <div>
                      <h3 className="text-lg font-medium">Email Notifications</h3>
                      <p className="text-gray-500 text-sm mt-1">Receive updates about your orders and special offers</p>
                    </div>
                    <div className="flex items-center">
                      <label className="inline-flex items-center cursor-pointer">
                        <input type="checkbox" className="sr-only peer" defaultChecked />
                        <div className="relative w-11 h-6 bg-gray-200 rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                      </label>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between pb-4 border-b border-gray-200">
                    <div>
                      <h3 className="text-lg font-medium">Password</h3>
                      <p className="text-gray-500 text-sm mt-1">Update your password to keep your account secure</p>
                    </div>
                    <Button variant="outline" size="sm">Change Password</Button>
                  </div>
                  
                  <div className="flex items-center justify-between pb-4 border-b border-gray-200">
                    <div>
                      <h3 className="text-lg font-medium">Delete Account</h3>
                      <p className="text-gray-500 text-sm mt-1">Permanently remove your account and data</p>
                    </div>
                    <Button variant="outline" size="sm" className="text-red-600 border-red-600 hover:bg-red-50">Delete Account</Button>
                  </div>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AccountPage;
