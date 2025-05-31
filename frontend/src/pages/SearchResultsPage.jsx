import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import SearchBar from '../components/ui/SearchBar';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import useSearch from '../hooks/useSearch';
import { formatCurrency } from '../utils/formatters';

const SearchResultsPage = () => {
  const [searchParams] = useSearchParams();
  const searchQuery = searchParams.get('q') || '';
  const [activeTab, setActiveTab] = useState('all');
  // Initialize search hook with query from URL
  const {
    setQuery,
    filters,
    updateFilters,
    results,
    loading,
    error,
    search
  } = useSearch();
    // Fetch search results when query or filters change
  useEffect(() => {
    if (searchQuery) {
      setQuery(searchQuery);
      search(searchQuery, filters);
    }
  }, [searchQuery, setQuery, search, filters]);
    // Handle filter changes
  const handleFilterChange = (key, value) => {
    updateFilters({ [key]: value });
  };
  
  // Handle dietary preference toggle
  const handleDietaryToggle = (preference) => {
    const current = [...filters.dietaryPreferences];
    const updatedPreferences = current.includes(preference)
      ? current.filter(p => p !== preference)
      : [...current, preference];
    
    updateFilters({ 
      dietaryPreferences: updatedPreferences 
    });
  };
  
  // Filter content based on active tab
  const filteredResults = activeTab === 'all' 
    ? results 
    : activeTab === 'restaurants' 
      ? { restaurants: results.restaurants, menuItems: [] }
      : { restaurants: [], menuItems: results.menuItems };
  
  // Total count
  const totalCount = (filteredResults.restaurants?.length || 0) + 
                     (filteredResults.menuItems?.length || 0);

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <SearchBar className="max-w-3xl mx-auto" />
        </div>
        
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 rounded-lg p-4 mb-6">
            <p>{error}</p>
          </div>
        )}
        
        {!loading && searchQuery && (
          <div className="mb-6">
            <h1 className="text-2xl font-bold">
              Search results for "{searchQuery}"
              <span className="text-gray-500 text-lg font-normal ml-2">
                ({totalCount} {totalCount === 1 ? 'result' : 'results'})
              </span>
            </h1>
          </div>
        )}
        
        <div className="flex flex-col md:flex-row gap-8">
          {/* Filters sidebar */}
          <div className="md:w-64 shrink-0">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-lg font-semibold mb-4">Filters</h2>
              
              {/* Tab navigation */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-500 mb-2">Show</h3>
                <div className="flex flex-wrap gap-2">
                  {['all', 'restaurants', 'dishes'].map((tab) => (
                    <button
                      key={tab}
                      className={`px-3 py-1 rounded-full text-sm ${
                        activeTab === tab 
                          ? 'bg-primary-100 text-primary-700' 
                          : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                      }`}
                      onClick={() => setActiveTab(tab)}
                    >
                      {tab.charAt(0).toUpperCase() + tab.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Cuisine filter */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-500 mb-2">Cuisine</h3>
                <select
                  className="w-full p-2 border border-gray-300 rounded bg-white focus:ring-primary-500 focus:border-primary-500"
                  value={filters.cuisine}
                  onChange={(e) => handleFilterChange('cuisine', e.target.value)}
                >
                  <option value="">All Cuisines</option>
                  <option value="italian">Italian</option>
                  <option value="chinese">Chinese</option>
                  <option value="mexican">Mexican</option>
                  <option value="indian">Indian</option>
                  <option value="japanese">Japanese</option>
                  <option value="american">American</option>
                  <option value="thai">Thai</option>
                </select>
              </div>
              
              {/* Price range filter */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-500 mb-2">Price Range</h3>
                <div className="flex flex-wrap gap-2">
                  {['$', '$$', '$$$', '$$$$'].map((price) => (
                    <button
                      key={price}
                      className={`px-3 py-1 rounded-full text-sm ${
                        filters.priceRange === price 
                          ? 'bg-primary-100 text-primary-700' 
                          : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                      }`}
                      onClick={() => handleFilterChange('priceRange', 
                        filters.priceRange === price ? '' : price
                      )}
                    >
                      {price}
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Dietary preferences */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-500 mb-2">Dietary Preferences</h3>
                <div className="space-y-2">
                  {['vegetarian', 'vegan', 'gluten-free', 'halal', 'kosher'].map((pref) => (
                    <label key={pref} className="flex items-center">
                      <input
                        type="checkbox"
                        className="rounded text-primary-600 focus:ring-primary-500"
                        checked={filters.dietaryPreferences.includes(pref)}
                        onChange={() => handleDietaryToggle(pref)}
                      />
                      <span className="ml-2 text-gray-700 capitalize">{pref}</span>
                    </label>
                  ))}
                </div>
              </div>
              
              {/* Sort by */}
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-500 mb-2">Sort By</h3>
                <select
                  className="w-full p-2 border border-gray-300 rounded bg-white focus:ring-primary-500 focus:border-primary-500"
                  value={filters.sortBy}
                  onChange={(e) => handleFilterChange('sortBy', e.target.value)}
                >
                  <option value="rating">Highest Rating</option>
                  <option value="popularity">Popularity</option>
                  <option value="price_low">Price: Low to High</option>
                  <option value="price_high">Price: High to Low</option>
                </select>
              </div>
              
              {/* Reset filters */}              <Button
                variant="outline"
                className="w-full"
                onClick={() => {
                  updateFilters({
                    cuisine: '',
                    priceRange: '',
                    sortBy: 'rating',
                    dietaryPreferences: []
                  });
                }}
              >
                Reset Filters
              </Button>
            </div>
          </div>
          
          {/* Search results */}
          <div className="flex-1">
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[...Array(6)].map((_, index) => (
                  <div key={index} className="animate-pulse bg-white rounded-lg shadow-md p-4">
                    <div className="h-40 bg-gray-200 rounded mb-4"></div>
                    <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                  </div>
                ))}
              </div>
            ) : totalCount === 0 ? (
              <div className="text-center py-12 bg-white rounded-lg shadow-md">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
                <h3 className="mt-2 text-lg font-medium text-gray-900">No results found</h3>
                <p className="mt-1 text-gray-500">
                  Try adjusting your search or filter to find what you're looking for.
                </p>
              </div>
            ) : (
              <div>
                {/* Restaurant results */}
                {filteredResults.restaurants?.length > 0 && (
                  <div className="mb-10">
                    <h2 className="text-xl font-semibold mb-4">Restaurants</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {filteredResults.restaurants.map((restaurant) => (
                        <Card key={restaurant.id} className="h-full">
                          <Link to={`/restaurants/${restaurant.id}`}>
                            <img
                              src={restaurant.image || 'https://via.placeholder.com/300x200'}
                              alt={restaurant.name}
                              className="w-full h-40 object-cover rounded-t-lg"
                            />
                            <div className="p-4">
                              <h3 className="font-semibold text-lg mb-1">{restaurant.name}</h3>
                              <div className="flex items-center mb-2">
                                <span className="text-yellow-500 mr-1">★</span>
                                <span>{restaurant.rating.toFixed(1)}</span>
                                <span className="mx-2">•</span>
                                <span className="text-gray-600">{restaurant.cuisine}</span>
                                <span className="mx-2">•</span>
                                <span className="text-gray-600">{restaurant.priceRange}</span>
                              </div>
                              <p className="text-gray-500 text-sm">{restaurant.address}</p>
                            </div>
                          </Link>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Menu item results */}
                {filteredResults.menuItems?.length > 0 && (
                  <div>
                    <h2 className="text-xl font-semibold mb-4">Dishes</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {filteredResults.menuItems.map((item) => (
                        <Card key={item.id} className="h-full">
                          <Link to={`/restaurants/${item.restaurantId}`}>
                            <img
                              src={item.image || 'https://via.placeholder.com/300x200'}
                              alt={item.name}
                              className="w-full h-40 object-cover rounded-t-lg"
                            />
                            <div className="p-4">
                              <h3 className="font-semibold text-lg mb-1">{item.name}</h3>
                              <p className="text-gray-500 text-sm mb-2">{item.restaurantName}</p>
                              <p className="text-primary-600 font-semibold">
                                {formatCurrency(item.price)}
                              </p>
                            </div>
                          </Link>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default SearchResultsPage;
