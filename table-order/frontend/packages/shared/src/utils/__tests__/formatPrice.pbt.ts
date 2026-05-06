import { describe, it } from 'vitest';
import * as fc from 'fast-check';
import { formatPrice, parsePrice } from '../formatPrice';

describe('formatPrice — Property-Based Tests', () => {
  it('round-trip: parsePrice(formatPrice(n)) === n for non-negative integers', () => {
    fc.assert(
      fc.property(fc.integer({ min: 0, max: 10_000_000 }), (amount) => {
        const formatted = formatPrice(amount);
        const parsed = parsePrice(formatted);
        return parsed === amount;
      }),
      { numRuns: 1000 },
    );
  });

  it('invariant: formatted string always starts with ₩', () => {
    fc.assert(
      fc.property(fc.integer({ min: 0, max: 10_000_000 }), (amount) => {
        const formatted = formatPrice(amount);
        return formatted.startsWith('₩');
      }),
      { numRuns: 500 },
    );
  });

  it('invariant: formatted string contains only ₩, digits, and commas', () => {
    fc.assert(
      fc.property(fc.integer({ min: 0, max: 10_000_000 }), (amount) => {
        const formatted = formatPrice(amount);
        return /^₩[\d,]+$/.test(formatted);
      }),
      { numRuns: 500 },
    );
  });

  it('invariant: parsePrice always returns non-negative integer', () => {
    fc.assert(
      fc.property(fc.string(), (input) => {
        const result = parsePrice(input);
        return result >= 0 && Number.isInteger(result);
      }),
      { numRuns: 500 },
    );
  });
});
