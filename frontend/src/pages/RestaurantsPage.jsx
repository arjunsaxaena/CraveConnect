import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import RestaurantService from '../services/restaurantService';
import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';

const RestaurantsPage = () => {
  const [restaurants, setRestaurants] = useState([]);
  const [filteredRestaurants, setFilteredRestaurants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCuisine, setFilterCuisine] = useState('');

  // Cuisine types for filter
  const cuisineTypes = [
    'All',
    'Italian',
    'Chinese',
    'Mexican',
    'Indian',
    'Japanese',
    'Thai',
    'American',
    'Mediterranean',
    'FastFood',
  ];

  useEffect(() => {
    const fetchRestaurants = async () => {
      try {
        setLoading(true);
        const data = await RestaurantService.getAllRestaurants();
        setRestaurants(data);
        setFilteredRestaurants(data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching restaurants:', err);
        setError('Failed to load restaurants. Please try again later.');
        setLoading(false);
      }
    };

    fetchRestaurants();
  }, []);

  // Filter restaurants based on search term and cuisine filter
  useEffect(() => {
    if (!restaurants.length) return;

    let result = [...restaurants];

    // Filter by search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      result = result.filter(
        (restaurant) =>
          restaurant.name.toLowerCase().includes(term) ||
          (restaurant.description && restaurant.description.toLowerCase().includes(term)) ||
          (restaurant.cuisine_type &&
            restaurant.cuisine_type.some((cuisine) =>
              cuisine.toLowerCase().includes(term)
            ))
      );
    }

    // Filter by cuisine type
    if (filterCuisine && filterCuisine !== 'All') {
      result = result.filter(
        (restaurant) =>
          restaurant.cuisine_type &&
          restaurant.cuisine_type.includes(filterCuisine)
      );
    }

    setFilteredRestaurants(result);
  }, [searchTerm, filterCuisine, restaurants]);

  // Handle search input change
  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  // Handle cuisine filter change
  const handleCuisineChange = (cuisine) => {
    setFilterCuisine(cuisine === 'All' ? '' : cuisine);
  };

  return (
    <div>
      <section className="bg-gradient-to-r from-primary-600 to-primary-800 text-white py-12">
        <div className="container-custom">
          <h1 className="text-3xl md:text-4xl font-bold mb-4">Restaurants</h1>
          <p className="text-lg md:text-xl opacity-90">
            Discover restaurants that satisfy your cravings
          </p>
        </div>
      </section>

      <section className="py-8">
        <div className="container-custom">
          {/* Search and filters */}
          <div className="mb-8">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-grow">
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <svg
                      className="h-5 w-5 text-gray-400"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                      />
                    </svg>
                  </div>
                  <input
                    type="text"
                    placeholder="Search restaurants by name, cuisine..."
                    className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                    value={searchTerm}
                    onChange={handleSearchChange}
                  />
                </div>
              </div>
            </div>

            {/* Cuisine type filters */}
            <div className="mt-4 flex flex-wrap gap-2">
              {cuisineTypes.map((cuisine) => (
                <button
                  key={cuisine}
                  onClick={() => handleCuisineChange(cuisine)}
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    (cuisine === 'All' && !filterCuisine) ||
                    cuisine === filterCuisine
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {cuisine}
                </button>
              ))}
            </div>
          </div>

          {/* Results */}
          {loading ? (
            <div className="flex justify-center py-10">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
            </div>
          ) : error ? (
            <div className="text-center py-10">
              <p className="text-red-600">{error}</p>
            </div>
          ) : (
            <>
              {/* Results count */}
              <p className="text-gray-600 mb-6">
                {filteredRestaurants.length === 0
                  ? 'No restaurants found'
                  : filteredRestaurants.length === 1
                  ? '1 restaurant found'
                  : `${filteredRestaurants.length} restaurants found`}
              </p>

              {/* Restaurant grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredRestaurants.length > 0 ? (
                  filteredRestaurants.map((restaurant) => (
                    <Link
                      to={`/restaurants/${restaurant.id}`}
                      key={restaurant.id}
                      className="block"
                    >
                      <Card className="h-full hover:shadow-lg transition-shadow">
                        <div className="aspect-[3/2] overflow-hidden rounded-md mb-4">
                          <img
                            src={restaurant.image_url || 'https://placehold.co/600x400?text=Restaurant'}
                            alt={restaurant.name}
                            className="w-full h-full object-cover"
                          />
                        </div>
                        <h2 className="font-semibold text-xl mb-2">{restaurant.name}</h2>
                        
                        {/* Cuisine tags */}
                        <div className="mb-3 flex flex-wrap gap-2">
                          {restaurant.cuisine_type?.map((cuisine, idx) => (
                            <Badge
                              key={idx}
                              variant={idx % 3 === 0 ? 'primary' : idx % 3 === 1 ? 'secondary' : 'info'}
                              size="sm"
                            >
                              {cuisine}
                            </Badge>
                          ))}
                        </div>
                        
                        <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                          {restaurant.description || 'Experience amazing cuisine and atmosphere at this restaurant.'}
                        </p>
                        
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <svg
                              className="h-5 w-5 text-yellow-500"
                              xmlns="http://www.w3.org/2000/svg"
                              viewBox="0 0 20 20"
                              fill="currentColor"
                            >
                              <path
                                d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
                              />
                            </svg>
                            <span className="text-gray-700 ml-1">
                              {restaurant.rating || '4.5'}
                            </span>
                          </div>
                          <span className="text-gray-600 text-sm">
                            {restaurant.delivery_time || '30-45'} min
                          </span>
                        </div>
                      </Card>
                    </Link>
                  ))
                ) : (
                  <div className="col-span-3 text-center py-10">
                    <p className="text-gray-500">
                      No restaurants match your search criteria. Please try a different search.
                    </p>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </section>
    </div>
  );
};

export default RestaurantsPage;
