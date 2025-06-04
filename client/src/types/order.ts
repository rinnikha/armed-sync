export enum OrderSyncStatus {
    SYNCED = 'synced',
    PENDING = 'pending',
    WAITING_FOR_CONFIRM = 'waiting_for_confirm',
    MODIFIED = 'modified',
    FAILED = 'failed'
}

export enum OrderModificationStatus {
    WAITING_FOR_APPROVE = 'waiting_for_approve',
    APPROVED = 'approved',
    RESYNCED = 'resynced'
}

export interface Order {
    id: number;
    ms1_order_id: string;
    config_id: number;
    sync_status: OrderSyncStatus;
    error?: string;
    ms1_status_id?: string;
    last_synced_at?: string;
    created_at: string;
    updated_at: string;
}

export interface OrderSyncConfig {
    id: number;
    name: string;
    ms1_cp_id: string;
    ms2_organization_id: string;
    ms2_group_id: string;
    ms2_store_id: string;
    is_active: boolean;
    start_sync_datetime: string;
}

export interface OrderSync {
    id: number;
    ms1_order_id: string;
    ms2_purchase_id: string | null;
    ms1_state_href: string;
    sync_status: OrderSyncStatus;
    order_amount: number;
    modification_status: OrderModificationStatus | null;
    info_msg: string | null;
    error_msg: string | null;
    moment: string;
    created: string;
    modified: string;
    config: {
        "name": string,
        "id": number
    };
}

export interface OrderSyncResponse {
    items: OrderSync[];
    total: number;
    skip: number;
    limit: number;
} 