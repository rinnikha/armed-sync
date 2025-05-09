import React, { useEffect, useState } from 'react';
import { Order, OrderSyncStatus } from '../types/order';
import { orderSyncApi } from '../api/orderSync';
import {
    Box,
    Container,
    Grid as MuiGrid,
    Paper,
    Typography,
    Button,
    CircularProgress,
    Alert,
} from '@mui/material';
import SyncIcon from '@mui/icons-material/Sync';
import { format } from 'date-fns';

const Grid = MuiGrid as any;

const OrderPanel: React.FC<{
    title: string;
    orders: Order[];
    onSync: (orderId: string) => void;
    onStatusChange: (orderId: string, status: OrderSyncStatus) => void;
    isLoading: boolean;
}> = ({ title, orders, onSync, onStatusChange, isLoading }) => {
    return (
        <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
                {title} ({orders.length})
            </Typography>
            {isLoading ? (
                <Box display="flex" justifyContent="center" p={3}>
                    <CircularProgress />
                </Box>
            ) : (
                <Box>
                    {orders.map((order) => (
                        <Paper
                            key={order.id}
                            sx={{
                                p: 2,
                                mb: 2,
                                backgroundColor: 'background.default',
                            }}
                        >
                            <Grid container spacing={2}>
                                <Grid item xs={12} sm={6}>
                                    <Typography variant="subtitle1">
                                        Order #{order.ms1_order_id}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        MS1 Status: {order.ms1_status || 'N/A'}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        MS2 Status: {order.ms2_status || 'N/A'}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        Last Synced: {order.last_synced_at ? format(new Date(order.last_synced_at), 'PPpp') : 'Never'}
                                    </Typography>
                                </Grid>
                                <Grid item xs={12} sm={6}>
                                    <Box display="flex" justifyContent="flex-end" gap={1}>
                                        {order.sync_status === 'PENDING' && (
                                            <Button
                                                variant="contained"
                                                startIcon={<SyncIcon />}
                                                onClick={() => onSync(order.ms1_order_id)}
                                            >
                                                Sync Now
                                            </Button>
                                        )}
                                        {order.sync_status === 'MODIFIED' && (
                                            <Button
                                                variant="outlined"
                                                onClick={() => onStatusChange(order.ms1_order_id, 'PENDING')}
                                            >
                                                Resync
                                            </Button>
                                        )}
                                    </Box>
                                </Grid>
                            </Grid>
                            {order.error && (
                                <Alert severity="error" sx={{ mt: 1 }}>
                                    {order.error}
                                </Alert>
                            )}
                        </Paper>
                    ))}
                </Box>
            )}
        </Paper>
    );
};

const OrderSync: React.FC = () => {
    const [orders, setOrders] = useState<Order[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchOrders = async () => {
        try {
            setIsLoading(true);
            const data = await orderSyncApi.getOrders();
            setOrders(data);
            setError(null);
        } catch (err) {
            setError('Failed to fetch orders');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchOrders();
    }, []);

    const handleSync = async (orderId: string) => {
        try {
            await orderSyncApi.syncOrder(orderId);
            fetchOrders();
        } catch (err) {
            console.error(err);
        }
    };

    const handleStatusChange = async (orderId: string, status: OrderSyncStatus) => {
        try {
            await orderSyncApi.updateOrderStatus(orderId, status);
            fetchOrders();
        } catch (err) {
            console.error(err);
        }
    };

    const handleSyncAllPending = async () => {
        try {
            await orderSyncApi.syncAllPending();
            fetchOrders();
        } catch (err) {
            console.error(err);
        }
    };

    const filterOrders = (status: OrderSyncStatus) => {
        return orders.filter((order) => order.sync_status === status);
    };

    return (
        <Container maxWidth="xl" sx={{ py: 4 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h4">Order Sync</Typography>
                <Box display="flex" gap={2}>
                    <Button
                        variant="outlined"
                        onClick={async () => {
                            try {
                                await orderSyncApi.checkStatuses();
                                fetchOrders();
                            } catch (err) {
                                console.error(err);
                            }
                        }}
                    >
                        Check Statuses
                    </Button>
                    <Button
                        variant="contained"
                        startIcon={<SyncIcon />}
                        onClick={handleSyncAllPending}
                    >
                        Sync All Pending
                    </Button>
                </Box>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                </Alert>
            )}

            <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                    <OrderPanel
                        title="Synced Orders"
                        orders={filterOrders('SYNCED')}
                        onSync={handleSync}
                        onStatusChange={handleStatusChange}
                        isLoading={isLoading}
                    />
                </Grid>
                <Grid item xs={12} md={6}>
                    <OrderPanel
                        title="Pending Orders"
                        orders={filterOrders('PENDING')}
                        onSync={handleSync}
                        onStatusChange={handleStatusChange}
                        isLoading={isLoading}
                    />
                </Grid>
                <Grid item xs={12} md={6}>
                    <OrderPanel
                        title="Modified Orders"
                        orders={filterOrders('MODIFIED')}
                        onSync={handleSync}
                        onStatusChange={handleStatusChange}
                        isLoading={isLoading}
                    />
                </Grid>
                <Grid item xs={12} md={6}>
                    <OrderPanel
                        title="Failed Orders"
                        orders={filterOrders('FAILED')}
                        onSync={handleSync}
                        onStatusChange={handleStatusChange}
                        isLoading={isLoading}
                    />
                </Grid>
            </Grid>
        </Container>
    );
};

export default OrderSync; 