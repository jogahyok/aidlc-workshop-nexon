import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Box, BottomNavigation as MuiBottomNav, BottomNavigationAction, Badge } from '@mui/material';
import RestaurantMenuIcon from '@mui/icons-material/RestaurantMenu';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong';
import { useCart } from '../contexts/CartContext';

export function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { cart } = useCart();

  const getNavValue = () => {
    if (location.pathname.startsWith('/menu')) return 'menu';
    if (location.pathname.startsWith('/cart')) return 'cart';
    if (location.pathname.startsWith('/orders')) return 'orders';
    return 'menu';
  };

  return (
    <Box sx={{ pb: 7 }}>
      <Outlet />

      <MuiBottomNav
        value={getNavValue()}
        onChange={(_, value) => navigate(`/${value}`)}
        showLabels
        sx={{ position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 1000 }}
        data-testid="bottom-navigation"
      >
        <BottomNavigationAction
          label="메뉴"
          value="menu"
          icon={<RestaurantMenuIcon />}
          data-testid="nav-menu"
          sx={{ minHeight: 56 }}
        />
        <BottomNavigationAction
          label="장바구니"
          value="cart"
          icon={
            <Badge badgeContent={cart.itemCount} color="secondary">
              <ShoppingCartIcon />
            </Badge>
          }
          data-testid="nav-cart"
          sx={{ minHeight: 56 }}
        />
        <BottomNavigationAction
          label="주문내역"
          value="orders"
          icon={<ReceiptLongIcon />}
          data-testid="nav-orders"
          sx={{ minHeight: 56 }}
        />
      </MuiBottomNav>
    </Box>
  );
}
