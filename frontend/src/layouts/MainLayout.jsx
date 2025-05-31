import React from 'react';
import Navigation from '../components/layout/Navigation';
import Footer from '../components/layout/Footer';

/**
 * MainLayout component that wraps all pages and provides consistent structure
 */
const MainLayout = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col">
      <Navigation />
      <main className="flex-grow container-custom py-6 md:py-8">
        {children}
      </main>
      <Footer />
    </div>
  );
};

export default MainLayout;
