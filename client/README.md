# Moysklad Integration Client

A React-based client application for managing Moysklad integration, including product mappings, orders, price lists, and reports.

## Features

- User authentication and authorization
- Product mapping management
- Order tracking and management
- Price list management
- Report generation and scheduling
- Real-time sync status monitoring
- Responsive Material-UI design

## Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)

## Installation

1. Clone the repository
2. Navigate to the client directory:
   ```bash
   cd client
   ```
3. Install dependencies:
   ```bash
   npm install
   ```

## Development

To start the development server:

```bash
npm start
```

The application will be available at `http://localhost:3000`.

## Building for Production

To create a production build:

```bash
npm run build
```

The build artifacts will be stored in the `build/` directory.

## Project Structure

```
src/
  ├── components/     # Reusable UI components
  ├── contexts/       # React contexts (auth, etc.)
  ├── pages/         # Page components
  ├── api/           # API integration
  ├── theme.ts       # Material-UI theme configuration
  └── App.tsx        # Main application component
```

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm test` - Launches the test runner
- `npm run build` - Builds the app for production
- `npm run eject` - Ejects from Create React App

## Dependencies

- React
- React Router
- Material-UI
- React Query
- Axios

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
