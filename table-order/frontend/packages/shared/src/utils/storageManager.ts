interface StorageItem<T> {
  value: T;
  expiresAt?: string;
  createdAt: string;
}

/**
 * localStorage 래퍼 — 만료 시간 관리 및 타입 안전 접근을 제공합니다.
 */
export const StorageManager = {
  get<T>(key: string): T | null {
    try {
      const raw = localStorage.getItem(key);
      if (!raw) return null;

      const item: StorageItem<T> = JSON.parse(raw);

      if (item.expiresAt && new Date(item.expiresAt).getTime() < Date.now()) {
        localStorage.removeItem(key);
        return null;
      }

      return item.value;
    } catch {
      localStorage.removeItem(key);
      return null;
    }
  },

  set<T>(key: string, value: T, ttlMs?: number): void {
    const item: StorageItem<T> = {
      value,
      createdAt: new Date().toISOString(),
      expiresAt: ttlMs ? new Date(Date.now() + ttlMs).toISOString() : undefined,
    };

    try {
      localStorage.setItem(key, JSON.stringify(item));
    } catch {
      // QuotaExceeded — 만료 항목 정리 후 재시도
      StorageManager.clearExpired();
      try {
        localStorage.setItem(key, JSON.stringify(item));
      } catch {
        // 여전히 실패하면 무시
      }
    }
  },

  remove(key: string): void {
    localStorage.removeItem(key);
  },

  isExpired(key: string): boolean {
    const raw = localStorage.getItem(key);
    if (!raw) return true;

    try {
      const item = JSON.parse(raw) as StorageItem<unknown>;
      if (!item.expiresAt) return false;
      return new Date(item.expiresAt).getTime() < Date.now();
    } catch {
      return true;
    }
  },

  clearExpired(): void {
    const keysToRemove: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && StorageManager.isExpired(key)) {
        keysToRemove.push(key);
      }
    }
    keysToRemove.forEach((key) => localStorage.removeItem(key));
  },
};
