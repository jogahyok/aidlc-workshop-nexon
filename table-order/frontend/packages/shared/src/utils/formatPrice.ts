/**
 * 숫자를 한국 원화 형식으로 포맷합니다.
 * @example formatPrice(12000) → "₩12,000"
 */
export function formatPrice(amount: number): string {
  return `₩${amount.toLocaleString('ko-KR')}`;
}

/**
 * 포맷된 가격 문자열에서 숫자를 추출합니다.
 * @example parsePrice("₩12,000") → 12000
 */
export function parsePrice(formatted: string): number {
  const cleaned = formatted.replace(/[₩,\s]/g, '');
  const parsed = parseInt(cleaned, 10);
  return isNaN(parsed) ? 0 : parsed;
}
