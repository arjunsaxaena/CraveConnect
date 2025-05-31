import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import RestaurantService from '../services/restaurantService';
import MenuService from '../services/menuService';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';

const HomePage = () => {
  const [featuredRestaurants, setFeaturedRestaurants] = useState([]);
  const [popularItems, setPopularItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch featured restaurants
        const restaurantsData = await RestaurantService.getAllRestaurants();
        
        // For featured restaurants, we'll just use the first few
        setFeaturedRestaurants(restaurantsData.slice(0, 4));

        // Fetch menu items
        const menuData = await MenuService.getAllMenuItems();
        
        // For popular items, we'll just use a few items
        setPopularItems(menuData.slice(0, 6));
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load data. Please try again later.');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Hero section with search
  const HeroSection = () => (
    <section className="bg-gradient-to-r from-primary-600 to-primary-800 text-white py-16 md:py-24">
      <div className="container-custom">
        <div className="max-w-3xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Discover and Connect with Great Food
          </h1>
          <p className="text-xl md:text-2xl mb-8 opacity-90">
            Find the best restaurants and dishes in your area
          </p>
          <div className="bg-white rounded-lg shadow-lg p-2 flex">
            <input
              type="text"
              placeholder="Search for restaurants or dishes..."
              className="w-full px-4 py-3 text-gray-800 focus:outline-none"
            />
            <Button className="ml-2 whitespace-nowrap">
              Find Food
            </Button>
          </div>
        </div>
      </div>
    </section>
  );

  // Featured Restaurants section
  const FeaturedRestaurants = () => (
    <section className="py-12 md:py-16 bg-white">
      <div className="container-custom">
        <div className="mb-10">
          <h2 className="text-3xl font-bold mb-2">Featured Restaurants</h2>
          <p className="text-gray-600">Discover the best dining experiences in your area</p>
        </div>

        {loading ? (
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
          </div>
        ) : error ? (
          <div className="text-center text-red-600">{error}</div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {featuredRestaurants.length > 0 ? (
              featuredRestaurants.map((restaurant) => (
                <Link to={`/restaurants/${restaurant.id}`} key={restaurant.id}>
                  <Card className="h-full transition-transform hover:scale-105">
                    <div className="aspect-[4/3] overflow-hidden rounded-md mb-4">
                      <img
                        src={restaurant.image_url || 'https://placehold.co/400x300?text=Restaurant'}
                        alt={restaurant.name}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <h3 className="font-semibold text-lg mb-1">{restaurant.name}</h3>
                    <p className="text-gray-600 text-sm mb-2">{restaurant.cuisine_type?.join(', ') || 'Various Cuisines'}</p>
                    <div className="flex items-center">
                      <div className="flex text-yellow-500">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
                        </svg>
                        <span className="ml-1 text-gray-700">4.5</span>
                      </div>
                      <span className="mx-2 text-gray-300">•</span>
                      <span className="text-gray-600 text-sm">30-45 min</span>
                    </div>
                  </Card>
                </Link>
              ))
            ) : (
              <div className="col-span-4 text-center py-10">
                <p className="text-gray-500">No restaurants found. Check back later!</p>
              </div>
            )}
          </div>
        )}

        {featuredRestaurants.length > 0 && (
          <div className="text-center mt-10">
            <Link to="/restaurants">
              <Button variant="outline">View All Restaurants</Button>
            </Link>
          </div>
        )}
      </div>
    </section>
  );

  // Popular menu items section
  const PopularItems = () => (
    <section className="py-12 md:py-16 bg-gray-50">
      <div className="container-custom">
        <div className="mb-10">
          <h2 className="text-3xl font-bold mb-2">Popular Menu Items</h2>
          <p className="text-gray-600">Discover dishes that people are craving right now</p>
        </div>

        {loading ? (
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
          </div>
        ) : error ? (
          <div className="text-center text-red-600">{error}</div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {popularItems.length > 0 ? (
              popularItems.map((item) => (
                <Link to={`/menu/${item.id}`} key={item.id}>
                  <Card className="h-full transition-transform hover:scale-105">
                    <div className="aspect-[4/3] overflow-hidden rounded-md mb-4">
                      <img
                        src={item.image_url || 'https://placehold.co/400x300?text=Food'}
                        alt={item.name}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <h3 className="font-semibold text-lg mb-1">{item.name}</h3>
                    <p className="text-gray-600 text-sm mb-3 line-clamp-2">{item.description}</p>
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-primary-700">${item.price}</span>
                      <div className="flex text-yellow-500">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
                        </svg>
                        <span className="ml-1 text-gray-700">4.8</span>
                      </div>
                    </div>
                  </Card>
                </Link>
              ))
            ) : (
              <div className="col-span-3 text-center py-10">
                <p className="text-gray-500">No menu items found. Check back later!</p>
              </div>
            )}
          </div>
        )}

        {popularItems.length > 0 && (
          <div className="text-center mt-10">
            <Link to="/menu">
              <Button variant="outline">View All Menu Items</Button>
            </Link>
          </div>
        )}
      </div>
    </section>
  );

  // How it works section
  const HowItWorks = () => (
    <section className="py-12 md:py-16 bg-white">
      <div className="container-custom">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-2">How CraveConnect Works</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Getting your favorite food has never been easier. We connect you directly with the best restaurants.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Discover</h3>
            <p className="text-gray-600">
              Browse through our extensive list of restaurants and explore their menus to find what you're craving.
            </p>
          </div>

          <div className="text-center">
            <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Order</h3>
            <p className="text-gray-600">
              Select your favorite meals, customize them to your taste, and place your order in just a few clicks.
            </p>
          </div>

          <div className="text-center">
            <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold mb-2">Enjoy</h3>
            <p className="text-gray-600">
              Sit back and relax as your order is prepared and delivered right to your doorstep, ready to be enjoyed.
            </p>
          </div>
        </div>
      </div>
    </section>
  );

  // CTA section
  const CTA = () => (
    <section className="py-12 md:py-16 bg-primary-700 text-white">
      <div className="container-custom">
        <div className="text-center max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold mb-4">Ready to satisfy your cravings?</h2>
          <p className="text-xl opacity-90 mb-8">
            Join CraveConnect today and discover the best restaurants and dishes near you.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link to="/restaurants">
              <Button className="bg-white text-primary-700 hover:bg-gray-100 border border-white">
                Browse Restaurants
              </Button>
            </Link>
            <Link to="/register">
              <Button className="bg-transparent hover:bg-primary-600 border border-white">
                Sign Up Now
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </section>
  );

  return (
    <>
      <HeroSection />
      <FeaturedRestaurants />
      <HowItWorks />
      <PopularItems />
      <CTA />
    </>
  );
};

export default HomePage;
