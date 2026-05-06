import { describe, it, expect } from 'vitest';
import { formatPrice, parsePrice } from '../formatPrice';

describe('formatPrice', () => {
  it('formats zero correctly', () => {
    expect(formatPrice(0)).toBe('₩0');
  });

  it('formats positive integers with comma separators', () => {
    expect(formatPrice(1000)).toBe('₩1,000');
    expect(formatPrice(12000)).toBe('₩12,000');
    expect(formatPrice(1000000)).toBe('₩1,000,000');
  });

  it('formats small amounts without commas', () => {
    expect(formatPrice(100)).toBe('₩100');
    expect(formatPrice(999)).toBe('₩999');
  });
});

describe('parsePrice', () => {
  it('parses formatted price string to number', () => {
    expect(parsePrice('₩12,000')).toBe(12000);
    expect(parsePrice('₩1,000,000')).toBe(1000000);
  });

  it('parses plain number string', () => {
    expect(parsePrice('12000')).toBe(12000);
  });

  it('returns 0 for invalid input', () => {
    expect(parsePrice('')).toBe(0);
    expect(parsePrice('abc')).toBe(0);
  });
});
