export type OrderSyncStatus = 'PENDING' | 'SYNCED' | 'WAITING_FOR_CONFIRM' | 'MODIFIED' | 'FAILED';

export interface Order {
    id: number;
    ms1_order_id: string;
    config_id: number;
    sync_status: OrderSyncStatus;
    error?: string;
    ms1_status?: string;
    ms2_status?: string;
    last_synced_at?: string;
    created_at: string;
    updated_at: string;
}

export interface OrderSyncConfig {
    id: number;
    name: string;
    ms1_cp_meta: string;
    ms2_organization: string;
    ms2_group_meta: string;
    ms2_store_meta: string;
    is_active: boolean;
    start_sync_datetime: string;
} 