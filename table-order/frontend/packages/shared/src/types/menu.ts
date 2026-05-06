export interface Category {
  id: string;
  storeId: string;
  name: string;
  sortOrder: number;
}

export interface MenuItem {
  id: string;
  categoryId: string;
  storeId: string;
  name: string;
  price: number;
  description?: string;
  imageUrl?: string;
  sortOrder: number;
  optionGroups: OptionGroup[];
}

export interface OptionGroup {
  id: string;
  menuItemId: string;
  name: string;
  isRequired: boolean;
  minSelections: number;
  maxSelections: number;
  options: OptionItem[];
}

export interface OptionItem {
  id: string;
  groupId: string;
  name: string;
  additionalPrice: number;
}
