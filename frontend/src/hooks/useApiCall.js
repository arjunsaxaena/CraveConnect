import { useState, useCallback } from 'react';

/**
 * A custom hook for handling API calls with loading and error states
 * 
 * @param {Function} apiCallFn - The API function to call
 * @returns {Object} - An object containing the fetchData function, loading state, error state, and data
 */
const useApiCall = (apiCallFn) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async (...args) => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await apiCallFn(...args);
      setData(result);
      return result;
    } catch (err) {
      setError(err.message || 'An error occurred');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiCallFn]);

  return { fetchData, loading, error, data };
};

export default useApiCall;
