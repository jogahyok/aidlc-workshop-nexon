import type { CartState, CartAction, CartItem, SelectedOption } from '@table-order/shared';
import type { MenuItem } from '@table-order/shared';

const INITIAL_CART_STATE: CartState = {
  items: [],
  totalAmount: 0,
  itemCount: 0,
  storeId: '',
  tableId: '',
  sessionId: '',
  lastUpdated: new Date().toISOString(),
  expiresAt: '',
};

/**
 * 항목 소계를 계산합니다.
 * (메뉴 기본가 + 옵션 추가가 합계) × 수량
 */
export function calculateItemTotal(
  menuPrice: number,
  options: SelectedOption[],
  quantity: number,
): number {
  const optionsTotal = options.reduce((sum, opt) => sum + opt.additionalPrice, 0);
  return (menuPrice + optionsTotal) * quantity;
}

/**
 * 장바구니 총 금액을 계산합니다.
 */
export function calculateCartTotal(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.itemTotal, 0);
}

/**
 * 장바구니 총 수량을 계산합니다.
 */
export function calculateItemCount(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.quantity, 0);
}

/**
 * 동일 메뉴+옵션 조합인지 확인합니다.
 */
function isSameItem(existing: CartItem, menuItem: MenuItem, options: SelectedOption[]): boolean {
  if (existing.menuItem.id !== menuItem.id) return false;
  if (existing.selectedOptions.length !== options.length) return false;

  const existingIds = existing.selectedOptions.map((o) => o.optionId).sort();
  const newIds = options.map((o) => o.optionId).sort();

  return existingIds.every((id, idx) => id === newIds[idx]);
}

export function cartReducer(state: CartState, action: CartAction): CartState {
  switch (action.type) {
    case 'ADD_ITEM': {
      const { menuItem, options, quantity } = action.payload;
      const existingIndex = state.items.findIndex((item) =>
        isSameItem(item, menuItem, options),
      );

      let newItems: CartItem[];

      if (existingIndex >= 0) {
        // 동일 메뉴+옵션 → 수량 증가
        newItems = state.items.map((item, idx) => {
          if (idx !== existingIndex) return item;
          const newQuantity = Math.min(item.quantity + quantity, 99);
          return {
            ...item,
            quantity: newQuantity,
            itemTotal: calculateItemTotal(item.menuItem.price, item.selectedOptions, newQuantity),
          };
        });
      } else {
        // 새 항목 추가
        const newItem: CartItem = {
          cartItemId: `cart-${Date.now()}-${Math.random().toString(36).slice(2)}`,
          menuItem,
          selectedOptions: options,
          quantity,
          itemTotal: calculateItemTotal(menuItem.price, options, quantity),
          addedAt: new Date().toISOString(),
        };
        newItems = [...state.items, newItem];
      }

      return {
        ...state,
        items: newItems,
        totalAmount: calculateCartTotal(newItems),
        itemCount: calculateItemCount(newItems),
        lastUpdated: new Date().toISOString(),
      };
    }

    case 'REMOVE_ITEM': {
      const newItems = state.items.filter((item) => item.cartItemId !== action.payload.cartItemId);
      return {
        ...state,
        items: newItems,
        totalAmount: calculateCartTotal(newItems),
        itemCount: calculateItemCount(newItems),
        lastUpdated: new Date().toISOString(),
      };
    }

    case 'UPDATE_QUANTITY': {
      const { cartItemId, quantity } = action.payload;

      if (quantity <= 0) {
        // 수량 0 이하 → 삭제
        const newItems = state.items.filter((item) => item.cartItemId !== cartItemId);
        return {
          ...state,
          items: newItems,
          totalAmount: calculateCartTotal(newItems),
          itemCount: calculateItemCount(newItems),
          lastUpdated: new Date().toISOString(),
        };
      }

      const clampedQuantity = Math.min(Math.max(quantity, 1), 99);
      const newItems = state.items.map((item) => {
        if (item.cartItemId !== cartItemId) return item;
        return {
          ...item,
          quantity: clampedQuantity,
          itemTotal: calculateItemTotal(item.menuItem.price, item.selectedOptions, clampedQuantity),
        };
      });

      return {
        ...state,
        items: newItems,
        totalAmount: calculateCartTotal(newItems),
        itemCount: calculateItemCount(newItems),
        lastUpdated: new Date().toISOString(),
      };
    }

    case 'CLEAR_CART':
      return {
        ...state,
        items: [],
        totalAmount: 0,
        itemCount: 0,
        lastUpdated: new Date().toISOString(),
      };

    case 'LOAD_FROM_STORAGE':
      return action.payload;

    case 'RESET_EXPIRED':
      return { ...INITIAL_CART_STATE, storeId: state.storeId, tableId: state.tableId, sessionId: state.sessionId };

    default:
      return state;
  }
}

export { INITIAL_CART_STATE };
