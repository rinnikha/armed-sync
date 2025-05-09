import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/Layout/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import Orders from './pages/Orders';
import Sync from './pages/Sync';
import Reports from './pages/Reports';
import PriceLists from './pages/PriceLists';
import OrderSyncConfigPage from './pages/OrderSyncConfig';
import OrderSync from './pages/OrderSync';

const queryClient = new QueryClient();

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/"
              element={
                <PrivateRoute>
                  <Layout>
                    <Dashboard />
                  </Layout>
                </PrivateRoute>
              }
            />
            <Route
              path="/products"
              element={
                <PrivateRoute>
                  <Layout>
                    <Products />
                  </Layout>
                </PrivateRoute>
              }
            />
            <Route
              path="/orders"
              element={
                <PrivateRoute>
                  <Layout>
                    <Orders />
                  </Layout>
                </PrivateRoute>
              }
            />
            <Route
              path="/sync"
              element={
                <PrivateRoute>
                  <Layout>
                    <Sync />
                  </Layout>
                </PrivateRoute>
              }
            />
            <Route
              path="/reports"
              element={
                <PrivateRoute>
                  <Layout>
                    <Reports />
                  </Layout>
                </PrivateRoute>
              }
            />
            <Route
              path="/price-lists"
              element={
                <PrivateRoute>
                  <Layout>
                    <PriceLists />
                  </Layout>
                </PrivateRoute>
              }
            />
            <Route
              path="/order-sync-config"
              element={
                <PrivateRoute>
                  <Layout>
                    <OrderSyncConfigPage />
                  </Layout>
                </PrivateRoute>
              }
            />
            <Route
              path="/order-sync"
              element={
                <PrivateRoute>
                  <Layout>
                    <OrderSync />
                  </Layout>
                </PrivateRoute>
              }
            />
          </Routes>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
};

export default App;
