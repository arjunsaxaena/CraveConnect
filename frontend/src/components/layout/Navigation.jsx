import React, { useState, useContext } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { CartContext } from '../../context/CartContext';
import SearchBar from '../ui/SearchBar';
import Cart from '../ui/Cart';

// Icons
import { 
  HomeIcon, 
  UserIcon,
  BuildingStorefrontIcon as RestaurantMenuIcon, 
  RectangleStackIcon, 
  Bars3Icon, 
  XMarkIcon,
  ShoppingCartIcon,
  MagnifyingGlassIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

const Navigation = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [showSearch, setShowSearch] = useState(false);
  // Get authentication state and user profile (we'll use isAuthenticated and logout)
  const { isAuthenticated, logout } = useAuth();
  
  // Access CartContext directly with fallback
  const cartContext = useContext(CartContext);
  const totalItems = cartContext?.totalItems || 0;
  
  const location = useLocation();

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const closeMenu = () => {
    setIsMenuOpen(false);
  };

  // Navigation links
  const navLinks = [
    { name: 'Home', to: '/', icon: HomeIcon },
    { name: 'Restaurants', to: '/restaurants', icon: RestaurantMenuIcon },
    { name: 'Menu', to: '/menu', icon: RectangleStackIcon },
  ];

  // Auth links
  const authLinks = isAuthenticated
    ? [
        { name: 'My Orders', to: '/orders', icon: ClockIcon },
        { name: 'My Account', to: '/account', icon: UserIcon },
        { name: 'Logout', onClick: logout, icon: null },
      ]
    : [
        { name: 'Login', to: '/login', icon: null },
        { name: 'Register', to: '/register', icon: null },
      ];

  const isActive = (path) => {
    return location.pathname === path;
  };
  return (
    <nav className="bg-white shadow-sm">
      <div className="container mx-auto px-4">
        {/* Desktop Navigation */}
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link to="/" className="text-2xl font-bold text-primary-600">
                CraveConnect
              </Link>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-4">
              {navLinks.map((link) => (
                <Link
                  key={link.name}
                  to={link.to}
                  className={`inline-flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                    isActive(link.to)
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  {link.icon && (
                    <link.icon className="mr-1.5 h-5 w-5" aria-hidden="true" />
                  )}
                  {link.name}
                </Link>
              ))}
            </div>
          </div>
          
          <div className="hidden sm:flex sm:items-center sm:space-x-4">
            {/* Search Button */}
            <button 
              onClick={() => setShowSearch(!showSearch)}
              className="p-2 rounded-full text-gray-500 hover:text-gray-700 hover:bg-gray-100"
            >
              <MagnifyingGlassIcon className="h-6 w-6" />
            </button>
            
            {/* Shopping Cart */}
            <button 
              onClick={() => setIsCartOpen(!isCartOpen)}
              className="p-2 rounded-full text-gray-500 hover:text-gray-700 hover:bg-gray-100 relative"
            >
              <ShoppingCartIcon className="h-6 w-6" />
              {totalItems > 0 && (
                <span className="absolute -top-1 -right-1 bg-primary-600 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
                  {totalItems}
                </span>
              )}
            </button>
            
            {/* Auth Links */}
            {authLinks.map((link) =>
              link.to ? (
                <Link
                  key={link.name}
                  to={link.to}
                  className={`px-3 py-2 text-sm font-medium rounded-md ${
                    isActive(link.to)
                      ? 'bg-primary-50 text-primary-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  {link.icon && (
                    <link.icon className="mr-1.5 inline h-5 w-5" aria-hidden="true" />
                  )}
                  {link.name}
                </Link>
              ) : (
                <button
                  key={link.name}
                  onClick={link.onClick}
                  className="px-3 py-2 text-sm font-medium rounded-md text-gray-700 hover:bg-gray-100"
                >
                  {link.name}
                </button>
              )
            )}
          </div>          {/* Mobile menu button */}
          <div className="flex items-center sm:hidden">
            <button
              type="button"
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-700 hover:text-gray-900 hover:bg-gray-100"
              aria-controls="mobile-menu"
              aria-expanded="false"
              onClick={toggleMenu}
            >
              <span className="sr-only">Open main menu</span>
              {isMenuOpen ? (
                <XMarkIcon className="block h-6 w-6" aria-hidden="true" />
              ) : (
                <Bars3Icon className="block h-6 w-6" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div
          className={`sm:hidden ${isMenuOpen ? 'block' : 'hidden'}`}
          id="mobile-menu"
        >
          <div className="pt-2 pb-3 space-y-1">
            {navLinks.map((link) => (
              <Link
                key={link.name}
                to={link.to}
                className={`block px-3 py-2 text-base font-medium rounded-md ${
                  isActive(link.to)
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
                onClick={closeMenu}
              >
                <div className="flex items-center">
                  {link.icon && (
                    <link.icon className="mr-3 h-5 w-5" aria-hidden="true" />
                  )}
                  {link.name}
                </div>
              </Link>
            ))}
          </div>
          <div className="pt-4 pb-3 border-t border-gray-200">
            <div className="space-y-1">
              {authLinks.map((link) =>
                link.to ? (
                  <Link
                    key={link.name}
                    to={link.to}
                    className={`block px-3 py-2 text-base font-medium rounded-md ${
                      isActive(link.to)
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                    onClick={closeMenu}
                  >
                    {link.icon && (
                      <link.icon
                        className="mr-3 h-5 w-5"
                        aria-hidden="true"
                      />
                    )}
                    {link.name}
                  </Link>
                ) : (
                  <button
                    key={link.name}
                    onClick={() => {
                      link.onClick();
                      closeMenu();
                    }}
                    className="block w-full text-left px-3 py-2 text-base font-medium rounded-md text-gray-700 hover:bg-gray-100"
                  >
                    {link.name}
                  </button>
                )
              )}
            </div>
          </div>        </div>
      </div>
      
      {/* Search Overlay */}
      {showSearch && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-40 flex items-start pt-24 justify-center">
          <div className="bg-white p-6 rounded-lg shadow-xl w-full max-w-3xl">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Search</h2>
              <button 
                onClick={() => setShowSearch(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>
            <SearchBar 
              placeholder="Search restaurants, dishes, and cuisines..." 
              className="w-full"
              showButton={false}
            />
          </div>
        </div>
      )}
      
      {/* Shopping Cart Overlay */}
      <Cart isOpen={isCartOpen} onClose={() => setIsCartOpen(false)} />
    </nav>
  );
};

export default Navigation;
