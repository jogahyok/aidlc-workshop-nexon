import { useState, useCallback } from 'react';
import { StorageManager } from '../utils/storageManager';

/**
 * localStorage와 동기화되는 상태 훅입니다.
 * @param key - localStorage 키
 * @param initialValue - 초기값
 * @param ttlMs - 만료 시간 (밀리초, 선택)
 */
export function useLocalStorage<T>(
  key: string,
  initialValue: T,
  ttlMs?: number,
): [T, (value: T) => void, () => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    const existing = StorageManager.get<T>(key);
    return existing !== null ? existing : initialValue;
  });

  const setValue = useCallback(
    (value: T) => {
      setStoredValue(value);
      StorageManager.set(key, value, ttlMs);
    },
    [key, ttlMs],
  );

  const removeValue = useCallback(() => {
    setStoredValue(initialValue);
    StorageManager.remove(key);
  }, [key, initialValue]);

  return [storedValue, setValue, removeValue];
}
