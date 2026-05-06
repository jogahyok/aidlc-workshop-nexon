import { createApiClient, type Order } from '@table-order/shared';

const apiClient = createApiClient({
  baseUrl: import.meta.env.VITE_API_URL || '/api',
  getToken: () => localStorage.getItem('customer_auth_token') ? JSON.parse(localStorage.getItem('customer_auth_token')!).value : null,
  onUnauthorized: () => { window.location.href = '/error'; },
});

export interface CreateOrderRequest {
  tableId: string;
  sessionId: string;
  items: CreateOrderItem[];
  totalAmount: number;
}

export interface CreateOrderItem {
  menuItemId: string;
  menuName: string;
  quantity: number;
  unitPrice: number;
  options: { optionItemId: string; optionName: string; additionalPrice: number }[];
}

export async function createOrder(storeId: string, data: CreateOrderRequest): Promise<Order> {
  const response = await apiClient.post<Order>(`/stores/${storeId}/orders`, data);
  return response.data;
}

export async function getTableOrders(
  storeId: string,
  tableId: string,
  sessionId: string,
): Promise<Order[]> {
  const response = await apiClient.get<Order[]>(
    `/stores/${storeId}/tables/${tableId}/orders`,
    { params: { sessionId } },
  );
  return response.data;
}
