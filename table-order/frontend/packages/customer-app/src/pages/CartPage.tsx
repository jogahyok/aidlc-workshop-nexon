import { useNavigate } from 'react-router-dom';
import { Box, Typography, Button, IconButton, Divider } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { PriceDisplay, QuantityControl, EmptyState, ConfirmDialog } from '@table-order/shared';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import { useState } from 'react';
import { useCart } from '../contexts/CartContext';

export default function CartPage() {
  const navigate = useNavigate();
  const { cart, removeItem, updateQuantity, clearCart } = useCart();
  const [showClearConfirm, setShowClearConfirm] = useState(false);

  if (cart.items.length === 0) {
    return (
      <EmptyState
        icon={<ShoppingCartIcon />}
        title="장바구니가 비어있습니다"
        description="메뉴에서 원하는 항목을 추가해보세요"
        action={{ label: '메뉴 보기', onClick: () => navigate('/menu') }}
      />
    );
  }

  return (
    <Box data-testid="cart-page" sx={{ p: 2, pb: 12 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">장바구니</Typography>
        <Button size="small" color="error" onClick={() => setShowClearConfirm(true)} data-testid="clear-cart-button">
          전체 삭제
        </Button>
      </Box>

      {cart.items.map((item) => (
        <Box key={item.cartItemId} sx={{ mb: 2 }} data-testid={`cart-item-${item.cartItemId}`}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="subtitle1" fontWeight="bold">{item.menuItem.name}</Typography>
              {item.selectedOptions.length > 0 && (
                <Typography variant="body2" color="text.secondary">
                  {item.selectedOptions.map((o) => o.optionName).join(', ')}
                </Typography>
              )}
            </Box>
            <IconButton onClick={() => removeItem(item.cartItemId)} aria-label="삭제" data-testid={`remove-item-${item.cartItemId}`}>
              <DeleteIcon />
            </IconButton>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
            <QuantityControl value={item.quantity} onChange={(q) => updateQuantity(item.cartItemId, q)} />
            <PriceDisplay amount={item.itemTotal} variant="body1" />
          </Box>
          <Divider sx={{ mt: 2 }} />
        </Box>
      ))}

      {/* 하단 고정 주문 버튼 */}
      <Box sx={{ position: 'fixed', bottom: 56, left: 0, right: 0, p: 2, bgcolor: 'background.paper', borderTop: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="subtitle1">총 금액</Typography>
          <PriceDisplay amount={cart.totalAmount} variant="h6" color="primary" />
        </Box>
        <Button
          variant="contained"
          fullWidth
          size="large"
          onClick={() => navigate('/cart/confirm')}
          data-testid="order-button"
          sx={{ minHeight: 48 }}
        >
          주문하기 ({cart.itemCount}개)
        </Button>
      </Box>

      <ConfirmDialog
        open={showClearConfirm}
        title="장바구니 비우기"
        message="장바구니의 모든 항목을 삭제하시겠습니까?"
        onConfirm={() => { clearCart(); setShowClearConfirm(false); }}
        onCancel={() => setShowClearConfirm(false)}
      />
    </Box>
  );
}
