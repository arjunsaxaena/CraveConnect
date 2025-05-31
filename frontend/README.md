# CraveConnect Frontend

This is the frontend application for the CraveConnect food delivery platform, built with React.

## Features

- User authentication (login, register, profile management)
- Restaurant and menu browsing
- Search functionality
- Shopping cart and order management
- Responsive design for all devices

## Technologies Used

- React (Create React App)
- React Router DOM for navigation
- Tailwind CSS for styling
- Axios for API communication
- Formik and Yup for form handling and validation
- Context API for state management

## Getting Started

### Prerequisites

- Node.js (v14.x or higher)
- npm (v6.x or higher)

### Installation

1. Clone the repository
2. Navigate to the frontend directory:
   ```
   cd CraveConnect/frontend
   ```
3. Install dependencies:
   ```
   npm install
   ```

### Running the Application

To start the development server:
```
npm start
```

This will start the application on [http://localhost:3000](http://localhost:3000).

### Building for Production

To create a production build:
```
npm run build
```

The build files will be available in the `build` directory.

## Project Structure

- `src/assets`: Static assets, images, etc.
- `src/components`: Reusable UI components
  - `ui`: Basic UI elements (Button, Input, Card, etc.)
  - `layout`: Layout components (Navigation, Footer, etc.)
- `src/context`: Context providers for state management
- `src/hooks`: Custom React hooks
- `src/layouts`: Page layout templates
- `src/pages`: Main application pages
- `src/services`: API service modules
- `src/utils`: Utility functions and helpers

## Testing

To run the tests:
```
npm test
```

## Authors

- Dhruv Sharma - Initial development

## License

This project is licensed under the MIT License - see the LICENSE file for details.
