import { describe, it, expect, beforeEach, vi } from 'vitest';
import { StorageManager } from '../storageManager';

describe('StorageManager', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  describe('set and get', () => {
    it('stores and retrieves a value', () => {
      StorageManager.set('test-key', { name: 'hello' });
      const result = StorageManager.get<{ name: string }>('test-key');
      expect(result).toEqual({ name: 'hello' });
    });

    it('returns null for non-existent key', () => {
      expect(StorageManager.get('non-existent')).toBeNull();
    });

    it('returns null for corrupted data', () => {
      localStorage.setItem('bad-key', 'not-json{{{');
      expect(StorageManager.get('bad-key')).toBeNull();
    });
  });

  describe('expiration', () => {
    it('returns value before expiration', () => {
      StorageManager.set('ttl-key', 'value', 60000); // 60초 TTL
      expect(StorageManager.get('ttl-key')).toBe('value');
    });

    it('returns null after expiration', () => {
      StorageManager.set('ttl-key', 'value', 1); // 1ms TTL
      vi.advanceTimersByTime(10);

      // 수동으로 만료 시뮬레이션
      const raw = localStorage.getItem('ttl-key');
      if (raw) {
        const item = JSON.parse(raw);
        item.expiresAt = new Date(Date.now() - 1000).toISOString();
        localStorage.setItem('ttl-key', JSON.stringify(item));
      }

      expect(StorageManager.get('ttl-key')).toBeNull();
    });
  });

  describe('remove', () => {
    it('removes a stored value', () => {
      StorageManager.set('remove-key', 'value');
      StorageManager.remove('remove-key');
      expect(StorageManager.get('remove-key')).toBeNull();
    });
  });

  describe('isExpired', () => {
    it('returns true for non-existent key', () => {
      expect(StorageManager.isExpired('no-key')).toBe(true);
    });

    it('returns false for non-expiring item', () => {
      StorageManager.set('no-ttl', 'value');
      expect(StorageManager.isExpired('no-ttl')).toBe(false);
    });
  });
});
