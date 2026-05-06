export type OrderStatus = 'pending' | 'preparing' | 'completed';

export interface Order {
  id: string;
  storeId: string;
  tableId: string;
  sessionId: string;
  orderNumber: string;
  status: OrderStatus;
  totalAmount: number;
  items: OrderItem[];
  createdAt: string;
  updatedAt: string;
}

export interface OrderItem {
  id: string;
  orderId: string;
  menuName: string;
  quantity: number;
  unitPrice: number;
  options: OrderItemOption[];
  subtotal: number;
}

export interface OrderItemOption {
  id: string;
  orderItemId: string;
  optionName: string;
  additionalPrice: number;
}

export type OrderEvent =
  | { type: 'new_order'; data: Order }
  | { type: 'status_changed'; data: { orderId: string; status: OrderStatus } }
  | { type: 'order_deleted'; data: { orderId: string; tableId: string } };
