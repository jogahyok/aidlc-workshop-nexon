import axios from 'axios';
import type { Category, MenuItem, OptionGroup } from '@table-order/shared';

// Vite 프록시를 통해 menu-service로 연결
const menuClient = axios.create({
  baseURL: '/menu-api',
  timeout: 10000,
});

// snake_case API 응답을 camelCase 프론트엔드 타입으로 변환
function mapCategory(raw: Record<string, unknown>): Category {
  return {
    id: String(raw.id),
    storeId: String(raw.store_id),
    name: raw.name as string,
    sortOrder: raw.sort_order as number,
  };
}

function mapMenuItem(raw: Record<string, unknown>): MenuItem {
  return {
    id: String(raw.id),
    categoryId: String(raw.category_id),
    storeId: String(raw.store_id),
    name: raw.name as string,
    price: raw.price as number,
    description: (raw.description as string) || undefined,
    imageUrl: (raw.image_url as string) || undefined,
    sortOrder: raw.sort_order as number,
    optionGroups: [],
  };
}

function mapOptionGroup(raw: Record<string, unknown>): OptionGroup {
  const items = (raw.items as Record<string, unknown>[]) || [];
  return {
    id: String(raw.id),
    menuItemId: String(raw.menu_item_id),
    name: raw.name as string,
    isRequired: raw.is_required as boolean,
    minSelections: (raw.is_required as boolean) ? 1 : 0,
    maxSelections: (raw.max_select as number) || 1,
    options: items.map((item) => ({
      id: String(item.id),
      groupId: String(item.option_group_id),
      name: item.name as string,
      additionalPrice: (item.price as number) || 0,
    })),
  };
}

export async function getCategories(storeId: string): Promise<Category[]> {
  const response = await menuClient.get(`/stores/${storeId}/categories`);
  return (response.data as Record<string, unknown>[]).map(mapCategory);
}

export async function getMenus(storeId: string, categoryId?: string): Promise<MenuItem[]> {
  const params = categoryId ? { category_id: categoryId } : {};
  const response = await menuClient.get(`/stores/${storeId}/menus`, { params });
  return (response.data as Record<string, unknown>[]).map(mapMenuItem);
}

export async function getMenuOptions(menuId: string): Promise<OptionGroup[]> {
  const response = await menuClient.get(`/menus/${menuId}/options`);
  return (response.data as Record<string, unknown>[]).map(mapOptionGroup);
}
