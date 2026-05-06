import { createContext, useContext, useReducer, useEffect, useCallback, type ReactNode } from 'react';
import { StorageManager, type CartState, type CartAction, type MenuItem, type SelectedOption } from '@table-order/shared';
import { cartReducer, INITIAL_CART_STATE } from './cartReducer';
import { useAuth } from './AuthContext';

interface CartContextValue {
  cart: CartState;
  addItem: (menuItem: MenuItem, options: SelectedOption[], quantity: number) => void;
  removeItem: (cartItemId: string) => void;
  updateQuantity: (cartItemId: string, quantity: number) => void;
  clearCart: () => void;
}

const CartContext = createContext<CartContextValue | null>(null);

function getCartKey(storeId: string, tableId: string): string {
  return `cart_${storeId}_${tableId}`;
}

export function CartProvider({ children }: { children: ReactNode }) {
  const { storeId, tableId } = useAuth();
  const cartKey = storeId && tableId ? getCartKey(storeId, tableId) : '';

  const [cart, dispatch] = useReducer(cartReducer, INITIAL_CART_STATE);

  // localStorage에서 장바구니 로드
  useEffect(() => {
    if (!cartKey) return;

    const saved = StorageManager.get<CartState>(cartKey);
    if (saved) {
      dispatch({ type: 'LOAD_FROM_STORAGE', payload: saved });
    }
  }, [cartKey]);

  // 장바구니 변경 시 localStorage에 저장
  useEffect(() => {
    if (!cartKey || cart.items.length === 0) return;
    StorageManager.set(cartKey, cart);
  }, [cart, cartKey]);

  const addItem = useCallback(
    (menuItem: MenuItem, options: SelectedOption[], quantity: number) => {
      dispatch({ type: 'ADD_ITEM', payload: { menuItem, options, quantity } });
    },
    [],
  );

  const removeItem = useCallback((cartItemId: string) => {
    dispatch({ type: 'REMOVE_ITEM', payload: { cartItemId } });
  }, []);

  const updateQuantity = useCallback((cartItemId: string, quantity: number) => {
    dispatch({ type: 'UPDATE_QUANTITY', payload: { cartItemId, quantity } });
  }, []);

  const clearCart = useCallback(() => {
    dispatch({ type: 'CLEAR_CART' });
    if (cartKey) StorageManager.remove(cartKey);
  }, [cartKey]);

  return (
    <CartContext.Provider value={{ cart, addItem, removeItem, updateQuantity, clearCart }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart(): CartContextValue {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}
