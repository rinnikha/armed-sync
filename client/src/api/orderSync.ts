import { Order, OrderSyncStatus } from '../types/order';
import api from './axios';

const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return {
        headers: {
            Authorization: `Bearer ${token}`
        }
    };
};

export const orderSyncApi = {
    getOrders: async (): Promise<Order[]> => {
        const response = await api.get('/api/order-sync/orders', getAuthHeaders());
        console.log(response);
        return response.data;
    },

    syncOrder: async (orderId: string): Promise<{ message: string }> => {
        const response = await api.post(`/api/order-sync/orders/${orderId}/sync`, {}, getAuthHeaders());
        return response.data;
    },

    updateOrderStatus: async (orderId: string, status: OrderSyncStatus): Promise<{ message: string }> => {
        const response = await api.post(
            `/api/order-sync/orders/${orderId}/status`, 
            { status }, 
            getAuthHeaders()
        );
        return response.data;
    },

    syncAllPending: async (): Promise<{ message: string }> => {
        const response = await api.post('/api/order-sync/orders/sync-all-pending', {}, getAuthHeaders());
        return response.data;
    },

    checkStatuses: async (): Promise<{ message: string }> => {
        const response = await api.post('/api/order-sync/orders/check-statuses', {}, getAuthHeaders());
        return response.data;
    },
}; 