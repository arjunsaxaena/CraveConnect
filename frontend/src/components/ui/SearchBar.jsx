import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

const SearchBar = ({ placeholder = "Search restaurants and dishes...", className = "", showButton = true }) => {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  return (
    <form onSubmit={handleSubmit} className={`flex items-center ${className}`}>
      <div className="relative flex-grow">
        <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
          <MagnifyingGlassIcon className="w-5 h-5 text-gray-400" />
        </div>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="block w-full p-3 pl-10 text-gray-700 bg-white border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
          placeholder={placeholder}
          required
        />
      </div>
      {showButton && (
        <button
          type="submit"
          className="p-3 ml-2 text-white bg-primary-600 rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <MagnifyingGlassIcon className="w-5 h-5" />
          <span className="sr-only">Search</span>
        </button>
      )}
    </form>
  );
};

export default SearchBar;
