import React, { useState } from 'react';
import {
    Box,
    Button,
    Card,
    CardContent,
    Container,
    Grid as MuiGrid,
    MenuItem,
    Paper,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TablePagination,
    TableRow,
    TextField,
    IconButton,
    Tooltip,
    Chip,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    List,
    ListItem,
    ListItemText,
    Divider,
    CircularProgress,
} from '@mui/material';
import { Refresh as RefreshIcon, Sync as SyncIcon, Info as InfoIcon } from '@mui/icons-material';
import { format } from 'date-fns';
import { orderSyncApi } from '../api/orderSync';
import { OrderSync, OrderSyncStatus, OrderModificationStatus } from '../types/order';
import { useSnackbar } from 'notistack';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import styles from './OrderSync.module.css';

const Grid = MuiGrid as any;

const getStatusColor = (status: OrderSyncStatus) => {
    switch (status) {
        case OrderSyncStatus.SYNCED:
            return 'success';
        case OrderSyncStatus.FAILED:
            return 'error';
        case OrderSyncStatus.PENDING:
            return 'warning';
        case OrderSyncStatus.WAITING_FOR_CONFIRM:
            return 'info';
        case OrderSyncStatus.MODIFIED:
            return 'secondary';
        default:
            return 'default';
    }
};

const OrderSyncPage: React.FC = () => {
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const { enqueueSnackbar } = useSnackbar();
    const [selectedOrder, setSelectedOrder] = useState<OrderSync | null>(null);
    const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
    const queryClient = useQueryClient();

    // Filters
    const [syncStatus, setSyncStatus] = useState<OrderSyncStatus | ''>('');
    const [modificationStatus, setModificationStatus] = useState<OrderModificationStatus | ''>('');
    const [search, setSearch] = useState('');

    const { data: ordersData, isLoading } = useQuery({
        queryKey: ['orders', page, rowsPerPage, syncStatus, modificationStatus, search],
        queryFn: async () => {
            const response = await orderSyncApi.getOrders(
                page * rowsPerPage,
                rowsPerPage,
                syncStatus || undefined,
                modificationStatus || undefined,
                undefined,
                undefined,
                undefined,
                search || undefined
            );
            return response;
        },
    });

    const handleChangePage = (event: unknown, newPage: number) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    const updateStatusesMutation = useMutation({
        mutationFn: async () => {
            const response = await orderSyncApi.updateStatuses();
            return response;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['orders'] });
            enqueueSnackbar('Order statuses updated successfully', { variant: 'success' });
        },
        onError: () => {
            enqueueSnackbar('Failed to update order statuses', { variant: 'error' });
        },
    });

    const syncPendingMutation = useMutation({
        mutationFn: async () => {
            const response = await orderSyncApi.syncPending();
            return response;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['orders'] });
            enqueueSnackbar('Pending orders synced successfully', { variant: 'success' });
        },
        onError: () => {
            enqueueSnackbar('Failed to sync pending orders', { variant: 'error' });
        },
    });

    const syncAllMutation = useMutation({
        mutationFn: async () => {
            const response = await orderSyncApi.syncAll();
            return response;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['orders'] });
            enqueueSnackbar('Full sync completed successfully', { variant: 'success' });
        },
        onError: () => {
            enqueueSnackbar('Failed to perform full sync', { variant: 'error' });
        },
    });

    const resyncOrderMutation = useMutation({
        mutationFn: async (orderId: number) => {
            const response = await orderSyncApi.resyncOrder(orderId);
            return response;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['orders'] });
            enqueueSnackbar('Order resynced successfully', { variant: 'success' });
        },
        onError: () => {
            enqueueSnackbar('Failed to resync order', { variant: 'error' });
        },
    });

    const handleShowDetails = async (orderId: number) => {
        try {
            const order = await orderSyncApi.getOrder(orderId);
            setSelectedOrder(order);
            setDetailsDialogOpen(true);
        } catch (error) {
            enqueueSnackbar('Failed to load order details', { variant: 'error' });
        }
    };

    const handleCloseDetails = () => {
        setDetailsDialogOpen(false);
        setSelectedOrder(null);
    };

    const orders = ordersData?.items || [];
    const total = ordersData?.total || 0;

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1>Order Sync</h1>
                <div className={styles.actions}>
                    <Button
                        variant="contained"
                        startIcon={<RefreshIcon />}
                        onClick={() => updateStatusesMutation.mutate()}
                        disabled={updateStatusesMutation.isPending}
                    >
                        {updateStatusesMutation.isPending ? (
                            <>
                                <CircularProgress size={20} color="inherit" />
                                <span style={{ marginLeft: '8px' }}>Updating...</span>
                            </>
                        ) : (
                            'Update Statuses'
                        )}
                    </Button>
                    <Button
                        variant="contained"
                        startIcon={<SyncIcon />}
                        onClick={() => syncPendingMutation.mutate()}
                        disabled={syncPendingMutation.isPending}
                    >
                        {syncPendingMutation.isPending ? (
                            <>
                                <CircularProgress size={20} color="inherit" />
                                <span style={{ marginLeft: '8px' }}>Syncing...</span>
                            </>
                        ) : (
                            'Sync Pending'
                        )}
                    </Button>
                    <Button
                        variant="contained"
                        color="primary"
                        startIcon={<SyncIcon />}
                        onClick={() => syncAllMutation.mutate()}
                        disabled={syncAllMutation.isPending}
                    >
                        {syncAllMutation.isPending ? (
                            <>
                                <CircularProgress size={20} color="inherit" />
                                <span style={{ marginLeft: '8px' }}>Syncing All...</span>
                            </>
                        ) : (
                            'Sync All'
                        )}
                    </Button>
                </div>
            </div>

            <Container maxWidth="xl">
                <Box sx={{ my: 4 }}>
                    <Card sx={{ mb: 3 }}>
                        <CardContent>
                            <Grid container spacing={3} sx={{ mb: 3 }}>
                                <Grid item xs={12} sm={4}>
                                    <TextField
                                        select
                                        fullWidth
                                        label="Sync Status"
                                        value={syncStatus}
                                        onChange={(e) => setSyncStatus(e.target.value as OrderSyncStatus | '')}
                                        sx={{ minWidth: 200 }}
                                    >
                                        <MenuItem value="">All</MenuItem>
                                        {Object.values(OrderSyncStatus).map((status) => (
                                            <MenuItem key={status} value={status}>
                                                {status}
                                            </MenuItem>
                                        ))}
                                    </TextField>
                                </Grid>
                                <Grid item xs={12} sm={4}>
                                    <TextField
                                        select
                                        fullWidth
                                        label="Modification Status"
                                        value={modificationStatus}
                                        onChange={(e) => setModificationStatus(e.target.value as OrderModificationStatus | '')}
                                        sx={{ minWidth: 250 }}
                                    >
                                        <MenuItem value="">All</MenuItem>
                                        {Object.values(OrderModificationStatus).map((status) => (
                                            <MenuItem key={status} value={status}>
                                                {status}
                                            </MenuItem>
                                        ))}
                                    </TextField>
                                </Grid>
                                <Grid item xs={12} sm={4}>
                                    <TextField
                                        fullWidth
                                        label="Search"
                                        value={search}
                                        onChange={(e) => setSearch(e.target.value)}
                                        placeholder="Search in order IDs and messages"
                                        sx={{ minWidth: 250 }}
                                    />
                                </Grid>
                            </Grid>

                            <TableContainer component={Paper}>
                                <Table>
                                    <TableHead>
                                        <TableRow>
                                            <TableCell>ID</TableCell>
                                            <TableCell>MS1 Order ID</TableCell>
                                            <TableCell>MS2 Purchase ID</TableCell>
                                            <TableCell>Config Name</TableCell>
                                            <TableCell>Order Amount</TableCell>
                                            <TableCell>Sync Status</TableCell>
                                            <TableCell>Modification Status</TableCell>
                                            <TableCell>Moment</TableCell>
                                            <TableCell>Actions</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {orders.map((order) => (
                                            <TableRow key={order.id}>
                                                <TableCell>{order.id}</TableCell>
                                                <TableCell>{order.ms1_order_id}</TableCell>
                                                <TableCell>{order.ms2_purchase_id || '-'}</TableCell>
                                                <TableCell>{order.config.name}</TableCell>
                                                <TableCell>{order.order_amount.toLocaleString()}</TableCell>
                                                <TableCell>
                                                    <Chip
                                                        label={order.sync_status}
                                                        color={getStatusColor(order.sync_status)}
                                                        size="small"
                                                    />
                                                </TableCell>
                                                <TableCell>
                                                    {order.modification_status ? (
                                                        <Chip
                                                            label={order.modification_status}
                                                            color="info"
                                                            size="small"
                                                        />
                                                    ) : (
                                                        '-'
                                                    )}
                                                </TableCell>
                                                <TableCell>
                                                    {format(new Date(order.moment), 'yyyy-MM-dd HH:mm:ss')}
                                                </TableCell>
                                                <TableCell>
                                                    <Box sx={{ display: 'flex', gap: 1 }}>
                                                        <Tooltip title="View Details">
                                                            <IconButton
                                                                onClick={() => handleShowDetails(order.id)}
                                                                disabled={isLoading}
                                                            >
                                                                <InfoIcon />
                                                            </IconButton>
                                                        </Tooltip>
                                                        {order.sync_status !== OrderSyncStatus.SYNCED && (
                                                            <Tooltip title="Resync Order">
                                                                <IconButton
                                                                    onClick={() => resyncOrderMutation.mutate(order.id)}
                                                                    disabled={resyncOrderMutation.isPending}
                                                                >
                                                                    <SyncIcon />
                                                                </IconButton>
                                                            </Tooltip>
                                                        )}
                                                    </Box>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </TableContainer>

                            <TablePagination
                                component="div"
                                count={total}
                                page={page}
                                onPageChange={handleChangePage}
                                rowsPerPage={rowsPerPage}
                                onRowsPerPageChange={handleChangeRowsPerPage}
                            />
                        </CardContent>
                    </Card>

                    <Dialog
                        open={detailsDialogOpen}
                        onClose={handleCloseDetails}
                        maxWidth="md"
                        fullWidth
                    >
                        {selectedOrder && (
                            <>
                                <DialogTitle>
                                    Order Details - ID: {selectedOrder.id}
                                </DialogTitle>
                                <DialogContent>
                                    <List>
                                        <ListItem>
                                            <ListItemText
                                                primary="MS1 Order ID"
                                                secondary={selectedOrder.ms1_order_id}
                                            />
                                        </ListItem>
                                        <Divider />
                                        <ListItem>
                                            <ListItemText
                                                primary="MS2 Purchase ID"
                                                secondary={selectedOrder.ms2_purchase_id || '-'}
                                            />
                                        </ListItem>
                                        <Divider />
                                        <ListItem>
                                            <ListItemText
                                                primary="Config Name"
                                                secondary={selectedOrder.config.name}
                                            />
                                        </ListItem>
                                        <Divider />
                                        <ListItem>
                                            <ListItemText
                                                primary="Sync Status"
                                                secondary={
                                                    <Chip
                                                        label={selectedOrder.sync_status}
                                                        color={getStatusColor(selectedOrder.sync_status)}
                                                        size="small"
                                                    />
                                                }
                                            />
                                        </ListItem>
                                        <Divider />
                                        <ListItem>
                                            <ListItemText
                                                primary="Modification Status"
                                                secondary={
                                                    selectedOrder.modification_status ? (
                                                        <Chip
                                                            label={selectedOrder.modification_status}
                                                            color="info"
                                                            size="small"
                                                        />
                                                    ) : (
                                                        '-'
                                                    )
                                                }
                                            />
                                        </ListItem>
                                        <Divider />
                                        <ListItem>
                                            <ListItemText
                                                primary="MS1 State"
                                                secondary={selectedOrder.ms1_state_href}
                                            />
                                        </ListItem>
                                        <Divider />
                                        {selectedOrder.info_msg && (
                                            <>
                                                <ListItem>
                                                    <ListItemText
                                                        primary="Info Message"
                                                        secondary={selectedOrder.info_msg}
                                                    />
                                                </ListItem>
                                                <Divider />
                                            </>
                                        )}
                                        {selectedOrder.error_msg && (
                                            <>
                                                <ListItem>
                                                    <ListItemText
                                                        primary="Error Message"
                                                        secondary={selectedOrder.error_msg}
                                                        secondaryTypographyProps={{ color: 'error' }}
                                                    />
                                                </ListItem>
                                                <Divider />
                                            </>
                                        )}
                                        <ListItem>
                                            <ListItemText
                                                primary="Created"
                                                secondary={format(new Date(selectedOrder.created), 'yyyy-MM-dd HH:mm:ss')}
                                            />
                                        </ListItem>
                                        <Divider />
                                        <ListItem>
                                            <ListItemText
                                                primary="Modified"
                                                secondary={format(new Date(selectedOrder.modified), 'yyyy-MM-dd HH:mm:ss')}
                                            />
                                        </ListItem>
                                    </List>
                                </DialogContent>
                                <DialogActions>
                                    <Button onClick={handleCloseDetails}>Close</Button>
                                </DialogActions>
                            </>
                        )}
                    </Dialog>
                </Box>
            </Container>
        </div>
    );
};

export default OrderSyncPage; 