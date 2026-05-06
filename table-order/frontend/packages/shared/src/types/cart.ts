import type { MenuItem } from './menu';

export interface SelectedOption {
  groupId: string;
  groupName: string;
  optionId: string;
  optionName: string;
  additionalPrice: number;
}

export interface CartItem {
  cartItemId: string;
  menuItem: MenuItem;
  selectedOptions: SelectedOption[];
  quantity: number;
  itemTotal: number;
  addedAt: string;
}

export interface CartState {
  items: CartItem[];
  totalAmount: number;
  itemCount: number;
  storeId: string;
  tableId: string;
  sessionId: string;
  lastUpdated: string;
  expiresAt: string;
}

export type CartAction =
  | { type: 'ADD_ITEM'; payload: { menuItem: MenuItem; options: SelectedOption[]; quantity: number } }
  | { type: 'REMOVE_ITEM'; payload: { cartItemId: string } }
  | { type: 'UPDATE_QUANTITY'; payload: { cartItemId: string; quantity: number } }
  | { type: 'CLEAR_CART' }
  | { type: 'LOAD_FROM_STORAGE'; payload: CartState }
  | { type: 'RESET_EXPIRED' };
