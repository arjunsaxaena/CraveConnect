import { useState } from 'react';
import searchService from '../services/searchService';

const useSearch = (initialQuery = '', initialFilters = {}) => {
  const [query, setQuery] = useState(initialQuery);
  const [filters, setFilters] = useState(initialFilters);
  const [results, setResults] = useState({
    restaurants: [],
    menuItems: []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  
  // Search with current query and filters
  const search = async (newQuery = query, newFilters = filters) => {
    if (!newQuery) {
      setResults({ restaurants: [], menuItems: [] });
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const data = await searchService.search(newQuery, newFilters);
      setResults(data);
    } catch (err) {
      console.error('Search error:', err);
      setError('Failed to fetch search results. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Get suggestions as user types
  const getSuggestions = async (text) => {
    if (!text || text.length < 2) {
      setSuggestions([]);
      return;
    }
    
    try {
      const data = await searchService.getSearchSuggestions(text);
      setSuggestions(data);
    } catch (err) {
      console.error('Suggestions error:', err);
      setSuggestions([]);
    }
  };

  // Update filters
  const updateFilters = (newFilters) => {
    const updatedFilters = {
      ...filters,
      ...newFilters
    };
    setFilters(updatedFilters);
    search(query, updatedFilters);
  };

  // Reset search to initial state
  const resetSearch = () => {
    setQuery('');
    setFilters(initialFilters);
    setResults({ restaurants: [], menuItems: [] });
    setSuggestions([]);
  };

  // Search for restaurants specifically
  const searchRestaurants = async (restaurantQuery, restaurantFilters = {}) => {
    setLoading(true);
    setError(null);
    try {
      const data = await searchService.searchRestaurants(
        restaurantQuery || query,
        restaurantFilters || filters
      );
      return data;
    } catch (err) {
      console.error('Restaurant search error:', err);
      setError('Failed to fetch restaurants. Please try again.');
      return [];
    } finally {
      setLoading(false);
    }
  };

  // Search for menu items specifically
  const searchMenuItems = async (menuQuery, menuFilters = {}) => {
    setLoading(true);
    setError(null);
    try {
      const data = await searchService.searchMenuItems(
        menuQuery || query,
        menuFilters || filters
      );
      return data;
    } catch (err) {
      console.error('Menu search error:', err);
      setError('Failed to fetch menu items. Please try again.');
      return [];
    } finally {
      setLoading(false);
    }
  };
  
  return {
    query,
    setQuery,
    filters,
    results,
    loading,
    error,
    suggestions,
    search,
    getSuggestions,
    updateFilters,
    resetSearch,
    searchRestaurants,
    searchMenuItems
  };
};

export default useSearch;
