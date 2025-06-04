import { OrderSync, OrderSyncStatus, OrderModificationStatus, OrderSyncResponse } from '../types/order';
import api from './axios';

export const orderSyncApi = {
    getOrders: async (
        skip: number = 0,
        limit: number = 10,
        syncStatus?: OrderSyncStatus,
        modificationStatus?: OrderModificationStatus,
        configId?: number,
        createdAfter?: string,
        createdBefore?: string,
        search?: string
    ): Promise<OrderSyncResponse> => {
        const params = new URLSearchParams();
        params.append('skip', skip.toString());
        params.append('limit', limit.toString());
        if (syncStatus) params.append('sync_status', syncStatus);
        if (modificationStatus) params.append('modification_status', modificationStatus);
        if (configId) params.append('config_id', configId.toString());
        if (createdAfter) params.append('created_after', createdAfter);
        if (createdBefore) params.append('created_before', createdBefore);
        if (search) params.append('search', search);

        const response = await api.get(`/order-sync/orders?${params.toString()}`);
        return response.data;
    },

    getOrder: async (orderId: number): Promise<OrderSync> => {
        const response = await api.get(`/order-sync/orders/${orderId}`);
        return response.data;
    },

    resyncOrder: async (orderId: number): Promise<{ message: string; order: OrderSync }> => {
        const response = await api.post(`/order-sync/orders/${orderId}/resync`);
        return response.data;
    },

    updateStatuses: async (): Promise<{ message: string }> => {
        const response = await api.post('/order-sync/update-statuses');
        return response.data;
    },

    syncPending: async (): Promise<{ message: string }> => {
        const response = await api.post('/order-sync/sync-pending');
        return response.data;
    },

    syncAll: async (): Promise<{ message: string }> => {
        const response = await api.post('/order-sync/sync-all');
        return response.data;
    },
}; 