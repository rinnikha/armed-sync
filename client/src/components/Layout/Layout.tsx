import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  ShoppingCart as ShoppingCartIcon,
  Inventory as InventoryIcon,
  Sync as SyncIcon,
  BarChart as BarChartIcon,
  AttachMoney as AttachMoneyIcon,
  Logout as LogoutIcon,
  Settings as SettingsIcon,
  SyncAlt as SyncAltIcon,
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import styles from './Layout.module.css';

const menuItems = [
  { path: '/', text: 'Dashboard', icon: <DashboardIcon className={styles.navIcon} /> },
  { path: '/products', text: 'Products', icon: <InventoryIcon className={styles.navIcon} /> },
  { path: '/orders', text: 'Orders', icon: <ShoppingCartIcon className={styles.navIcon} /> },
  { path: '/sync', text: 'Sync', icon: <SyncIcon className={styles.navIcon} /> },
  { path: '/reports', text: 'Reports', icon: <BarChartIcon className={styles.navIcon} /> },
  { path: '/price-lists', text: 'Price Lists', icon: <AttachMoneyIcon className={styles.navIcon} /> },
  { path: '/order-sync-config', text: 'Order Sync Config', icon: <SettingsIcon className={styles.navIcon} /> },
  { path: '/order-sync', text: 'Order Sync', icon: <SyncAltIcon className={styles.navIcon} /> },
];

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { logout } = useAuth();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    setMobileOpen(false);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const currentPage = menuItems.find(item => item.path === location.pathname)?.text || 'Dashboard';

  return (
    <div className={styles.layout}>
      <header className={styles.appBar}>
        <div className={styles.toolbar}>
          <button
            className={styles.menuButton}
            onClick={handleDrawerToggle}
            aria-label="menu"
          >
            <MenuIcon />
          </button>
          <img src="/logo.svg" alt="Logo" className={styles.logo} />
          <h1 className={styles.pageTitle}>{currentPage}</h1>
          <div className={styles.userInfo}>
            <span>Admin</span>
            <button
              className={styles.logoutButton}
              onClick={handleLogout}
              aria-label="logout"
            >
              <LogoutIcon />
            </button>
          </div>
        </div>
      </header>

      <nav className={`${styles.drawer} ${mobileOpen ? styles.drawerOpen : ''}`}>
        <div className={styles.drawerContent}>
          {menuItems.map((item) => (
            <div
              key={item.path}
              className={`${styles.navItem} ${location.pathname === item.path ? styles.active : ''}`}
              onClick={() => handleNavigation(item.path)}
            >
              {item.icon}
              {item.text}
            </div>
          ))}
        </div>
      </nav>

      <main className={styles.main}>
        {children}
      </main>
    </div>
  );
};

export default Layout; 