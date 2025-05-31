import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import RestaurantService from '../services/restaurantService';
import MenuService from '../services/menuService';
import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import Button from '../components/ui/Button';
import AddToCartButton from '../components/ui/AddToCartButton';
import { formatCurrency } from '../utils/formatters';

const RestaurantDetailPage = () => {
  const { id } = useParams();
  const [restaurant, setRestaurant] = useState(null);
  const [menuItems, setMenuItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);  const [activeCategory, setActiveCategory] = useState('all');

  // Fetch restaurant and menu data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch restaurant details
        const restaurantData = await RestaurantService.getRestaurantById(id);
        setRestaurant(restaurantData);
        
        // Fetch menu items for this restaurant
        const menuData = await MenuService.getMenuItemsByRestaurantId(id);
        setMenuItems(menuData);
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching restaurant data:', err);
        setError('Failed to load restaurant details. Please try again later.');
        setLoading(false);
      }
    };

    if (id) {
      fetchData();
    }
  }, [id]);
  // Extract unique categories from menu items
  const categories = menuItems.length > 0
    ? ['all', ...new Set(menuItems.map(item => item.category || 'Other'))]
    : ['all'];

  // Filter menu items by category
  const filteredMenuItems = activeCategory === 'all'
    ? menuItems
    : menuItems.filter(item => item.category === activeCategory);
  // Format operating hours for display
  const formatOperatingHours = (hours) => {
    if (!hours) return 'Hours not available';
    
    try {
      // Convert string to object if needed
      if (typeof hours === 'string') {
        hours = JSON.parse(hours);
      }
      
      // If hours is not an object after parsing, return default message
      if (typeof hours !== 'object' || hours === null) {
        return 'Hours not available';
      }
      
      const days = Object.keys(hours);
      if (!days.length) return 'Hours not available';
      
      // Format each day's hours
      return days.map(day => {
        const dayHours = hours[day];
        if (typeof dayHours === 'object' && dayHours !== null && 'open' in dayHours && 'close' in dayHours) {
          return `${day}: ${dayHours.open} - ${dayHours.close}`;
        } else if (typeof dayHours === 'string') {
          return `${day}: ${dayHours}`;
        }
        return `${day}: Closed`;
      }).join(', ');
    } catch (error) {
      console.error('Error formatting operating hours:', error);
      return 'Hours not available';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container-custom py-10">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <Link to="/restaurants">
            <Button variant="outline">Back to Restaurants</Button>
          </Link>
        </div>
      </div>
    );
  }

  if (!restaurant) {
    return (
      <div className="container-custom py-10">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Restaurant not found</p>
          <Link to="/restaurants">
            <Button variant="outline">Back to Restaurants</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Hero section with restaurant details */}
      <section 
        className="bg-cover bg-center py-16 text-white relative"
        style={{
          backgroundImage: `url(${restaurant.image_url || 'https://placehold.co/1200x400?text=Restaurant'})`,
        }}
      >
        <div className="absolute inset-0 bg-black bg-opacity-50"></div>
        <div className="container-custom relative z-10">
          <div className="max-w-3xl">
            <h1 className="text-4xl font-bold mb-2">{restaurant.name}</h1>
            
            {/* Cuisine badges */}
            <div className="mb-4 flex flex-wrap gap-2">
              {restaurant.cuisine_type?.map((cuisine, idx) => (
                <Badge 
                  key={idx}
                  variant="primary"
                  className="bg-white bg-opacity-20"
                >
                  {cuisine}
                </Badge>
              ))}
            </div>
            
            <p className="text-lg mb-6">{restaurant.description}</p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Rating */}
              <div className="flex items-center">
                <svg className="h-5 w-5 text-yellow-400 mr-1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                <span>{restaurant.rating || '4.5'} Rating</span>
              </div>
                {/* Operating hours */}
              <div className="flex items-center">
                <svg className="h-5 w-5 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>
                  {restaurant.operating_hours ? 
                    formatOperatingHours(restaurant.operating_hours) : 
                    'Opening hours not available'}
                </span>
              </div>
              
              {/* Contact */}
              <div className="flex items-center">
                <svg className="h-5 w-5 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                <span>{restaurant.phone || 'Contact unavailable'}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Menu section */}
      <section className="py-12">
        <div className="container-custom">
          <h2 className="text-3xl font-bold mb-6">Menu</h2>
          
          {/* Category filters */}
          <div className="mb-8 overflow-x-auto">
            <div className="flex space-x-2 pb-2">
              {categories.map((category) => (
                <button
                  key={category}
                  className={`px-4 py-2 rounded-md text-sm font-medium whitespace-nowrap ${
                    activeCategory === category
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                  onClick={() => setActiveCategory(category)}
                >
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </button>
              ))}
            </div>
          </div>
          
          {/* Menu items grid */}
          {filteredMenuItems.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredMenuItems.map((menuItem) => (
                <Card key={menuItem.id} className="h-full hover:shadow-lg transition-shadow">
                  <div className="flex h-full flex-col">
                    {menuItem.image_url && (
                      <div className="aspect-[4/3] overflow-hidden rounded-md mb-4">
                        <img
                          src={menuItem.image_url}
                          alt={menuItem.name}
                          className="w-full h-full object-cover"
                        />
                      </div>
                    )}
                    <h3 className="text-xl font-semibold mb-2">{menuItem.name}</h3>                    <p className="text-gray-600 mb-4 flex-grow">
                      {menuItem.description}
                    </p>
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-lg">{formatCurrency(menuItem.price)}</span>
                      <AddToCartButton 
                        menuItem={{
                          ...menuItem,
                          restaurantId: restaurant.id,
                          restaurantName: restaurant.name
                        }} 
                      />
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500">No menu items available in this category.</p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default RestaurantDetailPage;
