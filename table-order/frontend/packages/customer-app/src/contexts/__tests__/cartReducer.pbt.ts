import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';
import { cartReducer, calculateItemTotal, calculateCartTotal, INITIAL_CART_STATE } from '../cartReducer';
import type { CartState, CartItem, SelectedOption, MenuItem } from '@table-order/shared';

// --- Custom Generators (PBT-07) ---

const arbitraryOptionItem = fc.record({
  groupId: fc.uuid(),
  groupName: fc.string({ minLength: 1, maxLength: 10 }),
  optionId: fc.uuid(),
  optionName: fc.string({ minLength: 1, maxLength: 10 }),
  additionalPrice: fc.integer({ min: 0, max: 5000 }),
});

const arbitraryMenuItem: fc.Arbitrary<MenuItem> = fc.record({
  id: fc.uuid(),
  categoryId: fc.uuid(),
  storeId: fc.uuid(),
  name: fc.string({ minLength: 1, maxLength: 20 }),
  price: fc.integer({ min: 100, max: 100000 }),
  description: fc.option(fc.string({ maxLength: 50 }), { nil: undefined }),
  imageUrl: fc.option(fc.webUrl(), { nil: undefined }),
  sortOrder: fc.integer({ min: 0, max: 100 }),
  optionGroups: fc.constant([]),
});

const arbitraryQuantity = fc.integer({ min: 1, max: 99 });

describe('cartReducer — Property-Based Tests', () => {
  describe('Invariant: totalAmount = sum(items.itemTotal) (PBT-03)', () => {
    it('totalAmount is always consistent with items after ADD_ITEM', () => {
      fc.assert(
        fc.property(
          arbitraryMenuItem,
          fc.array(arbitraryOptionItem, { minLength: 0, maxLength: 3 }),
          arbitraryQuantity,
          (menuItem, options, quantity) => {
            const state = cartReducer(INITIAL_CART_STATE, {
              type: 'ADD_ITEM',
              payload: { menuItem, options, quantity },
            });

            expect(state.totalAmount).toBe(calculateCartTotal(state.items));
            expect(state.totalAmount).toBeGreaterThanOrEqual(0);
          },
        ),
        { numRuns: 200 },
      );
    });
  });

  describe('Invariant: itemTotal = (price + optionsSum) * quantity (PBT-03)', () => {
    it('each item total is correctly calculated', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 100, max: 100000 }),
          fc.array(fc.integer({ min: 0, max: 5000 }), { minLength: 0, maxLength: 5 }),
          arbitraryQuantity,
          (price, optionPrices, quantity) => {
            const options: SelectedOption[] = optionPrices.map((p, i) => ({
              groupId: `g${i}`,
              groupName: `Group ${i}`,
              optionId: `o${i}`,
              optionName: `Option ${i}`,
              additionalPrice: p,
            }));

            const total = calculateItemTotal(price, options, quantity);
            const expected = (price + optionPrices.reduce((s, p) => s + p, 0)) * quantity;

            expect(total).toBe(expected);
            expect(total).toBeGreaterThanOrEqual(0);
          },
        ),
        { numRuns: 500 },
      );
    });
  });

  describe('Invariant: quantity always in [1, 99] (PBT-03)', () => {
    it('UPDATE_QUANTITY clamps to valid range', () => {
      fc.assert(
        fc.property(
          arbitraryMenuItem,
          fc.integer({ min: -100, max: 200 }),
          (menuItem, newQuantity) => {
            // 먼저 아이템 추가
            const stateWithItem = cartReducer(INITIAL_CART_STATE, {
              type: 'ADD_ITEM',
              payload: { menuItem, options: [], quantity: 1 },
            });

            const cartItemId = stateWithItem.items[0]?.cartItemId;
            if (!cartItemId) return;

            const updated = cartReducer(stateWithItem, {
              type: 'UPDATE_QUANTITY',
              payload: { cartItemId, quantity: newQuantity },
            });

            // 수량 0 이하면 삭제됨
            if (newQuantity <= 0) {
              expect(updated.items.length).toBe(0);
            } else {
              const item = updated.items.find((i) => i.cartItemId === cartItemId);
              if (item) {
                expect(item.quantity).toBeGreaterThanOrEqual(1);
                expect(item.quantity).toBeLessThanOrEqual(99);
              }
            }
          },
        ),
        { numRuns: 200 },
      );
    });
  });

  describe('Invariant: totalAmount >= 0 always (PBT-03)', () => {
    it('totalAmount never goes negative after any sequence of actions', () => {
      fc.assert(
        fc.property(
          fc.array(
            fc.oneof(
              fc.record({
                type: fc.constant('ADD_ITEM' as const),
                menuItem: arbitraryMenuItem,
                options: fc.array(arbitraryOptionItem, { maxLength: 2 }),
                quantity: arbitraryQuantity,
              }),
              fc.record({ type: fc.constant('CLEAR_CART' as const) }),
            ),
            { minLength: 1, maxLength: 10 },
          ),
          (actions) => {
            let state: CartState = INITIAL_CART_STATE;

            for (const action of actions) {
              if (action.type === 'ADD_ITEM') {
                state = cartReducer(state, {
                  type: 'ADD_ITEM',
                  payload: {
                    menuItem: action.menuItem,
                    options: action.options,
                    quantity: action.quantity,
                  },
                });
              } else {
                state = cartReducer(state, { type: 'CLEAR_CART' });
              }

              expect(state.totalAmount).toBeGreaterThanOrEqual(0);
              expect(state.itemCount).toBeGreaterThanOrEqual(0);
            }
          },
        ),
        { numRuns: 100 },
      );
    });
  });
});
