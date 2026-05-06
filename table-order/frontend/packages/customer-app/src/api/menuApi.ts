import { createApiClient, type Category, type MenuItem, type OptionGroup } from '@table-order/shared';

const apiClient = createApiClient({
  baseUrl: import.meta.env.VITE_API_URL || '/api',
  getToken: () => localStorage.getItem('customer_auth_token') ? JSON.parse(localStorage.getItem('customer_auth_token')!).value : null,
  onUnauthorized: () => { window.location.href = '/error'; },
});

export async function getCategories(storeId: string): Promise<Category[]> {
  const response = await apiClient.get<Category[]>(`/stores/${storeId}/categories`);
  return response.data;
}

export async function getMenus(storeId: string, categoryId?: string): Promise<MenuItem[]> {
  const params = categoryId ? { categoryId } : {};
  const response = await apiClient.get<MenuItem[]>(`/stores/${storeId}/menus`, { params });
  return response.data;
}

export async function getMenuOptions(menuId: string): Promise<OptionGroup[]> {
  const response = await apiClient.get<OptionGroup[]>(`/menus/${menuId}/options`);
  return response.data;
}
