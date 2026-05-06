import { Typography, type TypographyProps } from '@mui/material';
import { formatPrice } from '../utils/formatPrice';

interface PriceDisplayProps extends Omit<TypographyProps, 'children'> {
  amount: number;
}

export function PriceDisplay({ amount, ...typographyProps }: PriceDisplayProps) {
  return (
    <Typography data-testid="price-display" fontWeight="bold" {...typographyProps}>
      {formatPrice(amount)}
    </Typography>
  );
}
