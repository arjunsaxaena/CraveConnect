import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import MenuService from '../services/menuService';
import RestaurantService from '../services/restaurantService';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';

const MenuPage = () => {
  const [menuItems, setMenuItems] = useState([]);
  const [filteredItems, setFilteredItems] = useState([]);
  const [restaurants, setRestaurants] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [priceRange, setPriceRange] = useState([0, 1000]);
  const [sortOption, setSortOption] = useState('name-asc');

  // Fetch menu items and restaurants
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch all menu items
        const menuData = await MenuService.getAllMenuItems();
        setMenuItems(menuData);
        setFilteredItems(menuData);
        
        // Fetch all restaurants to get names
        const restaurantsData = await RestaurantService.getAllRestaurants();
        
        // Create a map of restaurant id to restaurant name
        const restaurantMap = {};
        restaurantsData.forEach(restaurant => {
          restaurantMap[restaurant.id] = restaurant.name;
        });
        
        setRestaurants(restaurantMap);
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching menu data:', err);
        setError('Failed to load menu items. Please try again later.');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Filter and sort menu items
  useEffect(() => {
    if (!menuItems.length) return;

    let result = [...menuItems];

    // Filter by search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      result = result.filter(
        (item) =>
          item.name.toLowerCase().includes(term) ||
          (item.description && item.description.toLowerCase().includes(term))
      );
    }

    // Filter by price range
    result = result.filter(
      (item) => item.price >= priceRange[0] && item.price <= priceRange[1]
    );

    // Sort items
    switch (sortOption) {
      case 'name-asc':
        result.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'name-desc':
        result.sort((a, b) => b.name.localeCompare(a.name));
        break;
      case 'price-asc':
        result.sort((a, b) => a.price - b.price);
        break;
      case 'price-desc':
        result.sort((a, b) => b.price - a.price);
        break;
      default:
        break;
    }

    setFilteredItems(result);
  }, [searchTerm, priceRange, sortOption, menuItems]);

  // Handle search input change
  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  // Handle price range change
  const handlePriceRangeChange = (e) => {
    const value = e.target.value.split(',').map(Number);
    setPriceRange(value);
  };

  // Handle sort option change
  const handleSortChange = (e) => {
    setSortOption(e.target.value);
  };

  return (
    <div>
      <section className="bg-gradient-to-r from-secondary-600 to-secondary-800 text-white py-12">
        <div className="container-custom">
          <h1 className="text-3xl md:text-4xl font-bold mb-4">Menu</h1>
          <p className="text-lg md:text-xl opacity-90">
            Browse our selection of delicious dishes
          </p>
        </div>
      </section>

      <section className="py-8">
        <div className="container-custom">
          {/* Search and filters */}
          <div className="mb-8">
            <div className="flex flex-col lg:flex-row gap-4">
              {/* Search bar */}
              <div className="flex-grow">
                <label htmlFor="search" className="sr-only">
                  Search
                </label>
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
                    id="search"
                    type="text"
                    placeholder="Search menu items..."
                    className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:ring-secondary-500 focus:border-secondary-500"
                    value={searchTerm}
                    onChange={handleSearchChange}
                  />
                </div>
              </div>

              {/* Price range filter */}
              <div className="w-full lg:w-64">
                <label
                  htmlFor="price-range"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Price Range: ${priceRange[0]} - ${priceRange[1]}
                </label>
                <input
                  id="price-range"
                  type="range"
                  min="0"
                  max="1000"
                  step="10"
                  value={priceRange}
                  onChange={handlePriceRangeChange}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
              </div>

              {/* Sort options */}
              <div className="w-full lg:w-48">
                <label
                  htmlFor="sort"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Sort By
                </label>
                <select
                  id="sort"
                  value={sortOption}
                  onChange={handleSortChange}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-secondary-500 focus:border-secondary-500"
                >
                  <option value="name-asc">Name (A-Z)</option>
                  <option value="name-desc">Name (Z-A)</option>
                  <option value="price-asc">Price (Low to High)</option>
                  <option value="price-desc">Price (High to Low)</option>
                </select>
              </div>
            </div>
          </div>

          {/* Results */}
          {loading ? (
            <div className="flex justify-center py-10">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-secondary-600"></div>
            </div>
          ) : error ? (
            <div className="text-center py-10">
              <p className="text-red-600">{error}</p>
            </div>
          ) : (
            <>
              {/* Results count */}
              <p className="text-gray-600 mb-6">
                {filteredItems.length === 0
                  ? 'No menu items found'
                  : filteredItems.length === 1
                  ? '1 menu item found'
                  : `${filteredItems.length} menu items found`}
              </p>

              {/* Menu items grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredItems.length > 0 ? (
                  filteredItems.map((item) => (
                    <Card key={item.id} className="h-full hover:shadow-lg transition-shadow">
                      <div className="flex h-full flex-col">
                        {item.image_url ? (
                          <div className="aspect-[4/3] overflow-hidden rounded-md mb-4">
                            <img
                              src={item.image_url}
                              alt={item.name}
                              className="w-full h-full object-cover"
                            />
                          </div>
                        ) : (
                          <div className="aspect-[4/3] bg-gray-200 rounded-md flex items-center justify-center mb-4">
                            <svg
                              className="h-12 w-12 text-gray-400"
                              xmlns="http://www.w3.org/2000/svg"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                              />
                            </svg>
                          </div>
                        )}
                        
                        <h3 className="text-xl font-semibold mb-2">{item.name}</h3>
                        
                        {item.restaurant_id && restaurants[item.restaurant_id] && (
                          <Link
                            to={`/restaurants/${item.restaurant_id}`}
                            className="text-sm text-secondary-600 hover:text-secondary-700 mb-2"
                          >
                            {restaurants[item.restaurant_id]}
                          </Link>
                        )}
                        
                        <p className="text-gray-600 mb-4 flex-grow line-clamp-3">
                          {item.description || 'No description available.'}
                        </p>
                        
                        <div className="flex items-center justify-between mt-auto">
                          <span className="font-bold text-lg">${item.price.toFixed(2)}</span>
                          <Button size="sm">Add to Order</Button>
                        </div>
                      </div>
                    </Card>
                  ))
                ) : (
                  <div className="col-span-3 text-center py-10">
                    <p className="text-gray-500">
                      No menu items match your search criteria. Please try a different search.
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

export default MenuPage;
