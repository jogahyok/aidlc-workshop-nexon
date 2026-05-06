import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { Box, Typography, Button, Paper, List, ListItem, ListItemText, Dialog, DialogContent } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { PriceDisplay, Loading, useToast } from '@table-order/shared';
import { useAuth } from '../contexts/AuthContext';
import { useCart } from '../contexts/CartContext';
import { createOrder } from '../api/orderApi';

export default function OrderConfirmPage() {
  const navigate = useNavigate();
  const { storeId, tableId } = useAuth();
  const { cart, clearCart } = useCart();
  const { showToast } = useToast();
  const [orderNumber, setOrderNumber] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () =>
      createOrder(storeId!, {
        tableId: tableId!,
        sessionId: cart.sessionId,
        items: cart.items.map((item) => ({
          menuItemId: item.menuItem.id,
          menuName: item.menuItem.name,
          quantity: item.quantity,
          unitPrice: item.menuItem.price,
          options: item.selectedOptions.map((opt) => ({
            optionItemId: opt.optionId,
            optionName: opt.optionName,
            additionalPrice: opt.additionalPrice,
          })),
        })),
        totalAmount: cart.totalAmount,
      }),
    onSuccess: (order) => {
      setOrderNumber(order.orderNumber);
      clearCart();
      setTimeout(() => navigate('/menu'), 5000);
    },
    onError: () => {
      showToast({ message: '주문에 실패했습니다. 다시 시도해주세요.', severity: 'error' });
    },
  });

  if (cart.items.length === 0 && !orderNumber) {
    navigate('/cart');
    return null;
  }

  return (
    <Box data-testid="order-confirm-page" sx={{ p: 2 }}>
      <Typography variant="h6" sx={{ mb: 2 }}>주문 확인</Typography>

      <Paper sx={{ p: 2, mb: 2 }}>
        <List dense>
          {cart.items.map((item) => (
            <ListItem key={item.cartItemId} data-testid={`confirm-item-${item.cartItemId}`}>
              <ListItemText
                primary={`${item.menuItem.name} × ${item.quantity}`}
                secondary={item.selectedOptions.length > 0
                  ? item.selectedOptions.map((o) => o.optionName).join(', ')
                  : undefined}
              />
              <PriceDisplay amount={item.itemTotal} variant="body2" />
            </ListItem>
          ))}
        </List>
      </Paper>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h6">총 금액</Typography>
        <PriceDisplay amount={cart.totalAmount} variant="h5" color="primary" />
      </Box>

      <Button
        variant="contained"
        fullWidth
        size="large"
        onClick={() => mutation.mutate()}
        disabled={mutation.isPending}
        data-testid="confirm-order-button"
        sx={{ minHeight: 48 }}
      >
        {mutation.isPending ? <Loading size={24} /> : '주문 확정'}
      </Button>

      {/* 주문 성공 다이얼로그 */}
      <Dialog open={!!orderNumber} data-testid="order-success-dialog">
        <DialogContent sx={{ textAlign: 'center', p: 4 }}>
          <CheckCircleIcon sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
          <Typography variant="h5" gutterBottom>주문 완료!</Typography>
          <Typography variant="h4" color="primary" fontWeight="bold" sx={{ mb: 2 }}>
            #{orderNumber}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            5초 후 메뉴 화면으로 이동합니다
          </Typography>
        </DialogContent>
      </Dialog>
    </Box>
  );
}
