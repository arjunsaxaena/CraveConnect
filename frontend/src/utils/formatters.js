/**
 * Format price to display as currency
 * 
 * @param {number} price - The price to format
 * @param {string} currency - The currency code (default: USD)
 * @returns {string} - Formatted price
 */
export const formatCurrency = (price, currency = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(price);
};

/**
 * Truncate text to a specific length and add ellipsis
 * 
 * @param {string} text - The text to truncate
 * @param {number} maxLength - Maximum length before truncating
 * @returns {string} - Truncated text with ellipsis if needed
 */
export const truncateText = (text, maxLength = 100) => {
  if (!text || text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
};

/**
 * Format date to a readable string
 * 
 * @param {string|Date} date - Date to format
 * @param {Object} options - Intl.DateTimeFormat options
 * @returns {string} - Formatted date
 */
export const formatDate = (date, options = { 
  year: 'numeric', 
  month: 'long', 
  day: 'numeric',
}) => {
  return new Intl.DateTimeFormat('en-US', options).format(new Date(date));
};

/**
 * Generate a placeholder image URL
 * 
 * @param {number} width - Image width
 * @param {number} height - Image height
 * @param {string} text - Text to display on the image
 * @returns {string} - Placeholder image URL
 */
export const getPlaceholderImage = (width = 400, height = 300, text = 'Image') => {
  return `https://placehold.co/${width}x${height}?text=${text}`;
};

/**
 * Parse JSON safely without throwing errors
 * 
 * @param {string} jsonString - JSON string to parse
 * @param {*} fallback - Fallback value if parsing fails
 * @returns {*} - Parsed object or fallback value
 */
export const safeJsonParse = (jsonString, fallback = {}) => {
  try {
    return JSON.parse(jsonString);
  } catch (error) {
    return fallback;
  }
};

/**
 * Deep clone an object
 * 
 * @param {*} obj - Object to clone
 * @returns {*} - Cloned object
 */
export const deepClone = (obj) => {
  return JSON.parse(JSON.stringify(obj));
};

/**
 * Format phone number to a readable format
 * 
 * @param {string} phoneNumber - Phone number to format
 * @returns {string} - Formatted phone number
 */
export const formatPhoneNumber = (phoneNumber) => {
  if (!phoneNumber) return '';
  
  // Remove all non-digit characters
  const cleaned = phoneNumber.replace(/\D/g, '');
  
  // Format the phone number
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  }
  
  return phoneNumber;
};

/**
 * Extract cuisine types from a restaurant object
 * 
 * @param {Object} restaurant - Restaurant object
 * @returns {Array} - Array of cuisine types or default array
 */
export const getCuisineTypes = (restaurant) => {
  if (!restaurant) return [];
  
  if (Array.isArray(restaurant.cuisine_type)) {
    return restaurant.cuisine_type;
  }
  
  if (typeof restaurant.cuisine_type === 'string') {
    return restaurant.cuisine_type.split(',').map(item => item.trim());
  }
  
  return [];
};

/**
 * Format operating hours object to a readable string
 * 
 * @param {Object} hours - Operating hours object
 * @returns {string} - Formatted hours
 */
export const formatOperatingHours = (hours) => {
  if (!hours) return 'Hours not available';
  
  try {
    if (typeof hours === 'string') {
      hours = JSON.parse(hours);
    }
    
    const days = Object.keys(hours);
    if (!days.length) return 'Hours not available';
    
    return days.map(day => `${day}: ${hours[day].open} - ${hours[day].close}`).join(', ');
  } catch (error) {
    return 'Hours not available';
  }
};
