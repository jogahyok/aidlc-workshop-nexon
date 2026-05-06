import { useQuery } from '@tanstack/react-query';
import { Box, Typography, Paper, Chip, List, ListItem, ListItemText, Divider } from '@mui/material';
import { Loading, EmptyState, PriceDisplay, type OrderStatus } from '@table-order/shared';
import ReceiptIcon from '@mui/icons-material/Receipt';
import { useAuth } from '../contexts/AuthContext';
import { getTableOrders } from '../api/orderApi';
import { formatTime } from '@table-order/shared';

const STATUS_CONFIG: Record<OrderStatus, { label: string; color: 'warning' | 'info' | 'success' }> = {
  pending: { label: '대기중', color: 'warning' },
  preparing: { label: '준비중', color: 'info' },
  completed: { label: '완료', color: 'success' },
};

export default function OrderHistoryPage() {
  const { storeId, tableId } = useAuth();

  const { data: orders = [], isLoading } = useQuery({
    queryKey: ['orders', tableId],
    queryFn: () => getTableOrders(storeId!, tableId!, ''), // sessionId는 서버에서 현재 세션 자동 조회
    enabled: !!storeId && !!tableId,
    refetchInterval: 30 * 1000,
    refetchIntervalInBackground: false,
  });

  if (isLoading) return <Loading />;

  if (orders.length === 0) {
    return (
      <EmptyState
        icon={<ReceiptIcon />}
        title="주문 내역이 없습니다"
        description="메뉴에서 주문을 시작해보세요"
      />
    );
  }

  return (
    <Box data-testid="order-history-page" sx={{ p: 2, pb: 8 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>주문 내역</Typography>

      {orders.map((order) => (
        <Paper key={order.id} sx={{ p: 2, mb: 2 }} data-testid={`order-card-${order.id}`}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="subtitle2" color="text.secondary">
              #{order.orderNumber} · {formatTime(order.createdAt)}
            </Typography>
            <Chip
              label={STATUS_CONFIG[order.status].label}
              color={STATUS_CONFIG[order.status].color}
              size="small"
              data-testid={`order-status-${order.id}`}
            />
          </Box>
          <List dense>
            {order.items.map((item) => (
              <ListItem key={item.id} disablePadding>
                <ListItemText
                  primary={`${item.menuName} × ${item.quantity}`}
                  secondary={item.options.length > 0 ? item.options.map((o) => o.optionName).join(', ') : undefined}
                />
              </ListItem>
            ))}
          </List>
          <Divider sx={{ my: 1 }} />
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <PriceDisplay amount={order.totalAmount} variant="subtitle1" />
          </Box>
        </Paper>
      ))}
    </Box>
  );
}
