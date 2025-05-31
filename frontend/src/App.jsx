import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { CartProvider } from './context/CartContext';
import MainLayout from './layouts/MainLayout';
import ProtectedRoute from './utils/ProtectedRoute';

// Pages
import HomePage from './pages/HomePage';
import RestaurantsPage from './pages/RestaurantsPage';
import RestaurantDetailPage from './pages/RestaurantDetailPage';
import MenuPage from './pages/MenuPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import NotFoundPage from './pages/NotFoundPage';
import AccountPage from './pages/AccountPage';
import CheckoutPage from './pages/CheckoutPage';
import OrderTrackingPage from './pages/OrderTrackingPage';
import OrderHistoryPage from './pages/OrderHistoryPage';
import SearchResultsPage from './pages/SearchResultsPage';

function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <Router>
          <Routes>
            {/* Auth pages without main layout */}
            <Route 
              path="/login" 
              element={
                <ProtectedRoute requireAuth={false}>
                  <LoginPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/register" 
              element={
                <ProtectedRoute requireAuth={false}>
                  <RegisterPage />
                </ProtectedRoute>
              } 
            />
            
            {/* Public pages with main layout */}
            <Route path="/" element={<MainLayout><HomePage /></MainLayout>} />
            <Route path="/restaurants" element={<MainLayout><RestaurantsPage /></MainLayout>} />
            <Route path="/restaurants/:id" element={<MainLayout><RestaurantDetailPage /></MainLayout>} />
            <Route path="/menu" element={<MainLayout><MenuPage /></MainLayout>} />
            <Route path="/search" element={<MainLayout><SearchResultsPage /></MainLayout>} />
            
            {/* Protected pages with main layout */}
            <Route 
              path="/account" 
              element={
                <ProtectedRoute>
                  <MainLayout><AccountPage /></MainLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/checkout" 
              element={
                <ProtectedRoute>
                  <MainLayout><CheckoutPage /></MainLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/orders" 
              element={
                <ProtectedRoute>
                  <MainLayout><OrderHistoryPage /></MainLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/orders/:orderId" 
              element={
                <ProtectedRoute>
                  <MainLayout><OrderTrackingPage /></MainLayout>
                </ProtectedRoute>
              } 
            />
            
            {/* Not found page */}
            <Route path="*" element={<MainLayout><NotFoundPage /></MainLayout>} />
          </Routes>
        </Router>
      </CartProvider>
    </AuthProvider>
  );
}

export default App;
