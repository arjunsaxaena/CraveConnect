import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * A component to protect routes that require authentication
 * Redirects to login page if the user is not authenticated
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components to render when authenticated
 * @param {string} props.redirectTo - Path to redirect to if not authenticated
 * @returns {React.ReactNode} - Child components or redirect
 */
const ProtectedRoute = ({ 
  children, 
  redirectTo = '/login',
  requireAuth = true 
}) => {
  const { isAuthenticated, loading } = useAuth();

  // Show loading state if auth is still being determined
  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  // If requireAuth is true and user is not authenticated, redirect to login
  if (requireAuth && !isAuthenticated) {
    return <Navigate to={redirectTo} replace />;
  }

  // If requireAuth is false and user is authenticated, redirect to home
  // This is for pages like login/register that should not be accessible when logged in
  if (!requireAuth && isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  // If authentication status matches requirements, render the children
  return children;
};

export default ProtectedRoute;
