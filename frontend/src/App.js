import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import MainLayout from './layouts/MainLayout';

// Pages
import HomePage from './pages/HomePage';
import RestaurantsPage from './pages/RestaurantsPage';
import RestaurantDetailPage from './pages/RestaurantDetailPage';
import MenuPage from './pages/MenuPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import NotFoundPage from './pages/NotFoundPage';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Auth pages without main layout */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          {/* Pages with main layout */}
          <Route 
            path="/" 
            element={
              <MainLayout>
                <HomePage />
              </MainLayout>
            } 
          />
          <Route 
            path="/restaurants" 
            element={
              <MainLayout>
                <RestaurantsPage />
              </MainLayout>
            } 
          />
          <Route 
            path="/restaurants/:id" 
            element={
              <MainLayout>
                <RestaurantDetailPage />
              </MainLayout>
            } 
          />
          <Route 
            path="/menu" 
            element={
              <MainLayout>
                <MenuPage />
              </MainLayout>
            } 
          />
          
          {/* Not found page */}
          <Route 
            path="*" 
            element={
              <MainLayout>
                <NotFoundPage />
              </MainLayout>
            } 
          />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
