import React from 'react';

/**
 * Card component for displaying content in a boxed layout
 */
const Card = ({
  children,
  title,
  subtitle,
  className = '',
  bodyClassName = '',
  footer,
  ...props
}) => {
  return (
    <div className={`bg-white rounded-lg shadow-card overflow-hidden ${className}`} {...props}>
      {(title || subtitle) && (
        <div className="px-6 py-4 border-b border-gray-200">
          {title && <h3 className="text-xl font-semibold text-gray-800">{title}</h3>}
          {subtitle && <p className="mt-1 text-sm text-gray-600">{subtitle}</p>}
        </div>
      )}
      
      <div className={`p-6 ${bodyClassName}`}>
        {children}
      </div>
      
      {footer && (
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
          {footer}
        </div>
      )}
    </div>
  );
};

export default Card;
