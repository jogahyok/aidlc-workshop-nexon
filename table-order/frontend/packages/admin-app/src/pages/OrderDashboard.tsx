import { useState, useEffect, useCallback } from 'react';
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { Box, Typography, Grid, Card, CardContent, Chip, Paper, List, ListItem, ListItemText, Button, Divider } from '@mui/material';
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';
import { PriceDisplay, Loading, useToast, type Order, type OrderStatus, type OrderEvent } from '@table-order/shared';
import { useAuth } from '../contexts/AuthContext';
import { getOrders, updateOrderStatus, deleteOrder } from '../api/orderApi';
import { useSSE } from '../hooks/useSSE';

const STATUS_CONFIG: Record<OrderStatus, { label: string; color: 'warning' | 'info' | 'success' }> = {
  pending: { label: '대기중', color: 'warning' },
  preparing: { label: '준비중', color: 'info' },
  completed: { label: '완료', color: 'success' },
};

const NEXT_STATUS: Record<OrderStatus, OrderStatus | null> = {
  pending: 'preparing',
  preparing: 'completed',
  completed: null,
};

export default function OrderDashboard() {
  const { storeId, token } = useAuth();
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const [selectedTableId, setSelectedTableId] = useState<string | null>(null);

  const { data: orders = [], isLoading } = useQuery({
    queryKey: ['orders', storeId],
    queryFn: () => getOrders(storeId!),
    enabled: !!storeId,
  });

  // SSE 연결
  const handleSSEEvent = useCallback((event: OrderEvent) => {
    queryClient.invalidateQueries({ queryKey: ['orders', storeId] });
    if (event.type === 'new_order') {
      showToast({ message: `새 주문이 들어왔습니다!`, severity: 'info' });
    }
  }, [queryClient, storeId, showToast]);

  const { connectionState } = useSSE({
    url: `${import.meta.env.VITE_API_URL || '/api'}/stores/${storeId}/orders/stream`,
    token: token!,
    onEvent: handleSSEEvent,
    enabled: !!storeId && !!token,
  });

  // 테이블별 주문 그룹핑
  const tableOrders = orders.reduce<Record<string, Order[]>>((acc, order) => {
    if (!acc[order.tableId]) acc[order.tableId] = [];
    acc[order.tableId].push(order);
    return acc;
  }, {});

  const statusMutation = useMutation({
    mutationFn: ({ orderId, status }: { orderId: string; status: OrderStatus }) =>
      updateOrderStatus(orderId, status),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['orders'] }),
    onError: () => showToast({ message: '상태 변경에 실패했습니다', severity: 'error' }),
  });

  const selectedOrders = selectedTableId ? tableOrders[selectedTableId] || [] : [];

  if (isLoading) return <Loading />;

  return (
    <Box data-testid="order-dashboard">
      {/* 연결 상태 */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <FiberManualRecordIcon sx={{ fontSize: 12, color: connectionState === 'connected' ? 'success.main' : 'error.main' }} />
        <Typography variant="caption" color="text.secondary">
          {connectionState === 'connected' ? '실시간 연결됨' : '연결 끊김'}
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', gap: 2, height: 'calc(100vh - 140px)' }}>
        {/* 좌측: 테이블 그리드 */}
        <Box sx={{ flex: 7, overflow: 'auto' }}>
          <Grid container spacing={2}>
            {Object.entries(tableOrders).map(([tableId, tOrders]) => {
              const totalAmount = tOrders.reduce((sum, o) => sum + o.totalAmount, 0);
              const hasPending = tOrders.some((o) => o.status === 'pending');
              return (
                <Grid item xs={6} sm={4} md={3} key={tableId}>
                  <Card
                    onClick={() => setSelectedTableId(tableId)}
                    sx={{
                      cursor: 'pointer',
                      border: selectedTableId === tableId ? 2 : 1,
                      borderColor: selectedTableId === tableId ? 'primary.main' : hasPending ? 'warning.main' : 'divider',
                      minHeight: 44,
                    }}
                    data-testid={`table-card-${tableId}`}
                  >
                    <CardContent>
                      <Typography variant="subtitle2">테이블</Typography>
                      {hasPending && <Chip label="NEW" size="small" color="warning" sx={{ ml: 1 }} />}
                      <PriceDisplay amount={totalAmount} variant="body1" />
                      <Typography variant="caption" color="text.secondary">
                        {tOrders.length}건
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              );
            })}
          </Grid>
        </Box>

        {/* 우측: 선택된 테이블 상세 */}
        <Paper sx={{ flex: 3, overflow: 'auto', p: 2 }} data-testid="order-detail-panel">
          {selectedTableId ? (
            <>
              <Typography variant="h6" sx={{ mb: 2 }}>주문 상세</Typography>
              <List>
                {selectedOrders.map((order) => (
                  <Box key={order.id} sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="subtitle2">#{order.orderNumber}</Typography>
                      <Chip label={STATUS_CONFIG[order.status].label} color={STATUS_CONFIG[order.status].color} size="small" />
                    </Box>
                    {order.items.map((item) => (
                      <ListItem key={item.id} dense>
                        <ListItemText primary={`${item.menuName} × ${item.quantity}`} />
                      </ListItem>
                    ))}
                    <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                      {NEXT_STATUS[order.status] && (
                        <Button
                          size="small"
                          variant="contained"
                          onClick={() => statusMutation.mutate({ orderId: order.id, status: NEXT_STATUS[order.status]! })}
                          data-testid={`status-change-${order.id}`}
                        >
                          {STATUS_CONFIG[NEXT_STATUS[order.status]!].label}으로 변경
                        </Button>
                      )}
                    </Box>
                    <Divider sx={{ mt: 1 }} />
                  </Box>
                ))}
              </List>
            </>
          ) : (
            <Typography color="text.secondary" textAlign="center" sx={{ mt: 4 }}>
              테이블을 선택하세요
            </Typography>
          )}
        </Paper>
      </Box>
    </Box>
  );
}
