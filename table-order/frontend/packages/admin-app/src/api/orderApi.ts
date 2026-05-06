import { createApiClient, StorageManager, type Order, type OrderStatus } from '@table-order/shared';

const apiClient = createApiClient({
  baseUrl: import.meta.env.VITE_API_URL || '/api',
  getToken: () => StorageManager.get<string>('admin_auth_token'),
  onUnauthorized: () => { window.location.href = '/login'; },
});

export async function getOrders(storeId: string): Promise<Order[]> {
  const response = await apiClient.get<Order[]>(`/stores/${storeId}/orders`);
  return response.data;
}

export async function updateOrderStatus(orderId: string, status: OrderStatus): Promise<Order> {
  const response = await apiClient.patch<Order>(`/orders/${orderId}/status`, { status });
  return response.data;
}

export async function deleteOrder(orderId: string): Promise<void> {
  await apiClient.delete(`/orders/${orderId}`);
}
