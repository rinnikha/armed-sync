import React from 'react';
import {
  Inventory as InventoryIcon,
  ShoppingCart as ShoppingCartIcon,
  Sync as SyncIcon,
  BarChart as BarChartIcon,
} from '@mui/icons-material';
import styles from './Dashboard.module.css';

const Dashboard: React.FC = () => {
  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Dashboard</h1>
      
      <div className={styles.grid}>
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <InventoryIcon className={styles.icon} />
            <span className={styles.cardTitle}>Total Products</span>
          </div>
          <div className={styles.cardValue}>0</div>
        </div>

        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <ShoppingCartIcon className={styles.icon} />
            <span className={styles.cardTitle}>Pending Orders</span>
          </div>
          <div className={styles.cardValue}>0</div>
        </div>

        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <SyncIcon className={styles.icon} />
            <span className={styles.cardTitle}>Last Sync</span>
          </div>
          <div className={styles.cardValue}>-</div>
        </div>

        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <BarChartIcon className={styles.icon} />
            <span className={styles.cardTitle}>Reports</span>
          </div>
          <div className={styles.cardValue}>0</div>
        </div>
      </div>

      <div className={styles.twoColumnGrid}>
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>Recent Activity</h2>
          <p className={styles.emptyText}>No recent activity</p>
        </div>

        <div className={styles.card}>
          <h2 className={styles.cardTitle}>System Status</h2>
          <p className={styles.emptyText}>All systems operational</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 