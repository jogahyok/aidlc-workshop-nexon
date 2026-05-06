export interface Store {
  id: string;
  name: string;
  description?: string;
}

export interface Table {
  id: string;
  storeId: string;
  tableNumber: number;
  status: 'active' | 'inactive';
  currentSessionId?: string;
}

export interface TableSession {
  id: string;
  tableId: string;
  storeId: string;
  startedAt: string;
  endedAt?: string;
  status: 'active' | 'completed';
}
